from riftbounddeckexaminer.riftbound.deck import Deck


class DeckReader:

    def exclude_cards(self) -> dict[str, str]:
        # Default implementation
        return {}

    def read_decks(self) -> list[Deck]:
        # Default implementation
        return []
