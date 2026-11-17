#!/usr/bin/env python3
"""Validate every generated daily WATTCH cyclone scenario without re-downloading the source CSV."""
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DAYDIR=ROOT/"data/daily"
manifest=json.loads((DAYDIR/"manifest.json").read_text())
selected=json.loads((ROOT/"data/scenarios.json").read_text())["scenarios"]
ids={s["event_id"] for s in selected}
summaries={s["event_id"]:s for s in manifest["storms"]}
errors=[]
warnings=[]
totals=Counter()

if len(ids)!=86:
    errors.append(f"Expected 86 selected IDs, got {len(ids)}")
if ids!=summaries.keys():
    errors.append(f"Manifest ID mismatch: missing={sorted(ids-summaries.keys())}, extra={sorted(summaries.keys()-ids)}")

def dt(s):
    return datetime.fromisoformat(s.replace(" ","T"))

for event in sorted(ids):
    file=DAYDIR/(event+".json")
    if not file.exists():
        errors.append(event+": missing daily file")
        continue
    d=json.loads(file.read_text())
    if d["event_id"]!=event:
        errors.append(event+": wrong event ID")
    if not d.get("reference_track"):
        errors.append(event+": missing reference track")
    forecasts=d.get("forecasts",[])
    original=[f for f in forecasts if f["type"]=="original"]
    synthetic=[f for f in forecasts if f["type"]=="synthetic"]
    summary=summaries.get(event,{})
    if len(original)!=summary.get("original_initialisations"):
        errors.append(event+": original forecast count mismatch")
    if len(synthetic)!=summary.get("synthetic_initialisations"):
        errors.append(event+": synthetic forecast count mismatch")
    if [f["issue_date"] for f in forecasts]!=sorted(set(f["issue_date"] for f in forecasts)):
        errors.append(event+": unsorted or duplicate forecast dates")
    if set(d["metadata"]["original_initialisations"])!={f["issue_date"] for f in original}:
        errors.append(event+": original issue date provenance mismatch")
    if not original:
        errors.append(event+": no original WATTCH initialisations")
    fst=d["playable"]["first_issue_date"]
    lst=d["playable"]["last_issue_date"]
    in_window=[f for f in forecasts if fst<=f["issue_date"]<=lst] if fst and lst else []
    if not in_window:
        errors.append(event+": no playable forecasts")
    if len(in_window)!=summary.get("playable_briefings"):
        errors.append(event+": playable briefing count mismatch")
    if len(in_window)<5:
        warnings.append(event+": fewer than five playable briefings")
    if d["playable"]["status"].startswith("no_detected"):
        warnings.append(event+": no verified Madagascar threat by automatic geometry test")
    for forecast in forecasts:
        if not forecast.get("members"):
            errors.append(event+"/"+forecast["issue_date"]+": empty ensemble")
        for member in forecast["members"]:
            points=member["points"]
            if len(points)<2:
                errors.append(event+"/"+forecast["issue_date"]+": member fewer than two points")
                continue
            times=[dt(p[0]) for p in points]
            if times!=sorted(set(times)):
                errors.append(event+"/"+forecast["issue_date"]+": unsorted or duplicate member times")
            for p in points:
                if len(p)!=4 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in p[1:]):
                    errors.append(event+"/"+forecast["issue_date"]+": nonfinite or missing member value")
                    break
                if not -90<=p[1]<=90 or not -180<=p[2]<=180:
                    errors.append(event+"/"+forecast["issue_date"]+": coordinates out of range")
                    break
            if forecast["type"]=="synthetic":
                first=points[0]
                start=forecast.get("reference_start")
                if not start or any(not isinstance(v,(int,float)) for v in start):
                    errors.append(event+"/"+forecast["issue_date"]+": missing synthetic reference start")
                elif abs(first[1]-start[0])>0.001 or abs(first[2]-start[1])>0.001 or abs(first[3]-start[2])>0.01:
                    errors.append(event+"/"+forecast["issue_date"]+": synthetic member not anchored at reference")
        if forecast["type"]=="synthetic":
            a,b=forecast["bracketing_initialisations"]
            if not a<forecast["issue_date"]<b:
                errors.append(event+"/"+forecast["issue_date"]+": invalid bracketing dates")
    totals["original"]+=len(original)
    totals["synthetic"]+=len(synthetic)
    totals["storms"]+=1

print("Daily WATTCH library validation:")
print(f"  Storm files checked: {totals['storms']}")
print(f"  Original WATTCH runs: {totals['original']}")
print(f"  Synthetic daily runs: {totals['synthetic']}")
print(f"  Scientific review flags: {len(warnings)}")
print(f"  Structural validation errors: {len(errors)}")
for issue in warnings:
    print("REVIEW:",issue)
for error in errors:
    print("ERROR:",error)
if errors:
    raise SystemExit(1)
