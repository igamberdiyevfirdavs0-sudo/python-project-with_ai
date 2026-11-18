import csv
from pathlib import Path
from typing import Iterable

from .models import Expense

FIELDS = ["id", "date", "category", "amount", "note"]


def export_csv(expenses: Iterable[Expense], destination) -> int:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        for item in expenses:
            writer.writerow(
                [item.id, item.spent_on.isoformat(), item.category, f"{item.amount:.2f}", item.note]
            )
            count += 1
    return count
