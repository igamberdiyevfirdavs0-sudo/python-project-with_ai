from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Expense:
    id: Optional[int]
    amount: float
    category: str
    note: str
    spent_on: date
