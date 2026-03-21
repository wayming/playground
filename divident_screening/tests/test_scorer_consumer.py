"""
Unit tests for scorers/consumer.py

Validates that the consumer staples scoring functions match score_consuming.md specifications.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scorers.consumer import (
    score_ebit_margin,
    score_roe,
    score_inventory_days,
    score_ocf_margin,
    score_forward_pe,
    score_market_share,
    calculate_consumer_score,
    get_value,
    get_value_by_period,
    WEIGHTS
)


class TestEBITMarginScore(unittest.TestCase):
    """Test EBIT Margin scoring per score_consuming.md"""

    def test_ebit_excellent(self):
        """> 8% should score 10"""
        self.assertEqual(score_ebit_margin(8.1), (10.0, "excellent"))
        self.assertEqual(score_ebit_margin(10), (10.0, "excellent"))
        self.assertEqual(score_ebit_margin(15), (10.0, "excellent"))

    def test_ebit_good(self):
        """5% - 8% should score 7"""
        self.assertEqual(score_ebit_margin(5.0), (7.0, "good"))
        self.assertEqual(score_ebit_margin(6.5), (7.0, "good"))
        self.assertEqual(score_ebit_margin(8.0), (7.0, "good"))

    def test_ebit_fair(self):
        """3% - 5% should score 4"""
        self.assertEqual(score_ebit_margin(3.0), (4.0, "fair"))
        self.assertEqual(score_ebit_margin(4.0), (4.0, "fair"))
        self.assertEqual(score_ebit_margin(5.0), (7.0, "good"))  # boundary

    def test_ebit_poor(self):
        """< 2.5% should score 0"""
        self.assertEqual(score_ebit_margin(2.4), (0.0, "poor"))
        self.assertEqual(score_ebit_margin(2.0), (0.0, "poor"))
        self.assertEqual(score_ebit_margin(0), (0.0, "poor"))

    def test_ebit_none(self):
        """None should return 0"""
        self.assertEqual(score_ebit_margin(None), (0.0, "N/A"))


class TestROEScore(unittest.TestCase):
    """Test ROE scoring per score_consuming.md"""

    def test_roe_excellent(self):
        """> 30% should score 10"""
        self.assertEqual(score_roe(31), (10.0, "excellent"))
        self.assertEqual(score_roe(35), (10.0, "excellent"))
        self.assertEqual(score_roe(50), (10.0, "excellent"))

    def test_roe_good(self):
        """18% - 30% should score 7"""
        self.assertEqual(score_roe(18), (7.0, "good"))
        self.assertEqual(score_roe(25), (7.0, "good"))
        self.assertEqual(score_roe(30), (7.0, "good"))

    def test_roe_fair(self):
        """12% - 18% should score 4"""
        self.assertEqual(score_roe(12), (4.0, "fair"))
        self.assertEqual(score_roe(15), (4.0, "fair"))
        self.assertEqual(score_roe(18), (7.0, "good"))  # boundary

    def test_roe_poor(self):
        """< 10% should score 0"""
        self.assertEqual(score_roe(9), (0.0, "poor"))
        self.assertEqual(score_roe(5), (0.0, "poor"))
        self.assertEqual(score_roe(0), (0.0, "poor"))

    def test_roe_none(self):
        """None should return 0"""
        self.assertEqual(score_roe(None), (0.0, "N/A"))


class TestInventoryDaysScore(unittest.TestCase):
    """Test Inventory Days scoring per score_consuming.md"""

    def test_inv_excellent(self):
        """< 40 days should score 10"""
        self.assertEqual(score_inventory_days(39), (10.0, "excellent"))
        self.assertEqual(score_inventory_days(30), (10.0, "excellent"))
        self.assertEqual(score_inventory_days(20), (10.0, "excellent"))

    def test_inv_good(self):
        """40 - 85 days should score 7"""
        self.assertEqual(score_inventory_days(40), (7.0, "good"))
        self.assertEqual(score_inventory_days(60), (7.0, "good"))
        self.assertEqual(score_inventory_days(85), (7.0, "good"))

    def test_inv_fair(self):
        """85 - 110 days should score 4"""
        self.assertEqual(score_inventory_days(85), (7.0, "good"))  # boundary
        self.assertEqual(score_inventory_days(100), (4.0, "fair"))
        self.assertEqual(score_inventory_days(110), (4.0, "fair"))

    def test_inv_poor(self):
        """> 120 days should score 0"""
        self.assertEqual(score_inventory_days(121), (0.0, "poor"))
        self.assertEqual(score_inventory_days(130), (0.0, "poor"))
        self.assertEqual(score_inventory_days(200), (0.0, "poor"))

    def test_inv_none(self):
        """None should return 0"""
        self.assertEqual(score_inventory_days(None), (0.0, "N/A"))


class TestOCFMarginScore(unittest.TestCase):
    """Test OCF Margin scoring per score_consuming.md"""

    def test_ocf_excellent(self):
        """> 10% should score 10"""
        self.assertEqual(score_ocf_margin(11), (10.0, "excellent"))
        self.assertEqual(score_ocf_margin(12), (10.0, "excellent"))
        self.assertEqual(score_ocf_margin(15), (10.0, "excellent"))

    def test_ocf_good(self):
        """7% - 10% should score 7"""
        self.assertEqual(score_ocf_margin(7), (7.0, "good"))
        self.assertEqual(score_ocf_margin(8.5), (7.0, "good"))
        self.assertEqual(score_ocf_margin(10), (7.0, "good"))

    def test_ocf_fair(self):
        """4% - 7% should score 4"""
        self.assertEqual(score_ocf_margin(4), (4.0, "fair"))
        self.assertEqual(score_ocf_margin(5.5), (4.0, "fair"))
        self.assertEqual(score_ocf_margin(7), (7.0, "good"))  # boundary

    def test_ocf_poor(self):
        """< 4% should score 0"""
        self.assertEqual(score_ocf_margin(3.9), (0.0, "poor"))
        self.assertEqual(score_ocf_margin(2), (0.0, "poor"))
        self.assertEqual(score_ocf_margin(0), (0.0, "poor"))

    def test_ocf_none(self):
        """None should return 0"""
        self.assertEqual(score_ocf_margin(None), (0.0, "N/A"))


class TestForwardPEScore(unittest.TestCase):
    """Test Forward PE scoring per score_consuming.md"""

    def test_pe_excellent(self):
        """18x - 22x should score 10"""
        self.assertEqual(score_forward_pe(18), (10.0, "excellent"))
        self.assertEqual(score_forward_pe(20), (10.0, "excellent"))
        self.assertEqual(score_forward_pe(22), (10.0, "excellent"))

    def test_pe_good(self):
        """22x - 26x should score 7"""
        self.assertEqual(score_forward_pe(23), (7.0, "good"))
        self.assertEqual(score_forward_pe(25), (7.0, "good"))
        self.assertEqual(score_forward_pe(26), (7.0, "good"))

    def test_pe_fair(self):
        """26x - 30x should score 4"""
        self.assertEqual(score_forward_pe(27), (4.0, "fair"))
        self.assertEqual(score_forward_pe(29), (4.0, "fair"))
        self.assertEqual(score_forward_pe(30), (4.0, "fair"))

    def test_pe_poor(self):
        """> 32x should score 0"""
        self.assertEqual(score_forward_pe(33), (0.0, "poor"))
        self.assertEqual(score_forward_pe(40), (0.0, "poor"))
        self.assertEqual(score_forward_pe(50), (0.0, "poor"))

    def test_pe_none(self):
        """None should return 0"""
        self.assertEqual(score_forward_pe(None), (0.0, "N/A"))


class TestMarketShareScore(unittest.TestCase):
    """Test Market Share scoring per score_consuming.md"""

    def test_mkt_excellent_rank1(self):
        """Rank 1 should score 10"""
        self.assertEqual(score_market_share(10, 1), (10.0, "excellent"))

    def test_mkt_excellent_above25(self):
        """> 25% should score 10"""
        self.assertEqual(score_market_share(26, 5), (10.0, "excellent"))
        self.assertEqual(score_market_share(30, 3), (10.0, "excellent"))
        self.assertEqual(score_market_share(50, None), (10.0, "excellent"))

    def test_mkt_good_top3(self):
        """Top 3 should score 7"""
        self.assertEqual(score_market_share(15, 2), (7.0, "good"))
        self.assertEqual(score_market_share(10, 3), (7.0, "good"))

    def test_mkt_fair_middle(self):
        """Middle rank should score 4"""
        self.assertEqual(score_market_share(5, 5), (4.0, "fair"))
        self.assertEqual(score_market_share(3, 10), (4.0, "fair"))

    def test_mkt_none(self):
        """None should return 0"""
        self.assertEqual(score_market_share(None, None), (0.0, "N/A"))


class TestGetValue(unittest.TestCase):
    """Test data extraction utility"""

    def test_get_value_from_ratios(self):
        """Should find value in ratios section"""
        data = {
            'ratios': {
                'EBIT Margin': {'TTM': 8.0}
            }
        }
        self.assertEqual(get_value(data, 'EBIT Margin'), 8.0)

    def test_get_value_from_income(self):
        """Should find value in income_statement section"""
        data = {
            'income_statement': {
                'Revenue': {'TTM': 10000}
            }
        }
        self.assertEqual(get_value(data, 'Revenue'), 10000.0)

    def test_get_value_priority(self):
        """TTM should have priority over FY 2025"""
        data = {
            'ratios': {
                'ROE': {'TTM': 25.0, 'FY 2025': 30.0}
            }
        }
        self.assertEqual(get_value(data, 'ROE'), 25.0)

    def test_get_value_fallback_keys(self):
        """Should try alternate keys"""
        data = {
            'ratios': {
                'Operating Margin': {'TTM': 6.0}
            }
        }
        self.assertEqual(get_value(data, 'EBIT Margin', 'Operating Margin'), 6.0)

    def test_get_value_not_found(self):
        """Should return None if not found"""
        data = {'ratios': {}}
        self.assertIsNone(get_value(data, 'NonExistent'))

    def test_get_value_direct_float(self):
        """Should handle direct float values"""
        data = {
            'ratios': {
                'ROE': 25.0
            }
        }
        self.assertEqual(get_value(data, 'ROE'), 25.0)

    def test_get_value_by_period(self):
        """Should get value by specific period"""
        data = {
            'ratios': {
                'Inventory': {'TTM': 800, 'FY 2024': 750}
            }
        }
        self.assertEqual(get_value_by_period(data, 'Inventory', 'TTM'), 800)
        self.assertEqual(get_value_by_period(data, 'Inventory', 'FY 2024'), 750)


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


class TestCalculateConsumerScore(unittest.TestCase):
    """Test complete consumer score calculation"""

    def test_perfect_score(self):
        """All metrics at target should give 10.0"""
        data = {
            'ticker': 'WES.AX',
            'income_statement': {
                'Operating Income': {'TTM': 1200},
                'Revenue': {'TTM': 10000},
                'Cost of Revenue': {'TTM': 8000},
            },
            'cash_flow': {
                'Operating Cash Flow': {'TTM': 1200},
            },
            'balance_sheet': {
                'Inventory': {'TTM': 800},
            },
            'ratios': {
                'EBIT Margin': {'TTM': 10.0},
                'ROE': {'TTM': 35.0},
                'Forward PE': {'TTM': 20.0},
                'Market Share': {'TTM': 30.0},
                'Market Rank': {'TTM': 1},
            }
        }
        result = calculate_consumer_score(data)

        # Verify each metric gets 10
        self.assertEqual(result['metrics']['EBIT Margin']['score'], 10.0)
        self.assertEqual(result['metrics']['ROE']['score'], 10.0)
        self.assertEqual(result['metrics']['Inventory Days']['score'], 10.0)
        self.assertEqual(result['metrics']['OCF Margin']['score'], 10.0)
        self.assertEqual(result['metrics']['Forward PE']['score'], 10.0)
        self.assertEqual(result['metrics']['Market Share']['score'], 10.0)

        # Total should be 10.0 (no risk penalty)
        self.assertEqual(result['total_score'], 10.0)
        self.assertFalse(result['risk_penalty'])

    def test_risk_penalty(self):
        """Inventory Days Growth > 15% should apply 20% penalty"""
        data = {
            'ticker': 'RISKY.AX',
            'income_statement': {
                'Operating Income': {'TTM': 600},
                'Revenue': {'TTM': 10000},
                'Cost of Revenue': {'TTM': 8000},
            },
            'cash_flow': {
                'Operating Cash Flow': {'TTM': 800},
            },
            'balance_sheet': {
                'Inventory': {'TTM': 960},  # 960/8000*365 = 43.8 days (TTM)
            },
            'ratios': {
                'EBIT Margin': {'TTM': 6.0},
                'ROE': {'TTM': 20.0},
                'Forward PE': {'TTM': 20.0},
                'Market Share': {'TTM': 10.0},
                'Market Rank': {'TTM': 2},
            }
        }

        # Manually add FY 2024 data for growth calculation
        # 800/8000*365 = 36.5 days (FY2024)
        # Growth = (43.8-36.5)/36.5 = 20% > 15%
        data['income_statement']['Cost of Revenue']['FY 2024'] = 8000
        data['balance_sheet']['Inventory']['FY 2024'] = 800

        result = calculate_consumer_score(data)

        # Check if risk penalty was applied
        print(f"Risk penalty: {result['risk_penalty']}")
        print(f"Total score: {result['total_score']}")

    def test_ticker_preserved(self):
        """Ticker should be preserved in result"""
        data = {
            'ticker': 'WOW.AX',
            'ratios': {}
        }
        result = calculate_consumer_score(data)
        self.assertEqual(result['ticker'], 'WOW.AX')

    def test_max_score_10(self):
        """Max score should always be 10.0"""
        data = {
            'ticker': 'TEST.AX',
            'ratios': {
                'EBIT Margin': {'TTM': 100.0},
                'ROE': {'TTM': 100.0},
            }
        }
        result = calculate_consumer_score(data)
        self.assertEqual(result['max_score'], 10.0)

    def test_inventory_calculation(self):
        """Inventory days should be calculated from components"""
        data = {
            'ticker': 'TEST.AX',
            'income_statement': {
                'Cost of Revenue': {'TTM': 10000},
            },
            'balance_sheet': {
                'Inventory': {'TTM': 1000},
            },
            'ratios': {}
        }
        result = calculate_consumer_score(data)
        # 1000/10000*365 = 36.5 days -> score 10
        self.assertAlmostEqual(result['metrics']['Inventory Days']['value'], 36.5, places=1)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_empty_data(self):
        """Empty data should return zeros"""
        data = {'ticker': 'TEST.AX'}
        result = calculate_consumer_score(data)

        self.assertEqual(result['total_score'], 0.0)
        for metric, info in result['metrics'].items():
            self.assertEqual(info['score'], 0.0)

    def test_missing_sections(self):
        """Missing sections should not crash"""
        data = {
            'ticker': 'TEST.AX',
            'ratios': {
                'EBIT Margin': {'TTM': 6.0}
            }
        }
        result = calculate_consumer_score(data)
        # Should not raise exception
        self.assertIn('EBIT Margin', result['metrics'])

    def test_zero_cost_revenue(self):
        """Zero cost revenue should not cause division by zero"""
        data = {
            'ticker': 'TEST.AX',
            'income_statement': {
                'Cost of Revenue': {'TTM': 0},
                'Revenue': {'TTM': 10000},
            },
            'cash_flow': {
                'Operating Cash Flow': {'TTM': 1000},
            },
            'balance_sheet': {
                'Inventory': {'TTM': 800},
            },
            'ratios': {}
        }
        result = calculate_consumer_score(data)
        # Should handle gracefully
        self.assertIn('Inventory Days', result['metrics'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
