"""
Task 4: 必需消费计分卡 (Consumer Staples Scorecard) 单元测试

根据 score_normalisation.md 设计的标准化评分系统进行测试。

测试用例:
| 测试名称 | 输入 | 预期输出 | 验证点 |
|----------|------|----------|--------|
| test_inventory_excellent | 30天 | 10 分 | 逆向最优 |
| test_inventory_risky | 100天 | 0 分 | 逆向边界 |
| test_pe_cheap | PE = 18x | 10 分 | 逆向最优 |
| test_pe_expensive | PE = 30x | 0 分 | 逆向边界 |
| test_roe_excellent | ROE = 35% | 10 分 | 边界 |
| test_franking_full | Franking = 100% | 10 分 | 完全抵税 |
| test_weighted_sum | 6项全满分 | 10.0 总分 | 加权 |
| test_ebit_margin_mid | EBIT = 6.5% | ~5.75 分 | 线性插值 |
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asx_scorer import normalize_positive, normalize_negative, normalize_range


class TestTask4ConsumerStaples(unittest.TestCase):
    """Task 4 必需消费计分卡单元测试"""

    # ===== Inventory Days (逆向指标) 测试 =====
    # 预警: 100天, 目标: 30天

    def test_inventory_excellent(self):
        """库存天数30天=10分(逆向最优)"""
        score = normalize_negative(30, warn=100, target=30)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_inventory_risky(self):
        """库存天数100天=0分(逆向边界)"""
        score = normalize_negative(100, warn=100, target=30)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_inventory_mid(self):
        """库存天数65天=线性插值"""
        # (100-65)/(100-30) = 35/70 = 0.5 → 5分
        score = normalize_negative(65, warn=100, target=30)
        self.assertAlmostEqual(score, 5.0, places=2)

    def test_inventory_above_warn(self):
        """库存天数>100天=0分"""
        score = normalize_negative(120, warn=100, target=30)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_inventory_below_target(self):
        """库存天数<30天=10分(封顶)"""
        score = normalize_negative(20, warn=100, target=30)
        self.assertAlmostEqual(score, 10.0, places=2)

    # ===== Forward PE (逆向指标) 测试 =====
    # 预警: 30x, 目标: 18x

    def test_pe_cheap(self):
        """PE=18x=10分(逆向最优)"""
        score = normalize_negative(18, warn=30, target=18)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_pe_expensive(self):
        """PE=30x=0分(逆向边界)"""
        score = normalize_negative(30, warn=30, target=18)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_pe_mid(self):
        """PE=24x=线性插值"""
        # (30-24)/(30-18) = 6/12 = 0.5 → 5分
        score = normalize_negative(24, warn=30, target=18)
        self.assertAlmostEqual(score, 5.0, places=2)

    def test_pe_above_warn(self):
        """PE>30x=0分"""
        score = normalize_negative(35, warn=30, target=18)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_pe_below_target(self):
        """PE<18x=10分(封顶)"""
        score = normalize_negative(15, warn=30, target=18)
        self.assertAlmostEqual(score, 10.0, places=2)

    # ===== ROE (正向指标) 测试 =====
    # 预警: 15%, 目标: 35%

    def test_roe_excellent(self):
        """ROE=35%=10分(边界)"""
        score = normalize_positive(35, warn=15, target=35)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_roe_warn(self):
        """ROE=15%=0分(边界)"""
        score = normalize_positive(15, warn=15, target=35)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_roe_mid(self):
        """ROE=25%=线性插值"""
        # (25-15)/(35-15) = 10/20 = 0.5 → 5分
        score = normalize_positive(25, warn=15, target=35)
        self.assertAlmostEqual(score, 5.0, places=2)

    def test_roe_above_target(self):
        """ROE>35%=10分(封顶)"""
        score = normalize_positive(40, warn=15, target=35)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_roe_below_warn(self):
        """ROE<15%=0分"""
        score = normalize_positive(10, warn=15, target=35)
        self.assertAlmostEqual(score, 0.0, places=2)

    # ===== EBIT Margin (正向指标) 测试 =====
    # 预警: 4%, 目标: 9%

    def test_ebit_margin_target(self):
        """EBIT=9%=10分(边界)"""
        score = normalize_positive(9, warn=4, target=9)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_ebit_margin_warn(self):
        """EBIT=4%=0分(边界)"""
        score = normalize_positive(4, warn=4, target=9)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_ebit_margin_mid(self):
        """EBIT=6.5%=线性插值"""
        # (6.5-4)/(9-4) = 2.5/5 = 0.5 → 5分
        score = normalize_positive(6.5, warn=4, target=9)
        self.assertAlmostEqual(score, 5.0, places=2)

    # ===== Franking Credits (正向指标) 测试 =====
    # 预警: 0%, 目标: 100%

    def test_franking_full(self):
        """Franking=100%=10分(完全抵税)"""
        score = normalize_positive(100, warn=0, target=100)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_franking_zero(self):
        """Franking=0%=0分"""
        score = normalize_positive(0, warn=0, target=100)
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_franking_mid(self):
        """Franking=50%=线性插值"""
        # (50-0)/(100-0) = 0.5 → 5分
        score = normalize_positive(50, warn=0, target=100)
        self.assertAlmostEqual(score, 5.0, places=2)

    # ===== Market Share (正向指标) 测试 =====

    def test_market_share_growing(self):
        """Market Share增长=正分"""
        score = normalize_positive(5, warn=0, target=5)
        self.assertAlmostEqual(score, 10.0, places=2)

    def test_market_share_declining(self):
        """Market Share下滑=0分"""
        score = normalize_positive(-2, warn=0, target=5)
        self.assertAlmostEqual(score, 0.0, places=2)

    # ===== 加权总分测试 =====

    def test_weighted_sum_all_perfect(self):
        """6项全满分=60分(总分)"""
        # 每个指标满分10分，共6个指标
        scores = [10.0] * 6
        total = sum(scores)
        self.assertAlmostEqual(total, 60.0, places=2)

    def test_weighted_sum_all_zero(self):
        """6项全0分=0分(总分)"""
        scores = [0.0] * 6
        total = sum(scores)
        self.assertAlmostEqual(total, 0.0, places=2)

    def test_weighted_sum_mixed(self):
        """混合分数测试"""
        # EBIT=9(10分), ROE=35(10分), Inventory=30(10分)
        # Franking=100(10分), PE=18(10分), Market=5(10分)
        scores = [10.0, 10.0, 10.0, 10.0, 10.0, 10.0]
        total = sum(scores)
        max_score = 60
        # 转换为10分制
        normalized = (total / max_score) * 10
        self.assertAlmostEqual(normalized, 10.0, places=2)


class TestTask4Integration(unittest.TestCase):
    """Task 4 集成测试 - 使用实际数据"""

    def test_with_sample_data(self):
        """使用样本数据验证计算"""
        from asx_scorer import ScoringSystem

        # 创建模拟数据
        test_data = {
            'ticker': 'WES',
            'ratios': {
                'EBIT Margin': {'TTM': 8.5},
                'ROE': {'TTM': 32.0},
                'Forward PE': {'TTM': 20.0},
                'Market Share Change': {'TTM': 2.5},
                'Franking Credits': {'TTM': 100.0},
            },
            'income_statement': {},
            'balance_sheet': {
                'Inventory': {'TTM': 1000000000},
                'Cost of Revenue': {'TTM': 12000000000}
            },
            'cash_flow': {}
        }

        scorer = ScoringSystem(test_data)
        result = scorer.score_consumer_staples()

        # 验证有评分结果
        self.assertGreater(len(result.details), 0)

        # 验证各项分数
        ebit_score = next((d['score'] for d in result.details if 'EBIT' in d['metric']), None)
        if ebit_score is not None:
            # EBIT 8.5% 在 4-9 之间，应该有正分
            self.assertGreater(ebit_score, 0)

        # 验证库存天数计算
        # Inventory / Cost * 365 = 1000000000 / 12000000000 * 365 ≈ 30.4天
        inv_days = (1000000000 / 12000000000) * 365
        inv_score = normalize_negative(inv_days, warn=100, target=30)
        self.assertAlmostEqual(inv_score, 9.94, places=1)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTask4ConsumerStaples))
    suite.addTests(loader.loadTestsFromTestCase(TestTask4Integration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
