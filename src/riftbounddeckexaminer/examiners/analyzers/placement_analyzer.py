from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path

from riftbounddeckexaminer.examiners.analyzers.analyzer_result import AnalyzerResult
from riftbounddeckexaminer.examiners.analyzers.deck_analyzer import DeckAnalyzer
from riftbounddeckexaminer.riftbound.deck import Deck


@dataclass
class PlacementAnalyzer(DeckAnalyzer):
    """
    Uses weighted averages based on placement to determine the necessity of each card.
    """

    legend_name: str
    decks: list[Deck]
    excluded_cards: list[str]

    def exclude_base_decks(self, items):
        return {k: v for k, v in items if k != "decks"}

    def aggregate(self) -> AnalyzerResult:
        chosen_champs = defaultdict(float)
        main_deck = defaultdict(float)
        battlefields = defaultdict(float)
        runes = defaultdict(float)
        sideboard = defaultdict(float)

        valid_decks: list[Deck] = []
        total_weight = 0
        excluded_decks = 0
        for deck in self.decks:
            # get total weight
            skip = False
            for excluded_card in self.excluded_cards:
                if (
                    excluded_card in deck.main_deck
                    or excluded_card in deck.battlefields
                ):
                    skip = True

            if skip:
                excluded_decks += 1
                continue

            total_weight += deck.placement_weight
            valid_decks.append(deck)

        for deck in valid_decks:
            chosen_champs[deck.chosen_champion] += (
                1 * deck.placement_weight / total_weight
            )

            # Consider chosen champion as part of the main deck.
            main_deck[deck.chosen_champion] += 1 * deck.placement_weight / total_weight
            for main_card, val in deck.main_deck.items():
                main_deck[main_card] += val * deck.placement_weight / total_weight

            for bf, val in deck.battlefields.items():
                battlefields[bf] += val * deck.placement_weight / total_weight

            for rune, val in deck.runes.items():
                runes[rune] += val * deck.placement_weight / total_weight

            for side_card, val in deck.sideboard.items():
                sideboard[side_card] += val * deck.placement_weight / total_weight

        chosen_champs = {c: round(v, 2) for c, v in chosen_champs.items()}
        combined_chosen_champs = dict(
            sorted(chosen_champs.items(), key=lambda item: item[1], reverse=True)
        )

        main_deck = {c: round(v, 2) for c, v in main_deck.items()}
        combined_main_deck = dict(
            sorted(main_deck.items(), key=lambda item: item[1], reverse=True)
        )

        battlefields = {c: round(v, 2) for c, v in battlefields.items()}
        combined_battlefields = dict(
            sorted(battlefields.items(), key=lambda item: item[1], reverse=True)
        )
        runes = {c: round(v, 2) for c, v in runes.items()}
        combined_runes = dict(
            sorted(runes.items(), key=lambda item: item[1], reverse=True)
        )
        sideboard = {c: round(v, 2) for c, v in sideboard.items()}
        combined_sideboards = dict(
            sorted(sideboard.items(), key=lambda item: item[1], reverse=True)
        )

        return AnalyzerResult(
            excluded_cards=self.excluded_cards,
            excluded_decks=excluded_decks,
            combined_chosen_champs=combined_chosen_champs,
            combined_main_deck=combined_main_deck,
            combined_battlefields=combined_battlefields,
            combined_runes=combined_runes,
            combined_sideboards=combined_sideboards,
        )

    def output_to_json(self, results: AnalyzerResult):
        results.pretty_print()

        output_path = Path(
            f"{Path.cwd()}/src/riftbounddeckexaminer/data/analyzer/{self.legend_name}.json"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(
                asdict(results),
                f,
                indent=4,
                default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o),
            )

            print(f"See full output at: {output_path.as_posix()}")
