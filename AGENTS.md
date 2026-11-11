# Instructions for AI coding agents

Copy this into your own project's AGENTS.md or CLAUDE.md so an agent that runs code uses the
Python SDK. The same text is at https://offnadir-delta.com/docs/mcp#coding-agents.

## Off-Nadir Delta (geolocated world events, satellite imagery planning)
- Use the Python SDK: `pip install offnadir-delta`. The API key is in the
  OFFNADIR_DELTA_API_KEY environment variable; never print it or write it to a file.
- `from offnadir_delta import Client`; `client = Client()` reads the key.
- Before a metered call, check the balance with `client.usage()` (free).
- Events: `client.signals.list(bbox=[minLon, minLat, maxLon, maxLat], recency="24h")`;
  every page: `client.signals.iterate(...)`. One event in full:
  `client.developments.thread(event_id)`.
- A response states what the plan did not apply or withheld: read
  `meta.filter_clamp`, `meta.window_clamp` and each row's `plan_lock` before
  concluding that something is absent.
- Reference: https://offnadir-delta.com/docs/api (every endpoint),
  https://offnadir-delta.com/docs#python-sdk, runnable programs in the python/ folder of
  https://github.com/Off-Nadir-Lab/offnadir-delta-examples.
