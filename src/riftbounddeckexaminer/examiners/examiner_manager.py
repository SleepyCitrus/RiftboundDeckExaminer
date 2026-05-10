from riftbounddeckexaminer.examiners.analyzers.deck_analyzer import DeckAnalyzer
from riftbounddeckexaminer.examiners.analyzers.placement_analyzer import (
    PlacementAnalyzer,
)
from riftbounddeckexaminer.examiners.readers.deck_reader import DeckReader
from riftbounddeckexaminer.examiners.readers.riftdecks_deck_reader import (
    RiftdecksDeckReader,
)
from riftbounddeckexaminer.examiners.readers.terminal_deck_reader import (
    TerminalDeckReader,
)
from riftbounddeckexaminer.utils.util import get_user_input, unpack_single_dict_entry


class ExaminerManager:

    READERS: list[DeckReader] = [TerminalDeckReader(), RiftdecksDeckReader()]
    ANALYZERS_LIST: list[type[DeckAnalyzer]] = [PlacementAnalyzer]

    def examine(self):
        # Reader
        reader_options: dict[str, DeckReader] = {}
        for reader in self.READERS:
            reader_options[reader.__class__.__name__] = reader

        _, selected_reader = unpack_single_dict_entry(
            get_user_input(options=reader_options, prompt="Select reader to use:")
        )

        decks = selected_reader.read_decks()
        excluded_cards = selected_reader.exclude_cards()

        # Analyzer
        analyzer_options: dict[str, type[DeckAnalyzer]] = {}
        for analyzer in self.ANALYZERS_LIST:
            analyzer_options[analyzer.__name__] = analyzer
        _, selected_analyzer = unpack_single_dict_entry(
            get_user_input(options=analyzer_options, prompt="Select analyzer to use:")
        )

        analyzer = selected_analyzer(
            decks=decks, excluded_cards=[x for x in excluded_cards.keys()]
        )
        analyzer.output_to_json(analyzer.aggregate())


def main_function():
    ExaminerManager().examine()


if __name__ == "__main__":
    main_function()
