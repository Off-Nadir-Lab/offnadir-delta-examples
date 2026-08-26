"""Async client: concurrently search imagery and stream signals over an AOI."""

import asyncio

from offnadir_delta import AsyncClient

AOI = [22.0, 44.0, 40.0, 53.0]


async def main() -> None:
    async with AsyncClient() as client:
        # Run two independent requests concurrently.
        signals_task = client.signals.list(bbox=AOI, days=7, limit=10)
        imagery_task = client.imagery.search(
            bbox=AOI, collection="sentinel-2-l2a", cloud_cover_max=20, days=14
        )
        page, scenes = await asyncio.gather(signals_task, imagery_task)

        print(f"{page.meta.count} signals, {scenes.meta.count} scenes")
        for scene in scenes.scenes[:5]:
            print(f"  {scene.id} {scene.datetime} cloud={scene.cloud_cover}")

        # Async iteration over every signal.
        async for signal in client.signals.iterate(bbox=AOI, days=3, min_severity=7):
            print("  !", signal.title)


if __name__ == "__main__":
    asyncio.run(main())
