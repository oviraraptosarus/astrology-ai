"""
Regression test for the KP ayanamsha state-leak bug.

BUG (confirmed in kp_engine.calculate_kp_chart, pre-fix):
    The engine set the GLOBAL Swiss Ephemeris sidereal mode to Krishnamurti,
    then restored it to Lahiri only on the happy path (last statement before
    return). If ANY intermediate Swiss Ephemeris call raised (houses_ex,
    calc_ut, ABCD/CSL evaluation), the restore never executed and the global
    ayanamsha stayed on Krishnamurti -- silently corrupting every subsequent
    Lahiri chart computed in the same process.

    Additionally, the pre-fix code referenced `swe.get_sid_mode()` in the prior
    (previous-AI) audit narrative, but this pyswisseph build (2.10.x) exposes
    NO get_sid_mode function at all -- so the "save/restore prior mode" claim
    was not implementable as described.

FIX:
    Wrap the whole KP computation in try/finally and always restore Lahiri
    (the system's single canonical base mode) in finally.

DETECTION:
    There is no get_sid_mode in this build, and get_ayanamsa_ut() proved to be
    an unreliable proxy (it does not fully track the set mode on this build).
    The robust probe is an ACTUAL sidereal planetary longitude via
    swe.calc_ut(jd, SUN, FLG_SIDEREAL): Lahiri vs Krishnamurti move the Sun by
    ~5.8 arcmin here -- far above float noise -- and this is exactly the
    quantity that downstream charts would read corrupted if the mode leaked.
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import swisseph as swe
from kp_engine import KPEngine

_TEST_JD = swe.julday(2008, 8, 1, 12.9166667)


def _active_sidereal_sun():
    """Sidereal Sun longitude under whatever global mode is currently set."""
    return swe.calc_ut(_TEST_JD, swe.SUN, swe.FLG_SIDEREAL)[0][0]


class TestAyanamshaLeakRegression(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        cls.lahiri_sun = _active_sidereal_sun()
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
        cls.krish_sun = _active_sidereal_sun()
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        assert abs(cls.lahiri_sun - cls.krish_sun) * 60 > 1.0, \
            "Lahiri and Krishnamurti Sun indistinguishable?"

    def setUp(self):
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    def tearDown(self):
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    def test_happy_path_restores_lahiri(self):
        KPEngine.calculate_kp_chart(2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata")
        self.assertAlmostEqual(
            _active_sidereal_sun(), self.lahiri_sun, places=4,
            msg="KP happy path left the global sidereal mode on a non-Lahiri ayanamsha")

    def test_exception_midway_does_not_leak_krishnamurti(self):
        """
        Core regression: force an exception AFTER KP has switched to
        Krishnamurti; the global mode must still be restored to Lahiri.
        """
        with mock.patch.object(KPEngine, "_compute_abcd_matrix",
                               side_effect=RuntimeError("injected failure")):
            with self.assertRaises(RuntimeError):
                KPEngine.calculate_kp_chart(2008, 8, 1, 18, 25,
                                            16.8186, 82.0641, "Asia/Kolkata")

        self.assertAlmostEqual(
            _active_sidereal_sun(), self.lahiri_sun, places=4,
            msg="KP engine LEAKED Krishnamurti ayanamsha after an exception -- "
                "downstream Lahiri charts would be silently corrupted")


if __name__ == "__main__":
    unittest.main(verbosity=2)
