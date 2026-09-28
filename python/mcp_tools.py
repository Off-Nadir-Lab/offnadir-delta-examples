"""Call the MCP endpoint directly with a static API key."""

import json

from offnadir_delta import McpClient

AOI = [22.0, 44.0, 40.0, 53.0]


def main() -> None:
    with McpClient() as mcp:  # reads OFFNADIR_DELTA_API_KEY
        info = mcp.initialize()
        server = info.get("serverInfo", {})
        print(f"Connected to {server.get('name')} v{server.get('version')}")

        print("\nTools:", [t["name"] for t in mcp.list_tools()])

        result = mcp.call_tool("query_signals", {"bbox": AOI, "recency": "24h", "limit": 5})
        # Tool results are MCP content blocks; the payload is JSON text.
        for block in result.get("content", []):
            if block.get("type") == "text":
                print("\nquery_signals ->")
                print(json.dumps(json.loads(block["text"]), indent=2)[:800])

        brief = mcp.read_resource("brief://latest")
        print("\nbrief://latest keys:", list(brief.keys()))


if __name__ == "__main__":
    main()
