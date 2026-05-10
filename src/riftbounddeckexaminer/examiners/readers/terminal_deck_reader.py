from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TextIO

from riftbounddeckexaminer.examiners.readers.deck_reader import DeckReader
from riftbounddeckexaminer.examiners.readers.decklist_metadata import DecklistMetadata
from riftbounddeckexaminer.riftbound.deck import DATE_FORMAT, Deck
from riftbounddeckexaminer.utils.util import get_user_input

DECKS_PATH = Path(f"{Path.cwd()}/src/riftbounddeckexaminer/data/decklists")


@dataclass
class TerminalDeckReader(DeckReader):

    unique_cards: set[str] = field(default_factory=lambda: set())

    def read_raw_line(self, file: TextIO) -> str:
        try:
            return next(file).strip()
        except StopIteration:
            print("Reached the end of the file earlier than expected!")
        return ""

    def read_single_line(self, file: TextIO) -> tuple[str, int]:
        try:
            line = next(file).strip()
            return (line[2:], int(line[:1]))
        except StopIteration:
            print("Reached the end of the file earlier than expected!")
        return "", 0

    def read_block(self, file: TextIO) -> dict[str, int]:
        block = defaultdict(int)
        for l in file:
            if not l.strip():
                # empty line, end of block
                break
            line = l.strip()
            block[line[2:]] = int(line[:1])

        return block

    def compile_decks(self, deck_files: list[Path]) -> list[Deck]:
        valid_decks: list[Deck] = []

        for deck_file in deck_files:

            placement = int("".join(filter(str.isdigit, deck_file.name.split(" ")[0])))

            with open(deck_file, "r") as f:
                deck = Deck(placement)
                skip = False
                for l in f:
                    line = l.strip()
                    if DecklistMetadata.DATE in line:
                        date = self.read_raw_line(f)
                        if not date:
                            # Bad file format, skip this deck
                            skip = True
                            break
                        deck.date = datetime.strptime(date, DATE_FORMAT)
                    elif DecklistMetadata.TOURNAMENT_SIZE in line:
                        tournament_size = self.read_raw_line(f)
                        if not tournament_size:
                            skip = True
                            break
                        deck.tournament_size = int(tournament_size)
                    elif DecklistMetadata.LEGEND in line:
                        legend, _ = self.read_single_line(f)
                        if not legend:
                            # Bad file format, skip this deck
                            skip = True
                            break
                        deck.legend = legend
                    elif DecklistMetadata.CHAMPION in line:
                        chosen_champ, _ = self.read_single_line(f)
                        if not chosen_champ:
                            # Bad file format, skip this deck
                            skip = True
                            break
                        deck.chosen_champion = chosen_champ
                    elif DecklistMetadata.MAIN_DECK in line:
                        cards = self.read_block(f)
                        deck.main_deck = cards
                        self.unique_cards.update(cards.keys())
                    elif DecklistMetadata.BATTLEFIELDS in line:
                        cards = self.read_block(f)
                        deck.battlefields = cards
                    elif DecklistMetadata.RUNES in line:
                        cards = self.read_block(f)
                        deck.runes = cards
                    elif DecklistMetadata.SIDEBOARD in line:
                        cards = self.read_block(f)
                        deck.sideboard = cards

                if not skip:
                    # Process parsed deck information
                    valid_decks.append(deck)

        return valid_decks

    def pick_legend(self) -> tuple[str, Path]:
        """
        Looks through src/riftbounddeckexaminer/data to determine which legend to compile
        deck information about.
        """
        legends = {
            x.as_posix().split("/")[-1]: x for x in DECKS_PATH.iterdir() if x.is_dir()
        }

        user_input = get_user_input(
            legends, "Pick the legend to compile deck information about:"
        )

        return next(iter(user_input.items()))

    def exclude_cards(self) -> dict[str, str]:
        return get_user_input(
            {x: x for x in self.unique_cards},
            "Choose any decks with the following cards to exclude (enter to continue):",
            multiselect=True,
        )

    def read_decks(self) -> list[Deck]:
        """Find and return decks from local .txt files."""

        legend_name, legend_path = self.pick_legend()
        return self.compile_decks(list(legend_path.glob("*.txt")))
