import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from vedic_models import Chart, Planet
import config

class TestKarakas(unittest.TestCase):
    def setUp(self):
        self.chart = Chart(ascendant_sign="Aries", ascendant_degree=0.0)
        self.chart.add_planet(Planet("Sun", "Aries", 25.0, False))    # Highest degree = AK
        self.chart.add_planet(Planet("Moon", "Cancer", 20.0, False))  # AmK
        self.chart.add_planet(Planet("Mars", "Capricorn", 15.0, False))# BK
        self.chart.add_planet(Planet("Mercury", "Gemini", 10.0, False)) # MK
        self.chart.add_planet(Planet("Jupiter", "Leo", 8.0, False))   # PK
        self.chart.add_planet(Planet("Venus", "Libra", 5.0, False))   # GK
        self.chart.add_planet(Planet("Saturn", "Aquarius", 2.0, False)) # DK
        self.chart.add_planet(Planet("Rahu", "Taurus", 12.0, False))
        
    def test_natural_karakas(self):
        self.chart.build_relational_graph()
        sun = self.chart.planets["Sun"]
        self.assertIn("Father", sun.natural_karakas)
        self.assertIn("Soul", sun.natural_karakas)
        
        venus = self.chart.planets["Venus"]
        self.assertIn("Marriage", venus.natural_karakas)

    def test_chara_karakas_disabled(self):
        config.Config.USE_CHARA_KARAKAS = False
        self.chart.build_relational_graph()
        sun = self.chart.planets["Sun"]
        self.assertIsNone(sun.chara_karaka)

    def test_chara_karakas_enabled_7_scheme(self):
        config.Config.USE_CHARA_KARAKAS = True
        config.Config.CHARA_KARAKA_SCHEME = 7
        self.chart.build_relational_graph()
        
        self.assertEqual(self.chart.planets["Sun"].chara_karaka, "AK")
        self.assertEqual(self.chart.planets["Moon"].chara_karaka, "AmK")
        self.assertEqual(self.chart.planets["Saturn"].chara_karaka, "DK")
        # Rahu is excluded in 7-scheme
        self.assertIsNone(self.chart.planets["Rahu"].chara_karaka)

if __name__ == '__main__':
    unittest.main()
