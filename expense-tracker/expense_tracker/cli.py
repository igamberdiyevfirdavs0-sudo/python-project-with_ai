import argparse
import calendar
import sys
from datetime import date, datetime

from . import __version__
from .database import DEFAULT_PATH, ExpenseStore
from .exporter import export_csv
from .models import Expense
from .reports import by_category, by_month, total


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid date '{value}', expected YYYY-MM-DD")


def parse_month(value):
    try:
        first = datetime.strptime(value, "%Y-%m").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid month '{value}', expected YYYY-MM")
    last_day = calendar.monthrange(first.year, first.month)[1]
    return first, first.replace(day=last_day)


def positive_amount(value):
    try:
        amount = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a number")
    if amount <= 0:
        raise argparse.ArgumentTypeError("amount must be greater than zero")
    return round(amount, 2)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="Track and review personal expenses from the command line.",
    )
    parser.add_argument("--db", default=str(DEFAULT_PATH), help="path to the database file")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="record a new expense")
    add.add_argument("amount", type=positive_amount)
    add.add_argument("category")
    add.add_argument("-n", "--note", default="")
    add.add_argument("-d", "--date", type=parse_date, default=None)

    listing = commands.add_parser("list", help="show recorded expenses")
    listing.add_argument("-c", "--category")
    listing.add_argument("-m", "--month", type=parse_month)
    listing.add_argument("-l", "--limit", type=int, default=0)

    remove = commands.add_parser("remove", help="delete an expense by id")
    remove.add_argument("id", type=int)

    summary = commands.add_parser("summary", help="spending totals by category and month")
    summary.add_argument("-m", "--month", type=parse_month)

    export = commands.add_parser("export", help="write expenses to a CSV file")
    export.add_argument("output")
    export.add_argument("-m", "--month", type=parse_month)

    return parser


def month_bounds(args):
    return args.month if args.month else (None, None)


def render_table(expenses):
    header = f"{'ID':>4}  {'Date':<10}  {'Category':<14}  {'Amount':>12}  Note"
    lines = [header, "-" * len(header)]
    for item in expenses:
        lines.append(
            f"{item.id:>4}  {item.spent_on.isoformat():<10}  {item.category:<14.14}  "
            f"{item.amount:>12,.2f}  {item.note}"
        )
    return "\n".join(lines)


def handle_add(store, args):
    saved = store.add(
        Expense(None, args.amount, args.category, args.note, args.date or date.today())
    )
    print(f"Saved expense #{saved.id}: {saved.amount:,.2f} for {saved.category}")
    return 0


def handle_list(store, args):
    start, end = month_bounds(args)
    expenses = store.list(category=args.category, start=start, end=end)
    if args.limit > 0:
        expenses = expenses[: args.limit]
    if not expenses:
        print("No expenses found.")
        return 0
    print(render_table(expenses))
    print(f"\n{len(expenses)} expenses, total {total(expenses):,.2f}")
    return 0


def handle_remove(store, args):
    if store.remove(args.id):
        print(f"Removed expense #{args.id}")
        return 0
    print(f"No expense with id {args.id}", file=sys.stderr)
    return 1


def handle_summary(store, args):
    start, end = month_bounds(args)
    expenses = store.list(start=start, end=end)
    if not expenses:
        print("No expenses found.")
        return 0
    grand_total = total(expenses)
    print(f"Total spent: {grand_total:,.2f} across {len(expenses)} expenses\n")
    for category, amount in by_category(expenses).items():
        share = amount / grand_total * 100
        print(f"{category:<14.14} {amount:>12,.2f} {share:>5.1f}%  {'#' * int(share // 5)}")
    if not args.month:
        print("\nBy month")
        for month, amount in by_month(expenses).items():
            print(f"{month}  {amount:>12,.2f}")
    return 0


def handle_export(store, args):
    start, end = month_bounds(args)
    count = export_csv(store.list(start=start, end=end), args.output)
    print(f"Exported {count} expenses to {args.output}")
    return 0


HANDLERS = {
    "add": handle_add,
    "list": handle_list,
    "remove": handle_remove,
    "summary": handle_summary,
    "export": handle_export,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    with ExpenseStore(args.db) as store:
        return HANDLERS[args.command](store, args)
