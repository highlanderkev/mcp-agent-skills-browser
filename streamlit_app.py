from __future__ import annotations

import re
import urllib.error
import urllib.parse

import streamlit as st

from skill_scanner import ResponseTooLargeError, scan_web_agent_skills


_MARKDOWN_SPECIAL_CHARS_PATTERN = re.compile(r"([-\\`*_{}\[\]()#+.!|>])")


def _escape_markdown_text(text: str) -> str:
    return _MARKDOWN_SPECIAL_CHARS_PATTERN.sub(r"\\\1", str(text))


def _sanitize_http_url(url: str) -> str | None:
    parts = urllib.parse.urlsplit(str(url).strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return None

    safe_path = urllib.parse.quote(parts.path, safe="/-._~")
    safe_query = urllib.parse.quote(parts.query, safe="=&-._~")
    safe_fragment = urllib.parse.quote(parts.fragment, safe="-._~")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, safe_path, safe_query, safe_fragment))


def _build_skill_markdown(skill_data: dict) -> str:
    evidence_lines = (
        "\n".join(f"- {_escape_markdown_text(evidence)}" for evidence in skill_data.get("evidence", [])) or "- None"
    )

    source_lines_list = []
    for source in skill_data.get("sources", []):
        safe_url = _sanitize_http_url(source)
        if safe_url is None:
            source_lines_list.append(f"- {_escape_markdown_text(source)}")
        else:
            source_label = _escape_markdown_text(safe_url)
            source_lines_list.append(f"- [{source_label}]({safe_url})")
    source_lines = "\n".join(source_lines_list) or "- None"

    return (
        f"### {_escape_markdown_text(skill_data['skill'])}\n\n"
        f"**Mentions:** {skill_data.get('mentions', 0)}\n\n"
        f"**Evidence**\n{evidence_lines}\n\n"
        f"**Sources**\n{source_lines}"
    )


def _build_skill_expander_label(skill_data: dict) -> str:
    return f"{_escape_markdown_text(skill_data.get('skill', ''))} ({skill_data.get('mentions', 0)} mentions)"


def main() -> None:
    st.set_page_config(page_title="MCP Agent Skills Browser", layout="wide")
    st.title("MCP Agent Skills Browser")
    st.write("Search the web and extract likely agent skills from result snippets.")

    with st.form("skills-search-form"):
        query = st.text_input("Query", placeholder="e.g. agent planning skills")
        max_results = st.slider("Max results", min_value=1, max_value=25, value=10, step=1)
        submitted = st.form_submit_button("Scan")

    if not submitted:
        return

    try:
        data = scan_web_agent_skills(query=query, max_results=max_results)
    except ValueError as exc:
        st.error(str(exc))
        return
    except ResponseTooLargeError:
        st.error("Web search response too large")
        return
    except (urllib.error.URLError, TimeoutError):
        st.error("Web search request failed")
        return
    except Exception as exc:
        st.error("An unexpected error occurred while scanning results.")
        st.exception(exc)
        return

    st.subheader("Summary")
    st.json({"query": data["query"], "result_count": data["result_count"], "skills_found": len(data["skills"])})

    st.subheader("Extracted skills")
    if data["skills"]:
        for skill in data["skills"]:
            with st.expander(_build_skill_expander_label(skill), expanded=False):
                st.markdown(_build_skill_markdown(skill))
    else:
        st.info("No skill phrases found in the scanned results.")

    st.subheader("Search results")
    if data["results"]:
        st.dataframe(data["results"], use_container_width=True)
    else:
        st.info("No web results were parsed.")


if __name__ == "__main__":
    main()
