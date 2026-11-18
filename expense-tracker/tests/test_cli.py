import csv

import pytest

from expense_tracker.cli import main, parse_month


@pytest.fixture
def db(tmp_path):
    return str(tmp_path / "test.db")


def run(db, *arguments):
    return main(["--db", db, *arguments])


def test_add_and_list(db, capsys):
    assert run(db, "add", "15.5", "Food", "-n", "pizza", "-d", "2026-11-10") == 0
    assert run(db, "list") == 0
    output = capsys.readouterr().out
    assert "Saved expense #1" in output
    assert "pizza" in output
    assert "15.50" in output


def test_list_empty(db, capsys):
    run(db, "list")
    assert "No expenses found." in capsys.readouterr().out


def test_remove_missing_returns_error(db, capsys):
    assert run(db, "remove", "7") == 1
    assert "No expense with id 7" in capsys.readouterr().err


def test_summary_for_month(db, capsys):
    run(db, "add", "10", "food", "-d", "2026-11-01")
    run(db, "add", "30", "rent", "-d", "2026-11-02")
    run(db, "add", "99", "food", "-d", "2026-10-02")
    capsys.readouterr()
    run(db, "summary", "-m", "2026-11")
    output = capsys.readouterr().out
    assert "Total spent: 40.00" in output
    assert "rent" in output


def test_export_writes_csv(db, tmp_path):
    run(db, "add", "5", "coffee", "-d", "2026-11-03")
    target = tmp_path / "out" / "expenses.csv"
    assert run(db, "export", str(target)) == 0
    with target.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["category"] == "coffee"
    assert rows[0]["amount"] == "5.00"


def test_invalid_amount_exits(db):
    with pytest.raises(SystemExit):
        run(db, "add", "-3", "food")


def test_parse_month_returns_bounds():
    first, last = parse_month("2026-02")
    assert first.isoformat() == "2026-02-01"
    assert last.isoformat() == "2026-02-28"
