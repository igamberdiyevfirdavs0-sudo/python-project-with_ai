from datetime import date

import pytest

from expense_tracker.database import ExpenseStore
from expense_tracker.models import Expense


@pytest.fixture
def store():
    with ExpenseStore(":memory:") as instance:
        yield instance


@pytest.fixture
def filled_store(store):
    rows = [
        (12.5, "food", "lunch", date(2026, 10, 3)),
        (40.0, "transport", "taxi", date(2026, 10, 15)),
        (8.25, "food", "coffee", date(2026, 11, 2)),
        (120.0, "rent", "", date(2026, 11, 5)),
    ]
    for amount, category, note, day in rows:
        store.add(Expense(None, amount, category, note, day))
    return store
