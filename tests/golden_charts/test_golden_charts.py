import json
import os
import unittest
from astrology_engine import calculate_full_chart

class TestGoldenCharts(unittest.TestCase):
    def load_golden(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, "r") as f:
            return json.load(f)

    def test_steve_jobs(self):
        golden = self.load_golden("steve_jobs.json")
        actual = calculate_full_chart(1955, 2, 24, 19, 15, 37.7749, -122.4194).get("Basic_Chart")
        
        # Test Ascendant Degree
        self.assertAlmostEqual(actual["Ascendant"]["degree"], golden["Ascendant"]["degree"], places=2)
        
        # Test Sun Longitude & Sign
        self.assertEqual(actual["Sun"]["sign"], golden["Sun"]["sign"])
        self.assertAlmostEqual(actual["Sun"]["degree"], golden["Sun"]["degree"], places=2)
        
        # Test D9 and D10 Vargas for Moon
        self.assertEqual(actual["Moon"]["vargas"]["D9"], golden["Moon"]["vargas"]["D9"])
        self.assertEqual(actual["Moon"]["vargas"]["D10"], golden["Moon"]["vargas"]["D10"])

    def test_swami_vivekananda(self):
        golden = self.load_golden("swami_vivekananda.json")
        actual = calculate_full_chart(1863, 1, 12, 6, 33, 22.5726, 88.3639).get("Basic_Chart")
        
        # Test Ascendant Degree
        self.assertAlmostEqual(actual["Ascendant"]["degree"], golden["Ascendant"]["degree"], places=2)
        
        # Test Sun Longitude & Sign
        self.assertEqual(actual["Sun"]["sign"], golden["Sun"]["sign"])
        self.assertAlmostEqual(actual["Sun"]["degree"], golden["Sun"]["degree"], places=2)

if __name__ == '__main__':
    unittest.main()
