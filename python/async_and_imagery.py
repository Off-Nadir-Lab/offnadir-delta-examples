"""Async client: concurrently search imagery and stream signals over an AOI."""

import asyncio
from datetime import date, timedelta

from offnadir_delta import AsyncClient

AOI = [22.0, 44.0, 40.0, 53.0]
TODAY = date.today()


async def main() -> None:
    async with AsyncClient() as client:
        # Run two independent requests concurrently.
        signals_task = client.signals.list(bbox=AOI, recency="24h", limit=10)
        imagery_task = client.imagery.search(
            bbox=AOI,
            collection="sentinel-2-l2a",
            cloud_cover_max=20,
            start_date=(TODAY - timedelta(days=13)).isoformat(),
            end_date=TODAY.isoformat(),
        )
        page, scenes = await asyncio.gather(signals_task, imagery_task)

        print(f"{page.meta.count} signals, {scenes.meta.count} scenes")
        for scene in scenes.scenes[:5]:
            print(f"  {scene.id} {scene.datetime} cloud={scene.cloud_cover}")

        # Async iteration over every signal in a date range, Severity 6+ (a plan with event
        # filters applies the severity filter; meta.filter_clamp says when it was not applied).
        async for signal in client.signals.iterate(
            bbox=AOI,
            start_date=(TODAY - timedelta(days=2)).isoformat(),
            end_date=TODAY.isoformat(),
            min_severity_band=6,
        ):
            print("  !", signal.title)


if __name__ == "__main__":
    asyncio.run(main())
