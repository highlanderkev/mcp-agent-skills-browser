import unittest
import sys
import types

sys.modules.setdefault("streamlit", types.SimpleNamespace())
from streamlit_app import _build_skill_expander_label, _build_skill_markdown, _sanitize_http_url


class StreamlitAppFormattingTests(unittest.TestCase):
    def test_sanitize_http_url_allows_http_https(self):
        self.assertEqual("https://example.com/a", _sanitize_http_url("https://example.com/a"))
        self.assertEqual("http://example.com/a", _sanitize_http_url("http://example.com/a"))

    def test_sanitize_http_url_blocks_non_http_schemes(self):
        self.assertIsNone(_sanitize_http_url("javascript:alert(1)"))
        self.assertIsNone(_sanitize_http_url("data:text/html;base64,abcd"))
        self.assertIsNone(_sanitize_http_url("/relative/path"))

    def test_build_skill_markdown_escapes_untrusted_markdown_and_only_links_safe_urls(self):
        markdown = _build_skill_markdown(
            {
                "skill": "Prompt [engineering](javascript:alert(1))",
                "mentions": 1,
                "evidence": ["Potential **bold** _markdown_ [link](javascript:alert(2))"],
                "sources": ["javascript:alert(1)", "https://example.com/path(1)"],
            }
        )

        self.assertIn("Prompt \\[engineering\\]\\(javascript:alert\\(1\\)\\)", markdown)
        self.assertIn("Potential \\*\\*bold\\*\\* \\_markdown\\_ \\[link\\]\\(javascript:alert\\(2\\)\\)", markdown)
        self.assertIn("- javascript:alert\\(1\\)", markdown)
        self.assertIn("- [https://example\\.com/path\\(1\\)](https://example.com/path(1))", markdown)

    def test_build_skill_expander_label_escapes_untrusted_markdown(self):
        label = _build_skill_expander_label({"skill": "Prompt [engineering](javascript:alert(1))", "mentions": 2})
        self.assertEqual("Prompt \\[engineering\\]\\(javascript:alert\\(1\\)\\) (2 mentions)", label)


if __name__ == "__main__":
    unittest.main()
