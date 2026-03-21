"""
Unit tests for scorers/infrastructure.py

Validates that the infrastructure scoring functions match score_infra.md specifications.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scorers.infrastructure import (
    score_ebitda_margin,
    score_interest_cover,
    score_cash_conversion,
    score_ev_ebitda,
    score_cpi_linkage,
    score_wace,
    calculate_infrastructure_score,
    get_value,
    WEIGHTS
)


class TestEBITDAMarginScore(unittest.TestCase):
    """Test EBITDA Margin scoring per score_infra.md"""

    def test_ebitda_excellent(self):
        """> 60% should score 10"""
        self.assertEqual(score_ebitda_margin(61), (10.0, "excellent"))
        self.assertEqual(score_ebitda_margin(65), (10.0, "excellent"))
        self.assertEqual(score_ebitda_margin(80), (10.0, "excellent"))

    def test_ebitda_good(self):
        """45% - 60% should score 7"""
        self.assertEqual(score_ebitda_margin(45), (7.0, "good"))
        self.assertEqual(score_ebitda_margin(50), (7.0, "good"))
        self.assertEqual(score_ebitda_margin(60), (7.0, "good"))

    def test_ebitda_fair(self):
        """30% - 45% should score 4"""
        self.assertEqual(score_ebitda_margin(30), (4.0, "fair"))
        self.assertEqual(score_ebitda_margin(35), (4.0, "fair"))
        self.assertEqual(score_ebitda_margin(45), (7.0, "good"))  # boundary

    def test_ebitda_poor(self):
        """< 25% should score 0"""
        self.assertEqual(score_ebitda_margin(24), (0.0, "poor"))
        self.assertEqual(score_ebitda_margin(20), (0.0, "poor"))
        self.assertEqual(score_ebitda_margin(0), (0.0, "poor"))

    def test_ebitda_none(self):
        """None should return 0"""
        self.assertEqual(score_ebitda_margin(None), (0.0, "N/A"))


class TestInterestCoverScore(unittest.TestCase):
    """Test Interest Cover scoring per score_infra.md"""

    def test_interest_excellent(self):
        """> 4.0x should score 10"""
        self.assertEqual(score_interest_cover(4.1), (10.0, "excellent"))
        self.assertEqual(score_interest_cover(5.0), (10.0, "excellent"))
        self.assertEqual(score_interest_cover(10.0), (10.0, "excellent"))

    def test_interest_good(self):
        """2.5x - 4.0x should score 7"""
        self.assertEqual(score_interest_cover(2.5), (7.0, "good"))
        self.assertEqual(score_interest_cover(3.0), (7.0, "good"))
        self.assertEqual(score_interest_cover(4.0), (7.0, "good"))

    def test_interest_fair(self):
        """1.5x - 2.5x should score 4"""
        self.assertEqual(score_interest_cover(1.5), (4.0, "fair"))
        self.assertEqual(score_interest_cover(2.0), (4.0, "fair"))
        self.assertEqual(score_interest_cover(2.5), (7.0, "good"))  # boundary

    def test_interest_poor(self):
        """< 1.2x should score 0"""
        self.assertEqual(score_interest_cover(1.1), (0.0, "poor"))
        self.assertEqual(score_interest_cover(1.0), (0.0, "poor"))
        self.assertEqual(score_interest_cover(0.5), (0.0, "poor"))

    def test_interest_none(self):
        """None should return 0"""
        self.assertEqual(score_interest_cover(None), (0.0, "N/A"))


class TestCashConversionScore(unittest.TestCase):
    """Test Cash Conversion scoring per score_infra.md"""

    def test_cash_excellent(self):
        """> 85% should score 10"""
        self.assertEqual(score_cash_conversion(86), (10.0, "excellent"))
        self.assertEqual(score_cash_conversion(90), (10.0, "excellent"))
        self.assertEqual(score_cash_conversion(100), (10.0, "excellent"))

    def test_cash_good(self):
        """70% - 85% should score 7"""
        self.assertEqual(score_cash_conversion(70), (7.0, "good"))
        self.assertEqual(score_cash_conversion(75), (7.0, "good"))
        self.assertEqual(score_cash_conversion(85), (7.0, "good"))

    def test_cash_fair(self):
        """50% - 70% should score 4"""
        self.assertEqual(score_cash_conversion(50), (4.0, "fair"))
        self.assertEqual(score_cash_conversion(60), (4.0, "fair"))
        self.assertEqual(score_cash_conversion(70), (7.0, "good"))  # boundary

    def test_cash_poor(self):
        """< 40% should score 0"""
        self.assertEqual(score_cash_conversion(39), (0.0, "poor"))
        self.assertEqual(score_cash_conversion(30), (0.0, "poor"))
        self.assertEqual(score_cash_conversion(0), (0.0, "poor"))

    def test_cash_none(self):
        """None should return 0"""
        self.assertEqual(score_cash_conversion(None), (0.0, "N/A"))


class TestEVEBITDAScore(unittest.TestCase):
    """Test EV/EBITDA scoring per score_infra.md"""

    def test_ev_excellent(self):
        """10x - 13x should score 10"""
        self.assertEqual(score_ev_ebitda(10), (10.0, "excellent"))
        self.assertEqual(score_ev_ebitda(12), (10.0, "excellent"))
        self.assertEqual(score_ev_ebitda(13), (10.0, "excellent"))

    def test_ev_good(self):
        """13x - 16x should score 7"""
        self.assertEqual(score_ev_ebitda(14), (7.0, "good"))
        self.assertEqual(score_ev_ebitda(15), (7.0, "good"))
        self.assertEqual(score_ev_ebitda(16), (7.0, "good"))

    def test_ev_fair(self):
        """16x - 20x should score 4"""
        self.assertEqual(score_ev_ebitda(17), (4.0, "fair"))
        self.assertEqual(score_ev_ebitda(18), (4.0, "fair"))
        self.assertEqual(score_ev_ebitda(20), (4.0, "fair"))

    def test_ev_poor(self):
        """> 22x should score 0"""
        self.assertEqual(score_ev_ebitda(23), (0.0, "poor"))
        self.assertEqual(score_ev_ebitda(25), (0.0, "poor"))
        self.assertEqual(score_ev_ebitda(50), (0.0, "poor"))

    def test_ev_none(self):
        """None should return 0"""
        self.assertEqual(score_ev_ebitda(None), (0.0, "N/A"))


class TestCPILinkageScore(unittest.TestCase):
    """Test CPI Linkage scoring per score_infra.md"""

    def test_cpi_excellent(self):
        """> 80% should score 10"""
        self.assertEqual(score_cpi_linkage(81), (10.0, "excellent"))
        self.assertEqual(score_cpi_linkage(85), (10.0, "excellent"))
        self.assertEqual(score_cpi_linkage(100), (10.0, "excellent"))

    def test_cpi_good(self):
        """50% - 80% should score 7"""
        self.assertEqual(score_cpi_linkage(50), (7.0, "good"))
        self.assertEqual(score_cpi_linkage(65), (7.0, "good"))
        self.assertEqual(score_cpi_linkage(80), (7.0, "good"))

    def test_cpi_fair(self):
        """20% - 50% should score 4"""
        self.assertEqual(score_cpi_linkage(20), (4.0, "fair"))
        self.assertEqual(score_cpi_linkage(35), (4.0, "fair"))
        self.assertEqual(score_cpi_linkage(50), (7.0, "good"))  # boundary

    def test_cpi_poor(self):
        """< 20% should score 0"""
        self.assertEqual(score_cpi_linkage(19), (0.0, "poor"))
        self.assertEqual(score_cpi_linkage(10), (0.0, "poor"))
        self.assertEqual(score_cpi_linkage(0), (0.0, "poor"))

    def test_cpi_none(self):
        """None should return 0"""
        self.assertEqual(score_cpi_linkage(None), (0.0, "N/A"))


class TestWACEScore(unittest.TestCase):
    """Test WACE scoring per score_infra.md"""

    def test_wace_excellent(self):
        """> 20年 should score 10"""
        self.assertEqual(score_wace(21), (10.0, "excellent"))
        self.assertEqual(score_wace(25), (10.0, "excellent"))
        self.assertEqual(score_wace(30), (10.0, "excellent"))

    def test_wace_good(self):
        """12 - 20年 should score 7"""
        self.assertEqual(score_wace(12), (7.0, "good"))
        self.assertEqual(score_wace(15), (7.0, "good"))
        self.assertEqual(score_wace(20), (7.0, "good"))

    def test_wace_fair(self):
        """7 - 12年 should score 4"""
        self.assertEqual(score_wace(7), (4.0, "fair"))
        self.assertEqual(score_wace(10), (4.0, "fair"))
        self.assertEqual(score_wace(12), (7.0, "good"))  # boundary

    def test_wace_poor(self):
        """< 5年 should score 0"""
        self.assertEqual(score_wace(4), (0.0, "poor"))
        self.assertEqual(score_wace(3), (0.0, "poor"))
        self.assertEqual(score_wace(0), (0.0, "poor"))

    def test_wace_none(self):
        """None should return 0"""
        self.assertEqual(score_wace(None), (0.0, "N/A"))


class TestGetValue(unittest.TestCase):
    """Test data extraction utility"""

    def test_get_value_from_ratios(self):
        """Should find value in ratios section"""
        data = {
            'ratios': {
                'EBITDA Margin': {'TTM': 55.0}
            }
        }
        self.assertEqual(get_value(data, 'EBITDA Margin'), 55.0)

    def test_get_value_from_income(self):
        """Should find value in income_statement section"""
        data = {
            'income_statement': {
                'EBITDA': {'TTM': 1000}
            }
        }
        self.assertEqual(get_value(data, 'EBITDA'), 1000.0)

    def test_get_value_priority(self):
        """TTM should have priority over FY 2025"""
        data = {
            'ratios': {
                'EBITDA Margin': {'TTM': 55.0, 'FY 2025': 60.0}
            }
        }
        self.assertEqual(get_value(data, 'EBITDA Margin'), 55.0)

    def test_get_value_fallback_keys(self):
        """Should try alternate keys"""
        data = {
            'ratios': {
                'EV/EBITDA Ratio': {'TTM': 12.0}
            }
        }
        self.assertEqual(get_value(data, 'EV/EBITDA Ratio', 'EV / EBITDA Ratio'), 12.0)

    def test_get_value_not_found(self):
        """Should return None if not found"""
        data = {'ratios': {}}
        self.assertIsNone(get_value(data, 'NonExistent'))

    def test_get_value_direct_float(self):
        """Should handle direct float values"""
        data = {
            'ratios': {
                'WACE': 15.0
            }
        }
        self.assertEqual(get_value(data, 'WACE'), 15.0)


class TestWeights(unittest.TestCase):
    """Test weight configuration"""

    def test_weights_sum(self):
        """Weights should sum to 1.0"""
        total = sum(WEIGHTS.values())
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_weights_positive(self):
        """All weights should be positive"""
        for weight in WEIGHTS.values():
            self.assertGreater(weight, 0)


class TestCalculateInfrastructureScore(unittest.TestCase):
    """Test complete infrastructure score calculation"""

    def test_perfect_score(self):
        """All metrics at target should give 10.0"""
        data = {
            'ticker': 'APA.AX',
            'income_statement': {
                'EBITDA': {'TTM': 1000},
                'Operating Income': {'TTM': 800},
                'Interest Expense': {'TTM': 100},
            },
            'cash_flow': {
                'Operating Cash Flow': {'TTM': 900},
            },
            'balance_sheet': {
                'Cash & Equivalents': {'TTM': 200},
            },
            'ratios': {
                'EBITDA Margin': {'TTM': 65.0},
                'Interest Coverage Ratio': {'TTM': 5.0},
                'EV/EBITDA Ratio': {'TTM': 12.0},
                'CPI Linkage': {'TTM': 85.0},
                'WACE': {'TTM': 25.0}
            }
        }
        result = calculate_infrastructure_score(data)

        # Verify each metric gets 10
        self.assertEqual(result['metrics']['EBITDA Margin']['score'], 10.0)
        self.assertEqual(result['metrics']['Interest Cover']['score'], 10.0)
        self.assertEqual(result['metrics']['Cash Conversion']['score'], 10.0)
        self.assertEqual(result['metrics']['EV/EBITDA']['score'], 10.0)
        self.assertEqual(result['metrics']['CPI Linkage']['score'], 10.0)
        self.assertEqual(result['metrics']['WACE']['score'], 10.0)

        # Total should be 10.0 (no risk penalty)
        self.assertEqual(result['total_score'], 10.0)
        self.assertFalse(result['risk_penalty'])

    def test_risk_penalty(self):
        """Interest Cover < 1.4 should apply 50% penalty"""
        data = {
            'ticker': 'RISKY.AX',
            'income_statement': {
                'EBITDA': {'TTM': 1000},
                'Operating Income': {'TTM': 120},
                'Interest Expense': {'TTM': 100},
            },
            'cash_flow': {
                'Operating Cash Flow': {'TTM': 900},
            },
            'balance_sheet': {
                'Cash & Equivalents': {'TTM': 200},
            },
            'ratios': {
                'EBITDA Margin': {'TTM': 65.0},
                'Interest Coverage Ratio': {'TTM': 1.2},  # < 1.4 triggers penalty, but score = 0 (below threshold)
                'EV/EBITDA Ratio': {'TTM': 12.0},
                'CPI Linkage': {'TTM': 85.0},
                'WACE': {'TTM': 25.0}
            }
        }
        result = calculate_infrastructure_score(data)

        # Risk penalty should be applied (<1.4)
        self.assertTrue(result['risk_penalty'])
        # Score calculation:
        # EBITDA: 10 * 0.2 = 2.0
        # Interest: 0 * 0.25 = 0 (1.2 < 1.2 gives 0)
        # Cash: 10 * 0.15 = 1.5
        # EV/EBITDA: 10 * 0.15 = 1.5
        # CPI: 10 * 0.15 = 1.5
        # WACE: 10 * 0.1 = 1.0
        # Total: 7.5 -> halved = 3.75
        self.assertAlmostEqual(result['total_score'], 3.75, places=2)

    def test_ticker_preserved(self):
        """Ticker should be preserved in result"""
        data = {
            'ticker': 'TCL.AX',
            'ratios': {}
        }
        result = calculate_infrastructure_score(data)
        self.assertEqual(result['ticker'], 'TCL.AX')

    def test_max_score_10(self):
        """Max score should always be 10.0"""
        data = {
            'ticker': 'TEST.AX',
            'ratios': {
                'EBITDA Margin': {'TTM': 100.0},
                'Interest Coverage Ratio': {'TTM': 100.0},
            }
        }
        result = calculate_infrastructure_score(data)
        self.assertEqual(result['max_score'], 10.0)

    def test_interest_cover_calculation(self):
        """Interest cover should be calculated from components if not available"""
        data = {
            'ticker': 'TEST.AX',
            'income_statement': {
                'EBIT': {'TTM': 400},
                'Interest Expense': {'TTM': 100},
            },
            'ratios': {}
        }
        result = calculate_infrastructure_score(data)
        # 400/100 = 4.0, should score 7 (good)
        self.assertEqual(result['metrics']['Interest Cover']['value'], 4.0)
        self.assertEqual(result['metrics']['Interest Cover']['score'], 7.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_empty_data(self):
        """Empty data should return zeros"""
        data = {'ticker': 'TEST.AX'}
        result = calculate_infrastructure_score(data)

        self.assertEqual(result['total_score'], 0.0)
        for metric, info in result['metrics'].items():
            self.assertEqual(info['score'], 0.0)

    def test_missing_sections(self):
        """Missing sections should not crash"""
        data = {
            'ticker': 'TEST.AX',
            'ratios': {
                'EBITDA Margin': {'TTM': 55.0}
            }
        }
        result = calculate_infrastructure_score(data)
        # Should not raise exception
        self.assertIn('EBITDA Margin', result['metrics'])

    def test_zero_ebitda(self):
        """Zero EBITDA should not cause division by zero"""
        data = {
            'ticker': 'TEST.AX',
            'income_statement': {
                'EBITDA': {'TTM': 0},
            },
            'cash_flow': {
                'Operating Cash Flow': {'TTM': 100},
            },
            'ratios': {}
        }
        result = calculate_infrastructure_score(data)
        # Should handle gracefully
        self.assertIn('Cash Conversion', result['metrics'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
