"""
Task 3: Infrastructure Scorecard - Unit Tests
Validates the normalization-based scoring for Infrastructure industry.

根据 score_normalisation.md 设计:
- EBITDA Margin: 正向, warn=45%, target=65%
- Cash Conversion: 正向, warn=50%, target=95%
- Interest Cover: 正向, warn=1.5x, target=4.0x
- EV/EBITDA: 逆向, warn=18x, target=10x
- CPI Linkage: 正向, warn=50%, target=100%
- WACE: 正向, warn=5年, target=20年
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asx_scorer import ScoringSystem, normalize_positive, normalize_negative, normalize_range, ScoreResult


class TestInfrastructureNormalization(unittest.TestCase):
    """Test normalization functions for Infrastructure scoring."""

    # ===== EBITDA Margin Tests (正向指标: warn=45%, target=65%) =====

    def test_ebitda_margin_at_target(self):
        """EBITDA Margin at target (65%) should score 10"""
        score = normalize_positive(65, warn=45, target=65)
        self.assertEqual(score, 10.0)

    def test_ebitda_margin_at_warn(self):
        """EBITDA Margin at warn (45%) should score 0"""
        score = normalize_positive(45, warn=45, target=65)
        self.assertEqual(score, 0.0)

    def test_ebitda_margin_mid(self):
        """EBITDA Margin at midpoint (55%) should score ~5"""
        score = normalize_positive(55, warn=45, target=65)
        self.assertAlmostEqual(score, 5.0, places=1)

    def test_ebitda_margin_above_target(self):
        """EBITDA Margin above target (75%) should score 10 (capped)"""
        score = normalize_positive(75, warn=45, target=65)
        self.assertEqual(score, 10.0)

    def test_ebitda_margin_below_warn(self):
        """EBITDA Margin below warn (35%) should score 0 (floor)"""
        score = normalize_positive(35, warn=45, target=65)
        self.assertEqual(score, 0.0)

    # ===== Cash Conversion Tests (正向指标: warn=50%, target=95%) =====

    def test_cash_conversion_at_target(self):
        """Cash Conversion at target (95%) should score 10"""
        score = normalize_positive(95, warn=50, target=95)
        self.assertEqual(score, 10.0)

    def test_cash_conversion_at_warn(self):
        """Cash Conversion at warn (50%) should score 0"""
        score = normalize_positive(50, warn=50, target=95)
        self.assertEqual(score, 0.0)

    def test_cash_conversion_mid(self):
        """Cash Conversion at midpoint (72.5%) should score ~5"""
        score = normalize_positive(72.5, warn=50, target=95)
        self.assertAlmostEqual(score, 5.0, places=1)

    # ===== Interest Cover Tests (正向指标: warn=1.5x, target=4.0x) =====

    def test_interest_cover_safe(self):
        """Interest Cover at target (4.0x) should score 10"""
        score = normalize_positive(4.0, warn=1.5, target=4.0)
        self.assertEqual(score, 10.0)

    def test_interest_cover_risky(self):
        """Interest Cover at warn (1.5x) should score 0"""
        score = normalize_positive(1.5, warn=1.5, target=4.0)
        self.assertEqual(score, 0.0)

    def test_interest_cover_mid(self):
        """Interest Cover at midpoint (2.75x) should score ~5"""
        score = normalize_positive(2.75, warn=1.5, target=4.0)
        self.assertAlmostEqual(score, 5.0, places=1)

    def test_interest_cover_above_target(self):
        """Interest Cover above target (5.0x) should score 10 (capped)"""
        score = normalize_positive(5.0, warn=1.5, target=4.0)
        self.assertEqual(score, 10.0)

    def test_interest_cover_below_warn(self):
        """Interest Cover below warn (1.0x) should score 0 (floor)"""
        score = normalize_positive(1.0, warn=1.5, target=4.0)
        self.assertEqual(score, 0.0)

    # ===== EV/EBITDA Tests (逆向指标: warn=18x, target=10x) =====

    def test_ev_ebitda_cheap(self):
        """EV/EBITDA at target (10x) should score 10 (逆向最优)"""
        score = normalize_negative(10, warn=18, target=10)
        self.assertEqual(score, 10.0)

    def test_ev_ebitda_expensive(self):
        """EV/EBITDA at warn (18x) should score 0 (逆向边界)"""
        score = normalize_negative(18, warn=18, target=10)
        self.assertEqual(score, 0.0)

    def test_ev_ebitda_mid(self):
        """EV/EBITDA at midpoint (14x) should score ~5"""
        score = normalize_negative(14, warn=18, target=10)
        self.assertAlmostEqual(score, 5.0, places=1)

    def test_ev_ebitda_below_target(self):
        """EV/EBITDA below target (8x) should score 10 (capped)"""
        score = normalize_negative(8, warn=18, target=10)
        self.assertEqual(score, 10.0)

    def test_ev_ebitda_above_warn(self):
        """EV/EBITDA above warn (20x) should score 0 (floor)"""
        score = normalize_negative(20, warn=18, target=10)
        self.assertEqual(score, 0.0)

    # ===== CPI Linkage Tests (正向指标: warn=50%, target=100%) =====

    def test_cpi_full_hedge(self):
        """CPI Linkage at target (100%) should score 10"""
        score = normalize_positive(100, warn=50, target=100)
        self.assertEqual(score, 10.0)

    def test_cpi_no_hedge(self):
        """CPI Linkage at warn (50%) should score 0"""
        score = normalize_positive(50, warn=50, target=100)
        self.assertEqual(score, 0.0)

    def test_cpi_partial_hedge(self):
        """CPI Linkage at midpoint (75%) should score ~5"""
        score = normalize_positive(75, warn=50, target=100)
        self.assertAlmostEqual(score, 5.0, places=1)

    # ===== WACE Tests (正向指标: warn=5年, target=20年) =====

    def test_wace_long_term(self):
        """WACE at target (20 years) should score 10"""
        score = normalize_positive(20, warn=5, target=20)
        self.assertEqual(score, 10.0)

    def test_wace_short_term(self):
        """WACE at warn (5 years) should score 0"""
        score = normalize_positive(5, warn=5, target=20)
        self.assertEqual(score, 0.0)

    def test_wace_mid_term(self):
        """WACE at midpoint (12.5 years) should score ~5"""
        score = normalize_positive(12.5, warn=5, target=20)
        self.assertAlmostEqual(score, 5.0, places=1)


class TestInfrastructureScoring(unittest.TestCase):
    """Test full Infrastructure scoring with test data."""

    def test_weighted_sum_perfect_score(self):
        """All 6 metrics at target should give total score of 60 (10 each)"""
        # Create mock data with all perfect values
        data = {
            'ticker': 'TEST',
            'ratios': {
                'EBITDA Margin': {'TTM': 65.0},
                'Interest Coverage Ratio': {'TTM': 4.0},
                'EV/EBITDA Ratio': {'TTM': 10.0},
                'CPI Linkage': {'TTM': 100.0},
                'WACE': {'TTM': 20.0}
            },
            'income_statement': {
                'Operating Cash Flow': {'TTM': 950.0},
                'EBITDA': {'TTM': 1000.0}
            }
        }

        scorer = ScoringSystem(data)
        result = scorer.score_infrastructure()

        # Should have 6 details (6 metrics)
        self.assertEqual(len(result.details), 6)

        # Each should score 10, total should be 60
        total = sum(d['score'] for d in result.details)
        self.assertEqual(total, 60.0)

    def test_weighted_sum_zero_score(self):
        """All 6 metrics at warn should give total score of 0"""
        # Create mock data with all warning values
        data = {
            'ticker': 'TEST',
            'ratios': {
                'EBITDA Margin': {'TTM': 45.0},
                'Interest Coverage Ratio': {'TTM': 1.5},
                'EV/EBITDA Ratio': {'TTM': 18.0},
                'CPI Linkage': {'TTM': 50.0},
                'WACE': {'TTM': 5.0}
            },
            'income_statement': {
                'Operating Cash Flow': {'TTM': 500.0},
                'EBITDA': {'TTM': 1000.0}
            }
        }

        scorer = ScoringSystem(data)
        result = scorer.score_infrastructure()

        total = sum(d['score'] for d in result.details)
        self.assertEqual(total, 0.0)


class TestInfrastructureWithTestData(unittest.TestCase):
    """Test Infrastructure scoring with standard test data."""

    def setUp(self):
        """Load APA test data."""
        import json
        test_data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'tests', 'test_data', 'apa_standard.json'
        )
        with open(test_data_path, 'r') as f:
            self.test_data = json.load(f)
        self.scorer = ScoringSystem(self.test_data)

    def test_apa_ebitda_margin_scoring(self):
        """Test APA EBITDA Margin scoring (61.31%)"""
        ebitda_margin = self.scorer._get_value('EBITDA Margin')
        score = normalize_positive(ebitda_margin, warn=45, target=65)

        # 61.31% is between 45% and 65%
        # Score = (61.31 - 45) / (65 - 45) * 10 = 16.31/20 * 10 = 8.155
        self.assertAlmostEqual(score, 8.155, places=1)

    def test_apa_cash_conversion_scoring(self):
        """Test APA Cash Conversion scoring (61.02%)"""
        # Calculate from OCF/EBITDA
        ocf = self.scorer._get_value('Operating Cash Flow')
        ebitda = self.scorer._get_value('EBITDA')
        cash_conv = (ocf / ebitda) * 100

        score = normalize_positive(cash_conv, warn=50, target=95)

        # Score = (61.02 - 50) / (95 - 50) * 10 = 11.02/45 * 10 = 2.449
        self.assertAlmostEqual(score, 2.449, places=1)

    def test_apa_interest_cover_scoring(self):
        """Test APA Interest Cover scoring (1.44x)"""
        interest_cov = self.scorer._get_value('Interest Coverage Ratio')
        score = normalize_positive(interest_cov, warn=1.5, target=4.0)

        # 1.44x is below warn (1.5x), so score should be 0
        self.assertEqual(score, 0.0)

    def test_apa_ev_ebitda_scoring(self):
        """Test APA EV/EBITDA scoring (12.67x)"""
        ev_ebitda = self.scorer._get_value('EV/EBITDA Ratio')
        score = normalize_negative(ev_ebitda, warn=18, target=10)

        # Score = (18 - 12.67) / (18 - 10) * 10 = 5.33/8 * 10 = 6.6625
        self.assertAlmostEqual(score, 6.6625, places=1)


def run_tests():
    """Run all infrastructure tests."""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestInfrastructureNormalization))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestInfrastructureScoring))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestInfrastructureWithTestData))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
