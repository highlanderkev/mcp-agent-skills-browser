# mcp-agent-skills-browser

Minimal MCP server that scans the web for agent skills.

## Features

- Exposes an MCP tool: `scan_web_agent_skills`
- Searches the web (DuckDuckGo HTML endpoint)
- Extracts likely skill phrases from snippets and returns sources

## Run

```bash
uv sync
uv run python server.py
```

## Streamlit UI

```bash
uv sync
uv run streamlit run streamlit_app.py
```

This opens a local UI where you can enter a query, choose the number of results, and inspect extracted skills and sources.

The server communicates over stdio using JSON-RPC and supports:

- `initialize`
- `tools/list`
- `tools/call` for `scan_web_agent_skills`

## Tool arguments

- `query` (string, required): what skill/topic to scan for
- `max_results` (integer, optional, default `10`, range `1-25`)

## Quick local validation

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```
