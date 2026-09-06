import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from vedic_models import Chart, Planet

class TestJyotishaCore(unittest.TestCase):
    def setUp(self):
        self.chart = Chart(ascendant_sign="Aries", ascendant_degree=15.0)
        self.chart.add_planet(Planet("Sun", "Aries", 10.0, False))
        self.chart.add_planet(Planet("Moon", "Cancer", 15.0, False))
        self.chart.add_planet(Planet("Mars", "Capricorn", 5.0, False))
        self.chart.add_planet(Planet("Jupiter", "Cancer", 20.0, False))
        self.chart.add_planet(Planet("Saturn", "Libra", 25.0, False))
        self.chart.add_planet(Planet("Venus", "Pisces", 27.0, False))
        self.chart.add_planet(Planet("Mercury", "Gemini", 15.0, False))
        self.chart.build_relational_graph()

    def test_house_calculation(self):
        # Aries Asc = 1st house. 
        # Sun in Aries -> 1st house
        self.assertEqual(self.chart.planets["Sun"].house, 1)
        # Moon in Cancer -> 4th house
        self.assertEqual(self.chart.planets["Moon"].house, 4)
        # Saturn in Libra -> 7th house
        self.assertEqual(self.chart.planets["Saturn"].house, 7)

    def test_sign_lordships(self):
        # Sun in Aries (Lord is Mars)
        self.assertEqual(self.chart.planets["Sun"].dispositor, "Mars")
        # Moon in Cancer (Lord is Moon, so dispositor is itself)
        self.assertEqual(self.chart.planets["Moon"].dispositor, "Moon")

    def test_house_lordships(self):
        # Mars owns Aries (1) and Scorpio (8)
        self.assertIn(1, self.chart.planets["Mars"].owns_houses)
        self.assertIn(8, self.chart.planets["Mars"].owns_houses)
        # Moon owns Cancer (4)
        self.assertIn(4, self.chart.planets["Moon"].owns_houses)

    def test_special_aspects(self):
        # Mars in Capricorn (10th house)
        # Aspects: 4th from 10th (Aries/1st), 7th from 10th (Cancer/4th), 8th from 10th (Leo/5th)
        mars_aspects = self.chart.planets["Mars"].aspects_houses
        self.assertIn(1, mars_aspects)
        self.assertIn(4, mars_aspects)
        self.assertIn(5, mars_aspects)

        # Check receivers
        # Sun in 1st should receive aspect from Mars
        self.assertIn("Mars", self.chart.planets["Sun"].aspected_by)
        # Moon in 4th should receive aspect from Mars
        self.assertIn("Mars", self.chart.planets["Moon"].aspected_by)

    def test_conjunctions(self):
        # Moon and Jupiter are both in Cancer (4th house)
        self.assertIn("Jupiter", self.chart.planets["Moon"].conjunct_with)
        self.assertIn("Moon", self.chart.planets["Jupiter"].conjunct_with)
        # Sun shouldn't be conjunct with them
        self.assertNotIn("Sun", self.chart.planets["Moon"].conjunct_with)

if __name__ == '__main__':
    unittest.main()
