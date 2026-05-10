from dataclasses import dataclass, field
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"
DEFAULT_TOURNAMENT_SIZE = 128


@dataclass
class Deck:

    placement: int = 1
    tournament_size: int = DEFAULT_TOURNAMENT_SIZE
    date: datetime = datetime.now()
    legend: str = ""
    chosen_champion: str = ""
    main_deck: dict[str, int] = field(default_factory=lambda: {})
    battlefields: dict[str, int] = field(default_factory=lambda: {})
    runes: dict[str, int] = field(default_factory=lambda: {})
    sideboard: dict[str, int] = field(default_factory=lambda: {})

    @property
    def placement_weight(self):
        return self.tournament_size / self.placement
