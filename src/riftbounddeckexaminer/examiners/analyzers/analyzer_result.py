from dataclasses import dataclass, field
from pprint import pprint


@dataclass
class AnalyzerResult:

    excluded_cards: list[str] = field(default_factory=lambda: [])
    excluded_decks: int = 0
    combined_chosen_champs: dict[str, float] = field(default_factory=lambda: {})
    combined_main_deck: dict[str, float] = field(default_factory=lambda: {})
    combined_battlefields: dict[str, float] = field(default_factory=lambda: {})
    combined_runes: dict[str, float] = field(default_factory=lambda: {})
    combined_sideboards: dict[str, float] = field(default_factory=lambda: {})

    def pretty_print(self):
        pprint(self.combined_chosen_champs)
        pprint(self.combined_main_deck)
        pprint(self.combined_battlefields)
        pprint(self.combined_runes)
        pprint(self.combined_sideboards)
