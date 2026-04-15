import unittest
from unittest.mock import patch

from skill_scanner import extract_skills_from_text, parse_duckduckgo_results, scan_web_agent_skills


class ScannerTests(unittest.TestCase):
    def test_extract_skills_patterns(self):
        text = "Agent capabilities: Web browsing and research. Also supports prompt engineering skills."
        skills = extract_skills_from_text(text)
        self.assertIn("Web browsing and research", skills)
        self.assertIn("prompt engineering", [s.lower() for s in skills])

    def test_parse_duckduckgo_results(self):
        html = '''
        <a class="result__a" href="https://example.com/a">Agent Skill Guide</a>
        <a class="result__snippet">Capabilities: planning and web research.</a>
        <a class="result__a" href="https://example.com/b">Second</a>
        <a class="result__snippet">Skills: tool use</a>
        '''
        results = parse_duckduckgo_results(html, max_results=10)
        self.assertEqual(2, len(results))
        self.assertEqual("https://example.com/a", results[0].url)

    @patch("urllib.request.urlopen")
    def test_scan_web_agent_skills(self, mock_urlopen):
        class _Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return False

            def read(self):
                return b'''
                    <a class="result__a" href="https://skills.example/1">Agent Toolkit</a>
                    <a class="result__snippet">Skills: web search and summarization</a>
                    <a class="result__a" href="https://skills.example/2">Planner</a>
                    <a class="result__snippet">Agent capabilities: planning and memory</a>
                '''

        mock_urlopen.return_value = _Response()

        data = scan_web_agent_skills("agent skills", max_results=5)
        self.assertEqual("agent skills", data["query"])
        self.assertEqual(2, data["result_count"])
        self.assertGreaterEqual(len(data["skills"]), 1)


if __name__ == "__main__":
    unittest.main()
