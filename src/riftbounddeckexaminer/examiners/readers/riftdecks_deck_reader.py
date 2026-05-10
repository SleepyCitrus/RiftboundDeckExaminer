from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from riftbounddeckexaminer.examiners.readers.deck_reader import DeckReader
from seleniumbase import BaseCase
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from riftbounddeckexaminer.riftbound.deck import DATE_FORMAT, Deck
from riftbounddeckexaminer.utils.util import get_user_input, unpack_single_dict_entry

BASE_URL = "https://riftdecks.com/"
TIMEOUT_SEC = 2
DECK_LIMIT = 1


class DataCardType(StrEnum):
    LEGEND = "legend"
    CHAMPION = "champion"
    UNIT = "unit"
    SPELL = "spell"
    BATTLEFIELD = "battlefields"
    RUNES = "runes"
    SIDEBOARD = "sideboard"


@dataclass
class ConstructedLegend:
    name: str
    link: str
    # Maybe want to include the rest of the parsed data


@dataclass
class RiftdecksDeckReader(DeckReader):

    unique_cards: set = field(default_factory=lambda: set())

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

    def get_most_recent_decks(self, sb: BaseCase, limit=DECK_LIMIT):
        recent_decks: list[WebElement] = sb.find_elements(
            selector="table > tbody > tr", by=By.CSS_SELECTOR, limit=limit
        )
        for recent_deck in recent_decks:
            deck_link = recent_deck.get_attribute("data-href")
            deck_cells = recent_deck.find_elements(by=By.CSS_SELECTOR, value="td")
            placement = int(deck_cells[0].text.strip()[1])
            tournament_size = int(
                deck_cells[5]
                .find_elements(by=By.CSS_SELECTOR, value="div")[1]
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
                    if card_type in DataCardType:
                        cells = row.find_elements(by=By.CSS_SELECTOR, value="td")
                        # Example cells: ['', '1 ', 'Leblanc, Deceiver', '$0.22', '', '']
                        copies = int(cells[1].text.strip())
                        card_name = cells[2].text

    def exclude_cards(self) -> dict[str, str]: ...

    def read_decks(self):
        """ "
        Scrape information from Riftdecks and compile deck information for all players that placed
        in the top 16 of a 3★ tournament.
        """
        with SB(uc=True, incognito=True) as sb:
            name, legend = self.pick_legend(sb)

            sb.click(f"tr[data-href='{legend.link}']")
            sb.click(f'button[data-bs-target="#filters"]')
            sb.select_option_by_text("select#hide-banned", "Hide", timeout=TIMEOUT_SEC)
            sb.select_option_by_text("select#rank", "Top 16", timeout=TIMEOUT_SEC)
            sb.select_option_by_value("select#relevance", "3", timeout=TIMEOUT_SEC)
            sb.click(
                selector="//input[@value='Apply Filters']",
                by=By.XPATH,
                timeout=TIMEOUT_SEC,
            )

            print("happy happy happy")

            self.get_most_recent_decks(sb)

            # https://riftdecks.com/legends/constructed/leblanc-deceiver?deck_type=tournament&metagame_id=3&hide_banned=1&rank=top16&relevance=3
            # https://riftdecks.com/legends/constructed/leblanc-deceiver?metagame_id=3&deck_type=tournament&hide_banned=1&rank=top16&relevance=3
