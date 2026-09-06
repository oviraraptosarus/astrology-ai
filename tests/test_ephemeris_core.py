import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import swisseph as swe
from datetime import datetime
import pytz
from astrology_engine import calculate_full_chart, ZODIAC_SIGNS

class TestEphemerisCore(unittest.TestCase):
    def test_known_historical_chart(self):
        # We test a known chart. E.g. India Independence
        # August 15, 1947, 00:00, New Delhi (28.6139, 77.2090)
        chart_data = calculate_full_chart(1947, 8, 15, 0, 0, 28.6139, 77.2090, 'Asia/Kolkata')
        base = chart_data["Basic_Chart"]
        
        # Verify Ascendant (Taurus)
        self.assertEqual(base["Ascendant"]["sign"], "Taurus")
        
        # Verify Sun (Cancer)
        self.assertEqual(base["Sun"]["sign"], "Cancer")
        
        # Verify Moon (Cancer)
        self.assertEqual(base["Moon"]["sign"], "Cancer")
        
        # Verify Rahu (Taurus) - Mean/True Node varies slightly but should be Taurus in Lahiri
        self.assertEqual(base["Rahu"]["sign"], "Taurus")
        
        # Verify Ketu derivation (always exactly 180 degrees from Rahu -> Scorpio)
        self.assertEqual(base["Ketu"]["sign"], "Scorpio")
        
        # Ensure Ketu and Rahu are exactly 6 signs apart
        rahu_idx = ZODIAC_SIGNS.index(base["Rahu"]["sign"])
        ketu_idx = ZODIAC_SIGNS.index(base["Ketu"]["sign"])
        self.assertEqual((rahu_idx + 6) % 12, ketu_idx)

    def test_retrograde_detection(self):
        # Need a date where Jupiter or Saturn is definitely retrograde.
        # May 12, 1990: Jupiter is direct, Saturn is retrograde.
        chart_data = calculate_full_chart(1990, 5, 12, 10, 30, 28.6139, 77.2090)
        base = chart_data["Basic_Chart"]
        
        # Sun/Moon can never be retrograde in standard Jyotisha
        self.assertFalse(base["Sun"]["retrograde"])
        self.assertFalse(base["Moon"]["retrograde"])
        
        # On this specific date, Saturn is retrograde
        self.assertTrue(base["Saturn"]["retrograde"])

if __name__ == '__main__':
    unittest.main()
