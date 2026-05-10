from dataclasses import dataclass

from riftbounddeckexaminer.examiners.analyzers.analyzer_result import AnalyzerResult
from riftbounddeckexaminer.riftbound.deck import Deck


@dataclass
class DeckAnalyzer:

    decks: list[Deck]
    excluded_cards: list[str]

    def aggregate(self) -> AnalyzerResult:
        # Default
        return AnalyzerResult()

    def output_to_json(self, results: AnalyzerResult):
        # Default
        ...
