#!/usr/bin/env python3
"""Reconstruct daily WATTCH forecast initialisations for all selected storms.

Original WATTCH ensemble runs are preserved exactly in source coordinate/wind
values; synthetic daily initialisations are RETROSPECTIVE training products
blending the two surrounding original forecast runs, not real forecasts.

Output: data/daily/<Event_ID>.json (one per storm)
        data/daily/manifest.json (coverage, playable windows, QA)
"""
import bisect
import csv
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAY = timedelta(days=1)
SIX_HOURS = timedelta(hours=6)
FORECAST_DAYS = 7
EARTH_KM = 111.2
MIN_WIND_MS = 63 / 3.6
FORECAST_APPROACH_KM = 300
REFERENCE_APPROACH_KM = 350

def dt(s):
    return datetime.fromisoformat(str(s).strip().replace(" ", "T")).replace(tzinfo=timezone.utc)

def stamp(t):
    return t.strftime("%Y-%m-%d %H:%M")

def rounded(x):
    return round(x, 5) if x is not None else None

def median(a):
    a = sorted(a)
    return a[len(a)//2] if a else None

def reference_track(scenario):
    # Some extracted reference series combine overlapping best tracks.
    # Median aggregation removes duplicate observation times for anchoring.
    grouped = defaultdict(list)
    for raw in scenario["reference_track"]:
        if len(raw) < 4:
            continue
        try:
            t = dt(raw[0])
            p = [float(v) if v is not None else None for v in raw[1:4]]
        except (ValueError, TypeError):
            continue
        if all(v is not None and math.isfinite(v) for v in p[:2]):
            grouped[t].append(p)
    return [(t, *[median([p[k] for p in entries if p[k] is not None]) for k in range(3)])
            for t, entries in sorted(grouped.items())]

def interpolate(track, when):
    if not track:
        return None
    times = [p[0] for p in track]
    i = bisect.bisect_left(times, when)
    if i < len(track) and times[i] == when:
        return list(track[i][1:])
    if not 0 < i < len(track):
        return None
    a, b = track[i-1], track[i]
    # Never bridge missing chunks of more than 24 hours.
    total = (b[0]-a[0]).total_seconds()
    if total <= 0 or total > 24*3600:
        return None
    w = (when-a[0]).total_seconds()/total
    return [None if a[k] is None or b[k] is None else a[k]+w*(b[k]-a[k])
            for k in range(1, 4)]

def load_ensemble_csv(path, target_ids):
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    totals = defaultdict(int)
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            event = row.get("Event_ID", "")
            if event not in target_ids:
                continue
            totals[event] += 1
            try:
                member = int(row["Ensmember"])
                if member < 1:
                    continue
                lat = float(row["Lat"])
                lon = float(row["Lon"])
                wind = float(row["Wind"])
                issued = row["Forecast_initialisation"][:10]
                valid = dt(row["DateTime"])
                if not all(map(math.isfinite, (lat, lon, wind))):
                    continue
                result[event][issued][member].append((valid, lat, lon, wind))
            except (ValueError, TypeError, KeyError):
                continue
    for init_map in result.values():
        for member_map in init_map.values():
            for member, track in member_map.items():
                # Resolve any accidental duplicated valid times deterministically.
                uniq = {p[0]: p for p in track}
                member_map[member] = sorted(uniq.values(), key=lambda p: p[0])
    return result, totals

def reconstruct(event, scenario, initialisations, row_count):
    reference = reference_track(scenario)
    dates = sorted(initialisations)
    if not dates:
        return None, {"event_id": event, "name": scenario.get("storm_name"),
                      "error": "no_original_initialisations"}
    original_datetimes = [dt(day) for day in dates]
    daily_start, daily_end = original_datetimes[0], original_datetimes[-1]
    daily = []
    quality = defaultdict(int)
    issue = daily_start
    while issue <= daily_end:
        day = issue.strftime("%Y-%m-%d")
        origin = interpolate(reference, issue)
        if day in initialisations:
            members = []
            for member, points in sorted(initialisations[day].items()):
                members.append({
                    "member": member,
                    "points": [[stamp(p[0]), *[rounded(x) for x in p[1:]]] for p in points]
                })
            daily.append({"issue_date": day, "type": "original",
                          "members": members, "reference_start": [rounded(x) for x in origin] if origin else None})
        elif origin and all(v is not None for v in origin):
            after_idx = bisect.bisect_right(original_datetimes, issue)
            if after_idx == 0 or after_idx >= len(original_datetimes):
                issue += DAY
                continue
            before_day, after_day = dates[after_idx-1], dates[after_idx]
            before = initialisations[before_day]
            after = initialisations[after_day]
            t_before, t_after = original_datetimes[after_idx-1], original_datetimes[after_idx]
            w = (issue - t_before).total_seconds() / (t_after - t_before).total_seconds()
            members = []
            for member in sorted(set(before).intersection(after)):
                past, future = before[member], after[member]
                base_a, base_b = interpolate(past, t_before), interpolate(future, t_after)
                if not base_a or not base_b or any(v is None for v in base_a+base_b):
                    continue
                points = []
                for step in range(FORECAST_DAYS*4+1):
                    lead = SIX_HOURS*step
                    pa, pb = interpolate(past, t_before+lead), interpolate(future, t_after+lead)
                    if not pa or not pb or any(v is None for v in pa+pb):
                        break
                    # Interpolate lead-time-relative displacements and intensity
                    # tendencies. This anchors all synthetic members at the
                    # reference cyclone position on the issue date, and DOES NOT
                    # use subsequent reference observations.
                    pp = [
                        rounded(origin[k] + (1-w)*(pa[k]-base_a[k]) + w*(pb[k]-base_b[k]))
                        for k in range(3)
                    ]
                    pp[2] = max(0, pp[2])
                    points.append([stamp(issue+lead), *pp])
                if len(points) >= 2:
                    members.append({"member": member, "points": points})
            if len(members) >= 2:
                quality["synthetic_initialisations"] += 1
                daily.append({"issue_date": day, "type": "synthetic",
                              "bracketing_initialisations": [before_day, after_day],
                              "reference_start": [rounded(x) for x in origin],
                              "members": members})
            else:
                quality["unreconstructed_dates"] += 1
        else:
            quality["missing_reference_positions"] += 1
        issue += DAY

    # The exact, already-used Madagascar coastline polygon is parsed from the
    # game's code so threat checks use the same geography, not a bounding box.
    coast = load_madagascar_outline()

    def distance_km(lat, lon):
        # Planar local km distance to polygon boundary; zero within polygon.
        inside = False
        for i in range(len(coast)):
            a, b = coast[i], coast[(i+1) % len(coast)]
            if (a[1] > lat) != (b[1] > lat):
                if lon < (b[0]-a[0])*(lat-a[1])/(b[1]-a[1])+a[0]:
                    inside = not inside
        if inside:
            return 0.0
        closest = float("inf")
        for i in range(len(coast)):
            a, b = coast[i], coast[(i+1) % len(coast)]
            factor = max(.3, math.cos(math.radians(lat)))
            x1, y1 = (a[0]-lon)*EARTH_KM*factor, (a[1]-lat)*EARTH_KM
            x2, y2 = (b[0]-lon)*EARTH_KM*factor, (b[1]-lat)*EARTH_KM
            dx, dy = x2-x1, y2-y1
            u = max(0, min(1, -(x1*dx+y1*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
            closest = min(closest, math.hypot(x1+u*dx, y1+u*dy))
        return closest

    def reference_near(day):
        begin, end = dt(day), dt(day)+DAY
        return any(begin <= p[0] < end and
                   p[3] is not None and p[3] >= MIN_WIND_MS and
                   distance_km(p[1], p[2]) <= REFERENCE_APPROACH_KM
                   for p in reference)

    def ensemble_probability(item):
        issued = dt(item["issue_date"])
        count = 0
        for member in item["members"]:
            has_threat = False
            for valid, lat, lon, wind in member["points"]:
                t = dt(valid)
                if issued <= t <= issued + timedelta(days=FORECAST_DAYS) and wind is not None and wind >= MIN_WIND_MS:
                    if distance_km(lat, lon) <= FORECAST_APPROACH_KM:
                        has_threat = True
                        break
            count += has_threat
        return count/len(item["members"]) if item["members"] else 0

    for item in daily:
        item["madagascar_approach_fraction"] = round(ensemble_probability(item), 3)

    # Determine one connected, meaningful Madagascar decision window.
    # Later possible returns remain included because we use the *last* relevant
    # day from the entire reference track and all forecast issue dates.
    near_days = sorted({p[0].strftime("%Y-%m-%d") for p in reference
                        if p[3] is not None and p[3] >= MIN_WIND_MS and
                        distance_km(p[1], p[2]) <= REFERENCE_APPROACH_KM})
    forecast_days = sorted(x["issue_date"] for x in daily
                           if x["madagascar_approach_fraction"] >= .20)
    if near_days:
        first_approach = dt(near_days[0])
        last_approach = dt(near_days[-1])
        # Ensure at least a week for mobilisation decisions where available.
        proposed_start = first_approach-timedelta(days=7)
        proposed_end = last_approach
        # Don't cut off continuing ensemble landfall concern more than 2 days
        # after the last track proximity. Anything later is flagged for review.
        later = [dt(x) for x in forecast_days if dt(x)>last_approach]
        if later:
            proposed_end = max(proposed_end, min(max(later), last_approach+timedelta(days=2)))
        status = "reference_approached_madagascar"
    elif forecast_days:
        proposed_start = dt(forecast_days[0])
        proposed_end = dt(forecast_days[-1])
        status = "ensemble_only_potential_threat"
    else:
        proposed_start = daily_start
        proposed_end = min(daily_end, daily_start + timedelta(days=3))
        status = "no_detected_madagascar_threat_review_for_removal"
    # User-reviewed Gamede playtest: retain the initial approach and final
    # threat briefing (18–28 Feb), rather than the shorter automatic estimate.
    if event == "2007_tr0013":
        proposed_start, proposed_end = dt("2007-02-18"), dt("2007-02-28")
        quality["manual_window_override"] = 1
    playable = [x for x in daily if proposed_start <= dt(x["issue_date"]) <= proposed_end]
    if not playable and daily:
        playable = daily[:min(len(daily), 3)]
        status += "_fallback_window"
    first_play = playable[0]["issue_date"] if playable else None
    last_play = playable[-1]["issue_date"] if playable else None
    # Preserve full reference and original forecast data for audit.
    record = {
        "event_id": event, "storm_name": scenario["storm_name"],
        "reference_track": scenario["reference_track"],
        "historical_scenario_id": scenario["id"],
        "metadata": {
            "data_source": "WATTCH Southern Hemisphere CSV, Zenodo 20446920",
            "forecast_type": "original WATTCH initialisation or synthetic interpolation",
            "synthetic_method": "Member-ID-matched blending of lead-time-relative position and wind changes from bracketing WATTCH runs; reference track used only at the issue time",
            "retrospective_warning": "Synthetic runs use a later archived forecast unavailable at issue time; do not use them to assess independent forecast skill",
            "wind_units": "Original WATTCH Wind units (m/s), not preconverted",
            "original_initialisations": dates,
            "source_rows_for_event": row_count,
        },
        "playable": {"first_issue_date": first_play, "last_issue_date": last_play,
                     "status": status, "reference_approach_dates": near_days,
                     "forecast_potential_threat_dates": forecast_days,
                     "requires_manual_review": True},
        "forecasts": daily
    }
    summary = {"event_id": event, "name": scenario["storm_name"],
               "original_initialisations": len(dates),
               "synthetic_initialisations": sum(x["type"]=="synthetic" for x in daily),
               "total_forecast_dates": len(daily),
               "first_playable_date": first_play, "last_playable_date": last_play,
               "playable_briefings": len(playable), "threat_status": status,
               "source_rows": row_count, **quality}
    return record, summary

def load_madagascar_outline():
    html = (ROOT/"index.html").read_text(encoding="utf-8")
    match = re.search(r"const coast=(\[\[.*?\]\]);", html, flags=re.S)
    if match is None:
        raise ValueError("Cannot locate game mainland Madagascar coastline")
    coords = json.loads(match.group(1))
    if len(coords)<20:
        raise ValueError("Unreasonably short mainland coastline")
    return coords

def main():
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python scripts/build_daily_library.py WATTCH_SH.csv")
    csv_path = Path(sys.argv[1])
    data = json.loads((ROOT/"data/scenarios.json").read_text(encoding="utf-8"))
    scenarios = {s["event_id"]:s for s in data["scenarios"]}
    print("Loading WATTCH rows for", len(scenarios), "selected events...", flush=True)
    original, totals = load_ensemble_csv(csv_path, set(scenarios))
    target = ROOT/"data/daily"
    target.mkdir(parents=True, exist_ok=True)
    summary = []
    for i, (event, scenario) in enumerate(scenarios.items(), 1):
        result, stats = reconstruct(event,scenario,original.get(event,{}),totals.get(event,0))
        if result:
            (target/(event+".json")).write_text(json.dumps(result,separators=(",",":")),encoding="utf-8")
        summary.append(stats)
        print(f"{i:02}/{len(scenarios)} {event} {scenario['storm_name']}: "
              f"{stats.get('original_initialisations',0)} original, "
              f"{stats.get('synthetic_initialisations',0)} synthetic, "
              f"play {stats.get('first_playable_date')}–{stats.get('last_playable_date')}",flush=True)
    manifest = {"version":"experimental-2026-11","selected_storm_count":len(scenarios),
                "created_with":"scripts/build_daily_library.py",
                "warning":"NOT YET APPROVED FOR THE MAIN GAME: threat windows need storm-by-storm review",
                "storms":summary}
    (target/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    missing = [s for s in summary if s.get("original_initialisations",0)==0]
    if missing:
        raise RuntimeError(f"Missing WATTCH source data for {len(missing)} selected storms: "
                           +", ".join(s["event_id"] for s in missing))
    print("Completed",len(summary),"storms, "
          +str(sum(s.get("synthetic_initialisations",0) for s in summary))
          +" synthetic forecasts",flush=True)

if __name__ == "__main__":
    main()
