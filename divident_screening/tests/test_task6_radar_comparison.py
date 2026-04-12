"""
Tests for Task 6: Comparison data generation.
Validates that asx_scorer.py score_to_dict / generate_comparison_data
produce correct structured data for frontend rendering.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asx_scorer import ScoringSystem, ScoreResult, score_to_dict, generate_comparison_data


class TestComparisonData(unittest.TestCase):
    """Test comparison data generation."""

    def _make_result(self, ticker, industry, score, details=None, passed=None):
        r = ScoreResult(ticker=ticker, industry=industry, total_score=score, max_score=10)
        r.details = details or [
            {'metric': 'M1', 'score': score, 'max': 10},
            {'metric': 'M2', 'score': score - 1, 'max': 10},
        ]
        r.passed_checks = passed or []
        return r

    def test_score_to_dict_basic(self):
        """Test single result serialization."""
        result = self._make_result("CBA", "Banks", 8.0, passed=['NIM', 'CET1'])
        d = score_to_dict(result)

        self.assertEqual(d['ticker'], 'CBA')
        self.assertEqual(d['industry'], 'Banks')
        self.assertEqual(d['score']['total'], 8.0)
        self.assertEqual(d['score']['max'], 10)
        self.assertEqual(d['score']['percentage'], 80.0)
        self.assertEqual(d['passed_checks'], ['NIM', 'CET1'])
        self.assertEqual(len(d['details']), 2)

    def test_score_to_dict_zero_max(self):
        """Test edge case: max_score is 0."""
        result = ScoreResult(ticker="X", industry="Banks", total_score=0, max_score=0)
        d = score_to_dict(result)
        self.assertEqual(d['score']['percentage'], 0)

    def test_two_stock_comparison(self):
        """Test two stock comparison data."""
        r1 = self._make_result("CBA", "Banks", 8.0, passed=['NIM', 'CET1'])
        r2 = self._make_result("NAB", "Banks", 6.0, passed=['ROE'])

        data = generate_comparison_data([r1, r2])

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['ticker'], 'CBA')
        self.assertEqual(data[1]['ticker'], 'NAB')
        self.assertEqual(data[0]['score']['total'], 8.0)
        self.assertEqual(data[1]['score']['total'], 6.0)

    def test_three_stock_same_industry(self):
        """Test three same-industry stocks."""
        results = [
            self._make_result("CBA", "Banks", 8.0),
            self._make_result("NAB", "Banks", 6.0),
            self._make_result("WBC", "Banks", 5.0),
        ]
        data = generate_comparison_data(results)

        self.assertEqual(len(data), 3)
        tickers = [d['ticker'] for d in data]
        self.assertIn('CBA', tickers)
        self.assertIn('NAB', tickers)
        self.assertIn('WBC', tickers)

    def test_cross_industry_comparison(self):
        """Test cross-industry comparison."""
        results = [
            self._make_result("CBA", "Banks", 8.0),
            self._make_result("RIO", "Materials", 7.0),
            self._make_result("WES", "Consumer", 9.0),
        ]
        data = generate_comparison_data(results)

        self.assertEqual(len(data), 3)
        industries = [d['industry'] for d in data]
        self.assertIn('Banks', industries)
        self.assertIn('Materials', industries)
        self.assertIn('Consumer', industries)

    def test_empty_results(self):
        """Test empty results returns empty list."""
        data = generate_comparison_data([])
        self.assertEqual(data, [])

    def test_single_stock(self):
        """Test single stock comparison data."""
        r = self._make_result("CBA", "Banks", 8.5, passed=['NIM'])
        data = generate_comparison_data([r])

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['ticker'], 'CBA')
        self.assertEqual(data[0]['score']['total'], 8.5)

    def test_details_preserved(self):
        """Test that metric details are preserved."""
        details = [
            {'metric': 'NIM', 'score': 8.0, 'max': 10, 'value': '1.93%', 'description': 'Net Interest Margin'},
            {'metric': 'CET1', 'score': 7.0, 'max': 10, 'value': '12.5%'},
        ]
        r = ScoreResult(ticker="CBA", industry="Banks", total_score=8.0, max_score=10)
        r.details = details

        d = score_to_dict(r)
        self.assertEqual(len(d['details']), 2)
        self.assertEqual(d['details'][0]['metric'], 'NIM')
        self.assertEqual(d['details'][0]['value'], '1.93%')
        self.assertEqual(d['details'][1]['metric'], 'CET1')

    def test_percentage_calculation(self):
        """Test percentage rounding."""
        r = self._make_result("CBA", "Banks", 7.33)
        d = score_to_dict(r)
        self.assertEqual(d['score']['percentage'], 73.3)


def run_tests():
    """Run all comparison data tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestComparisonData)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
