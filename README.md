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

## Docker

Build the image:

```bash
docker build -t mcp-agent-skills-browser .
```

Run the MCP server in the container:

```bash
docker run --rm -i mcp-agent-skills-browser
```

The default container command starts `server.py`, which communicates over stdio using JSON-RPC.

Run the Streamlit UI from the same image:

```bash
docker run --rm -p 8501:8501 mcp-agent-skills-browser \
  python -m streamlit run streamlit_app.py --server.address=0.0.0.0
```

Then open `http://localhost:8501` in your browser.

The image uses a multi-stage build: dependencies are assembled in a builder stage, and the final runtime stage only contains the virtual environment and application files.
