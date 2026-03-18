"""
Tests for Task 1: Banks Scorecard

根据 score_normalisation.md 设计文档的测试用例

| 测试名称 | 输入 | 预期输出 | 验证点 |
|----------|------|----------|--------|
| test_nim_at_target | NIM = 2.10 | 10 分 | 边界条件 |
| test_nim_at_warn | NIM = 1.70 | 0 分 | 边界条件 |
| test_nim_mid | NIM = 1.90 | ~5.67 分 | 线性插值 |
| test_nim_above_target | NIM = 2.50 | 10 分 | 封顶 |
| test_nim_below_warn | NIM = 1.50 | 0 分 | 垫底 |
| test_cti_above_warn | Cost-to-Income = 55% | 0 分 | 逆向越界 |
| test_payout_optimal | Payout = 75% | 10 分 | 趋中最优 |
| test_weighted_sum | 6项全满分 | 10.0 总分 | 加权计算 |
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scorers.banks import (
    normalize_positive,
    normalize_negative,
    normalize_range,
    calculate_nim_score,
    calculate_cet1_score,
    calculate_cost_to_income_score,
    calculate_roe_score,
    calculate_bad_debt_score,
    calculate_payout_score,
    calculate_banks_score,
    BANKS_METRICS
)


class TestNIMScore(unittest.TestCase):
    """NIM (净息差) 正向指标测试"""

    def test_nim_at_target(self):
        """NIM @ 2.10 (目标) -> 10 分"""
        score = calculate_nim_score(2.10)
        self.assertEqual(score, 10.0)

    def test_nim_at_warn(self):
        """NIM @ 1.70 (预警) -> 0 分"""
        score = calculate_nim_score(1.70)
        self.assertEqual(score, 0.0)

    def test_nim_mid(self):
        """NIM @ 1.90 (中间) -> ~5.67 分"""
        # 公式: (1.90 - 1.70) / (2.10 - 1.70) * 10 = 0.2 / 0.4 * 10 = 5
        score = calculate_nim_score(1.90)
        self.assertAlmostEqual(score, 5.0, places=1)

    def test_nim_above_target(self):
        """NIM @ 2.50 (超出目标) -> 10 分 (封顶)"""
        score = calculate_nim_score(2.50)
        self.assertEqual(score, 10.0)

    def test_nim_below_warn(self):
        """NIM @ 1.50 (低于预警) -> 0 分 (垫底)"""
        score = calculate_nim_score(1.50)
        self.assertEqual(score, 0.0)

    def test_nim_none(self):
        """NIM = None -> 0 分"""
        score = calculate_nim_score(None)
        self.assertEqual(score, 0.0)


class TestCET1Score(unittest.TestCase):
    """CET1 Ratio 正向指标测试"""

    def test_cet1_at_target(self):
        """CET1 @ 13.0% (目标) -> 10 分"""
        score = calculate_cet1_score(13.0)
        self.assertEqual(score, 10.0)

    def test_cet1_at_warn(self):
        """CET1 @ 11.0% (预警) -> 0 分"""
        score = calculate_cet1_score(11.0)
        self.assertEqual(score, 0.0)

    def test_cet1_mid(self):
        """CET1 @ 12.0% (中间) -> 5 分"""
        # 公式: (12.0 - 11.0) / (13.0 - 11.0) * 10 = 1/2 * 10 = 5
        score = calculate_cet1_score(12.0)
        self.assertEqual(score, 5.0)

    def test_cet1_above_target(self):
        """CET1 @ 15.0% (超出目标) -> 10 分"""
        score = calculate_cet1_score(15.0)
        self.assertEqual(score, 10.0)

    def test_cet1_below_warn(self):
        """CET1 @ 10.0% (低于预警) -> 0 分"""
        score = calculate_cet1_score(10.0)
        self.assertEqual(score, 0.0)


class TestCostToIncomeScore(unittest.TestCase):
    """Cost-to-Income 逆向指标测试"""

    def test_cti_at_target(self):
        """CTI @ 40% (目标) -> 10 分"""
        score = calculate_cost_to_income_score(40.0)
        self.assertEqual(score, 10.0)

    def test_cti_at_warn(self):
        """CTI @ 50% (预警) -> 0 分"""
        score = calculate_cost_to_income_score(50.0)
        self.assertEqual(score, 0.0)

    def test_cti_mid(self):
        """CTI @ 45% (中间) -> 5 分"""
        # 公式: (50 - 45) / (50 - 40) * 10 = 5/10 * 10 = 5
        score = calculate_cost_to_income_score(45.0)
        self.assertEqual(score, 5.0)

    def test_cti_below_target(self):
        """CTI @ 35% (低于目标) -> 10 分"""
        score = calculate_cost_to_income_score(35.0)
        self.assertEqual(score, 10.0)

    def test_cti_above_warn(self):
        """CTI @ 55% (超出预警) -> 0 分"""
        score = calculate_cost_to_income_score(55.0)
        self.assertEqual(score, 0.0)

    def test_cti_none(self):
        """CTI = None -> 0 分"""
        score = calculate_cost_to_income_score(None)
        self.assertEqual(score, 0.0)


class TestROEScore(unittest.TestCase):
    """ROE 正向指标测试"""

    def test_roe_at_target(self):
        """ROE @ 14% (目标) -> 10 分"""
        score = calculate_roe_score(14.0)
        self.assertEqual(score, 10.0)

    def test_roe_at_warn(self):
        """ROE @ 10% (预警) -> 0 分"""
        score = calculate_roe_score(10.0)
        self.assertEqual(score, 0.0)

    def test_roe_mid(self):
        """ROE @ 12% (中间) -> 5 分"""
        score = calculate_roe_score(12.0)
        self.assertEqual(score, 5.0)

    def test_roe_above_target(self):
        """ROE @ 16% (超出目标) -> 10 分"""
        score = calculate_roe_score(16.0)
        self.assertEqual(score, 10.0)

    def test_roe_below_warn(self):
        """ROE @ 8% (低于预警) -> 0 分"""
        score = calculate_roe_score(8.0)
        self.assertEqual(score, 0.0)


class TestBadDebtScore(unittest.TestCase):
    """Bad Debt Ratio 逆向指标测试"""

    def test_bad_debt_at_target(self):
        """Bad Debt @ 0.05% (目标) -> 10 分"""
        score = calculate_bad_debt_score(0.05)
        self.assertEqual(score, 10.0)

    def test_bad_debt_at_warn(self):
        """Bad Debt @ 0.15% (预警) -> 0 分"""
        score = calculate_bad_debt_score(0.15)
        self.assertEqual(score, 0.0)

    def test_bad_debt_mid(self):
        """Bad Debt @ 0.10% (中间) -> 5 分"""
        # 公式: (0.15 - 0.10) / (0.15 - 0.05) * 10 = 0.05/0.10 * 10 = 5
        score = calculate_bad_debt_score(0.10)
        self.assertAlmostEqual(score, 5.0, places=1)

    def test_bad_debt_below_target(self):
        """Bad Debt @ 0.03% (低于目标) -> 10 分"""
        score = calculate_bad_debt_score(0.03)
        self.assertEqual(score, 10.0)

    def test_bad_debt_above_warn(self):
        """Bad Debt @ 0.20% (超出预警) -> 0 分"""
        score = calculate_bad_debt_score(0.20)
        self.assertEqual(score, 0.0)


class TestPayoutScore(unittest.TestCase):
    """Payout Ratio 趋中指标测试"""

    def test_payout_optimal(self):
        """Payout @ 75% (最优) -> 10 分"""
        score = calculate_payout_score(75.0)
        self.assertEqual(score, 10.0)

    def test_payout_at_low_warn(self):
        """Payout @ 50% (低位预警) -> 0 分"""
        score = calculate_payout_score(50.0)
        self.assertEqual(score, 0.0)

    def test_payout_at_high_warn(self):
        """Payout @ 90% (高位预警) -> 0 分"""
        score = calculate_payout_score(90.0)
        self.assertEqual(score, 0.0)

    def test_payout_mid_low(self):
        """Payout @ 62.5% (中间偏左) -> 5 分"""
        # 公式: (62.5 - 50) / (75 - 50) * 10 = 12.5/25 * 10 = 5
        score = calculate_payout_score(62.5)
        self.assertEqual(score, 5.0)

    def test_payout_mid_high(self):
        """Payout @ 87.5% (中间偏右) -> 5 分"""
        # 公式: (90 - 87.5) / (90 - 75) * 10 = 2.5/15 * 10 = 1.67
        score = calculate_payout_score(87.5)
        self.assertAlmostEqual(score, 1.67, places=1)

    def test_payout_below_low_warn(self):
        """Payout @ 30% (低于低位预警) -> 0 分"""
        score = calculate_payout_score(30.0)
        self.assertEqual(score, 0.0)

    def test_payout_above_high_warn(self):
        """Payout @ 100% (高于高位预警) -> 0 分"""
        score = calculate_payout_score(100.0)
        self.assertEqual(score, 0.0)


class TestWeightedSum(unittest.TestCase):
    """加权总分测试"""

    def test_weighted_sum_perfect(self):
        """6项全满分 -> 10.0 总分"""
        test_data = {
            'ratios': {
                'NIM': {'FY 2025': 2.10},
                'CET1 Ratio': {'FY 2025': 13.0},
                'Cost-to-Income Ratio': {'FY 2025': 40.0},
                'ROE': {'FY 2025': 14.0},
                'Bad Debt Ratio': {'FY 2025': 0.05},
                'Payout Ratio': {'FY 2025': 75.0}
            }
        }
        result = calculate_banks_score(test_data)
        self.assertAlmostEqual(result['total_score'], 10.0, places=1)

    def test_weighted_sum_all_zero(self):
        """6项全0分 -> 0.0 总分"""
        test_data = {
            'ratios': {
                'NIM': {'FY 2025': 1.70},
                'CET1 Ratio': {'FY 2025': 11.0},
                'Cost-to-Income Ratio': {'FY 2025': 50.0},
                'ROE': {'FY 2025': 10.0},
                'Bad Debt Ratio': {'FY 2025': 0.15},
                'Payout Ratio': {'FY 2025': 50.0}
            }
        }
        result = calculate_banks_score(test_data)
        self.assertAlmostEqual(result['total_score'], 0.0, places=1)

    def test_weighted_sum_mixed(self):
        """混合分数测试"""
        test_data = {
            'ratios': {
                'NIM': {'FY 2025': 1.90},  # 5分
                'CET1 Ratio': {'FY 2025': 12.0},  # 5分
                'Cost-to-Income Ratio': {'FY 2025': 45.0},  # 5分
                'ROE': {'FY 2025': 12.0},  # 5分
                'Bad Debt Ratio': {'FY 2025': 0.10},  # 5分
                'Payout Ratio': {'FY 2025': 75.0}  # 10分
            }
        }
        result = calculate_banks_score(test_data)

        # 计算期望值
        expected = (
            5.0 * 0.20 +  # NIM
            5.0 * 0.15 +  # CET1
            5.0 * 0.15 +  # Cost-to-Income
            5.0 * 0.20 +  # ROE
            5.0 * 0.20 +  # Bad Debt
            10.0 * 0.10   # Payout
        )
        self.assertAlmostEqual(result['total_score'], expected, places=1)


class TestNormalizeFunctions(unittest.TestCase):
    """标准化函数基础测试"""

    def test_normalize_positive_basic(self):
        """正向指标基础测试"""
        # 边界条件
        self.assertEqual(normalize_positive(10, 0, 10), 10.0)
        self.assertEqual(normalize_positive(0, 0, 10), 0.0)
        # 线性
        self.assertEqual(normalize_positive(5, 0, 10), 5.0)

    def test_normalize_negative_basic(self):
        """逆向指标基础测试"""
        # 边界条件
        self.assertEqual(normalize_negative(0, 10, 0), 10.0)
        self.assertEqual(normalize_negative(10, 10, 0), 0.0)
        # 线性
        self.assertEqual(normalize_negative(5, 10, 0), 5.0)

    def test_normalize_range_basic(self):
        """趋中指标基础测试"""
        # 最优区间
        self.assertEqual(normalize_range(75, 50, 75, 75, 90), 10.0)
        # 低位边界
        self.assertEqual(normalize_range(50, 50, 75, 75, 90), 0.0)
        self.assertEqual(normalize_range(90, 50, 75, 75, 90), 0.0)
        # 中间值
        self.assertAlmostEqual(normalize_range(62.5, 50, 75, 75, 90), 5.0, places=1)


class TestBanksMetrics(unittest.TestCase):
    """指标定义测试"""

    def test_weights_sum_to_one(self):
        """权重总和为 100%"""
        total_weight = sum(m['weight'] for m in BANKS_METRICS.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)

    def test_all_metrics_have_required_fields(self):
        """所有指标都有必需字段"""
        required_fields = ['weight', 'polarity', 'display_name', 'unit']
        for metric_name, metric_info in BANKS_METRICS.items():
            for field in required_fields:
                self.assertIn(field, metric_info, f"{metric_name} missing {field}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
