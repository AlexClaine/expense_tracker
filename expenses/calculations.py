from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from decouple import config

VAT_RATE = Decimal(config("VAT_RATE", default="0.16"))
CENT = Decimal("0.01")

def calculate_vat(amount, is_taxable):
    """Calculate VAT on amount before tax."""

    amount = Decimal(str(amount))

    if not is_taxable:
        return Decimal("0.00")

    return (amount * VAT_RATE).quantize(CENT, rounding=ROUND_HALF_UP)

def calculate_expense_totals(expenses):
    """
    Calculate VAT and totals for each expense.
    Summarize by category and currency to avoid mixing currencies.
    """
    processed_expenses = []
    category_totals = defaultdict(
        lambda:{
            "amount": Decimal("0.00"),
            "vat": Decimal("0.00"),
            "total": Decimal("0.00"),
        }
    )
    currency_totals = defaultdict(lambda: {
        "amount": Decimal("0.00"),
        "vat": Decimal("0.00"),
        "total": Decimal("0.00"),
    })

    for expense in expenses:
        item = dict(expense)
        amount = Decimal(str(item["amount"])).quantize(CENT)
        vat = calculate_vat(amount, item["is_taxable"])
        total = amount + vat
        currency = item["currency"]
        category = item["category"]

        item["vat_amount"] = vat
        item["total_with_tax"] = total
        processed_expenses.append(item)

        for summary in (
            category_totals[(category, currency)],
            currency_totals[currency],
        ):
            summary["amount"] += amount
            summary["vat"] += vat
            summary["total"] += total

    categories = [
        {
            "category": category,
            "currency": currency,
            **totals,
        }
        for (category, currency), totals in category_totals.items()
    ]

    currencies = [
        {
            "currency": currency,
            **totals,
        }
        for currency, totals in currency_totals.items()
    ]

    return processed_expenses, categories, currencies

