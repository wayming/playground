"""
Unit tests for scorers/materials.py
Validates that the materials scoring module matches score_material.md definitions.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scorers.materials import (
    score_aisc,
    score_reserves_life,
    score_capex_intensity,
    score_underlying_roe,
    score_fcf_yield,
    score_leverage,
    score_payout,
    calculate_materials_score,
    get_extra_value,
    _compute_weighted_reserves_life,
    WEIGHTS,
)


class TestAiscScoring(unittest.TestCase):
    """Test AISC (全维持成本率) scoring according to score_material.md"""

    def test_aisc_below_60_excellent(self):
        """AISC < 60% -> 10分 (excellent)"""
        score, level = score_aisc(50.0)
        self.assertEqual(score, 10.0)
        self.assertEqual(level, "excellent")

    def test_aisc_at_60_good(self):
        """AISC = 60% -> 7分 (good, boundary case)"""
        score, level = score_aisc(60.0)
        self.assertEqual(score, 7.0)
        self.assertEqual(level, "good")

    def test_aisc_60_to_75_good(self):
        """AISC 60%-75% -> 7分 (good)"""
        score, level = score_aisc(65.0)
        self.assertEqual(score, 7.0)
        self.assertEqual(level, "good")

    def test_aisc_75_to_85_fair(self):
        """AISC 75%-85% -> 4分 (fair)"""
        score, level = score_aisc(80.0)
        self.assertEqual(score, 4.0)
        self.assertEqual(level, "fair")

    def test_aisc_above_85_poor(self):
        """AISC > 85% -> 0分 (poor)"""
        score, level = score_aisc(90.0)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "poor")

    def test_aisc_none(self):
        """AISC = None -> 0分 (N/A)"""
        score, level = score_aisc(None)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "N/A")


class TestReservesLifeScoring(unittest.TestCase):
    """Test Reserves Life (储量寿命) scoring according to score_material.md"""

    def test_life_above_20_excellent(self):
        """Life > 20年 -> 10分 (excellent)"""
        score, level = score_reserves_life(25.0)
        self.assertEqual(score, 10.0)
        self.assertEqual(level, "excellent")

    def test_life_12_to_20_good(self):
        """Life 12-20年 -> 7分 (good)"""
        score, level = score_reserves_life(15.0)
        self.assertEqual(score, 7.0)
        self.assertEqual(level, "good")

    def test_life_7_to_12_fair(self):
        """Life 7-12年 -> 4分 (fair)"""
        score, level = score_reserves_life(10.0)
        self.assertEqual(score, 4.0)
        self.assertEqual(level, "fair")

    def test_life_below_5_poor(self):
        """Life < 5年 -> 0分 (poor)"""
        score, level = score_reserves_life(3.0)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "poor")

    def test_life_none(self):
        """Life = None -> 0分 (N/A)"""
        score, level = score_reserves_life(None)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "N/A")


class TestCapexIntensityScoring(unittest.TestCase):
    """Test Capex Intensity (资本支出强度) scoring according to score_material.md"""

    def test_ci_above_15_excellent(self):
        """CI > 15% -> 10分 (excellent)"""
        score, level = score_capex_intensity(20.0)
        self.assertEqual(score, 10.0)
        self.assertEqual(level, "excellent")

    def test_ci_8_to_15_good(self):
        """CI 8%-15% -> 7分 (good)"""
        score, level = score_capex_intensity(12.0)
        self.assertEqual(score, 7.0)
        self.assertEqual(level, "good")

    def test_ci_3_to_8_fair(self):
        """CI 3%-8% -> 4分 (fair)"""
        score, level = score_capex_intensity(5.0)
        self.assertEqual(score, 4.0)
        self.assertEqual(level, "fair")

    def test_ci_below_3_poor(self):
        """CI < 3% -> 0分 (poor)"""
        score, level = score_capex_intensity(1.0)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "poor")

    def test_ci_none(self):
        """CI = None -> 0分 (N/A)"""
        score, level = score_capex_intensity(None)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "N/A")


class TestUnderlyingRoeScoring(unittest.TestCase):
    """Test Underlying ROE (核心收益率) scoring according to score_material.md"""

    def test_roe_above_25_excellent(self):
        """ROE > 25% -> 10分 (excellent)"""
        score, level = score_underlying_roe(30.0)
        self.assertEqual(score, 10.0)
        self.assertEqual(level, "excellent")

    def test_roe_15_to_25_good(self):
        """ROE 15%-25% -> 7分 (good)"""
        score, level = score_underlying_roe(20.0)
        self.assertEqual(score, 7.0)
        self.assertEqual(level, "good")

    def test_roe_8_to_15_fair(self):
        """ROE 8%-15% -> 4分 (fair)"""
        score, level = score_underlying_roe(10.0)
        self.assertEqual(score, 4.0)
        self.assertEqual(level, "fair")

    def test_roe_below_5_poor(self):
        """ROE < 5% -> 0分 (poor)"""
        score, level = score_underlying_roe(3.0)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "poor")

    def test_roe_none(self):
        """ROE = None -> 0分 (N/A)"""
        score, level = score_underlying_roe(None)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "N/A")


class TestFcfYieldScoring(unittest.TestCase):
    """Test FCF Yield (自由现金流收益率) scoring according to score_material.md"""

    def test_fcf_above_10_excellent(self):
        """FCF > 10% -> 10分 (excellent)"""
        score, level = score_fcf_yield(12.0)
        self.assertEqual(score, 10.0)
        self.assertEqual(level, "excellent")

    def test_fcf_6_to_10_good(self):
        """FCF 6%-10% -> 7分 (good)"""
        score, level = score_fcf_yield(8.0)
        self.assertEqual(score, 7.0)
        self.assertEqual(level, "good")

    def test_fcf_2_to_5_fair(self):
        """FCF 2%-5% -> 4分 (fair)"""
        score, level = score_fcf_yield(3.0)
        self.assertEqual(score, 4.0)
        self.assertEqual(level, "fair")

    def test_fcf_negative_poor(self):
        """FCF < 0% -> 0分 (poor)"""
        score, level = score_fcf_yield(-5.0)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "poor")

    def test_fcf_none(self):
        """FCF = None -> 0分 (N/A)"""
        score, level = score_fcf_yield(None)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "N/A")


class TestLeverageScoring(unittest.TestCase):
    """Test Net Debt/EBITDA (净杠杆率) scoring according to score_material.md"""

    def test_leverage_below_0_5_excellent(self):
        """Leverage < 0.5x -> 10分 (excellent)"""
        score, level = score_leverage(0.3)
        self.assertEqual(score, 10.0)
        self.assertEqual(level, "excellent")

    def test_leverage_0_5_to_1_2_good(self):
        """Leverage 0.5x-1.2x -> 7分 (good)"""
        score, level = score_leverage(0.8)
        self.assertEqual(score, 7.0)
        self.assertEqual(level, "good")

    def test_leverage_1_5_to_2_5_fair(self):
        """Leverage 1.5x-2.5x -> 3分 (fair)"""
        score, level = score_leverage(2.0)
        self.assertEqual(score, 3.0)
        self.assertEqual(level, "fair")

    def test_leverage_above_3_poor(self):
        """Leverage > 3.0x -> 0分 (poor)"""
        score, level = score_leverage(4.0)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "poor")

    def test_leverage_none(self):
        """Leverage = None -> 0分 (N/A)"""
        score, level = score_leverage(None)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "N/A")


class TestPayoutScoring(unittest.TestCase):
    """Test Payout Ratio (分红率) scoring according to score_material.md"""

    def test_payout_50_to_70_excellent(self):
        """Payout 50%-70% -> 10分 (excellent)"""
        score, level = score_payout(60.0)
        self.assertEqual(score, 10.0)
        self.assertEqual(level, "excellent")

    def test_payout_40_to_50_good(self):
        """Payout 40%-50% -> 7分 (good)"""
        score, level = score_payout(45.0)
        self.assertEqual(score, 7.0)
        self.assertEqual(level, "good")

    def test_payout_below_30_fair(self):
        """Payout < 30% -> 4分 (fair)"""
        score, level = score_payout(20.0)
        self.assertEqual(score, 4.0)
        self.assertEqual(level, "fair")

    def test_payout_above_100_poor(self):
        """Payout > 100% -> 0分 (poor)"""
        score, level = score_payout(120.0)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "poor")

    def test_payout_none(self):
        """Payout = None -> 0分 (N/A)"""
        score, level = score_payout(None)
        self.assertEqual(score, 0.0)
        self.assertEqual(level, "N/A")


class TestWeights(unittest.TestCase):
    """Test that weights match score_material.md"""

    def test_weights_sum_to_1(self):
        """权重总和应为1.0"""
        total = sum(WEIGHTS.values())
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_weights_values(self):
        """验证各指标权重"""
        expected = {
            'AISC': 0.20,
            'Reserves Life': 0.20,
            'Capex Intensity': 0.15,
            'Underlying ROE': 0.15,
            'FCF Yield': 0.10,
            'Leverage': 0.10,
            'Payout': 0.10
        }
        self.assertEqual(WEIGHTS, expected)


class TestCalculateMaterialsScore(unittest.TestCase):
    """Test the main calculate_materials_score function"""

    def test_perfect_score(self):
        """测试满分案例 - 所有指标都达到优秀"""
        # AISC = (30000 + 20000) / 100000 = 50% -> 10分
        perfect_data = {
            'ticker': 'RIO.AX',
            'income_statement': {
                'Revenue': {'FY 2025': 100000},
                'Cost of Revenue': {'FY 2025': 30000},
                'Capital Expenditures': {'FY 2025': -20000},
                'Net Income': {'FY 2025': 30000},
                'Asset Writedown': {'FY 2025': 0},
                'Common Dividends Paid': {'FY 2025': 18000}
            },
            'balance_sheet': {
                'Total Proved Reserves': {'FY 2025': 500},
                'Annual Production Volume': {'FY 2025': 20},
                'Construction in Progress': {'FY 2025': 20000},
                'Total PPE': {'FY 2025': 100000},
                'Total Common Equity': {'FY 2025': 80000},
                'Total Debt': {'FY 2025': 10000},
                'Cash & Equivalents': {'FY 2025': 20000},
                'EBITDA': {'FY 2025': 40000}
            },
            'cash_flow': {
                'Free Cash Flow': {'FY 2025': 15000}
            },
            'ratios': {
                'FCF Yield': {'FY 2025': 12.0},
                'Net Debt / EBITDA Ratio': {'FY 2025': -0.25},
                'Payout Ratio': {'FY 2025': 60}
            }
        }

        result = calculate_materials_score(perfect_data)

        # 验证总分接近满分
        self.assertGreaterEqual(result['total_score'], 9.0)
        self.assertEqual(result['max_score'], 10.0)
        self.assertEqual(result['ticker'], 'RIO.AX')

    def test_poor_score(self):
        """测试低分案例 - 所有指标都较差"""
        poor_data = {
            'ticker': 'BAD.AX',
            'income_statement': {
                'Revenue': {'FY 2025': 100000},
                'Cost of Revenue': {'FY 2025': 90000},
                'Capital Expenditures': {'FY 2025': -1000},
                'Net Income': {'FY 2025': 1000},
                'Asset Writedown': {'FY 2025': -500},
                'Common Dividends Paid': {'FY 2025': 0}
            },
            'balance_sheet': {
                'Total Proved Reserves': {'FY 2025': 10},
                'Annual Production Volume': {'FY 2025': 20},
                'Construction in Progress': {'FY 2025': 1000},
                'Total PPE': {'FY 2025': 100000},
                'Total Common Equity': {'FY 2025': 10000},
                'Total Debt': {'FY 2025': 40000},
                'Cash & Equivalents': {'FY 2025': 1000},
                'EBITDA': {'FY 2025': 10000}
            },
            'cash_flow': {
                'Free Cash Flow': {'FY 2025': -5000}
            },
            'ratios': {
                'FCF Yield': {'FY 2025': -5.0},
                'Net Debt / EBITDA Ratio': {'FY 2025': 3.9},
                'Payout Ratio': {'FY 2025': 0}
            }
        }

        result = calculate_materials_score(poor_data)

        # 验证总分较低
        self.assertLess(result['total_score'], 4.0)

    def test_partial_data(self):
        """测试部分数据 - 某些指标缺失"""
        partial_data = {
            'ticker': 'PARTIAL.AX',
            'income_statement': {
                'Revenue': {'FY 2025': 100000},
                'Cost of Revenue': {'FY 2025': 50000}
            }
        }

        result = calculate_materials_score(partial_data)

        # 验证有结果返回
        self.assertIn('total_score', result)
        self.assertIn('metrics', result)
        self.assertEqual(result['ticker'], 'PARTIAL.AX')


class TestGetExtraValue(unittest.TestCase):
    """Test get_extra_value helper"""

    def test_direct_float(self):
        data = {'extra': {'X': 42.0}}
        self.assertEqual(get_extra_value(data, 'X'), 42.0)

    def test_dict_with_period(self):
        data = {'extra': {'X': {'FY 2025': 1360.0}}}
        self.assertEqual(get_extra_value(data, 'X'), 1360.0)

    def test_dict_priority(self):
        data = {'extra': {'X': {'FY 2024': 100, 'FY 2025': 200}}}
        self.assertEqual(get_extra_value(data, 'X'), 200.0)

    def test_missing_key(self):
        data = {'extra': {'X': 42}}
        self.assertIsNone(get_extra_value(data, 'Y'))

    def test_no_extra(self):
        data = {'ratios': {}}
        self.assertIsNone(get_extra_value(data, 'X'))

    def test_none_value(self):
        data = {'extra': {'X': None}}
        self.assertIsNone(get_extra_value(data, 'X'))


class TestComputeWeightedReservesLife(unittest.TestCase):
    """Test _compute_weighted_reserves_life with per-commodity data"""

    def _make_data(self, **overrides):
        data = {
            'extra': {
                'Iron Ore Proved Reserves': {'FY 2025': 800},
                'Iron Ore Probable Reserves': {'FY 2025': 560},
                'Iron Ore Annual Production': {'FY 2025': 263},
                'Copper Proved Reserves': {'FY 2025': 8},
                'Copper Probable Reserves': {'FY 2025': 4},
                'Copper Annual Production': {'FY 2025': 1.5},
                'Coal Proved Reserves': {'FY 2025': 200},
                'Coal Probable Reserves': {'FY 2025': 100},
                'Coal Annual Production': {'FY 2025': 30},
                'Iron Ore EBITDA Contribution': {'FY 2025': 60},
                'Copper EBITDA Contribution': {'FY 2025': 25},
                'Coal EBITDA Contribution': {'FY 2025': 15},
            }
        }
        data['extra'].update(overrides)
        return data

    def test_weighted_rli_basic(self):
        data = self._make_data()
        rli, details = _compute_weighted_reserves_life(data)
        self.assertIsNotNone(rli)
        self.assertEqual(len(details), 3)
        self.assertGreater(rli, 0)

    def test_per_commodity_rli_values(self):
        data = self._make_data()
        _, details = _compute_weighted_reserves_life(data)
        iron = next(d for d in details if d['commodity'] == 'Iron Ore')
        self.assertAlmostEqual(iron['rli'], (800 + 560) / 263, places=1)
        copper = next(d for d in details if d['commodity'] == 'Copper')
        self.assertAlmostEqual(copper['rli'], (8 + 4) / 1.5, places=1)

    def test_ebitda_weighting(self):
        """Higher EBITDA weight commodities should dominate the final RLI."""
        data = self._make_data(**{
            'Iron Ore EBITDA Contribution': {'FY 2025': 90},
            'Copper EBITDA Contribution': {'FY 2025': 5},
            'Coal EBITDA Contribution': {'FY 2025': 5},
        })
        rli, details = _compute_weighted_reserves_life(data)
        iron_rli = (800 + 560) / 263
        self.assertAlmostEqual(rli, iron_rli, delta=1.5)

    def test_no_extra_returns_none(self):
        data = {'ratios': {}}
        rli, details = _compute_weighted_reserves_life(data)
        self.assertIsNone(rli)
        self.assertEqual(details, [])

    def test_partial_commodities(self):
        """Only iron ore data available."""
        data = {
            'extra': {
                'Iron Ore Proved Reserves': {'FY 2025': 1000},
                'Iron Ore Probable Reserves': {'FY 2025': 360},
                'Iron Ore Annual Production': {'FY 2025': 263},
                'Iron Ore EBITDA Contribution': {'FY 2025': 100},
            }
        }
        rli, details = _compute_weighted_reserves_life(data)
        self.assertIsNotNone(rli)
        self.assertEqual(len(details), 1)
        self.assertAlmostEqual(rli, 1360 / 263, places=1)

    def test_no_ebitda_weight_falls_back_to_average(self):
        """When EBITDA weights are all missing, use simple average."""
        data = {
            'extra': {
                'Iron Ore Proved Reserves': {'FY 2025': 1000},
                'Iron Ore Probable Reserves': {'FY 2025': 360},
                'Iron Ore Annual Production': {'FY 2025': 263},
                'Copper Proved Reserves': {'FY 2025': 12},
                'Copper Probable Reserves': {'FY 2025': 0},
                'Copper Annual Production': {'FY 2025': 1.5},
            }
        }
        rli, details = _compute_weighted_reserves_life(data)
        iron_rli = 1360 / 263
        copper_rli = 12 / 1.5
        expected_avg = (iron_rli + copper_rli) / 2
        self.assertAlmostEqual(rli, expected_avg, places=1)

    def test_zero_production_skipped(self):
        data = {
            'extra': {
                'Iron Ore Proved Reserves': {'FY 2025': 1000},
                'Iron Ore Probable Reserves': {'FY 2025': 360},
                'Iron Ore Annual Production': {'FY 2025': 0},
            }
        }
        rli, details = _compute_weighted_reserves_life(data)
        self.assertIsNone(rli)
        self.assertEqual(details, [])


class TestCalculateMaterialsScoreWithExtra(unittest.TestCase):
    """Test that calculate_materials_score uses per-commodity data from extra."""

    def test_weighted_reserves_life_from_extra(self):
        data = {
            'ticker': 'BHP.AX',
            'extra': {
                'Iron Ore Proved Reserves': {'FY 2025': 800},
                'Iron Ore Probable Reserves': {'FY 2025': 560},
                'Iron Ore Annual Production': {'FY 2025': 263},
                'Iron Ore EBITDA Contribution': {'FY 2025': 60},
                'Copper Proved Reserves': {'FY 2025': 8},
                'Copper Probable Reserves': {'FY 2025': 4},
                'Copper Annual Production': {'FY 2025': 1.5},
                'Copper EBITDA Contribution': {'FY 2025': 25},
                'Coal Proved Reserves': {'FY 2025': 200},
                'Coal Probable Reserves': {'FY 2025': 100},
                'Coal Annual Production': {'FY 2025': 30},
                'Coal EBITDA Contribution': {'FY 2025': 15},
            },
            'income_statement': {'Revenue': {'FY 2025': 100000}, 'Cost of Revenue': {'FY 2025': 50000}},
        }
        result = calculate_materials_score(data)
        rl = result['metrics']['Reserves Life']
        self.assertIsNotNone(rl['value'])
        self.assertGreater(rl['value'], 0)
        self.assertGreater(len(rl['commodity_details']), 0)

    def test_fallback_to_simple_reserves_life(self):
        """When no extra per-commodity data, falls back to simple Reserves/Production."""
        data = {
            'ticker': 'FMG.AX',
            'balance_sheet': {
                'Total Proved Reserves': {'FY 2025': 500},
                'Annual Production Volume': {'FY 2025': 20},
            },
        }
        result = calculate_materials_score(data)
        rl = result['metrics']['Reserves Life']
        self.assertAlmostEqual(rl['value'], 25.0)
        self.assertEqual(rl['commodity_details'], [])


def run_tests():
    """Run all materials scoring tests."""
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAiscScoring))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReservesLifeScoring))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCapexIntensityScoring))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUnderlyingRoeScoring))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFcfYieldScoring))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLeverageScoring))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPayoutScoring))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestWeights))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCalculateMaterialsScore))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGetExtraValue))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestComputeWeightedReservesLife))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCalculateMaterialsScoreWithExtra))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
