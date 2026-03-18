"""
Base module for formula verification.
Provides common utilities for testing calculation accuracy.
"""

import json
import unittest
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path


class FormulaTestBase(unittest.TestCase):
    """Base class for formula verification tests."""

    TOLERANCE = 1.0  # 1% tolerance for float comparison (to account for rounding in source data)

    @classmethod
    def setUpClass(cls):
        """Load test data files."""
        cls.test_data_dir = Path(__file__).parent / "test_data"
        cls.results = []  # Store verification results

    def load_test_data(self, filename: str) -> Dict[str, Any]:
        """Load test data from JSON file."""
        file_path = self.test_data_dir / filename
        with open(file_path, 'r') as f:
            return json.load(f)

    def assert_float_equal(self, actual: float, expected: float,
                          msg: str = "Values not equal") -> None:
        """Assert two floats are equal within tolerance."""
        if expected == 0:
            self.assertAlmostEqual(actual, expected, places=4, msg=msg)
        else:
            diff = abs(actual - expected)
            percent_diff = (diff / abs(expected)) * 100
            self.assertLessEqual(percent_diff, self.TOLERANCE,
                               msg=f"{msg}: expected={expected}, actual={actual}, diff={percent_diff:.4f}%")

    def verify_formula(self, name: str, calculated: float, expected: float,
                       formula_desc: str = "") -> Tuple[bool, str]:
        """
        Verify a formula calculation.

        Returns:
            (passed, message)
        """
        if expected == 0:
            diff = abs(calculated - expected)
            passed = diff < 0.0001
        else:
            diff = abs(calculated - expected)
            percent_diff = (diff / abs(expected)) * 100
            passed = percent_diff <= self.TOLERANCE

        if passed:
            msg = f"[PASS] {name}: {calculated:.4f} == {expected:.4f}"
        else:
            msg = f"[FAIL] {name}: {calculated:.4f} != {expected:.4f} (diff: {abs(calculated - expected):.4f}, {abs(calculated - expected)/max(abs(expected), 0.0001)*100:.4f}%)"

        if formula_desc:
            msg += f"\n      Formula: {formula_desc}"

        return passed, msg


class VerificationReport:
    """Collects and reports verification results."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def add_result(self, industry: str, metric: str, passed: bool,
                   expected: float, actual: float, formula: str = ""):
        """Add a verification result."""
        self.results.append({
            'industry': industry,
            'metric': metric,
            'passed': passed,
            'expected': expected,
            'actual': actual,
            'formula': formula,
            'diff': abs(actual - expected) if expected != 0 else abs(actual - expected),
            'diff_percent': (abs(actual - expected) / max(abs(expected), 0.0001)) * 100 if expected != 0 else 0
        })

    def print_report(self) -> None:
        """Print verification report."""
        print("\n" + "=" * 60)
        print("FORMULA VERIFICATION REPORT")
        print("=" * 60)

        # Group by industry
        industries = {}
        for r in self.results:
            ind = r['industry']
            if ind not in industries:
                industries[ind] = []
            industries[ind].append(r)

        for industry, items in industries.items():
            print(f"\n{'='*20} {industry} {'='*20}")
            for item in items:
                status = "PASS" if item['passed'] else "FAIL"
                print(f"  [{status}] {item['metric']}")
                print(f"         Expected: {item['expected']:.4f}, Actual: {item['actual']:.4f}")
                if not item['passed']:
                    print(f"         Diff: {item['diff_percent']:.4f}%")
                if item['formula']:
                    print(f"         Formula: {item['formula']}")

        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        if total > 0:
            print(f"Pass rate: {passed/total*100:.1f}%")
        else:
            print("Pass rate: N/A")
        print("=" * 60)


def load_json_data(file_path: str) -> Dict[str, Any]:
    """Load JSON data from file."""
    with open(file_path, 'r') as f:
        return json.load(f)
