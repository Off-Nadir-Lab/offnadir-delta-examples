# Off-Nadir Delta — examples

Runnable examples for the [Off-Nadir Delta](https://offnadir-delta.com) event-intelligence
API and MCP server: live, geolocated and source-linked world events, enriched with satellite
observability and collection recommendations.

These are the same example programs shipped with the official Python SDK, kept in sync with it.

## Setup

```bash
pip install offnadir-delta
export OFFNADIR_DELTA_API_KEY=ond_...
```

Create a key at [offnadir-delta.com/account/api](https://offnadir-delta.com/account/api).
The API and MCP server are available on every plan, including the free tier, and usage is
metered against your token balance. Your first call can be a free one:

```bash
curl -H "Authorization: Bearer $OFFNADIR_DELTA_API_KEY" https://offnadir-delta.com/api/v1/usage
```

## Examples

| File | What it does |
|---|---|
| [`python/async_and_imagery.py`](python/async_and_imagery.py) | Async client: concurrently search imagery and stream signals over an AOI. |
| [`python/collection_tasking.py`](python/collection_tasking.py) | A collection manager's loop: rank targets, plan the imagery, check the next pass. |
| [`python/intelligence.py`](python/intelligence.py) | AI assessment and the analyst agent (metered — these are the expensive calls). |
| [`python/mcp_tools.py`](python/mcp_tools.py) | Call the MCP endpoint directly with a static API key. |
| [`python/paginate_and_aggregate.py`](python/paginate_and_aggregate.py) | Iterate every signal across pages, then pull aggregate stats and hotspots. |
| [`python/quickstart.py`](python/quickstart.py) | Fetch the top signals in an area of interest. |

Run any of them with `python python/<file>`.

## The same workflows in other surfaces

Each of these jobs can also be run from the web app, over REST with `curl`, or from an
MCP-connected agent. The recipe pages show all four side by side:

- Recipes: https://offnadir-delta.com/docs/recipes
- API reference: https://offnadir-delta.com/docs/api
- MCP server: https://offnadir-delta.com/docs/mcp
- In-browser API playground: https://offnadir-delta.com/docs/playground

## License

Apache-2.0 — see [LICENSE](LICENSE).

---

Generated from the Off-Nadir Delta application repo. Edit the examples there, not here.
