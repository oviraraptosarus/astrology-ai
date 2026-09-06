import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import app, ChartCalculationRequest, LocationResolution, get_current_user
from fastapi.testclient import TestClient

app.dependency_overrides[get_current_user] = lambda: {"email": "test@test.com", "full_name": "Test User", "plan": "free"}
client = TestClient(app)

class TestLocationResolution(unittest.TestCase):
    def test_timezone_resolution(self):
        """Test that the backend correctly resolves IANA timezones from coordinates."""
        # Ramachandrapuram, India (Asia/Kolkata)
        res = client.get("/api/location/timezone?lat=16.85&lon=82.02")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["timezone"], "Asia/Kolkata")
        
        # San Francisco, USA (America/Los_Angeles)
        res = client.get("/api/location/timezone?lat=37.77&lon=-122.41")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["timezone"], "America/Los_Angeles")

    def test_calculate_chart_auth_bypass(self):
        """Test schema serialization for ChartCalculationRequest"""
        loc = LocationResolution(
            display_name="Ramachandrapuram, AP, India",
            latitude=16.85,
            longitude=82.02,
            timezone="Asia/Kolkata",
            place_id="12345"
        )
        req = ChartCalculationRequest(
            session_id="test_session",
            full_name="Steve Jobs",
            year=1955,
            month=2,
            day=24,
            hour=19,
            minute=15,
            location=loc
        )
        self.assertEqual(req.location.latitude, 16.85)
        self.assertEqual(req.location.longitude, 82.02)

if __name__ == "__main__":
    unittest.main()
