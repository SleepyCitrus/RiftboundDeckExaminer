from collections import defaultdict
from dataclasses import dataclass, field
from pprint import pprint
from typing import Self

from riftbounddeckanalyzer.decks.deck import Deck
from riftbounddeckanalyzer.readers.utils.util import get_user_input


@dataclass
class DeckAnalyzer:

    decks: list[Deck]
    excluded_cards: list[str]

    excluded_decks: int = 0
    combined_chosen_champs: dict[str, float] = field(default_factory=lambda: {})
    combined_main_deck: dict[str, float] = field(default_factory=lambda: {})
    combined_battlefields: dict[str, float] = field(default_factory=lambda: {})
    combined_runes: dict[str, float] = field(default_factory=lambda: {})
    combined_sideboards: dict[str, float] = field(default_factory=lambda: {})

    def exclude_base_decks(self, items):
        return {k: v for k, v in items if k != "decks"}

    def aggregate(self) -> Self:
        chosen_champs = defaultdict(int)
        main_deck = defaultdict(int)
        battlefields = defaultdict(int)
        runes = defaultdict(int)
        sideboard = defaultdict(int)

        for deck in self.decks:

            skip = False
            for excluded_card in self.excluded_cards:
                if (
                    excluded_card in deck.main_deck
                    or excluded_card in deck.battlefields
                ):
                    skip = True

            if skip:
                self.excluded_decks += 1
                continue

            chosen_champs[deck.chosen_champion] += 1

            # Consider chosen champion as part of the main deck.
            main_deck[deck.chosen_champion] += 1
            for main_card, val in deck.main_deck.items():
                main_deck[main_card] += val

            for bf, val in deck.battlefields.items():
                battlefields[bf] += val

            for rune, val in deck.runes.items():
                runes[rune] += val

            for side_card, val in deck.sideboard.items():
                sideboard[side_card] += val

        chosen_champs = {
            c: round(v / (len(self.decks) - self.excluded_decks), 2)
            for c, v in chosen_champs.items()
        }
        self.combined_chosen_champs = dict(
            sorted(chosen_champs.items(), key=lambda item: item[1], reverse=True)
        )

        main_deck = {
            c: round(v / (len(self.decks) - self.excluded_decks), 2)
            for c, v in main_deck.items()
        }
        self.combined_main_deck = dict(
            sorted(main_deck.items(), key=lambda item: item[1], reverse=True)
        )

        battlefields = {
            c: round(v / (len(self.decks) - self.excluded_decks), 2)
            for c, v in battlefields.items()
        }
        self.combined_battlefields = dict(
            sorted(battlefields.items(), key=lambda item: item[1], reverse=True)
        )
        runes = {
            c: round(v / (len(self.decks) - self.excluded_decks), 2)
            for c, v in runes.items()
        }
        self.combined_runes = dict(
            sorted(runes.items(), key=lambda item: item[1], reverse=True)
        )
        sideboard = {
            c: round(v / (len(self.decks) - self.excluded_decks), 2)
            for c, v in sideboard.items()
        }
        self.combined_sideboards = dict(
            sorted(sideboard.items(), key=lambda item: item[1], reverse=True)
        )

        return self

    def pretty_print(self):
        pprint(self.combined_chosen_champs)
        pprint(self.combined_main_deck)
        pprint(self.combined_battlefields)
        pprint(self.combined_runes)
        pprint(self.combined_sideboards)
