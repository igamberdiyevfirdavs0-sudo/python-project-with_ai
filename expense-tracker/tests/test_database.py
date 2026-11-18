from datetime import date

import pytest

from expense_tracker.models import Expense


def test_add_assigns_id_and_normalizes_category(store):
    saved = store.add(Expense(None, 9.99, "  Food ", " snack ", date(2026, 11, 1)))
    assert saved.id == 1
    assert saved.category == "food"
    assert saved.note == "snack"


def test_add_rejects_empty_category(store):
    with pytest.raises(ValueError):
        store.add(Expense(None, 5, "   ", "", date(2026, 11, 1)))


def test_get_returns_none_for_missing_id(store):
    assert store.get(42) is None


def test_remove(filled_store):
    assert filled_store.remove(1) is True
    assert filled_store.remove(1) is False
    assert len(filled_store.list()) == 3


def test_list_is_sorted_newest_first(filled_store):
    days = [item.spent_on for item in filled_store.list()]
    assert days == sorted(days, reverse=True)


def test_list_filters_by_category(filled_store):
    result = filled_store.list(category="FOOD")
    assert {item.category for item in result} == {"food"}
    assert len(result) == 2


def test_list_filters_by_date_range(filled_store):
    result = filled_store.list(start=date(2026, 11, 1), end=date(2026, 11, 30))
    assert len(result) == 2
