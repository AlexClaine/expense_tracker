from decimal import Decimal

from django.test import SimpleTestCase

from expenses.calculations import (
    calculate_vat,
    calculate_expense_totals,
)


class VATCalculationTests(SimpleTestCase):

    def test_taxable_expense(self):
        self.assertEqual(
            calculate_vat(Decimal("1000.00"), True),
            Decimal("160.00"),
        )

    def test_non_taxable_expense(self):
        self.assertEqual(
            calculate_vat(Decimal("1000.00"), False),
            Decimal("0.00"),
        )

    def test_vat_rounds_to_two_decimal_places(self):
        self.assertEqual(
            calculate_vat(Decimal("10.05"), True),
            Decimal("1.61"),
        )