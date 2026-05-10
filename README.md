# RiftboundDeckAnalyzer

This project is meant as a lightweight analysis of Riftbound decks. For a specific legend, we can ideally determine the most central cards based on popularity, copies per deck, and other statistics.

1. Export decks from [RiftDecks](https://riftdecks.com/) to `/src/riftbounddeckexaminer/data/decklists/{legend_name}`
    1. The file should be named using the placement and tournament (e.g. **"5th at S3 Shenzhen City Challenge.txt"**). You can simply copy/paste this from the website.
    2. Include inside the file the following information if you need:
        - "Date:" followed by tournament date on the next line
        - "Tournament Size:" followed by the total number of players of that tournament
        - The card list information. You can copy/paste this from **Export this Deck > Export TXT > Copy to Clipboard**
2. Run `poetry run read-decks` and go through the interactive prompts to see the distribution of cards across all decks.
3. The result distribution uses a weighted model based on ranking/tournament size of each deck with more emphasis on better placing decks. 
4. **TODO:** Maybe add other models such as a co-occurrence model so that card combos (e.g. Unsung Hero + B.F. Sword) are coupled tightly in the rankings.

## Installation

Run `poetry install` prior to running any scripts. (or `pipx install poetry` prior to that if poetry is not installed yet)

## Run Scripts

To run a specific script, look at the aliases defined in `[project.scripts]` in `pyproject.toml`:

```
➜ poetry run read-decks
```

Alternatively, to run specific files use the poetry run python command (assuming python points to python3)

```
➜ poetry run python src/riftbounddeckexaminer/readers/deck_reader.py
```
