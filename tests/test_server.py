import unittest
from unittest.mock import patch

from server import handle_request


class ServerRequestHandlingTests(unittest.TestCase):
    def test_initialize_request_returns_response(self):
        response = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertIsNotNone(response)
        self.assertEqual(1, response["id"])
        self.assertIn("result", response)

    def test_initialize_notification_returns_no_response(self):
        response = handle_request({"jsonrpc": "2.0", "method": "initialize", "params": {}})
        self.assertIsNone(response)

    def test_tools_list_notification_returns_no_response(self):
        response = handle_request({"jsonrpc": "2.0", "method": "tools/list", "params": {}})
        self.assertIsNone(response)

    @patch("server.scan_web_agent_skills")
    def test_tools_call_notification_returns_no_response(self, mock_scan_web_agent_skills):
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "scan_web_agent_skills", "arguments": {"query": "mcp skills"}},
            }
        )
        self.assertIsNone(response)
        mock_scan_web_agent_skills.assert_not_called()


if __name__ == "__main__":
    unittest.main()
