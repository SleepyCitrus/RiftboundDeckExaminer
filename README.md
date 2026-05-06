# RiftboundDeckAnalyzer

This project is meant as a lightweight analysis of Riftbound decks. For a specific legend, we can ideally determine the most central cards based on popularity, copies per deck, and other statistics.

1. Upload decks from [RiftDecks](https://riftdecks.com/) to `/src/riftbounddeckanalyzer/data/decklists/{legend_name}`
2. Run `poetry run read-decks` and go through the interactive prompts to see the distribution of cards across all decks.
3. **TODO:** Update the distribution to use a weighted model based on ranking/winrate of each deck and/or a co-occurrence model so that key-card combos (e.g. Unsung Hero + B.F. Sword) are rated higher.

## Installation

Run `poetry install` prior to running any scripts. (or `pipx install poetry` prior to that if poetry is not installed yet)

## Run Scripts

To run a specific script, look at the aliases defined in `[project.scripts]` in `pyproject.toml`:

```
➜ poetry run read-decks
```

Alternatively, to run specific files use the poetry run python command (assuming python points to python3)

```
➜ poetry run python src/riftbounddeckanalyzer/readers/deck_reader.py
```
