from expense_tracker.reports import by_category, by_month, total


def test_total(filled_store):
    assert total(filled_store.list()) == 180.75


def test_total_of_nothing_is_zero():
    assert total([]) == 0


def test_by_category_is_ranked(filled_store):
    ranked = by_category(filled_store.list())
    assert list(ranked) == ["rent", "transport", "food"]
    assert ranked["food"] == 20.75


def test_by_month(filled_store):
    assert by_month(filled_store.list()) == {"2026-10": 52.5, "2026-11": 128.25}
