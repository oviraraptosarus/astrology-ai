import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from vedic_models import Chart, Planet

class TestDispositorChains(unittest.TestCase):
    def setUp(self):
        self.chart = Chart(ascendant_sign="Aries", ascendant_degree=0.0)
        # Sun in Leo (Own sign)
        self.chart.add_planet(Planet("Sun", "Leo", 10.0, False))
        # Moon in Cancer (Own sign)
        self.chart.add_planet(Planet("Moon", "Cancer", 15.0, False))
        
        # Mars in Gemini (Dispositor = Mercury)
        self.chart.add_planet(Planet("Mars", "Gemini", 5.0, False))
        # Mercury in Aries (Dispositor = Mars) -> Parivartana with Mars
        self.chart.add_planet(Planet("Mercury", "Aries", 10.0, False))
        
        # Jupiter in Taurus (Dispositor = Venus)
        self.chart.add_planet(Planet("Jupiter", "Taurus", 8.0, False))
        # Venus in Capricorn (Dispositor = Saturn)
        self.chart.add_planet(Planet("Venus", "Capricorn", 5.0, False))
        # Saturn in Aquarius (Own sign) 
        self.chart.add_planet(Planet("Saturn", "Aquarius", 2.0, False))

        self.chart.build_relational_graph()

    def test_own_sign_chain(self):
        sun = self.chart.planets["Sun"]
        self.assertEqual(sun.dispositor_chain, ["Sun"])
        self.assertFalse(sun.is_parivartana)

    def test_parivartana(self):
        mars = self.chart.planets["Mars"]
        mercury = self.chart.planets["Mercury"]
        
        # Mars -> Mercury -> Mars (loop stops at Mercury because Mars is already in chain)
        self.assertEqual(mars.dispositor_chain, ["Mercury", "Mars"])
        self.assertTrue(mars.is_parivartana)
        
        self.assertEqual(mercury.dispositor_chain, ["Mars", "Mercury"])
        self.assertTrue(mercury.is_parivartana)

    def test_long_chain(self):
        jupiter = self.chart.planets["Jupiter"]
        # Jupiter -> Venus -> Saturn -> Saturn (loop stops at Saturn)
        self.assertEqual(jupiter.dispositor_chain, ["Venus", "Saturn"])
        self.assertFalse(jupiter.is_parivartana)

if __name__ == '__main__':
    unittest.main()
