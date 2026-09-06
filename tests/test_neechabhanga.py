import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from vedic_models import Chart, Planet
from synthesis_engine import CancellationRule

class TestNeechabhanga(unittest.TestCase):
    def setUp(self):
        self.chart = Chart(ascendant_sign="Aries", ascendant_degree=0.0)
        # Debilitated Mars in Cancer
        self.chart.add_planet(Planet("Mars", "Cancer", 28.0, False))
        # Moon (Dispositor of Mars) in Libra (Kendra 7)
        self.chart.add_planet(Planet("Moon", "Libra", 15.0, False))
        
        # Debilitated Sun in Libra (Retrograde is false but let's say it's just debilitated)
        self.chart.add_planet(Planet("Sun", "Libra", 10.0, False))
        # Exaltation lord of Sun is Mars (Aries). 
        # Mars is in Cancer (House 4, a Kendra)
        
        # Debilitated Jupiter in Capricorn, Retrograde
        self.chart.add_planet(Planet("Jupiter", "Capricorn", 5.0, True))
        
        self.chart.build_relational_graph()

    def test_neechabhanga_dispositor_in_kendra(self):
        # Mars debilitated
        contradicting_evidence = [
            {
                "source_rule": "dignity",
                "subject": "Mars",
                "reason": "Mars is Debilitated in Cancer"
            }
        ]
        cancellations = CancellationRule.detect_neechabhanga(self.chart, contradicting_evidence)
        self.assertEqual(len(cancellations), 1)
        self.assertIn("Dispositor Moon is in a Kendra from Ascendant (House 7)", cancellations[0]["cancellation_condition"])

    def test_neechabhanga_exalt_lord_in_kendra(self):
        # Sun debilitated
        contradicting_evidence = [
            {
                "source_rule": "dignity",
                "subject": "Sun",
                "reason": "Sun is Debilitated in Libra"
            }
        ]
        cancellations = CancellationRule.detect_neechabhanga(self.chart, contradicting_evidence)
        self.assertEqual(len(cancellations), 1)
        # Exaltation lord of Sun is Mars, which is in House 4
        self.assertIn("Exaltation lord Mars is in a Kendra from Ascendant", cancellations[0]["cancellation_condition"])

    def test_neechabhanga_retrograde(self):
        # Jupiter debilitated
        contradicting_evidence = [
            {
                "source_rule": "dignity",
                "subject": "Jupiter",
                "reason": "Jupiter is Debilitated in Capricorn"
            }
        ]
        cancellations = CancellationRule.detect_neechabhanga(self.chart, contradicting_evidence)
        self.assertEqual(len(cancellations), 1)
        self.assertIn("Jupiter is retrograde", cancellations[0]["cancellation_condition"])

if __name__ == '__main__':
    unittest.main()
