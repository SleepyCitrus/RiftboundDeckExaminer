from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from riftbounddeckexaminer.examiners.readers.deck_reader import DeckReader
from seleniumbase import SB, BaseCase
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from riftbounddeckexaminer.riftbound.card import Card, CardType
from riftbounddeckexaminer.riftbound.deck import DATE_FORMAT, Deck
from riftbounddeckexaminer.utils.util import (
    get_user_input,
    get_user_input_freeform_int,
    unpack_single_dict_entry,
)

BASE_URL = "https://riftdecks.com/"
TIMEOUT_SEC = 2
DEFAULT_DECK_LIMIT = 10


MAIN_DECK_CARD_TYPES = [CardType.CHAMPION, CardType.UNIT, CardType.GEAR, CardType.SPELL]

TOP_CUT_OPTIONS = {
    "Winners": "Winners",
    "Top 2": "Top 2",
    "Top 4": "Top 4",
    "Top 8": "Top 8",
    "Top 16": "Top 16",
    "Top 32": "Top 32",
}


@dataclass
class ConstructedLegend:
    name: str
    link: str
    # Maybe want to include the rest of the parsed data


@dataclass
class RiftdecksDeckReader(DeckReader):

    @classmethod
    def reader_description(cls) -> str:
        return "Pulls the most recent deck information from Riftdecks (requires Chrome installation)."

    unique_cards: set[Card] = field(default_factory=lambda: set())

    def pick_legend(self, sb: BaseCase) -> tuple[str, ConstructedLegend]:
        sb.uc_open_with_reconnect(f"{BASE_URL}legends", 5)
        # sb.uc_gui_click_captcha()
        sb.wait_for_element("div#metagame")
        divs_with_tables: list[WebElement] = sb.find_elements("#metagame")

        legend_data: dict[str, ConstructedLegend] = defaultdict()
        for div in divs_with_tables:
            table_rows = div.find_elements(
                by=By.CSS_SELECTOR, value="table > tbody > tr"
            )
            for row in table_rows:
                legend_link = row.get_attribute("data-href")
                # Find cells within each row
                cells = row.find_elements(by=By.CSS_SELECTOR, value="td")
                # Extract text from cells
                legend_name = cells[1].text.split("\n")[0]

                # Remove unnecessary carriage return
                legend_name.replace("\r", "")
                constructed_legend = ConstructedLegend(
                    name=legend_name,
                    link=legend_link if isinstance(legend_link, str) else "",
                )
                legend_data[legend_name] = constructed_legend

        return unpack_single_dict_entry(
            get_user_input(
                options=legend_data,
                prompt="Select legend to analyze deck information about:",
            )
        )

    def get_most_recent_decks(
        self, sb: BaseCase, limit=DEFAULT_DECK_LIMIT
    ) -> list[Deck]:
        discovered_decks: list[Deck] = []

        for i in range(limit):
            recent_decks = sb.find_elements(
                selector="table > tbody > tr", by=By.CSS_SELECTOR, limit=limit
            )
            if len(recent_decks) <= i:
                print(f"No more decks to process.")
                return discovered_decks

            recent_deck: WebElement = recent_decks[i]
            deck_link = recent_deck.get_attribute("data-href")
            deck_cells = recent_deck.find_elements(by=By.CSS_SELECTOR, value="td")
            placement = int("".join(filter(str.isdigit, deck_cells[0].text.strip())))
            tournament_size = int(
                deck_cells[5]
                .find_elements(by=By.CSS_SELECTOR, value="div")[2]
                .text.strip()
                .split(" ")[0]
            )
            date = datetime.strptime(deck_cells[8].text, DATE_FORMAT)

            sb.click(f"tr[data-href='{deck_link}']")

            sb.wait_for_element("div#text-decklist-container")
            decklist_div = sb.find_element("div#text-decklist-container")

            deck = Deck(placement=placement, tournament_size=tournament_size, date=date)
            if isinstance(decklist_div, WebElement):
                rows = decklist_div.find_elements(
                    by=By.CSS_SELECTOR, value="table > tbody > tr"
                )
                for row in rows:
                    card_type = row.get_attribute("data-card-type")
                    if card_type and card_type in CardType:
                        cells = row.find_elements(by=By.CSS_SELECTOR, value="td")
                        # Example cells: ['', '1 ', 'Leblanc, Deceiver', '$0.22', '', '']
                        copies = int(cells[1].text.strip())
                        card_name = cells[2].text
                        if card_type in MAIN_DECK_CARD_TYPES:
                            converted_card_type = card_type
                            if card_type == CardType.CHAMPION:
                                # Chosen champion should be considered a unit type
                                converted_card_type = CardType.UNIT

                            if converted_card_type not in deck.main_deck:
                                deck.main_deck[CardType(converted_card_type)] = {}
                            deck.main_deck[CardType(converted_card_type)][
                                card_name
                            ] = copies
                            unique_card = Card(
                                name=card_name, type=CardType(converted_card_type)
                            )
                            self.unique_cards.add(unique_card)

                        if card_type == CardType.CHAMPION:
                            deck.chosen_champion = card_name
                        elif card_type == CardType.LEGEND:
                            deck.legend = card_name
                        elif card_type == CardType.BATTLEFIELD:
                            deck.battlefields[card_name] = 1
                        elif card_type == CardType.RUNES:
                            deck.runes[card_name] = copies
                        elif card_type == CardType.SIDEBOARD:
                            deck.sideboard[card_name] = copies

            discovered_decks.append(deck)
            print(
                f"Found deck with tournament placement {deck.placement} out of {deck.tournament_size} players..."
            )
            sb.go_back()

        return discovered_decks

    def exclude_cards(self) -> dict[str, Card]:
        return get_user_input(
            {x.name: x for x in self.unique_cards},
            "Choose any cards to exclude deck(s) containing those cards (enter to continue):",
            multiselect=True,
        )

    def read_decks(self) -> list[Deck]:
        """
        Scrape information from Riftdecks and compile deck information for all players that placed
        in the top 16 of a 3★ tournament.
        """
        with SB(uc=True, test=True, incognito=True) as sb:
            _, legend = self.pick_legend(sb)

            top_cut, _ = unpack_single_dict_entry(
                get_user_input(
                    TOP_CUT_OPTIONS,
                    "Choose placement cutoff:",
                    multiselect=False,
                    sort_options=False,
                )
            )

            decks_to_process = get_user_input_freeform_int(
                DEFAULT_DECK_LIMIT,
                20,
                0,
                f"Choose how many decks that placed in the {top_cut} to compare:",
            )

            sb.click(f"tr[data-href='{legend.link}']")
            sb.click(f'button[data-bs-target="#filters"]')
            sb.select_option_by_text("select#hide-banned", "Hide", timeout=TIMEOUT_SEC)
            sb.select_option_by_text("select#rank", top_cut, timeout=TIMEOUT_SEC)
            sb.select_option_by_value("select#relevance", "3", timeout=TIMEOUT_SEC)
            sb.click(
                selector="//input[@value='Apply Filters']",
                by=By.XPATH,
                timeout=TIMEOUT_SEC,
            )

            print(
                f"Getting the most recent {decks_to_process} decks that are in the Top 16..."
            )
            recent_decks = self.get_most_recent_decks(sb, limit=decks_to_process)
            return recent_decks
