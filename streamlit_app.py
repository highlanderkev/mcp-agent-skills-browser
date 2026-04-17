from __future__ import annotations

import urllib.error

import streamlit as st

from skill_scanner import ResponseTooLargeError, scan_web_agent_skills


def _build_skill_markdown(skill_data: dict) -> str:
    evidence_lines = "\n".join(f"- {evidence}" for evidence in skill_data.get("evidence", [])) or "- None"
    source_lines = "\n".join(f"- {source}" for source in skill_data.get("sources", [])) or "- None"
    return (
        f"### {skill_data['skill']}\n\n"
        f"**Mentions:** {skill_data.get('mentions', 0)}\n\n"
        f"**Evidence**\n{evidence_lines}\n\n"
        f"**Sources**\n{source_lines}"
    )


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
            label = f"{skill['skill']} ({skill.get('mentions', 0)} mentions)"
            with st.expander(label, expanded=False):
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
