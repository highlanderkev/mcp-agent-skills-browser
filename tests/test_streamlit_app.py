import unittest
import importlib
import sys
import types


class _DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


streamlit_stub = types.ModuleType("streamlit")
streamlit_stub_any = streamlit_stub
setattr(streamlit_stub_any, "set_page_config", lambda *args, **kwargs: None)
setattr(streamlit_stub_any, "title", lambda *args, **kwargs: None)
setattr(streamlit_stub_any, "write", lambda *args, **kwargs: None)
setattr(streamlit_stub_any, "form", lambda *args, **kwargs: _DummyContext())
setattr(streamlit_stub_any, "text_input", lambda *args, **kwargs: "")
setattr(streamlit_stub_any, "slider", lambda *args, **kwargs: 10)
setattr(streamlit_stub_any, "form_submit_button", lambda *args, **kwargs: False)
setattr(streamlit_stub_any, "error", lambda *args, **kwargs: None)
setattr(streamlit_stub_any, "exception", lambda *args, **kwargs: None)
setattr(streamlit_stub_any, "subheader", lambda *args, **kwargs: None)
setattr(streamlit_stub_any, "json", lambda *args, **kwargs: None)
setattr(streamlit_stub_any, "expander", lambda *args, **kwargs: _DummyContext())
setattr(streamlit_stub_any, "markdown", lambda *args, **kwargs: None)
setattr(streamlit_stub_any, "info", lambda *args, **kwargs: None)
setattr(streamlit_stub_any, "dataframe", lambda *args, **kwargs: None)
sys.modules.setdefault("streamlit", streamlit_stub)

streamlit_app = importlib.import_module("streamlit_app")
_build_search_result_markdown = streamlit_app._build_search_result_markdown
_build_skill_expander_label = streamlit_app._build_skill_expander_label
_build_skill_markdown = streamlit_app._build_skill_markdown
_sanitize_http_url = streamlit_app._sanitize_http_url


class StreamlitAppFormattingTests(unittest.TestCase):
    def test_sanitize_http_url_allows_http_https(self):
        self.assertEqual("https://example.com/a", _sanitize_http_url("https://example.com/a"))
        self.assertEqual("http://example.com/a", _sanitize_http_url("http://example.com/a"))

    def test_sanitize_http_url_blocks_non_http_schemes(self):
        self.assertIsNone(_sanitize_http_url("javascript:alert(1)"))
        self.assertIsNone(_sanitize_http_url("data:text/html;base64,abcd"))
        self.assertIsNone(_sanitize_http_url("/relative/path"))

    def test_sanitize_http_url_preserves_existing_percent_encoding(self):
        self.assertEqual(
            "https://example.com/path?q=alpha%20beta#section%201",
            _sanitize_http_url("https://example.com/path?q=alpha%20beta#section%201"),
        )

    def test_sanitize_http_url_encodes_invalid_percent_sequences(self):
        self.assertEqual(
            "https://example.com/path?q=100%25organic#part%25done",
            _sanitize_http_url("https://example.com/path?q=100%organic#part%done"),
        )

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
        self.assertIn("- [https://example\\.com/path\\(1\\)]", markdown)
        self.assertIn("(https://example.com/path%281%29)", markdown)

    def test_build_skill_expander_label_escapes_untrusted_markdown(self):
        label = _build_skill_expander_label({"skill": "Prompt [engineering](javascript:alert(1))", "mentions": 2})
        self.assertEqual("Prompt \\[engineering\\]\\(javascript:alert\\(1\\)\\) (2 mentions)", label)

    def test_build_search_result_markdown_uses_decoded_url_as_link_label(self):
        markdown = _build_search_result_markdown(
            {
                "title": "Agent Toolkit",
                "snippet": "Skills: planning and research",
                "url": "https://example.com/path(1)?q=alpha beta",
            }
        )

        self.assertIn("**Source page:** Agent Toolkit", markdown)
        self.assertIn("**Snippet:** Skills: planning and research", markdown)
        self.assertIn("**URL:**", markdown)
        self.assertIn("[https://example\\.com/path\\(1\\)?q=alpha beta]", markdown)
        self.assertIn("(https://example.com/path%281%29?q=alpha%20beta)", markdown)


if __name__ == "__main__":
    unittest.main()
