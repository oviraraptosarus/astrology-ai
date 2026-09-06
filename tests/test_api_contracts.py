import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from ai_agent import message_content_to_text
from app import chart_session_key


class TestApiContracts(unittest.TestCase):
    def test_gemini_structured_content_is_normalized(self):
        content = [
            {"type": "text", "text": "First paragraph."},
            {"type": "text", "text": "Second paragraph."},
        ]
        self.assertEqual(
            message_content_to_text(content),
            "First paragraph.\nSecond paragraph.",
        )

    def test_chart_cache_key_is_private_and_filesystem_safe(self):
        first_user = {"id": 1}
        second_user = {"id": 2}
        session = "same-browser-session"

        first_key = chart_session_key(first_user, session)
        self.assertNotEqual(first_key, chart_session_key(second_user, session))
        self.assertRegex(first_key, r"^chart-[0-9a-f]{64}$")

    def test_chart_cache_key_rejects_empty_session(self):
        with self.assertRaises(Exception):
            chart_session_key({"id": 1}, "  ")


if __name__ == "__main__":
    unittest.main()
