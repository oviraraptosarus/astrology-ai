import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from vedic_models import Chart, Planet
from ashtakavarga_engine import AshtakavargaEngine

class TestAshtakavargaEngine(unittest.TestCase):
    def setUp(self):
        self.chart = Chart(ascendant_sign="Aries", ascendant_degree=0.0)
        # Add all 7 planets to get 337 total bindus
        self.chart.add_planet(Planet("Sun", "Aries", 10.0, False))
        self.chart.add_planet(Planet("Moon", "Cancer", 15.0, False))
        self.chart.add_planet(Planet("Mars", "Capricorn", 5.0, False))
        self.chart.add_planet(Planet("Mercury", "Aries", 12.0, False))
        self.chart.add_planet(Planet("Jupiter", "Taurus", 15.0, False))
        self.chart.add_planet(Planet("Venus", "Pisces", 20.0, False))
        self.chart.add_planet(Planet("Saturn", "Libra", 25.0, False))
        self.chart.build_relational_graph()
        AshtakavargaEngine.calculate_ashtakavarga(self.chart)

    def test_bhinna_ashtakavarga_sun(self):
        # Sun BAV.
        # Sun in Aries (1) provides to 1,2,4,7,8,9,10,11 from Aries (1,2,4,7,8,9,10,11)
        # Moon in Cancer (4) provides to 3,6,10,11 from Cancer (6,9,1,2)
        # Mars in Capricorn (10) provides to 1,2,4,7,8,9,10,11 from Capricorn (10,11,1,4,5,6,7,8)
        
        sun_bav = self.chart.bhinna_ashtakavarga["Sun"]
        # House 1 gets bindus from:
        # Sun (yes)
        # Moon (yes, 1 is 10th from Cancer 4)
        # Mars (yes, 1 is 4th from Capricorn 10)
        self.assertGreaterEqual(sun_bav[1], 3)
        
        # House 3 gets bindus from:
        # Sun (no)
        # Moon (no)
        # Mars (no)
        # Note: we also have Ascendant in Aries, which provides 3,4,6,10,11,12 from Aries (3,4,6,10,11,12)
        # With the remaining planets added, the bindu count increases.
        self.assertGreaterEqual(sun_bav[3], 1)

    def test_sarvashtakavarga(self):
        # We now calculate SAV for all 7 planets.
        # Just check that the total sum of bindus across all 12 houses is 337 (the classical Parashari constant)
        sav = self.chart.sarvashtakavarga
        total_bindus = sum(sav.values())
        self.assertEqual(total_bindus, 337)

if __name__ == '__main__':
    unittest.main()
