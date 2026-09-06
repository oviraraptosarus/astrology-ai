import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from vedic_models import Chart, Planet
from house_engine import HouseEngine
from planet_engine import PlanetEngine

class TestHouseAndPlanetEngines(unittest.TestCase):
    def setUp(self):
        self.chart = Chart(ascendant_sign="Aries", ascendant_degree=0.0)
        # Add a planet that owns house 1 (Aries is House 1)
        self.chart.add_planet(Planet("Mars", "Gemini", 15.0, False)) # House 3
        # Add a planet in house 1
        self.chart.add_planet(Planet("Sun", "Aries", 10.0, False)) # Exalted
        
        self.chart.build_relational_graph()

    def test_house_engine(self):
        h1_analysis = HouseEngine.analyze_house(self.chart, 1)
        self.assertEqual(h1_analysis["sign"], "Aries")
        self.assertEqual(h1_analysis["lord"], "Mars")
        self.assertIn("Sun", h1_analysis["occupants"])

    def test_planet_engine(self):
        mars_analysis = PlanetEngine.analyze_planet(self.chart, "Mars")
        self.assertEqual(mars_analysis["base"]["sign"], "Gemini")
        self.assertEqual(mars_analysis["base"]["house"], 3)
        self.assertIn(1, mars_analysis["ownership"]["owns_houses"])
        self.assertIn(8, mars_analysis["ownership"]["owns_houses"])

if __name__ == '__main__':
    unittest.main()
