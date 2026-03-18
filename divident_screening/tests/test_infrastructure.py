"""
Tests for Infrastructure industry formula verification.
Validates that asx_scorer.py calculations match score_system.md definitions.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_formula_base import FormulaTestBase, VerificationReport
from asx_scorer import ScoringSystem


class TestInfrastructureFormulas(FormulaTestBase):
    """Test all formula calculations for Infrastructure industry."""

    def setUp(self):
        """Load APA test data."""
        self.test_data = self.load_test_data('apa_standard.json')
        self.scorer = ScoringSystem(self.test_data)
        self.report = VerificationReport()

    def test_ebitda_margin_value(self):
        """Verify EBITDA Margin value from ratios."""
        ebitda_margin = self.scorer._get_value('EBITDA Margin')

        expected_margin = self.test_data['expected_results']['EBITDA Margin']['expected']

        if ebitda_margin:
            passed, msg = self.verify_formula('EBITDA Margin', ebitda_margin, expected_margin)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            # Try calculating from components
            ebitda = self.scorer._get_value('EBITDA')
            revenue = self.scorer._get_value('Revenue')
            if ebitda and revenue and revenue > 0:
                calculated_margin = (ebitda / revenue) * 100
                print(f"\n[DEBUG] EBITDA Margin calculated: {calculated_margin}")
                passed, msg = self.verify_formula('EBITDA Margin (calculated)', calculated_margin, expected_margin)
                print(f"\n{msg}")
                self.assertTrue(passed, msg)
            else:
                self.fail("EBITDA Margin value not found")

    def test_cash_conversion_calculation(self):
        """Verify Cash Conversion formula: Operating Cash Flow / EBITDA"""
        operating_cf = self.scorer._get_value('Operating Cash Flow')
        ebitda = self.scorer._get_value('EBITDA')

        print(f"\n[DEBUG] Operating CF: {operating_cf}, EBITDA: {ebitda}")

        expected_cc = self.test_data['expected_results']['Cash Conversion']['expected']

        if operating_cf and ebitda and ebitda > 0:
            calculated_cc = (operating_cf / ebitda) * 100
            print(f"[DEBUG] Cash Conversion calculated: {calculated_cc}")
            passed, msg = self.verify_formula('Cash Conversion', calculated_cc, expected_cc)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("Cannot calculate Cash Conversion")

    def test_interest_cover_calculation(self):
        """Verify Interest Coverage formula: EBIT / Interest Expense"""
        ebit = self.scorer._get_value('EBIT', 'Operating Income')
        interest_expense = self.scorer._get_value('Interest Expense')

        print(f"\n[DEBUG] EBIT: {ebit}, Interest Expense: {interest_expense}")

        expected_ic = self.test_data['expected_results']['Interest Cover']['expected']

        if ebit and interest_expense and interest_expense > 0:
            calculated_ic = ebit / interest_expense
            print(f"[DEBUG] Interest Cover calculated: {calculated_ic}")
            passed, msg = self.verify_formula('Interest Cover', calculated_ic, expected_ic)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("Cannot calculate Interest Cover")

    def test_ev_ebitda_calculation(self):
        """Verify EV/EBITDA formula: (Market Cap + Debt - Cash) / EBITDA"""
        market_cap = self.scorer._get_value('Market Capitalization')
        total_debt = self.scorer._get_value('Total Debt')
        cash = self.scorer._get_value('Cash & Equivalents')
        ebitda = self.scorer._get_value('EBITDA')

        print(f"\n[DEBUG] Market Cap: {market_cap}, Debt: {total_debt}, Cash: {cash}, EBITDA: {ebitda}")

        expected_ev = self.test_data['expected_results']['EV/EBITDA']['expected']

        if all([market_cap, total_debt, cash is not None, ebitda]) and ebitda > 0:
            calculated_ev = (market_cap + total_debt - cash) / ebitda
            print(f"[DEBUG] EV/EBITDA calculated: {calculated_ev}")
            passed, msg = self.verify_formula('EV/EBITDA', calculated_ev, expected_ev)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("Cannot calculate EV/EBITDA")


def run_tests():
    """Run all infrastructure tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInfrastructureFormulas)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
