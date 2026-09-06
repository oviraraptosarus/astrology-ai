"""
Regression test: the reliability engine must never emit a HARDCODED benchmark
performance figure.

BUG (confirmed pre-fix):
    uncertainty_engine.py hardcoded
        "empirical_benchmark_performance": "78% (Historical Median ...)"
    into every reliability payload. No computation, no measurement, no source --
    a fabricated confidence number, which directly violates the mandate
    "NEVER INVENT VALIDATION RESULTS." The ACTUAL measured blind precision-hit
    rate is ~15-42% depending on house-set width, and it does NOT exceed the
    negative-control base rate -- i.e. no demonstrated skill on this benchmark.

FIX:
    empirical_benchmark_performance is now looked up from benchmark_results.json
    (produced by dual_track_benchmarks.run_and_export), and reports UNMEASURED
    when no data exists. It also appends the negative-control base rate for
    honest context.

This test fails if the fabricated "78%" string ever reappears in the source.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class TestNoFabricatedBenchmark(unittest.TestCase):

    def test_source_has_no_hardcoded_78_percent(self):
        with open(os.path.join(ROOT, "uncertainty_engine.py"), "r",
                  encoding="utf-8", errors="ignore") as fh:
            src = fh.read()
        self.assertNotIn("78%", src,
                         "Fabricated '78%' benchmark figure reappeared in uncertainty_engine.py")
        self.assertNotIn("Historical Median", src,
                         "Fabricated 'Historical Median' benchmark string reappeared")

    def test_lookup_returns_measured_or_unmeasured(self):
        from uncertainty_engine import UncertaintyEngine
        UncertaintyEngine._BENCHMARK_CACHE = None  # force reload
        msg = UncertaintyEngine._lookup_benchmark("CAREER")
        # Must be either a measured "H/T (P%)" string or an explicit UNMEASURED note.
        ok = ("precision-hit rate" in msg) or msg.startswith("UNMEASURED")
        self.assertTrue(ok, f"Unexpected benchmark string: {msg!r}")
        # It must never claim the old fabricated number.
        self.assertNotIn("78%", msg)

    def test_measured_file_carries_negative_control(self):
        """
        If benchmark_results.json exists, it MUST include a negative_control so
        hit rates are never reported without their base-rate context.
        """
        import json
        path = os.path.join(ROOT, "benchmark_results.json")
        if not os.path.exists(path):
            self.skipTest("benchmark_results.json not generated in this environment")
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertIn("negative_control", data)
        self.assertIn("base_rate", data["negative_control"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
