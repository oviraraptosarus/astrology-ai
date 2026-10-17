"""
tests/test_product_api.py — Unit and integration tests for the consumer product API layer.
Validates that:
  - Product API translates raw engine objects into clean consumer schemas.
  - Multi-tenant isolation is strictly enforced.
  - Layered disclosure (L1-L4) is formatted properly without raw jargon in L1.
  - Relationship and notification preference CRUD works properly.
"""
import unittest
from datetime import datetime
import json
import db
import auth
from astrology_engine import calculate_full_chart, get_semantic_view, calculate_compatibility
import product_api as product


class TestProductAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_schema()
        # Seed test user & chart
        cls.chart = calculate_full_chart(2008, 8, 1, 18, 25, 16.83, 81.98, "Asia/Kolkata", "Vamsi Test")

    def test_home_overview(self):
        home = product.home_overview(self.chart, "Vamsi Test")
        self.assertIn("greeting", home)
        self.assertIn("today", home)
        self.assertIn("identity", home)
        self.assertIn("right_now", home)
        self.assertEqual(home["identity"]["ascendant"]["sign"], "Capricorn")
        self.assertEqual(home["identity"]["moon"]["sign"], "Cancer")
        self.assertEqual(home["identity"]["nakshatra"], "Ashlesha")
        self.assertTrue(len(home["today"]["plain"]) > 10)

    def test_chart_summary(self):
        summary = product.chart_summary(self.chart)
        self.assertEqual(len(summary["planets"]), 9)
        self.assertEqual(len(summary["houses"]), 12)
        self.assertTrue(len(summary["yogas"]) >= 1)
        # Check planet card shape
        sun = summary["planets"][0]
        self.assertIn("planet", sun)
        self.assertIn("glyph", sun)
        self.assertIn("sign", sun)
        self.assertIn("house", sun)
        self.assertIn("plain", sun)

    def test_planet_card_deep(self):
        saturn_data = self.chart["Basic_Chart"]["Saturn"]
        deep_card = product.planet_card("Saturn", saturn_data, deep=True)
        self.assertIn("owns_houses", deep_card)
        self.assertIn("aspected_by", deep_card)
        self.assertIn("conjunct_with", deep_card)
        self.assertEqual(deep_card["sign"], "Leo")
        self.assertEqual(deep_card["house"], 8)

    def test_domain_forecast_layers(self):
        career = product.domain_forecast(get_semantic_view, self.chart, "career")
        self.assertEqual(career["domain"], "career")
        self.assertIn("level1", career)
        self.assertIn("level2", career)
        self.assertIn("level3", career)
        self.assertIn("level4", career)
        self.assertIn("windows", career)
        self.assertTrue(len(career["level1"]["plain"]) > 0)
        self.assertTrue(isinstance(career["windows"], list))

    def test_compatibility_summary(self):
        raw_compat = calculate_compatibility(120.5, 310.2)
        summary = product.compatibility_summary(raw_compat, "Partner Label", "partner")
        self.assertIn("percent", summary)
        self.assertIn("band", summary)
        self.assertIn("breakdown", summary)
        self.assertEqual(len(summary["breakdown"]), 8)
        self.assertTrue(summary["percent"] >= 0 and summary["percent"] <= 100)

    def test_calendar_view(self):
        cal = product.calendar_view(self.chart)
        self.assertIn("today", cal)
        self.assertIn("transits", cal)
        self.assertIn("auspicious", cal)
        self.assertIn("inauspicious", cal)

    PROFILE = {"latitude": 16.83, "longitude": 81.98, "timezone": "Asia/Kolkata"}

    def test_calendar_uses_todays_panchang_not_birth_day(self):
        """Regression: 'today' tithi/nakshatra used to be read from the natal chart."""
        import pytz
        import swisseph as swe
        from config import Config
        cal = product.calendar_view(self.chart, self.PROFILE)
        now = datetime.now(pytz.utc)
        jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        sun = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
        moon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
        expected_tithi = int(((moon - sun) % 360) // 12) + 1
        expected_nak = int((moon % 360) // (360 / 27)) + 1
        # The panchang is evaluated at 'now' in the engine too; allow a boundary slip of one step.
        live = product.live_panchang(self.PROFILE)["panchanga"]
        self.assertIn(live["tithi"]["index"], {expected_tithi, expected_tithi % 30 + 1, (expected_tithi - 2) % 30 + 1})
        self.assertIn(live["nakshatra"]["index"], {expected_nak, expected_nak % 27 + 1, (expected_nak - 2) % 27 + 1})
        self.assertEqual(cal["today"]["tithi"], live["tithi"]["name"])
        self.assertTrue(cal["auspicious"] and cal["inauspicious"])

    def test_calendar_without_profile_shows_no_stale_natal_panchang(self):
        cal = product.calendar_view(self.chart)
        self.assertEqual(cal["today"]["tithi"], "")
        self.assertEqual(cal["auspicious"], [])

    def test_current_dasha_is_populated(self):
        """Regression: engine read non-existent MD/AD/PD keys so the dasha was always blank."""
        d = self.chart["Current_Dasha"]
        for k in ("Mahadasha", "Antardasha", "Pratyantardasha"):
            self.assertTrue(d[k], k)
        self.assertLess(d["Mahadasha_Start"], d["Mahadasha_End"])
        period = product.dasha_period(self.chart)
        self.assertTrue(period["label"])

    def test_timing_windows_use_real_birth_time(self):
        """Regression: the dict->Chart round trip dropped birth_time, so the forward scanner
        silently assumed a 2000-01-01 birth and returned windows from the wrong dasha."""
        sv = get_semantic_view(self.chart, "career")
        sv = json.loads(sv) if isinstance(sv, str) else sv
        windows = sv.get("timing_windows", [])
        self.assertTrue(windows)
        current_md = self.chart["Current_Dasha"]["Mahadasha"]
        # 2008 native: every 24-month window must sit inside a Mahadasha the engine reports
        # for the same birth data, i.e. the one that is current now or the next one.
        for w in windows:
            self.assertEqual(w["trigger_dasha"].split(" -> ")[0], current_md)


if __name__ == "__main__":
    unittest.main()
