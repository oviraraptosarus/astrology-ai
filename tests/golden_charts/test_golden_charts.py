import json
import os
import unittest

sys_path_setup = True
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_full_chart

# Birth times below are LOCAL times at the birthplace (the correct
# astrological interpretation); timezone is passed explicitly so results do
# not depend on ambient auto-detection.
CASES = {
    "steve_jobs": dict(
        args=(1955, 2, 24, 19, 15, 37.7749, -122.4194, "America/Los_Angeles"),
        filename="steve_jobs.json",
    ),
    "swami_vivekananda": dict(
        args=(1863, 1, 12, 6, 33, 22.5726, 88.3639, "Asia/Kolkata"),
        filename="swami_vivekananda.json",
    ),
}


class TestGoldenCharts(unittest.TestCase):
    def load_golden(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, "r") as f:
            return json.load(f)

    def _check(self, key):
        case = CASES[key]
        golden = self.load_golden(case["filename"])
        actual = calculate_full_chart(*case["args"]).get("Basic_Chart")

        # Test Ascendant Degree
        self.assertAlmostEqual(actual["Ascendant"]["degree"], golden["Ascendant"]["degree"], places=2)

        # Test Sun Longitude & Sign
        self.assertEqual(actual["Sun"]["sign"], golden["Sun"]["sign"])
        self.assertAlmostEqual(actual["Sun"]["degree"], golden["Sun"]["degree"], places=2)

        # Test D9 and D10 Vargas for Moon (Jobs case only, matches original fixture content)
        if key == "steve_jobs":
            self.assertEqual(actual["Moon"]["vargas"]["D9"], golden["Moon"]["vargas"]["D9"])
            self.assertEqual(actual["Moon"]["vargas"]["D10"], golden["Moon"]["vargas"]["D10"])

    def test_steve_jobs(self):
        self._check("steve_jobs")

    def test_swami_vivekananda(self):
        self._check("swami_vivekananda")


if __name__ == '__main__':
    unittest.main()
