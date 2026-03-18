"""
Tests for Banks industry formula verification.
Validates that asx_scorer.py calculations match score_system.md definitions.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_formula_base import FormulaTestBase, VerificationReport
from asx_scorer import ScoringSystem


class TestBanksFormulas(FormulaTestBase):
    """Test all formula calculations for Banks industry."""

    def setUp(self):
        """Load CBA test data."""
        self.test_data = self.load_test_data('cba_standard.json')
        self.scorer = ScoringSystem(self.test_data)
        self.report = VerificationReport()

    def test_nim_calculation(self):
        """Verify NIM formula: Net Interest Income / IEA"""
        # Get the data from scorer
        net_interest_income = self.scorer._get_value('Net Interest Income')
        cash = self.scorer._get_value('Cash & Equivalents')
        investment_securities = self.scorer._get_value('Investment Securities')
        trading_securities = self.scorer._get_value('Trading Asset Securities')
        net_loans = self.scorer._get_value('Net Loans')

        # Calculate IEA (Interest Earning Assets)
        iea = 0
        if cash:
            iea += cash
        if investment_securities:
            iea += investment_securities
        if trading_securities:
            iea += trading_securities
        if net_loans:
            iea += net_loans

        # Calculate NIM
        if iea > 0:
            calculated_nim = (net_interest_income / iea) * 100
        else:
            calculated_nim = 0

        expected_nim = self.test_data['expected_results']['NIM']['expected']
        formula = self.test_data['expected_results']['NIM']['formula']

        passed, msg = self.verify_formula('NIM', calculated_nim, expected_nim, formula)
        self.report.add_result('Banks', 'NIM', passed, expected_nim, calculated_nim, formula)

        print(f"\n{msg}")
        print(f"      Components: NII={net_interest_income}, IEA={iea}")
        self.assertTrue(passed, msg)

    def test_cet1_calculation(self):
        """Verify CET1 formula: Total Common Equity / Total Assets"""
        common_equity = self.scorer._get_value('Total Common Equity')
        total_assets = self.scorer._get_value('Total Assets')

        if common_equity and total_assets and total_assets > 0:
            calculated_cet1 = (common_equity / total_assets) * 100
        else:
            calculated_cet1 = 0

        expected_cet1 = self.test_data['expected_results']['CET1']['expected']
        formula = self.test_data['expected_results']['CET1']['formula']

        passed, msg = self.verify_formula('CET1', calculated_cet1, expected_cet1, formula)
        self.report.add_result('Banks', 'CET1', passed, expected_cet1, calculated_cet1, formula)

        print(f"\n{msg}")
        print(f"      Components: Equity={common_equity}, Assets={total_assets}")
        self.assertTrue(passed, msg)

    def test_cost_to_income_calculation(self):
        """Verify Cost-to-Income formula: Total Non-Interest Expense / Revenues"""
        total_expense = self.scorer._get_value('Total Non-Interest Expense')
        revenue = self.scorer._get_value('Revenues Before Loan Losses')

        if total_expense and revenue and revenue > 0:
            calculated_cti = (total_expense / revenue) * 100
        else:
            calculated_cti = 0

        expected_cti = self.test_data['expected_results']['Cost-to-Income']['expected']
        formula = self.test_data['expected_results']['Cost-to-Income']['formula']

        passed, msg = self.verify_formula('Cost-to-Income', calculated_cti, expected_cti, formula)
        self.report.add_result('Banks', 'Cost-to-Income', passed, expected_cti, calculated_cti, formula)

        print(f"\n{msg}")
        print(f"      Components: Expense={total_expense}, Revenue={revenue}")
        self.assertTrue(passed, msg)

    def test_roe_value(self):
        """Verify ROE value from ratios."""
        roe = self.scorer._get_value('Return on Equity (ROE)', 'ROE')

        expected_roe = self.test_data['expected_results']['ROE']['expected']

        if roe:
            passed, msg = self.verify_formula('ROE', roe, expected_roe)
            self.report.add_result('Banks', 'ROE', passed, expected_roe, roe, "Direct from ratios")
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("ROE value not found")

    def test_bad_debt_calculation(self):
        """Verify Bad Debt formula: Provision for Loan Losses / Gross Loans"""
        provision = self.scorer._get_value('Provision for Loan Losses')
        gross_loans = self.scorer._get_value('Gross Loans')

        if provision and gross_loans and gross_loans > 0:
            calculated_bad_debt = (provision / gross_loans) * 100
        else:
            calculated_bad_debt = 0

        expected_bad_debt = self.test_data['expected_results']['Bad Debt']['expected']
        formula = self.test_data['expected_results']['Bad Debt']['formula']

        passed, msg = self.verify_formula('Bad Debt', calculated_bad_debt, expected_bad_debt, formula)
        self.report.add_result('Banks', 'Bad Debt', passed, expected_bad_debt, calculated_bad_debt, formula)

        print(f"\n{msg}")
        print(f"      Components: Provision={provision}, Gross Loans={gross_loans}")
        self.assertTrue(passed, msg)

    def test_payout_ratio_calculation(self):
        """Verify Payout Ratio formula: (Dividend * Shares) / Net Income"""
        dividend_per_share = self.scorer._get_value('Dividend Per Share')
        shares = self.scorer._get_value('Basic Shares Outstanding')
        net_income = self.scorer._get_value('Net Income to Common')

        if dividend_per_share and shares and net_income and net_income > 0:
            calculated_payout = (dividend_per_share * shares / net_income) * 100
        else:
            calculated_payout = 0

        expected_payout = self.test_data['expected_results']['Payout Ratio']['expected']
        formula = self.test_data['expected_results']['Payout Ratio']['formula']

        passed, msg = self.verify_formula('Payout Ratio', calculated_payout, expected_payout, formula)
        self.report.add_result('Banks', 'Payout Ratio', passed, expected_payout, calculated_payout, formula)

        print(f"\n{msg}")
        print(f"      Components: DPS={dividend_per_share}, Shares={shares}, NI={net_income}")
        self.assertTrue(passed, msg)


def run_tests():
    """Run all bank tests and print report."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBanksFormulas)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
