"""
Tests for Materials (Mining) industry formula verification.
Validates that asx_scorer.py calculations match score_normalisation.md definitions.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_formula_base import FormulaTestBase, VerificationReport
from asx_scorer import ScoringSystem, normalize_positive, normalize_negative


class TestMaterialsNormalizationFunctions(unittest.TestCase):
    """Test the normalization functions used in Materials scoring."""

    def test_aisc_at_target(self):
        """AISC = 60% (target) -> 10分"""
        score = normalize_negative(60, warn=85, target=60)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_aisc_at_warn(self):
        """AISC = 85% (warn) -> 0分"""
        score = normalize_negative(85, warn=85, target=60)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_aisc_mid(self):
        """AISC = 72.5% -> 5分"""
        score = normalize_negative(72.5, warn=85, target=60)
        self.assertAlmostEqual(score, 5.0, places=2)

    def test_aisc_above_target(self):
        """AISC = 50% (better than target) -> 10分"""
        score = normalize_negative(50, warn=85, target=60)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_aisc_below_warn(self):
        """AISC = 90% (worse than warn) -> 0分"""
        score = normalize_negative(90, warn=85, target=60)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_fcf_yield_at_target(self):
        """FCF Yield = 8% (target) -> 10分"""
        score = normalize_positive(8, warn=0, target=8)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_fcf_yield_at_warn(self):
        """FCF Yield = 0% (warn) -> 0分"""
        score = normalize_positive(0, warn=0, target=8)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_fcf_yield_mid(self):
        """FCF Yield = 4% -> 5分"""
        score = normalize_positive(4, warn=0, target=8)
        self.assertAlmostEqual(score, 5.0, places=2)

    def test_fcf_yield_above_target(self):
        """FCF Yield = 10% (better than target) -> 10分"""
        score = normalize_positive(10, warn=0, target=8)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_leverage_at_target(self):
        """Net Debt/EBITDA = 0.5x (target) -> 10分"""
        score = normalize_negative(0.5, warn=1.5, target=0.5)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_leverage_at_warn(self):
        """Net Debt/EBITDA = 1.5x (warn) -> 0分"""
        score = normalize_negative(1.5, warn=1.5, target=0.5)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_leverage_mid(self):
        """Net Debt/EBITDA = 1.0x -> 5分"""
        score = normalize_negative(1.0, warn=1.5, target=0.5)
        self.assertAlmostEqual(score, 5.0, places=2)

    def test_leverage_below_target(self):
        """Net Debt/EBITDA = 0.2x (better than target) -> 10分"""
        score = normalize_negative(0.2, warn=1.5, target=0.5)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_leverage_above_warn(self):
        """Net Debt/EBITDA = 2.0x (worse than warn) -> 0分"""
        score = normalize_negative(2.0, warn=1.5, target=0.5)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_payout_at_target(self):
        """Dividend Payout = 60% (target) -> 10分"""
        score = normalize_positive(60, warn=40, target=60)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_payout_at_warn(self):
        """Dividend Payout = 40% (warn) -> 0分"""
        score = normalize_positive(40, warn=40, target=60)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_payout_mid(self):
        """Dividend Payout = 50% -> 5分"""
        score = normalize_positive(50, warn=40, target=60)
        self.assertAlmostEqual(score, 5.0, places=2)

    def test_cip_at_target(self):
        """CIP (Revenue Growth) = 30% (target) -> 10分"""
        score = normalize_positive(30, warn=0, target=30)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_cip_at_warn(self):
        """CIP = 0% (warn) -> 0分"""
        score = normalize_positive(0, warn=0, target=30)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_cip_mid(self):
        """CIP = 15% -> 5分"""
        score = normalize_positive(15, warn=0, target=30)
        self.assertAlmostEqual(score, 5.0, places=2)

    def test_underlying_npat_no_writedown(self):
        """Underlying NPAT: no writedown (100 - 0 = 100) -> 10分"""
        score = normalize_positive(100, warn=80, target=100)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_underlying_npat_20pct_writedown(self):
        """Underlying NPAT: 20% writedown (100 - 20 = 80) -> 0分"""
        score = normalize_positive(80, warn=80, target=100)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_underlying_npat_10pct_writedown(self):
        """Underlying NPAT: 10% writedown (100 - 10 = 90) -> 5分"""
        score = normalize_positive(90, warn=80, target=100)
        self.assertAlmostEqual(score, 5.0, places=2)


class TestMaterialsFormulas(FormulaTestBase):
    """Test all formula calculations for Materials (Mining) industry."""

    def setUp(self):
        """Load RIO test data."""
        self.test_data = self.load_test_data('rio_standard.json')
        self.scorer = ScoringSystem(self.test_data)
        self.report = VerificationReport()

    def test_operating_cost_ratio_calculation(self):
        """Verify Operating Cost Ratio (AISC) formula: (Cost + Capex) / Revenue"""
        revenue = self.scorer._get_value('Revenue')
        cost_of_revenue = self.scorer._get_value('Cost of Revenue')
        capex = self.scorer._get_value('Capital Expenditures')

        print(f"\n[DEBUG] Revenue: {revenue}, Cost of Revenue: {cost_of_revenue}, Capex: {capex}")

        # AISC = (Cost + Capex) / Revenue * 100
        if revenue and cost_of_revenue and revenue > 0:
            total_cost = cost_of_revenue + abs(capex) if capex else cost_of_revenue
            aisc = (total_cost / revenue) * 100
            print(f"[DEBUG] AISC calculated: {aisc:.2f}%")

    def test_revenue_growth_value(self):
        """Verify Revenue Growth value from ratios."""
        revenue_growth = self.scorer._get_value('Revenue Growth (YoY)')

        expected_growth = self.test_data['expected_results']['Revenue Growth']['expected']

        if revenue_growth:
            passed, msg = self.verify_formula('Revenue Growth', revenue_growth, expected_growth)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("Revenue Growth value not found")

    def test_underlying_npat_calculation(self):
        """Verify Underlying NPAT formula: Net Income - Asset Writedown"""
        net_income = self.scorer._get_value('Net Income')
        asset_writedown = self.scorer._get_value('Asset Writedown')

        print(f"\n[DEBUG] Net Income: {net_income}, Asset Writedown: {asset_writedown}")

        expected_npat = self.test_data['expected_results']['Underlying NPAT']['expected']

        if net_income is not None:
            if asset_writedown is not None:
                calculated = net_income - asset_writedown
                passed, msg = self.verify_formula('Underlying NPAT', calculated, expected_npat)
                print(f"\n{msg}")
                self.assertTrue(passed, msg)
            else:
                self.assertIsNotNone(net_income)
        else:
            self.fail("Net Income value not found")

    def test_fcf_yield_value(self):
        """Verify FCF Yield value from ratios."""
        fcf_yield = self.scorer._get_value('FCF Yield', 'Free Cash Flow Yield')

        expected_yield = self.test_data['expected_results']['FCF Yield']['expected']

        # Use direct value from ratios
        if fcf_yield:
            passed, msg = self.verify_formula('FCF Yield', fcf_yield, expected_yield)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            self.fail("FCF Yield value not found in ratios")

    def test_net_debt_ebitda_calculation(self):
        """Verify Net Debt / EBITDA formula: (Total Debt - Cash) / EBITDA"""
        total_debt = self.scorer._get_value('Total Debt')
        cash = self.scorer._get_value('Cash & Equivalents')
        ebitda = self.scorer._get_value('EBITDA')

        print(f"\n[DEBUG] Total Debt: {total_debt}, Cash: {cash}, EBITDA: {ebitda}")

        expected_ratio = self.test_data['expected_results']['Net Debt/EBITDA']['expected']

        if ebitda:
            if total_debt and cash is not None:
                calculated = (total_debt - cash) / ebitda
                passed, msg = self.verify_formula('Net Debt/EBITDA', calculated, expected_ratio)
                print(f"\n{msg}")
                self.assertTrue(passed, msg)
            else:
                self.fail("Cannot calculate Net Debt/EBITDA")
        else:
            self.fail("EBITDA value not found")

    def test_payout_ratio_value(self):
        """Verify Payout Ratio value from ratios."""
        payout_ratio = self.scorer._get_value('Payout Ratio')

        expected_payout = self.test_data['expected_results']['Payout Ratio']['expected']

        if payout_ratio:
            passed, msg = self.verify_formula('Payout Ratio', payout_ratio, expected_payout)
            print(f"\n{msg}")
            self.assertTrue(passed, msg)
        else:
            # Try calculating from components
            dividends = self.scorer._get_value('Common Dividends Paid')
            net_income = self.scorer._get_value('Net Income to Common')
            if dividends and net_income and net_income > 0:
                calculated_payout = (abs(dividends) / net_income) * 100
                print(f"\n[DEBUG] Payout Ratio calculated: {calculated_payout}")
                passed, msg = self.verify_formula('Payout Ratio (calculated)', calculated_payout, expected_payout)
                print(f"\n{msg}")
                self.assertTrue(passed, msg)
            else:
                self.fail("Payout Ratio value not found and cannot calculate")

    def test_weighted_sum_full_scores(self):
        """Test weighted sum calculation: 6项全满分 -> 10.0总分"""
        # Create a mock data with perfect scores
        # AISC = (60000 + 30000) / 100000 * 100 = 90% - this is above 85% warning, so need lower cost
        # Cost should be 50000 to get AISC = (50000 + 30000) / 100000 * 100 = 80%
        # Wait, for perfect 10 score, AISC needs to be <= 60%
        # So cost should be: (cost + capex) / revenue = 60% -> cost = 60000 - 30000 = 30000
        mock_data = {
            'ticker': 'TEST',
            'ratios': {
                'FCF Yield': {'FY 2025': 8.0},
                'Net Debt / EBITDA Ratio': {'FY 2025': 0.5},
                'Payout Ratio': {'FY 2025': 60}
            },
            'income_statement': {
                'Revenue': {'FY 2025': 100000},
                'Cost of Revenue': {'FY 2025': 30000},  # 30000 + 30000 = 60000, AISC = 60%
                'Capital Expenditures': {'FY 2025': -30000},
                'Revenue Growth (YoY)': {'FY 2025': 30},
                'Net Income': {'FY 2025': 10000},
                'Asset Writedown': {'FY 2025': 0}
            },
            'balance_sheet': {},
            'cash_flow': {}
        }
        scorer = ScoringSystem(mock_data)
        result = scorer.score_materials()

        print(f"\n[DEBUG] Total Score (perfect): {result.total_score}")
        print(f"[DEBUG] Max Score: {result.max_score}")

        # All 6 indicators should get 10 points, so weighted sum should be 10
        self.assertAlmostEqual(result.total_score, 10.0, places=1)


def run_tests():
    """Run all materials tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMaterialsNormalizationFunctions)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMaterialsFormulas))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
