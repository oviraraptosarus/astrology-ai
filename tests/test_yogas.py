import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vedic_models import Chart, Planet
from yogas import KemadrumaYoga, RajaYoga, DhanaYoga

class TestYogas(unittest.TestCase):
    def setUp(self):
        self.chart = Chart(ascendant_sign="Aries", ascendant_degree=0.0)
        # Ascendant in Aries -> Lords: 
        # Mars(1,8), Venus(2,7), Mercury(3,6), Moon(4), Sun(5), Mercury(6), Venus(7), Mars(8), Jupiter(9,12), Saturn(10,11)
        
        # Add planets so we can test yogas
        # Let's make Moon isolated for Kemadruma
        self.chart.add_planet(Planet("Moon", "Cancer", 15.0, False)) # House 4
        
        # Sun (Lord of 5 - Trikona) conjunct Moon (Lord of 4 - Kendra) -> Raja Yoga!
        # Wait, if Sun is in Cancer, it's in House 4.
        self.chart.add_planet(Planet("Sun", "Cancer", 10.0, False))
        
        # Venus (Lord of 2 - Wealth) conjunct Jupiter (Lord of 9 - Trikona) in Gemini (House 3)
        self.chart.add_planet(Planet("Venus", "Gemini", 15.0, False))
        self.chart.add_planet(Planet("Jupiter", "Gemini", 16.0, False))
        
        self.chart.build_relational_graph()

    def test_kemadruma_yoga(self):
        yoga = KemadrumaYoga()
        result = yoga.evaluate(self.chart)
        
        # Moon is in House 4. 
        # House 3 (Gemini) has Venus, Jupiter.
        # House 5 (Leo) is empty.
        # Wait, Kemadruma checks 2nd and 12th FROM Moon. 
        # House 4 + 1 = House 5. House 4 - 1 = House 3.
        # Since House 3 has Venus/Jupiter, Kemadruma is NOT present.
        self.assertFalse(result.fired)
        
        # Now let's remove Venus and Jupiter to trigger it.
        chart2 = Chart(ascendant_sign="Aries", ascendant_degree=0.0)
        chart2.add_planet(Planet("Moon", "Cancer", 15.0, False))
        chart2.build_relational_graph()
        result2 = yoga.evaluate(chart2)
        self.assertTrue(result2.fired)

    def test_raja_yoga(self):
        yoga = RajaYoga()
        result = yoga.evaluate(self.chart)
        self.assertTrue(result.fired)
        # Sun (L5) and Moon (L4) are conjunct in House 4
        self.assertTrue(any("Raja Yoga formed by Sun (Trikona lord) and Moon (Kendra lord)" in m or 
                            "Raja Yoga formed by Moon (Kendra lord) and Sun (Trikona lord)" in m 
                            for m in result.modifiers))

    def test_dhana_yoga(self):
        yoga = DhanaYoga()
        result = yoga.evaluate(self.chart)
        self.assertTrue(result.fired)
        # Venus (L2, wealth) and Jupiter (L9, trikona) conjunct in House 3
        self.assertTrue(any("Dhana Yoga formed" in m for m in result.modifiers))

if __name__ == '__main__':
    unittest.main()
