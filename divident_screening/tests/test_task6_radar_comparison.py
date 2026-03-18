"""
Tests for Task 6: Radar Comparison functionality.
Validates that asx_scorer.py generate_comparison_html works correctly.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asx_scorer import ScoringSystem, ScoreResult, generate_comparison_html


class TestRadarComparison(unittest.TestCase):
    """Test radar comparison functionality."""

    def test_two_stock_radar(self):
        """Test two stock radar overlay."""
        # Create two mock score results
        result1 = ScoreResult(ticker="CBA", industry="Banks", total_score=8.0, max_score=10)
        result1.details = [
            {'metric': 'NIM (净息差)', 'score': 8.0, 'max': 10, 'is_common': False},
            {'metric': 'CET1 Ratio', 'score': 7.0, 'max': 10, 'is_common': False},
            {'metric': 'Cost-to-Income', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'ROE', 'score': 9.0, 'max': 10, 'is_common': False},
            {'metric': 'Bad Debt Ratio', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'Payout Ratio', 'score': 7.0, 'max': 10, 'is_common': False},
        ]
        result1.passed_checks = ['NIM', 'CET1']

        result2 = ScoreResult(ticker="NAB", industry="Banks", total_score=6.0, max_score=10)
        result2.details = [
            {'metric': 'NIM (净息差)', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'CET1 Ratio', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'Cost-to-Income', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'ROE', 'score': 7.0, 'max': 10, 'is_common': False},
            {'metric': 'Bad Debt Ratio', 'score': 4.0, 'max': 10, 'is_common': False},
            {'metric': 'Payout Ratio', 'score': 6.0, 'max': 10, 'is_common': False},
        ]
        result2.passed_checks = ['ROE']

        # Generate comparison HTML
        html = generate_comparison_html([result1, result2])

        # Verify HTML contains expected elements
        self.assertIn('CBA', html)
        self.assertIn('NAB', html)
        self.assertIn('雷达图对比', html)
        self.assertIn('总分对比', html)
        self.assertIn('详细对比', html)
        self.assertIn('radarChart', html)
        self.assertIn('barChart', html)

    def test_same_industry_compare(self):
        """Test same industry comparison."""
        # Create three bank stocks
        results = []
        for ticker, score in [("CBA", 8.0), ("NAB", 6.0), ("WBC", 5.0)]:
            result = ScoreResult(ticker=ticker, industry="Banks", total_score=score, max_score=10)
            result.details = [
                {'metric': 'NIM (净息差)', 'score': score, 'max': 10, 'is_common': False},
                {'metric': 'CET1 Ratio', 'score': score - 1, 'max': 10, 'is_common': False},
                {'metric': 'Cost-to-Income', 'score': score - 2, 'max': 10, 'is_common': False},
                {'metric': 'ROE', 'score': score + 1, 'max': 10, 'is_common': False},
                {'metric': 'Bad Debt Ratio', 'score': score - 3, 'max': 10, 'is_common': False},
                {'metric': 'Payout Ratio', 'score': score - 1, 'max': 10, 'is_common': False},
            ]
            result.passed_checks = ['NIM']
            results.append(result)

        html = generate_comparison_html(results)

        # Verify all three stocks are in the HTML
        self.assertIn('CBA', html)
        self.assertIn('NAB', html)
        self.assertIn('WBC', html)
        self.assertIn('Banks', html)

    def test_cross_industry_compare(self):
        """Test cross industry comparison."""
        # Create different industry stocks
        result1 = ScoreResult(ticker="CBA", industry="Banks", total_score=8.0, max_score=10)
        result1.details = [
            {'metric': 'NIM', 'score': 8.0, 'max': 10, 'is_common': False},
            {'metric': 'CET1', 'score': 7.0, 'max': 10, 'is_common': False},
            {'metric': 'Cost', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'ROE', 'score': 9.0, 'max': 10, 'is_common': False},
            {'metric': 'Bad Debt', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'Payout', 'score': 7.0, 'max': 10, 'is_common': False},
        ]
        result1.passed_checks = ['NIM', 'CET1']

        result2 = ScoreResult(ticker="RIO", industry="Materials", total_score=7.0, max_score=10)
        result2.details = [
            {'metric': 'AISC', 'score': 7.0, 'max': 10, 'is_common': False},
            {'metric': 'CIP', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'NPAT', 'score': 8.0, 'max': 10, 'is_common': False},
            {'metric': 'FCF', 'score': 7.0, 'max': 10, 'is_common': False},
            {'metric': 'Leverage', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'Dividend', 'score': 8.0, 'max': 10, 'is_common': False},
        ]
        result2.passed_checks = ['AISC', 'FCF']

        result3 = ScoreResult(ticker="WES", industry="Consumer", total_score=9.0, max_score=10)
        result3.details = [
            {'metric': 'Margin', 'score': 9.0, 'max': 10, 'is_common': False},
            {'metric': 'ROE', 'score': 9.0, 'max': 10, 'is_common': False},
            {'metric': 'Inventory', 'score': 8.0, 'max': 10, 'is_common': False},
            {'metric': 'PE', 'score': 7.0, 'max': 10, 'is_common': False},
            {'metric': 'Yield', 'score': 9.0, 'max': 10, 'is_common': False},
            {'metric': 'Payout', 'score': 8.0, 'max': 10, 'is_common': False},
        ]
        result3.passed_checks = ['Margin', 'ROE']

        html = generate_comparison_html([result1, result2, result3])

        # Verify all industries present
        self.assertIn('Banks', html)
        self.assertIn('Materials', html)
        self.assertIn('Consumer', html)

    def test_stacked_bar_data(self):
        """Test stacked bar chart data generation."""
        result1 = ScoreResult(ticker="CBA", industry="Banks", total_score=8.5, max_score=10)
        result1.details = [
            {'metric': 'Metric1', 'score': 8.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric2', 'score': 9.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric3', 'score': 7.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric4', 'score': 9.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric5', 'score': 8.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric6', 'score': 9.0, 'max': 10, 'is_common': False},
        ]

        result2 = ScoreResult(ticker="NAB", industry="Banks", total_score=5.5, max_score=10)
        result2.details = [
            {'metric': 'Metric1', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric2', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric3', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric4', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric5', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'Metric6', 'score': 6.0, 'max': 10, 'is_common': False},
        ]

        html = generate_comparison_html([result1, result2])

        # Verify bar chart is in HTML
        self.assertIn('barChart', html)
        # Scores should be displayed
        self.assertIn('8.5', html)
        self.assertIn('5.5', html)

    def test_html_generation(self):
        """Test HTML generation renders correctly."""
        result = ScoreResult(ticker="CBA", industry="Banks", total_score=8.0, max_score=10)
        result.details = [
            {'metric': 'NIM', 'score': 8.0, 'max': 10, 'is_common': False},
            {'metric': 'CET1', 'score': 7.0, 'max': 10, 'is_common': False},
            {'metric': 'Cost', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'ROE', 'score': 9.0, 'max': 10, 'is_common': False},
            {'metric': 'Debt', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'Payout', 'score': 7.0, 'max': 10, 'is_common': False},
        ]
        result.passed_checks = ['NIM', 'CET1', 'ROE']

        html = generate_comparison_html([result])

        # Basic HTML structure checks
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('<html', html)
        self.assertIn('</html>', html)
        self.assertIn('echarts', html)
        self.assertIn('股票对比分析', html)

    def test_empty_results(self):
        """Test empty results handling."""
        html = generate_comparison_html([])
        self.assertIn('No data', html)

    def test_single_stock_comparison(self):
        """Test single stock comparison."""
        result = ScoreResult(ticker="CBA", industry="Banks", total_score=8.0, max_score=10)
        result.details = [
            {'metric': 'NIM', 'score': 8.0, 'max': 10, 'is_common': False},
            {'metric': 'CET1', 'score': 7.0, 'max': 10, 'is_common': False},
            {'metric': 'Cost', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'ROE', 'score': 9.0, 'max': 10, 'is_common': False},
            {'metric': 'Debt', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'Payout', 'score': 7.0, 'max': 10, 'is_common': False},
        ]
        result.passed_checks = ['NIM']

        html = generate_comparison_html([result])

        self.assertIn('CBA', html)
        self.assertIn('1 只股票对比', html)

    def test_indicators_alignment(self):
        """Test that indicators are properly aligned across different result sets."""
        result1 = ScoreResult(ticker="CBA", industry="Banks", total_score=8.0, max_score=10)
        result1.details = [
            {'metric': 'NIM (净息差)', 'score': 8.0, 'max': 10, 'is_common': False},
            {'metric': 'CET1', 'score': 7.0, 'max': 10, 'is_common': False},
        ]

        result2 = ScoreResult(ticker="RIO", industry="Materials", total_score=6.0, max_score=10)
        result2.details = [
            {'metric': 'AISC', 'score': 6.0, 'max': 10, 'is_common': False},
            {'metric': 'FCF', 'score': 5.0, 'max': 10, 'is_common': False},
            {'metric': 'Leverage', 'score': 7.0, 'max': 10, 'is_common': False},
        ]

        html = generate_comparison_html([result1, result2])

        # Should contain unique indicators from both
        self.assertIn('NIM', html)
        self.assertIn('AISC', html)
        self.assertIn('CET1', html)
        self.assertIn('FCF', html)
        self.assertIn('Leverage', html)


def run_tests():
    """Run all radar comparison tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRadarComparison)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
