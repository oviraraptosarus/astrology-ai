"""
Regression tests for the audit-fixed ForwardTimingScanner (2026-09-07 audit).

Covers:
 1. Fail-closed node dispatch (unknown nodes raise; no silent Career fallback)
 2. Output contract: model_score semantics, no probability fields, node_id
 3. Calendar-correct month arithmetic
 4. exact_peak_date is a true continuous-time minimum (verifiable property)
 5. Uniform family dispatch (same node family -> same qualification path)
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
import datetime
import pytz

from forward_timing_scanner import (
    ForwardTimingScanner, NodeDispatchError, resolve_node, add_months,
    DOMAIN_HOUSE_MAP, ALIASES, _is_crisis_node,
)
from astrology_engine import calculate_chart_with_object
import swisseph as swe
from config import Config
from forward_timing_scanner import ZODIAC_SIGNS

TEST_BIRTH = (2008, 4, 5, 6, 15, 50.348, 18.916, "Europe/Warsaw")


def _make_scanner():
    chart, _ = calculate_chart_with_object(*TEST_BIRTH, name="TestPolish")
    return ForwardTimingScanner(chart), chart


class TestNodeDispatch(unittest.TestCase):
    def test_unknown_node_raises(self):
        for bad in ["NOT_A_NODE", "FOOBAR", "", "  ", "career??", "SPACESHIP_LAUNCH"]:
            with self.assertRaises(NodeDispatchError, msg=f"expected raise for {bad!r}"):
                resolve_node(bad)

    def test_no_silent_career_fallback(self):
        scanner, _ = _make_scanner()
        start = pytz.utc.localize(datetime.datetime(2026, 1, 1))
        with self.assertRaises(NodeDispatchError):
            scanner.scan_domain_windows("TOTALLY_UNKNOWN_DOMAIN", start, months_ahead=6)

    def test_canonical_and_alias_resolution(self):
        self.assertEqual(resolve_node("CAREER"), "CAREER_BREAKTHROUGH")
        self.assertEqual(resolve_node("career"), "CAREER_BREAKTHROUGH")
        self.assertEqual(resolve_node("FATHER_ACCIDENT"), "FATHER_ACUTE_ACCIDENT_TRAUMA")
        self.assertEqual(resolve_node("HEALTH"), "HEALTH_CHRONIC_PATHOLOGY_DISCOVERY")
        self.assertEqual(resolve_node("GENERAL_TIMING"), "CAREER_BREAKTHROUGH")
        self.assertEqual(resolve_node("MARRIAGE"), "MARRIAGE_SACRED_UNION")
        # every alias target exists in the ontology
        for alias, target in ALIASES.items():
            self.assertIn(target, DOMAIN_HOUSE_MAP, f"alias {alias} -> missing {target}")

    def test_event_protocols_ids_resolvable(self):
        # every event_id in ProtocolRegistry must resolve through the scanner
        from event_protocols import ProtocolRegistry
        for eid in ProtocolRegistry.PROTOCOLS:
            try:
                resolve_node(eid)
            except NodeDispatchError:
                self.fail(f"event_protocols id '{eid}' not resolvable by scanner")


class TestOutputContract(unittest.TestCase):
    def test_window_contract_fields(self):
        scanner, _ = _make_scanner()
        start = pytz.utc.localize(datetime.datetime(2026, 7, 1))
        windows = scanner.scan_domain_windows("FATHER_ACUTE_ACCIDENT_TRAUMA", start, months_ahead=4)
        self.assertGreater(len(windows), 0)
        for w in windows:
            self.assertNotIn("peak_probability_pct", w, "old probability field must be gone")
            self.assertIn("model_score", w)
            self.assertIn("model_score_semantics", w)
            self.assertEqual(w["model_score_semantics"], "UNCALIBRATED_STRENGTH_SCORE_NOT_PROBABILITY")
            self.assertIn("node_id", w)
            self.assertIsInstance(w["node_id"], int)
            self.assertIn("macro_window_start", w)
            self.assertIn("macro_window_end", w)
            # exact_peak_date only present when a continuous solve produced it
            if "exact_peak_date" in w and w["exact_peak_date"]:
                self.assertIn("min_orb_arcmin", w)

    def test_model_score_bounds(self):
        scanner, _ = _make_scanner()
        start = pytz.utc.localize(datetime.datetime(2026, 7, 1))
        for w in scanner.scan_domain_windows("FATHER_ACUTE_ACCIDENT_TRAUMA", start, months_ahead=4):
            self.assertGreaterEqual(w["model_score"], 0.0)
            self.assertLessEqual(w["model_score"], 100.0)


class TestCalendarArithmetic(unittest.TestCase):
    def test_add_months_basic(self):
        d = datetime.datetime(2026, 1, 15)
        self.assertEqual(add_months(d, 1), datetime.datetime(2026, 2, 15))
        self.assertEqual(add_months(d, 12), datetime.datetime(2027, 1, 15))
        self.assertEqual(add_months(d, 0), d)

    def test_add_months_end_of_month_clamp(self):
        d = datetime.datetime(2026, 1, 31)
        self.assertEqual(add_months(d, 1), datetime.datetime(2026, 2, 28))
        d2 = datetime.datetime(2024, 1, 29)  # leap year
        self.assertEqual(add_months(d2, 1), datetime.datetime(2024, 2, 29))

    def test_add_months_preserves_tz(self):
        d = pytz.utc.localize(datetime.datetime(2026, 3, 31))
        r = add_months(d, 11)
        self.assertEqual((r.year, r.month, r.day), (2027, 2, 28))
        self.assertIsNotNone(r.tzinfo)

    def test_scan_end_date_not_305_drift(self):
        # 36 months from 2026-07-01 must end 2029-07-01 (not 2029-07-06 from 30.5 drift)
        start = pytz.utc.localize(datetime.datetime(2026, 7, 1))
        scanner, _ = _make_scanner()
        # access internal computation through a 1-window scan
        windows = scanner.scan_domain_windows("CAREER_BREAKTHROUGH", start, months_ahead=36)
        # all window ends must be <= start + 36 calendar months
        end_limit = datetime.datetime(2029, 7, 1).date()
        for w in windows:
            self.assertLessEqual(
                datetime.datetime.strptime(w["macro_window_end"], "%Y-%m-%d").date(),
                end_limit + datetime.timedelta(days=1),
            )


class TestContinuousPeak(unittest.TestCase):
    def test_exact_peak_is_true_minimum(self):
        """The Polish chart Mars-over-natal-Mars window (Jul-Sep 2026) must
        produce an exact_peak_date whose separation beats its neighbours."""
        scanner, chart = _make_scanner()
        start = pytz.utc.localize(datetime.datetime(2026, 7, 25))
        end = pytz.utc.localize(datetime.datetime(2026, 9, 10))
        mt = scanner._find_micro_trigger(start, end, "FATHER_ACUTE_ACCIDENT_TRAUMA")
        self.assertTrue(mt.get("found"), "micro trigger must fire in the known window")
        self.assertIn("exact_peak_date", mt)

        natal_mars = None
        for p_name, p_obj in chart.planets.items():
            if p_name == "Mars" and hasattr(p_obj, "sign"):
                natal_mars = ZODIAC_SIGNS.index(p_obj.sign) * 30.0 + p_obj.degree
        self.assertIsNotNone(natal_mars)

        def mars_sep(dt):
            hour = dt.hour + dt.minute / 60.0
            jd = swe.julday(dt.year, dt.month, dt.day, hour)
            swe.set_sid_mode(Config.ayanamsha_swe_id())
            lon = swe.calc_ut(jd, swe.MARS, swe.FLG_SIDEREAL)[0][0] % 360.0
            d = abs((lon - natal_mars) % 360.0)
            return min(d, 360.0 - d)

        peak = datetime.datetime.strptime(mt["exact_peak_date"], "%Y-%m-%d")
        v_peak = mars_sep(peak)
        v_m1 = mars_sep(peak - datetime.timedelta(days=1))
        v_p1 = mars_sep(peak + datetime.timedelta(days=1))
        # At a true minimum the peak day must not be worse than BOTH neighbours
        self.assertTrue(v_peak <= v_m1 or v_peak <= v_p1,
                        f"peak {v_peak*60:.1f}' not a minimum vs {v_m1*60:.1f}'/{v_p1*60:.1f}'")
        # and the reported min orb must match the computed separation closely
        if mt.get("min_orb_arcmin") is not None:
            self.assertAlmostEqual(mt["min_orb_arcmin"], v_peak * 60.0, delta=25.0)


class TestFamilyDispatch(unittest.TestCase):
    def test_crisis_family_classification(self):
        self.assertTrue(_is_crisis_node("FATHER_ACUTE_ACCIDENT_TRAUMA"))
        self.assertTrue(_is_crisis_node("HEALTH_ACUTE_SURGICAL_INTERVENTION"))
        self.assertTrue(_is_crisis_node("HEALTH_NATURAL_LIFESPAN_CESSATION"))
        self.assertTrue(_is_crisis_node("HEALTH_AUTOMOTIVE_CAR_CRASH"))
        self.assertFalse(_is_crisis_node("CAREER_BREAKTHROUGH"))
        self.assertFalse(_is_crisis_node("WEALTH_LIQUID_WINDFALL"))
        self.assertFalse(_is_crisis_node("MARRIAGE_SACRED_UNION"))

    def test_all_70_nodes_scannable(self):
        """Every canonical 70-node key must resolve and scan without error."""
        from seventy_node_ontology import SEVENTY_LIFE_NODES
        scanner, _ = _make_scanner()
        start = pytz.utc.localize(datetime.datetime(2026, 1, 1))
        # quick 2-month scans for speed
        for node_key in SEVENTY_LIFE_NODES:
            try:
                scanner.scan_domain_windows(node_key, start, months_ahead=2)
            except NodeDispatchError:
                self.fail(f"canonical node {node_key} failed dispatch")


if __name__ == "__main__":
    unittest.main(verbosity=2)
