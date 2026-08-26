"""Fetch the top signals in an area of interest.

Run with:  OFFNADIR_DELTA_API_KEY=ond_... python examples/quickstart.py
"""

from offnadir_delta import Client

# bbox = [min_lon, min_lat, max_lon, max_lat] — this one roughly covers Ukraine.
UKRAINE = [22.0, 44.0, 40.0, 53.0]


def main() -> None:
    with Client() as client:  # reads OFFNADIR_DELTA_API_KEY
        usage = client.usage()
        print(f"Balance: {usage.tokens.remaining} tokens | LLM access: {usage.plan.api_llm_access}")

        page = client.signals.list(
            bbox=UKRAINE,
            days=7,
            min_severity=5,
            sort="severity",
            limit=20,
        )
        charged = page.meta.tokens.charged if page.meta.tokens else 0
        print(f"\n{page.meta.count} signals ({charged} tokens charged):\n")
        for s in page.signals:
            print(f"  [{s.severity_score}] {s.event_date} {s.country_code} — {s.title}")
            if s.source_url:
                print(f"      source: {s.source_url}")


if __name__ == "__main__":
    main()
