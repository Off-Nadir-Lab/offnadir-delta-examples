"""A collection manager's loop: rank targets, plan the imagery, check the next pass.

This is the workflow the SDK could not express before 0.4.0 — you could read events but
not act on them. Nothing here invents a capability: every step reports what the data can
and cannot support, which is the part a tasking decision actually rests on.

Run with:  OFFNADIR_DELTA_API_KEY=ond_... python examples/collection_tasking.py
"""

from offnadir_delta import Client

# bbox = [min_lon, min_lat, max_lon, max_lat].
AOI = [-180.0, -85.0, 180.0, 85.0]   # worldwide; narrow this to your own area of interest.


def main() -> None:
    with Client() as client:
        # 1. WHAT IS WORTH IMAGING. `total_available` vs `returned` matters: a short list
        #    can mean "few candidates" or "few that survived the readiness gates", and
        #    those are different situations for a collection manager.
        ranked = client.collection.priority(bbox=AOI, top_n=5)
        body = ranked.priority
        if body is None:
            print("No priority body returned.")
            return
        print(f"{body.returned} target(s) returned of {body.total_available} available")

        # An empty list is a real answer, and the exclusion breakdown is the useful part
        # of it: it says WHICH gate emptied the funnel (measured worldwide on 2026-07-28,
        # 28 of 34 candidates were dropped for `geo_not_ready` alone). A collection
        # manager needs that, not a silent zero.
        if not ranked.targets:
            print("\nNothing is collection-ready. Excluded by:")
            for gate, count in sorted((body.excluded or {}).items(), key=lambda kv: -kv[1]):
                if count:
                    print(f"  {gate:32s} {count}")
            print("\nResolve the blocking gate (usually an event-specific coordinate) and re-run.")
            return
        print()

        for target in ranked.targets:
            blockers = target.readiness_blockers or []
            state = "ready" if target.collection_ready else f"blocked ({', '.join(blockers) or 'n/a'})"
            print(f"  {target.global_event_id}  {(target.headline or '')[:52]:52s} {target.rs_level or '-':10s} {state}")

        # 2. PLAN THE FIRST READY TARGET. The plan searches each collection exactly once
        #    against the event footprint, so the all-weather SAR look is never skipped in
        #    favour of whichever optical scene happened to be cloud-free.
        target = next((t for t in ranked.targets if t.collection_ready), ranked.targets[0])
        print(f"\nPlanning imagery for {target.global_event_id}…")
        plan = client.collection.plan(event_id=target.global_event_id, analysis_goal="damage_assessment")
        for step in (plan.plan.steps if plan.plan else []):
            pair = f" sar_pair={step.sar_pair_status}" if step.sar_pair_status else ""
            print(f"  {step.collection:18s} returned={step.returned_count} usable={step.usable_count}{pair}")

        # 3. WHEN CAN IT NEXT BE SEEN. `collection_mode` is the field to read: a
        #    systematic satellite will acquire on its own plan (the data will exist), an
        #    agile one only images if somebody orders it. A pass is an OPPORTUNITY.
        aoi = target.rs_aoi or []
        if len(aoi) != 4:
            print("\n(no AOI on the target — pass prediction needs a point or bbox)")
        else:
            lon, lat = (aoi[0] + aoi[2]) / 2, (aoi[1] + aoi[3]) / 2
            passes = client.collection.passes(lat=lat, lon=lon, max_passes=5)
            if passes.retrieval_ok is False:
                print("\n! orbital elements could not be refreshed — treat these windows as indicative")
            print()
            for p in passes.passes:
                print(f"  {p.start}  {p.satellite:22s} {p.collection_mode or '-':10s} peak={p.peak_elevation_deg}°")

        # 4. WATCH IT — the app's "Watch this area", checked weekly. Creating the order is
        #    free; only a check that finds something new runs the Analyst and is metered,
        #    and the response states the monthly ceiling.
        order = client.standing_orders.create(bbox=AOI, name="aoi-watch-example")
        print(f"\n{order.summary}")
        if order.watch_id:
            # The order joined the Watchlist. Pause or remove it there, as in the app — note that
            # deleting a watch also removes everything else bound to the same area.
            print(f"(stop it with client.watches.pause({order.watch_id!r}) or .delete(...))")


if __name__ == "__main__":
    main()
