from dataclasses import dataclass, field
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"


@dataclass
class Deck:

    date: datetime = datetime.now()
    legend: str = ""
    chosen_champion: str = ""
    main_deck: dict[str, int] = field(default_factory=lambda: {})
    battlefields: dict[str, int] = field(default_factory=lambda: {})
    runes: dict[str, int] = field(default_factory=lambda: {})
    sideboard: dict[str, int] = field(default_factory=lambda: {})
