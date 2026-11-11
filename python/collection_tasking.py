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
        #    can mean "few candidates" or "few that could be placed precisely enough to
        #    image", and those are different situations for a collection manager.
        ranked = client.collection.priority(bbox=AOI, top_n=5)
        body = ranked.priority
        if body is None:
            print("No priority body returned.")
            return
        print(f"{body.returned} target(s) returned of {body.total_available} available")

        # An empty list is a real answer, and the exclusion breakdown is the useful part
        # of it: it says WHICH gate emptied the funnel. A collection manager needs that,
        # not a silent zero.
        if not ranked.targets:
            print("\nNothing to rank. Excluded by:")
            for gate, count in sorted((body.excluded or {}).items(), key=lambda kv: -kv[1]):
                if count:
                    print(f"  {gate:32s} {count}")
            return
        print()

        for target in ranked.targets:
            print(
                f"  {target.event_id}  {(target.title or '')[:52]:52s} "
                f"{target.spec_class or '-':6s} {target.sensor or '-'}"
            )

        # 2. PLAN THE TOP TARGET. The plan searches each collection exactly once against
        #    the event footprint, so the all-weather SAR look is never skipped in favour of
        #    whichever optical scene happened to be cloud-free.
        target = ranked.targets[0]
        print(f"\nPlanning imagery for {target.event_id}…")
        plan = client.collection.plan(
            event_id=target.event_id or "", analysis_goal="damage_assessment"
        )
        for step in (plan.plan.steps if plan.plan else []):
            pair = f" sar_pair={step.sar_pair_status}" if step.sar_pair_status else ""
            print(
                f"  {step.collection:18s} returned={step.returned_count} "
                f"usable={step.usable_count}{pair}"
            )

        # 3. WHEN CAN IT NEXT BE SEEN. `collection_mode` is the field to read: a
        #    systematic satellite will acquire on its own plan (the data will exist), an
        #    agile one only images if somebody orders it. A pass is an OPPORTUNITY.
        if target.lat is None or target.lng is None:
            print("\n(no point on the target — pass prediction needs a point or bbox)")
        else:
            passes = client.collection.passes(lat=target.lat, lon=target.lng, max_passes=5)
            if passes.retrieval_ok is False:
                print("\n! orbital elements could not be refreshed — windows are indicative")
            print()
            for p in passes.passes:
                mode = p.collection_mode or "-"
                print(f"  {p.start}  {p.satellite:22s} {mode:10s} peak={p.peak_elevation_deg}°")

        # 4. WATCH IT — the app's "Watch this area", checked weekly. Creating the order is
        #    free, and its checks run no model and are not charged. The area has an upper
        #    size limit, so watch the target's surroundings, not the whole search box.
        if target.lat is not None and target.lng is not None:
            box = [target.lng - 0.25, target.lat - 0.25, target.lng + 0.25, target.lat + 0.25]
            order = client.standing_orders.create(bbox=box, name="collection-tasking-example")
            print(f"\n{order.summary}")
            if order.watch_id:
                # The order joined the Watchlist. Pause or remove it there, as in the app — note
                # that deleting a watch also removes everything else bound to the same area.
                print(f"(stop it with client.watches.pause({order.watch_id!r}) or .delete(...))")


if __name__ == "__main__":
    main()
