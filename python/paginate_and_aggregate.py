"""Iterate every signal across pages and count them by category on the client side."""

from collections import Counter
from datetime import date, timedelta

from offnadir_delta import Client

AOI = [22.0, 44.0, 40.0, 53.0]


def main() -> None:
    with Client() as client:
        # Auto-pagination: follows the cursor until exhausted (each page is metered).
        by_category: Counter[str] = Counter()
        today = date.today()
        for signal in client.signals.iterate(
            bbox=AOI,
            start_date=(today - timedelta(days=13)).isoformat(),
            end_date=today.isoformat(),
            min_severity_band=6,
        ):
            by_category[signal.category or "unknown"] += 1
        print("High-severity signals by category:")
        for category, count in by_category.most_common():
            print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
