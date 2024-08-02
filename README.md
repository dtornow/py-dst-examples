# Detecting Race Conditions

**tl;dr** This example explores how Resonate's **Determinisitic Simulation Testing** capabilities enable you to detect and address a variety of concurrency issues such as race conditions.

## How to run

### Using [rye](https://rye.astral.sh) (Recommended)

1. Setup project's virtual environment and install dependencies
```zsh
rye sync
```

2. Run tests
```zsh
rye test
```

### Using pip

1. Install dependencies
```zsh
pip install -r requirements-dev.lock
```

4. Run tests
```zsh
pytest
```