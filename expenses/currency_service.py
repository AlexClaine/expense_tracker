
from decimal import Decimal, ROUND_HALF_UP

import requests
from django.core.cache import cache


API_BASE = "https://api.frankfurter.dev/v2"
CENT = Decimal("0.01")


def get_exchange_rate(source, target):
    """Return the latest rate from one currency to another."""
    source = source.upper()
    target = target.upper()

    if source == target:
        return Decimal("1")

    cache_key = f"exchange_rate_{source}_{target}"
    cached_rate = cache.get(cache_key)

    if cached_rate is not None:
        return Decimal(str(cached_rate))

    response = requests.get(
        f"{API_BASE}/rate/{source}/{target}",
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    rate = Decimal(str(data["rate"]))

    cache.set(cache_key, str(rate), 3600)
    return rate


def convert_amount(amount, source, target):
    """Convert a monetary amount and round to two decimal places."""
    amount = Decimal(str(amount))
    rate = get_exchange_rate(source, target)

    return (amount * rate).quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def convert_expenses(expenses, target_currency):
    """Convert expense totals, including VAT, to a reporting currency."""
    converted = []
    grand_total = Decimal("0.00")
    rates_used = {}

    for expense in expenses:
        item = dict(expense)
        source_currency = item["currency"].upper()

        if source_currency not in rates_used:
            rates_used[source_currency] = get_exchange_rate(
                source_currency,
                target_currency,
            )

        rate = rates_used[source_currency]

        item["original_currency"] = source_currency
        item["original_total"] = item["total_with_tax"]
        item["reporting_currency"] = target_currency
        item["exchange_rate"] = rate

        item["converted_total"] = (
            Decimal(str(item["total_with_tax"])) * rate
        ).quantize(CENT, rounding=ROUND_HALF_UP)

        grand_total += item["converted_total"]
        converted.append(item)

    return converted, grand_total
