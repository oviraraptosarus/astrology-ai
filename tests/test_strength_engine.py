import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from vedic_models import Chart, Planet
from strength_engine import StrengthEngine

class TestStrengthEngine(unittest.TestCase):
    def setUp(self):
        # Chart with Ascendant in Aries, 0 degrees
        self.chart = Chart(ascendant_sign="Aries", ascendant_degree=0.0)
        # Sun in Aries (exalted at 10 deg), 1st house
        self.chart.add_planet(Planet("Sun", "Aries", 10.0, False))
        # Saturn in Aries (debilitated at 20 deg), 1st house
        self.chart.add_planet(Planet("Saturn", "Aries", 20.0, True))  # Retrograde
        # Moon in Cancer, 4th house
        self.chart.add_planet(Planet("Moon", "Cancer", 15.0, False))
        # Synthetic-chart fixture: attach the birth time Cheshta Bala needs
        # (production charts get this from calculate_chart_with_object).
        from datetime import datetime
        self.chart.birth_time = datetime(2000, 1, 1, 12, 0)
        self.chart.build_relational_graph()
        StrengthEngine.calculate_shadbala(self.chart)

    def test_sthana_bala_exaltation(self):
        sun = self.chart.planets["Sun"]
        # Sun is exactly exalted. Uchcha Bala = 60.
        # Kendradi Bala (1st house) = 60.
        # Ojayugmarasyamsa (Sun in odd sign) = 15.
        # Total Sthana = 135.
        self.assertEqual(sun.shadbala["sthana_bala"], 135.0)

    def test_sthana_bala_debilitation(self):
        sat = self.chart.planets["Saturn"]
        # Saturn is exactly debilitated at 20 Aries. Uchcha Bala = 0.
        # Kendradi Bala (1st house) = 60.
        # Ojayugmarasyamsa (Saturn in odd sign) = 15.
        # Total Sthana = 75.
        self.assertEqual(sat.shadbala["sthana_bala"], 75.0)

    def test_dig_bala(self):
        sun = self.chart.planets["Sun"]
        # Sun max Dig Bala is in 10th house (approx 270 deg from Asc). 
        # Sun is at 10 deg absolute. Dist = 100 degrees.
        # (180 - 100) / 180 * 60 = 80 / 3 = 26.67
        self.assertAlmostEqual(sun.shadbala["dig_bala"], 26.67, places=1)

    def test_kala_bala(self):
        sun = self.chart.planets["Sun"]
        # Sun is in 1st house -> Night birth
        # Therefore Sun gets 0 Kala Bala (from Nathonnatha).
        # And 0 from Tribhaga. Shukla paksha -> malefics get no Paksha Bala.
        self.assertEqual(sun.shadbala["kala_bala"], 0.0)
        
        moon = self.chart.planets["Moon"]
        # Night birth: Moon gets 60 Nathonnatha + 60 Tribhaga (lord of 1st part of night).
        # Paksha: Shukla (Moon-Sun dist 95/180 waxing) -> 60 * (95/180) = 31.67.
        # Classical Kala Bala has no separate Dina term (that was a Nathonnatha double-count).
        self.assertAlmostEqual(moon.shadbala["kala_bala"], 151.67, places=1)

    def test_cheshta_bala(self):
        sat = self.chart.planets["Saturn"]
        # We now calculate true Cheshta Kendra (fractional) instead of statically assigning 60
        self.assertGreater(sat.shadbala["cheshta_bala"], 0.0)
        
        # Sun/Moon don't have retrograde, they use a different calculation
        moon = self.chart.planets["Moon"]
        self.assertGreater(moon.shadbala["cheshta_bala"], 0.0)

if __name__ == '__main__':
    unittest.main()
