from collections import defaultdict
from typing import Dict, Iterable

from .models import Expense


def total(expenses: Iterable[Expense]) -> float:
    return round(sum(item.amount for item in expenses), 2)


def by_category(expenses: Iterable[Expense]) -> Dict[str, float]:
    totals = defaultdict(float)
    for item in expenses:
        totals[item.category] += item.amount
    ranked = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    return {name: round(amount, 2) for name, amount in ranked}


def by_month(expenses: Iterable[Expense]) -> Dict[str, float]:
    totals = defaultdict(float)
    for item in expenses:
        totals[item.spent_on.strftime("%Y-%m")] += item.amount
    return {month: round(totals[month], 2) for month in sorted(totals)}
