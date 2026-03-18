"""
Tests for Task 5: Yield vs Score

根据 score_normalisation.md 设计文档的测试用例

| 测试名称 | 描述 | 验证点 |
|----------|------|--------|
| test_add_single_stock | 添加单只股票 | 数据正确存储 |
| test_quadrant_classification | 象限分类 | 四象限边界 |
| test_top_right_recommendation | 右上都推荐 | 过滤逻辑 |
| test_empty_handling | 空数据处理 | 容错 |
| test_multi_industry | 多行业数据 | 对比功能 |
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yield_vs_score import (
    YieldVsScore,
    StockData,
    Quadrant,
    SCORE_THRESHOLD_HIGH,
    SCORE_THRESHOLD_LOW,
    YIELD_THRESHOLD
)


class TestAddStock(unittest.TestCase):
    """添加股票测试"""

    def test_add_single_stock(self):
        """添加单只股票 - 数据正确存储"""
        analyzer = YieldVsScore()
        analyzer.add_stock("CBA", score=8.0, dividend_yield=5.0, industry="Banks")

        self.assertEqual(len(analyzer.stocks), 1)
        stock = analyzer.stocks[0]
        self.assertEqual(stock.ticker, "CBA")
        self.assertEqual(stock.score, 8.0)
        self.assertEqual(stock.dividend_yield, 5.0)
        self.assertEqual(stock.industry, "Banks")

    def test_add_multiple_stocks(self):
        """添加多只股票"""
        analyzer = YieldVsScore()
        analyzer.add_stock("CBA", score=8.0, dividend_yield=5.0)
        analyzer.add_stock("NAB", score=6.0, dividend_yield=6.0)
        analyzer.add_stock("WES", score=7.0, dividend_yield=4.0)

        self.assertEqual(len(analyzer.stocks), 3)

    def test_add_industry(self):
        """添加行业数据"""
        analyzer = YieldVsScore()
        stocks = [
            {'ticker': 'CBA', 'score': 8.0, 'dividend_yield': 5.0},
            {'ticker': 'NAB', 'score': 6.0, 'dividend_yield': 6.0}
        ]
        analyzer.add_industry("Banks", stocks)

        self.assertEqual(len(analyzer.stocks), 2)
        self.assertEqual(analyzer.stocks[0].industry, "Banks")
        self.assertEqual(analyzer.stocks[1].industry, "Banks")


class TestQuadrantClassification(unittest.TestCase):
    """象限分类测试"""

    def setUp(self):
        self.analyzer = YieldVsScore()

    def test_high_quality_low_valuation(self):
        """高质量 + 低估值 = 优质低估"""
        stock = StockData("TEST", score=8.0, dividend_yield=6.0)
        q = self.analyzer.classify_quadrant(stock)
        self.assertEqual(q, Quadrant.HIGH_QUALITY_LOW_VALUATION)

    def test_high_quality_high_valuation(self):
        """高质量 + 高估值 = 价值陷阱"""
        stock = StockData("TEST", score=8.0, dividend_yield=2.0)
        q = self.analyzer.classify_quadrant(stock)
        self.assertEqual(q, Quadrant.HIGH_QUALITY_HIGH_VALUATION)

    def test_low_quality_low_valuation(self):
        """低质量 + 低估值 = 价值风险"""
        stock = StockData("TEST", score=3.0, dividend_yield=6.0)
        q = self.analyzer.classify_quadrant(stock)
        self.assertEqual(q, Quadrant.LOW_QUALITY_LOW_VALUATION)

    def test_low_quality_high_valuation(self):
        """低质量 + 高估值 = 垃圾"""
        stock = StockData("TEST", score=3.0, dividend_yield=2.0)
        q = self.analyzer.classify_quadrant(stock)
        self.assertEqual(q, Quadrant.LOW_QUALITY_HIGH_VALUATION)

    def test_boundary_high_score(self):
        """边界: score = 6"""
        stock = StockData("TEST", score=6.0, dividend_yield=5.0)
        q = self.analyzer.classify_quadrant(stock)
        self.assertEqual(q, Quadrant.HIGH_QUALITY_LOW_VALUATION)

    def test_boundary_low_score(self):
        """边界: score = 4"""
        stock = StockData("TEST", score=4.0, dividend_yield=5.0)
        q = self.analyzer.classify_quadrant(stock)
        self.assertEqual(q, Quadrant.LOW_QUALITY_LOW_VALUATION)

    def test_boundary_yield(self):
        """边界: yield = 4"""
        stock = StockData("TEST", score=8.0, dividend_yield=4.0)
        q = self.analyzer.classify_quadrant(stock)
        self.assertEqual(q, Quadrant.HIGH_QUALITY_LOW_VALUATION)

    def test_middle_range(self):
        """中间地带: 4 < score < 6"""
        stock = StockData("TEST", score=5.0, dividend_yield=5.0)
        q = self.analyzer.classify_quadrant(stock)
        self.assertEqual(q, "中性偏低估值")

    def test_no_yield_data(self):
        """无收益率数据"""
        stock = StockData("TEST", score=5.0, dividend_yield=None, pe=None)
        q = self.analyzer.classify_quadrant(stock)
        self.assertEqual(q, "未知")


class TestRecommendations(unittest.TestCase):
    """推荐功能测试"""

    def test_top_right_recommendation(self):
        """右上象限推荐"""
        analyzer = YieldVsScore()
        analyzer.add_stock("CBA", score=8.0, dividend_yield=5.0)  # 推荐
        analyzer.add_stock("NAB", score=7.0, dividend_yield=6.0)  # 推荐
        analyzer.add_stock("BAD", score=3.0, dividend_yield=5.0)  # 不推荐
        analyzer.add_stock("UGLY", score=2.0, dividend_yield=2.0)  # 不推荐

        recommendations = analyzer.get_recommendations()

        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0]['ticker'], "CBA")
        self.assertEqual(recommendations[1]['ticker'], "NAB")

    def test_recommendations_sorted_by_score(self):
        """推荐按分数排序"""
        analyzer = YieldVsScore()
        analyzer.add_stock("LOW", score=6.1, dividend_yield=5.0)
        analyzer.add_stock("HIGH", score=9.0, dividend_yield=5.0)
        analyzer.add_stock("MID", score=7.5, dividend_yield=5.0)

        recommendations = analyzer.get_recommendations()

        self.assertEqual(recommendations[0]['ticker'], "HIGH")
        self.assertEqual(recommendations[1]['ticker'], "MID")
        self.assertEqual(recommendations[2]['ticker'], "LOW")

    def test_no_recommendations(self):
        """无推荐"""
        analyzer = YieldVsScore()
        analyzer.add_stock("BAD1", score=3.0, dividend_yield=5.0)
        analyzer.add_stock("BAD2", score=2.0, dividend_yield=2.0)

        recommendations = analyzer.get_recommendations()

        self.assertEqual(len(recommendations), 0)


class TestEmptyHandling(unittest.TestCase):
    """空数据处理测试"""

    def test_empty_analyzer(self):
        """空分析器"""
        analyzer = YieldVsScore()

        recommendations = analyzer.get_recommendations()
        self.assertEqual(len(recommendations), 0)

        quadrant_data = analyzer.get_all_by_quadrant()
        for stocks in quadrant_data.values():
            self.assertEqual(len(stocks), 0)

    def test_stock_with_no_yield(self):
        """无收益率数据的股票"""
        analyzer = YieldVsScore()
        analyzer.add_stock("UNKNOWN", score=5.0, dividend_yield=None, pe=None)

        # 应该能添加但不会被推荐
        self.assertEqual(len(analyzer.stocks), 1)
        recommendations = analyzer.get_recommendations()
        self.assertEqual(len(recommendations), 0)


class TestMultiIndustry(unittest.TestCase):
    """多行业测试"""

    def test_multi_industry(self):
        """多行业数据"""
        analyzer = YieldVsScore()
        analyzer.add_stock("CBA", score=8.0, dividend_yield=5.0, industry="Banks")
        analyzer.add_stock("NAB", score=7.0, dividend_yield=6.0, industry="Banks")
        analyzer.add_stock("WES", score=8.0, dividend_yield=4.0, industry="Consumer")
        analyzer.add_stock("BHP", score=7.0, dividend_yield=8.0, industry="Materials")

        self.assertEqual(len(analyzer.industries), 3)
        self.assertEqual(len(analyzer.industries["Banks"]), 2)
        self.assertEqual(len(analyzer.industries["Consumer"]), 1)
        self.assertEqual(len(analyzer.industries["Materials"]), 1)

    def test_industry_with_recommendations(self):
        """行业推荐"""
        analyzer = YieldVsScore()
        analyzer.add_stock("CBA", score=8.5, dividend_yield=5.2, industry="Banks")
        analyzer.add_stock("WES", score=7.5, dividend_yield=4.2, industry="Consumer")

        recommendations = analyzer.get_recommendations()

        # 两个都应该被推荐
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0]['industry'], "Banks")
        self.assertEqual(recommendations[1]['industry'], "Consumer")


class TestEarningYield(unittest.TestCase):
    """Earning Yield 计算测试"""

    def test_pe_to_earning_yield(self):
        """PE 转 Earning Yield"""
        stock = StockData("TEST", score=5.0, pe=20)
        self.assertAlmostEqual(stock.earning_yield, 5.0, places=1)

    def test_pe_zero_handling(self):
        """PE=0 处理"""
        stock = StockData("TEST", score=5.0, pe=0)
        self.assertIsNone(stock.earning_yield)

    def test_valuation_yield_preference(self):
        """估值收益率优先使用 Earning Yield"""
        stock = StockData("TEST", score=5.0, dividend_yield=3.0, pe=10)
        # earning_yield = 10%, dividend_yield = 3%
        self.assertAlmostEqual(stock.valuation_yield, 10.0, places=1)

    def test_valuation_yield_fallback(self):
        """无 PE 时回退到 Dividend Yield"""
        stock = StockData("TEST", score=5.0, dividend_yield=4.5, pe=None)
        self.assertAlmostEqual(stock.valuation_yield, 4.5, places=1)


class TestGetAllByQuadrant(unittest.TestCase):
    """象限汇总测试"""

    def test_all_quadrants(self):
        """所有象限"""
        analyzer = YieldVsScore()
        analyzer.add_stock("RECOMMENDED", score=8.0, dividend_yield=5.0)
        analyzer.add_stock("TRAP", score=8.0, dividend_yield=2.0)
        analyzer.add_stock("RISKY", score=3.0, dividend_yield=5.0)
        analyzer.add_stock("GARBAGE", score=3.0, dividend_yield=2.0)

        quadrant_data = analyzer.get_all_by_quadrant()

        self.assertEqual(len(quadrant_data[Quadrant.HIGH_QUALITY_LOW_VALUATION]), 1)
        self.assertEqual(len(quadrant_data[Quadrant.HIGH_QUALITY_HIGH_VALUATION]), 1)
        self.assertEqual(len(quadrant_data[Quadrant.LOW_QUALITY_LOW_VALUATION]), 1)
        self.assertEqual(len(quadrant_data[Quadrant.LOW_QUALITY_HIGH_VALUATION]), 1)


class TestConstants(unittest.TestCase):
    """常量测试"""

    def test_score_thresholds(self):
        """分数阈值"""
        self.assertEqual(SCORE_THRESHOLD_HIGH, 6.0)
        self.assertEqual(SCORE_THRESHOLD_LOW, 4.0)

    def test_yield_threshold(self):
        """收益率阈值"""
        self.assertEqual(YIELD_THRESHOLD, 4.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
