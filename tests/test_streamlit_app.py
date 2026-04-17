import unittest
from unittest.mock import patch

from skill_scanner import ResponseTooLargeError
from streamlit_app import run_scan


class StreamlitAppTests(unittest.TestCase):
    @patch("streamlit_app.scan_web_agent_skills")
    def test_run_scan_calls_scanner(self, mock_scan_web_agent_skills):
        mock_scan_web_agent_skills.return_value = {"query": "agent skills", "result_count": 0, "results": [], "skills": []}
        result = run_scan(query="agent skills", max_results=7)
        self.assertEqual("agent skills", result["query"])
        mock_scan_web_agent_skills.assert_called_once_with(query="agent skills", max_results=7)

    @patch("streamlit_app.scan_web_agent_skills", side_effect=ValueError("query is required"))
    def test_run_scan_propagates_value_error(self, _mock_scan_web_agent_skills):
        with self.assertRaises(ValueError):
            run_scan(query="", max_results=10)

    @patch("streamlit_app.scan_web_agent_skills", side_effect=ResponseTooLargeError("too large"))
    def test_run_scan_propagates_large_response_error(self, _mock_scan_web_agent_skills):
        with self.assertRaises(ResponseTooLargeError):
            run_scan(query="x", max_results=10)


if __name__ == "__main__":
    unittest.main()
