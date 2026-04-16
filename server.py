from __future__ import annotations

import json
import sys
import urllib.error
from typing import Any

from skill_scanner import ResponseTooLargeError, scan_web_agent_skills


TOOLS = [
    {
        "name": "scan_web_agent_skills",
        "description": "Search the web and extract likely agent skills and supporting sources.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for skills"},
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 25,
                    "default": 10,
                    "description": "Maximum number of search results to parse",
                },
            },
            "required": ["query"],
        },
    }
]


def _success_response(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle_request(payload: dict[str, Any]) -> dict[str, Any] | None:
    method = payload.get("method")
    has_request_id = "id" in payload
    request_id = payload.get("id")

    if not isinstance(method, str):
        return _error_response(request_id if has_request_id else None, -32600, "Invalid Request")

    if not has_request_id and method in {"initialize", "tools/list", "tools/call"}:
        return None

    if method == "initialize":
        return _success_response(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "mcp-agent-skills-browser", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return _success_response(request_id, {"tools": TOOLS})

    if method == "tools/call":
        raw_params = payload.get("params")
        if raw_params is None:
            params: dict[str, Any] = {}
        elif isinstance(raw_params, dict):
            params = raw_params
        else:
            return _error_response(request_id, -32602, "Invalid params: params must be an object")

        tool_name = params.get("name")
        if tool_name is None:
            return _error_response(request_id, -32602, "Invalid params: name is required")
        if not isinstance(tool_name, str):
            return _error_response(request_id, -32602, "Invalid params: name must be a string")

        raw_arguments = params.get("arguments")
        if raw_arguments is None:
            arguments: dict[str, Any] = {}
        elif isinstance(raw_arguments, dict):
            arguments = raw_arguments
        else:
            return _error_response(request_id, -32602, "Invalid params: arguments must be an object")

        if tool_name != "scan_web_agent_skills":
            return _error_response(request_id, -32601, f"Unknown tool: {tool_name}")

        try:
            result = scan_web_agent_skills(
                query=arguments.get("query", ""),
                max_results=arguments.get("max_results", 10),
            )
        except ValueError as exc:
            return _error_response(request_id, -32602, str(exc))
        except ResponseTooLargeError:
            return _error_response(request_id, -32000, "Web search response too large")
        except (urllib.error.URLError, TimeoutError):
            return _error_response(request_id, -32000, "Web search request failed")
        except Exception as exc:
            print(f"Unhandled error in scan_web_agent_skills: {type(exc).__name__}", file=sys.stderr, flush=True)
            return _error_response(request_id, -32000, "Unexpected server error")

        return _success_response(
            request_id,
            {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                "structuredContent": result,
            },
        )

    if request_id is not None:
        return _error_response(request_id, -32601, f"Unknown method: {method}")

    return None


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            response = _error_response(None, -32700, "Parse error")
            print(json.dumps(response, ensure_ascii=False), flush=True)
            continue

        if not isinstance(payload, dict):
            print(
                json.dumps(_error_response(None, -32600, "Invalid Request"), ensure_ascii=False),
                flush=True,
            )
            continue

        response = handle_request(payload)
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
