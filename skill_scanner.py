from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

_SEARCH_ENDPOINT = "https://duckduckgo.com/html/"
_USER_AGENT = "mcp-agent-skills-browser/1.0"
_REQUEST_TIMEOUT_SECONDS = 15


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def parse_duckduckgo_results(html_text: str, max_results: int) -> list[SearchResult]:
    pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>.*?'
        r'<a[^>]*class="result__snippet"[^>]*>(?P<snippet>.*?)</a>',
        re.DOTALL,
    )

    results: list[SearchResult] = []
    for match in pattern.finditer(html_text):
        title = html.unescape(_strip_tags(match.group("title"))).strip()
        url = html.unescape(match.group("url")).strip()
        snippet = html.unescape(_strip_tags(match.group("snippet"))).strip()
        if title and url:
            results.append(SearchResult(title=title, url=url, snippet=snippet))
        if len(results) >= max_results:
            break

    return results


def extract_skills_from_text(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    candidates = set()

    for match in re.finditer(
        r"(?:skills?|capabilities?)\s*[:\-]\s*([A-Za-z][A-Za-z0-9 /+&\-]{2,80})",
        normalized,
        flags=re.IGNORECASE,
    ):
        candidates.add(match.group(1).strip(" .,:;"))

    for match in re.finditer(
        r"\b([A-Za-z][A-Za-z0-9 /+&\-]{2,60})\s+(?:skills?|capability|capabilities)\b",
        normalized,
        flags=re.IGNORECASE,
    ):
        candidates.add(match.group(1).strip(" .,:;"))

    cleaned = []
    for phrase in candidates:
        phrase = re.sub(r"^(?:also\s+)?supports?\s+", "", phrase, flags=re.IGNORECASE)
        phrase = re.sub(r"\s+", " ", phrase).strip()
        if phrase.lower() in {"agent", "agents", "ai"}:
            continue
        if len(phrase) < 3 or len(phrase.split()) > 8:
            continue
        cleaned.append(phrase)

    return sorted(set(cleaned), key=str.lower)


def scan_web_agent_skills(query: str, max_results: int = 10) -> dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("query is required")

    try:
        max_results = int(max_results)
    except (TypeError, ValueError) as exc:
        raise ValueError("max_results must be an integer") from exc
    query = query.strip()
    max_results = max(1, min(25, max_results))
    encoded_query = urllib.parse.urlencode({"q": query})
    request = urllib.request.Request(
        f"{_SEARCH_ENDPOINT}?{encoded_query}",
        headers={"User-Agent": _USER_AGENT},
    )

    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        body = response.read().decode("utf-8", errors="replace")

    results = parse_duckduckgo_results(body, max_results=max_results)

    by_skill: dict[str, dict[str, Any]] = defaultdict(lambda: {"mentions": 0, "sources": set(), "evidence": []})
    for result in results:
        combined = f"{result.title}. {result.snippet}".strip()
        for skill in extract_skills_from_text(combined):
            skill_data = by_skill[skill]
            skill_data["mentions"] += 1
            skill_data["sources"].add(result.url)
            if len(skill_data["evidence"]) < 3:
                skill_data["evidence"].append(combined[:220])

    skills = [
        {
            "skill": skill,
            "mentions": data["mentions"],
            "sources": sorted(data["sources"]),
            "evidence": data["evidence"],
        }
        for skill, data in sorted(by_skill.items(), key=lambda x: (-x[1]["mentions"], x[0].lower()))
    ]

    return {
        "query": query,
        "result_count": len(results),
        "results": [result.__dict__ for result in results],
        "skills": skills,
    }
