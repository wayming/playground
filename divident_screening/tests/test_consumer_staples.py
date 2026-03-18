"""
Tests for Consumer Staples industry formula verification.
Validates that asx_scorer.py calculations match score_system.md definitions.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_formula_base import FormulaTestBase, VerificationReport
from asx_scorer import ScoringSystem


class TestConsumerStaplesFormulas(FormulaTestBase):
    """Test all formula calculations for Consumer Staples industry."""

    def setUp(self):
        """Load WES test data."""
        self.test_data = self.load_test_data('wes_standard.json')
        self.scorer = ScoringSystem(self.test_data)
        self.report = VerificationReport()

    def test_ebit_margin_value(self):
        """Verify EBIT Margin value from ratios."""
        ebit_margin = self.scorer._get_value('EBIT Margin')

        expected_margin = self.test_data['expected_results']['EBIT Margin']['expected']

        if ebit_margin:
            passed, msg = self.verify_formula('EBIT Margin', ebit_margin, expected_margin)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            # Try calculating from components
            ebit = self.scorer._get_value('EBIT', 'Operating Income')
            revenue = self.scorer._get_value('Revenue')
            if ebit and revenue and revenue > 0:
                calculated_margin = (ebit / revenue) * 100
                print(f"\n[DEBUG] EBIT Margin calculated: {calculated_margin}")
                passed, msg = self.verify_formula('EBIT Margin (calculated)', calculated_margin, expected_margin)
                print(f"\n{msg}")
                self.assertTrue(passed, msg)
            else:
                self.fail("EBIT Margin value not found")

    def test_roe_value(self):
        """Verify ROE value from ratios."""
        roe = self.scorer._get_value('Return on Equity (ROE)', 'ROE')

        expected_roe = self.test_data['expected_results']['ROE']['expected']

        if roe:
            passed, msg = self.verify_formula('ROE', roe, expected_roe)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            # Try calculating from components
            net_income = self.scorer._get_value('Net Income to Common')
            equity = self.scorer._get_value('Shareholders Equity')
            if net_income and equity and equity > 0:
                calculated_roe = (net_income / equity) * 100
                print(f"\n[DEBUG] ROE calculated: {calculated_roe}")
                passed, msg = self.verify_formula('ROE (calculated)', calculated_roe, expected_roe)
                print(f"\n{msg}")
                self.assertTrue(passed, msg)
            else:
                self.fail("ROE value not found")

    def test_inventory_days_calculation(self):
        """Verify Inventory Days formula: (Inventory / Cost of Revenue) * 365"""
        inventory = self.scorer._get_value('Inventory')
        cost_of_revenue = self.scorer._get_value('Cost of Revenue')

        print(f"\n[DEBUG] Inventory: {inventory}, Cost of Revenue: {cost_of_revenue}")

        expected_days = self.test_data['expected_results']['Inventory Days']['expected']

        if inventory and cost_of_revenue and cost_of_revenue > 0:
            calculated_days = (inventory / cost_of_revenue) * 365
            print(f"[DEBUG] Inventory Days calculated: {calculated_days}")
            passed, msg = self.verify_formula('Inventory Days', calculated_days, expected_days)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("Cannot calculate Inventory Days")

    def test_forward_pe_value(self):
        """Verify Forward PE value from ratios."""
        forward_pe = self.scorer._get_value('Forward PE')

        expected_pe = self.test_data['expected_results']['Forward PE']['expected']

        if forward_pe:
            passed, msg = self.verify_formula('Forward PE', forward_pe, expected_pe)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("Forward PE value not found")

    def test_dividend_yield_value(self):
        """Verify Dividend Yield value from ratios."""
        dividend_yield = self.scorer._get_value('Dividend Yield')

        expected_yield = self.test_data['expected_results']['Dividend Yield']['expected']

        if dividend_yield:
            passed, msg = self.verify_formula('Dividend Yield', dividend_yield, expected_yield)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("Dividend Yield value not found")

    def test_payout_ratio_value(self):
        """Verify Payout Ratio value from ratios."""
        payout_ratio = self.scorer._get_value('Payout Ratio')

        expected_payout = self.test_data['expected_results']['Payout Ratio']['expected']

        if payout_ratio:
            passed, msg = self.verify_formula('Payout Ratio', payout_ratio, expected_payout)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("Payout Ratio value not found")


def run_tests():
    """Run all consumer staples tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConsumerStaplesFormulas)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
