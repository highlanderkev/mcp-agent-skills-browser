import unittest
import sys
import types


class _DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


sys.modules.setdefault(
    "streamlit",
    types.SimpleNamespace(
        set_page_config=lambda *args, **kwargs: None,
        title=lambda *args, **kwargs: None,
        write=lambda *args, **kwargs: None,
        form=lambda *args, **kwargs: _DummyContext(),
        text_input=lambda *args, **kwargs: "",
        slider=lambda *args, **kwargs: 10,
        form_submit_button=lambda *args, **kwargs: False,
        error=lambda *args, **kwargs: None,
        exception=lambda *args, **kwargs: None,
        subheader=lambda *args, **kwargs: None,
        json=lambda *args, **kwargs: None,
        expander=lambda *args, **kwargs: _DummyContext(),
        markdown=lambda *args, **kwargs: None,
        info=lambda *args, **kwargs: None,
        dataframe=lambda *args, **kwargs: None,
    ),
)
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
        self.assertIn("- [https://example\\.com/path%281%29]", markdown)
        self.assertIn("(https://example.com/path%281%29)", markdown)

    def test_build_skill_expander_label_escapes_untrusted_markdown(self):
        label = _build_skill_expander_label({"skill": "Prompt [engineering](javascript:alert(1))", "mentions": 2})
        self.assertEqual("Prompt \\[engineering\\]\\(javascript:alert\\(1\\)\\) (2 mentions)", label)


if __name__ == "__main__":
    unittest.main()
