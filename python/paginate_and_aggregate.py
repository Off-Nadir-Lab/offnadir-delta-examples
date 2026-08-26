"""Iterate every signal across pages, then pull aggregate stats and hotspots."""

from collections import Counter

from offnadir_delta import Client

AOI = [22.0, 44.0, 40.0, 53.0]


def main() -> None:
    with Client() as client:
        # Auto-pagination: follows the cursor until exhausted (each page is metered).
        by_category: Counter[str] = Counter()
        for signal in client.signals.iterate(bbox=AOI, days=14, min_severity=6):
            by_category[signal.category or "unknown"] += 1
        print("High-severity signals by category:")
        for category, count in by_category.most_common():
            print(f"  {category}: {count}")

        # Cheaper: server-side rollups (1 token) instead of walking every row.
        stats = client.signals.stats(bbox=AOI, days=14)
        print(f"\nTotal events (server stats): {stats.meta.total}")

        # Grid-aggregated hotspots.
        hotspots = client.signals.hotspots(bbox=AOI, days=14, precision=0.5)
        print("\nTop hotspots:")
        for h in hotspots.hotspots[:5]:
            print(f"  ({h.lat:.2f}, {h.lng:.2f}) count={h.count} max_severity={h.max_severity}")


if __name__ == "__main__":
    main()
