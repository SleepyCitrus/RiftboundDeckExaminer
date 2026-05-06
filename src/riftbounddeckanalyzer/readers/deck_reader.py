from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import TextIO

from riftbounddeckanalyzer.analyzers.deck_analyzer import DeckAnalyzer
from riftbounddeckanalyzer.decks.deck import DATE_FORMAT, Deck

decks_path = Path(f"{Path.cwd()}/src/riftbounddeckanalyzer/data/decklists")


@dataclass
class DeckReader:

    def get_user_input[T](
        self, options: dict[str, T], prompt: str = ""
    ) -> tuple[str, T]:
        """
        Options should be a key-value pair consisting of the name of the object and the
        object iself. Prompt (optional) is printed before the choices in numerical order.

        Returns the name of the selected object and the selected object itself.
        """
        options_as_numbers = defaultdict()

        for idx, (key, value) in enumerate(options.items()):
            options_as_numbers[idx + 1] = key

        option_list = [""]
        for option_key, option_val in options_as_numbers.items():
            option_list.append(f"{option_key}. {option_val}")

        full_prompt = prompt + "\n".join(option_list) + "\n"
        retry_prompt = "\nInvalid input, retry:\n" + full_prompt

        retry = False
        first_run = True
        while True:
            if retry:
                full_prompt = retry_prompt
            user_choice = input(full_prompt)

            if user_choice.isdigit() and int(user_choice) in options_as_numbers:
                return (
                    options_as_numbers[int(user_choice)],
                    options[options_as_numbers[int(user_choice)]],
                )

            retry = True

    def read_date(self, file: TextIO) -> str:
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
            with open(deck_file, "r") as f:
                deck = Deck()
                skip = False
                for l in f:
                    line = l.strip()
                    if "Date:" in line:
                        date = self.read_date(f)
                        if not date:
                            # Bad file format, skip this deck
                            skip = True
                            break
                        deck.date = datetime.strptime(date, DATE_FORMAT)
                    elif "Legend:" in line:
                        legend, _ = self.read_single_line(f)
                        if not legend:
                            # Bad file format, skip this deck
                            skip = True
                            break
                        deck.legend = legend
                    elif "Champion:" in line:
                        chosen_champ, _ = self.read_single_line(f)
                        if not chosen_champ:
                            # Bad file format, skip this deck
                            skip = True
                            break
                        deck.chosen_champion = chosen_champ
                    elif "MainDeck:" in line:
                        cards = self.read_block(f)
                        deck.main_deck = cards
                    elif "Battlefields:" in line:
                        cards = self.read_block(f)
                        deck.battlefields = cards
                    elif "Rune Pool:" in line:
                        cards = self.read_block(f)
                        deck.runes = cards
                    elif "Sideboard:" in line:
                        cards = self.read_block(f)
                        deck.sideboard = cards

                if not skip:
                    # Process parsed deck information
                    valid_decks.append(deck)

        return valid_decks

    def pick_legend(self):
        """
        Looks through src/riftbounddeckanalyzer/data to determine which legend to compile
        deck information about.
        """
        legends = {
            x.as_posix().split("/")[-1]: x for x in decks_path.iterdir() if x.is_dir()
        }

        legend_name, legend_path = self.get_user_input(
            legends, "Pick the legend to compile deck information about:"
        )
        decks = self.compile_decks(list(legend_path.glob("*.txt")))

        analyzer = DeckAnalyzer(decks)
        analyzer.aggregate().pretty_print()

        output_path = Path(
            f"{Path.cwd()}/src/riftbounddeckanalyzer/data/analyzer/{legend_name}.json"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(
                asdict(analyzer, dict_factory=analyzer.exclude_decks),
                f,
                indent=4,
                default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o),
            )

            print(f"See full output at: {output_path.as_posix()}")


def main_function():
    DeckReader().pick_legend()


if __name__ == "__main__":
    main_function()
