"""
Regression test: node-convention (Rahu/Ketu ephemeris model) consistency.

BUG (confirmed pre-fix):
    The canonical chart engine (astrology_engine) used swe.TRUE_NODE for Rahu,
    but gochara_vedha_engine, realtime_engine and sarvatobhadra_chakra_engine
    independently hardcoded swe.MEAN_NODE. True vs Mean node differ by up to
    ~1.6 deg, enough to flip a nakshatra/pada near a boundary, so the same
    person's Rahu could land in different nakshatras depending on which engine
    reported it -- a Phase-9 canonical-source violation and silent methodology
    mixing.

FIX:
    Declared a single canonical Config.NODE_TYPE ("true") + Config.node_swe_id()
    and routed all Parashari-context engines through it. KP is a separate school
    (traditionally Mean Node) and is intentionally excluded.

These tests pin the convention so a future edit that reintroduces a hardcoded
MEAN_NODE in the Parashari stack fails loudly.
"""

import os
import re
import sys
import glob
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import swisseph as swe
from config import Config


class TestNodeConventionConsistency(unittest.TestCase):

    def test_config_declares_true_node(self):
        self.assertEqual(Config.NODE_TYPE, "true")
        self.assertEqual(Config.node_swe_id(), swe.TRUE_NODE)

    def test_parashari_engines_do_not_hardcode_mean_node(self):
        """
        No Parashari-context engine may hardcode swe.MEAN_NODE. Only kp_engine
        (a separate methodology) is allowed to reference MEAN_NODE directly.
        """
        # kp_engine: separate methodology (Mean Node by tradition).
        # config.py: the single definition point of node_swe_id().
        allowed = {"kp_engine.py", "config.py"}
        offenders = []
        for path in glob.glob(os.path.join(ROOT, "*.py")):
            fname = os.path.basename(path)
            if fname in allowed:
                continue
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                src = fh.read()
            # Strip comments so a comment mentioning MEAN_NODE doesn't trip us.
            code = "\n".join(line.split("#", 1)[0] for line in src.splitlines())
            if re.search(r"\bswe\.MEAN_NODE\b", code):
                offenders.append(fname)
        self.assertEqual(
            offenders, [],
            f"Parashari-context files hardcode swe.MEAN_NODE (should use "
            f"Config.node_swe_id()): {offenders}")

    def test_canonical_chart_uses_config_node(self):
        """The chart engine's Rahu must match the config-declared node model."""
        from astrology_engine import calculate_chart_with_object
        chart, _ = calculate_chart_with_object(
            2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata", name="probe")
        rahu = chart.planets["Rahu"]

        swe.set_sid_mode(swe.SIDM_LAHIRI)
        jd = swe.julday(2008, 8, 1, 12.9166667)
        expected = swe.calc_ut(jd, Config.node_swe_id(), swe.FLG_SIDEREAL)[0][0] % 360.0
        # Same-day; allow a small tolerance for the exact minute/JD rounding.
        diff = abs(rahu.longitude - expected)
        diff = min(diff, 360 - diff)
        self.assertLess(diff, 0.2,
                        f"Chart Rahu {rahu.longitude:.4f} does not match config "
                        f"node model {expected:.4f} (diff {diff:.4f} deg)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
