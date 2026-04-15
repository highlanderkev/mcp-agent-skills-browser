import unittest
import urllib.error
from unittest.mock import patch

from server import handle_request
from skill_scanner import ResponseTooLargeError


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

    def test_tools_list_request_returns_tools(self):
        response = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        self.assertIsNotNone(response)
        self.assertEqual(2, response["id"])
        self.assertEqual("scan_web_agent_skills", response["result"]["tools"][0]["name"])

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

    @patch("server.scan_web_agent_skills")
    def test_tools_call_request_invokes_scanner(self, mock_scan_web_agent_skills):
        mock_scan_web_agent_skills.return_value = {"query": "mcp skills", "result_count": 0, "results": [], "skills": []}
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {"name": "scan_web_agent_skills", "arguments": {"query": "mcp skills", "max_results": 3}},
            }
        )
        self.assertIsNotNone(response)
        self.assertEqual(9, response["id"])
        self.assertIn("result", response)
        mock_scan_web_agent_skills.assert_called_once_with(query="mcp skills", max_results=3)

    def test_unknown_method_with_id_returns_error(self):
        response = handle_request({"jsonrpc": "2.0", "id": 5, "method": "bogus"})
        self.assertIsNotNone(response)
        self.assertEqual(-32601, response["error"]["code"])

    def test_tools_call_unknown_tool_returns_error(self):
        response = handle_request(
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "unknown", "arguments": {}}}
        )
        self.assertIsNotNone(response)
        self.assertEqual(-32601, response["error"]["code"])

    @patch("server.scan_web_agent_skills", side_effect=ValueError("query is required"))
    def test_tools_call_value_error_returns_invalid_params(self, _mock_scan_web_agent_skills):
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {"name": "scan_web_agent_skills", "arguments": {}},
            }
        )
        self.assertIsNotNone(response)
        self.assertEqual(-32602, response["error"]["code"])

    @patch("server.scan_web_agent_skills", side_effect=urllib.error.URLError("boom"))
    def test_tools_call_network_error_returns_server_error(self, _mock_scan_web_agent_skills):
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {"name": "scan_web_agent_skills", "arguments": {"query": "mcp"}},
            }
        )
        self.assertIsNotNone(response)
        self.assertEqual(-32000, response["error"]["code"])

    @patch("server.scan_web_agent_skills", side_effect=ResponseTooLargeError("web search response too large"))
    def test_tools_call_large_response_returns_server_error(self, _mock_scan_web_agent_skills):
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {"name": "scan_web_agent_skills", "arguments": {"query": "mcp"}},
            }
        )
        self.assertIsNotNone(response)
        self.assertEqual(-32000, response["error"]["code"])


if __name__ == "__main__":
    unittest.main()
