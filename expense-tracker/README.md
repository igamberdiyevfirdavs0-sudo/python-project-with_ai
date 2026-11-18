# Expense Tracker

A small command line application for recording and reviewing personal expenses. Data is stored locally in a SQLite database, so there is nothing to configure and no third-party dependencies at runtime.

## Features

- Add expenses with an amount, category, optional note and date
- List expenses, filtered by category or month
- Spending summary with category shares and monthly totals
- Export any selection to CSV
- Remove entries by id
- Test suite covering the storage layer, reports and the CLI

## Requirements

Python 3.10 or newer.

## Installation

```bash
git clone https://github.com/igamberdiyevfirdavs0-sudo/expense-tracker.git
cd expense-tracker
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

On macOS or Linux, activate the environment with `source .venv/bin/activate`.

## Usage

```bash
expense-tracker add 12.5 food -n "lunch"
expense-tracker add 40 transport -n "taxi" -d 2026-11-10
expense-tracker list
expense-tracker list -c food -m 2026-11
expense-tracker summary
expense-tracker summary -m 2026-11
expense-tracker export reports/november.csv -m 2026-11
expense-tracker remove 3
```

You can also run it as a module with `python -m expense_tracker list`.

By default the database lives in `~/.expense_tracker/expenses.db`. Use `--db path/to/file.db` to point somewhere else.

### Example output

```
$ expense-tracker summary
Total spent: 180.75 across 4 expenses

rent                 120.00  66.4%  #############
transport             40.00  22.1%  ####
food                  20.75  11.5%  ##

By month
2026-10         52.50
2026-11        128.25
```

## Project structure

```
expense_tracker/
    cli.py         argument parsing and command handlers
    database.py    SQLite storage layer
    models.py      Expense dataclass
    reports.py     totals and grouping
    exporter.py    CSV export
tests/             pytest suite
```

## Running the tests

```bash
pytest
```

## License

MIT
