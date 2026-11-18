import sqlite3
from datetime import date
from pathlib import Path
from typing import List, Optional

from .models import Expense

DEFAULT_PATH = Path.home() / ".expense_tracker" / "expenses.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL CHECK (amount > 0),
    category TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    spent_on TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_expenses_spent_on ON expenses (spent_on);
"""


def _to_expense(row: sqlite3.Row) -> Expense:
    return Expense(
        id=row["id"],
        amount=row["amount"],
        category=row["category"],
        note=row["note"],
        spent_on=date.fromisoformat(row["spent_on"]),
    )


class ExpenseStore:
    def __init__(self, path=DEFAULT_PATH):
        target = str(path)
        if target != ":memory:":
            Path(target).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(target)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self) -> None:
        self._conn.close()

    def add(self, expense: Expense) -> Expense:
        category = expense.category.strip().lower()
        if not category:
            raise ValueError("category cannot be empty")
        cursor = self._conn.execute(
            "INSERT INTO expenses (amount, category, note, spent_on) VALUES (?, ?, ?, ?)",
            (expense.amount, category, expense.note.strip(), expense.spent_on.isoformat()),
        )
        self._conn.commit()
        return Expense(
            id=cursor.lastrowid,
            amount=expense.amount,
            category=category,
            note=expense.note.strip(),
            spent_on=expense.spent_on,
        )

    def get(self, expense_id: int) -> Optional[Expense]:
        row = self._conn.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
        return _to_expense(row) if row else None

    def remove(self, expense_id: int) -> bool:
        cursor = self._conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def list(
        self,
        category: Optional[str] = None,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> List[Expense]:
        clauses, params = [], []
        if category:
            clauses.append("category = ?")
            params.append(category.strip().lower())
        if start:
            clauses.append("spent_on >= ?")
            params.append(start.isoformat())
        if end:
            clauses.append("spent_on <= ?")
            params.append(end.isoformat())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._conn.execute(
            f"SELECT * FROM expenses {where} ORDER BY spent_on DESC, id DESC", params
        ).fetchall()
        return [_to_expense(row) for row in rows]
