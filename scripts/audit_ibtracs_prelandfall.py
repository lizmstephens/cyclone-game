#!/usr/bin/env python3
"""Audit Madagascar pre-landfall IBTrACS wind for the cyclone-game catalogue.
Generates a review file; does not change historical impact data or game logic.
"""
import csv, io, json, re, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.SI.list.v04r01.csv"
index=(ROOT/"index.html").read_text()
map_ids=json.loads(re.search(r"const ibtracsMatches=(\{.*?\});",index).group(1))
catalogue=json.loads((ROOT/"data/verified_impacts.json").read_text())["by_event_id"]
coast=json.loads("["+re.search(r"const coast=(\[.*?\]);",index).group(1)[1:-1]+"]")
def inside(lat,lon):
    hit=False
    for j in range(len(coast)):
        x1,y1=coast[j-1];x2,y2=coast[j]
        if (y1>lat)!=(y2>lat) and lon < (x2-x1)*(lat-y1)/(y2-y1)+x1: hit=not hit
    return hit
def crossing(a,b):
    # Detect sea-to-land crossing of the mainland outline. IBTrACS positions are interpolated.
    x,y=float(a["LON"]),float(a["LAT"])
    dx=float(b["LON"])-x;dy=float(b["LAT"])-y
    if inside(y,x):return False
    for j in range(1,len(coast)):
        x1,y1=coast[j-1];x2,y2=coast[j]
        ex=x2-x1;ey=y2-y1;den=dx*ey-dy*ex
        if abs(den)<1e-12:continue
        qx=x1-x;qy=y1-y
        t=(qx*ey-qy*ex)/den
        u=(qx*dy-qy*dx)/den
        if 0<=t<=1 and 0<=u<=1 and inside(y+min(1,t+1e-5)*dy,x+min(1,t+1e-5)*dx):
            return True
    return False
def numeric(x):
    try:return float(x)
    except (TypeError,ValueError):return None
def wind_before(fixes,idx):
    # Prefer last nonblank Réunion 10-minute sustained estimate at/before offshore fix.
    # WMO_WIND often duplicates Réunion but period depends on source; avoid unlabelled merging.
    for key,agency,period in [("REUNION_WIND","RSMC La Réunion","10-minute sustained"),("USA_WIND","JTWC/USA","1-minute sustained")]:
        for back in range(idx,-1,-1):
            v=numeric(fixes[back].get(key))
            if v is not None:
                return {"wind_kmh":round(v*1.852),"agency":agency,"wind_averaging_period":period,
                  "wind_time_utc":fixes[back]["ISO_TIME"],"wind_lat":numeric(fixes[back]["LAT"]),
                  "wind_lon":numeric(fixes[back]["LON"]),"lag_hours":round((__import__("datetime").datetime.fromisoformat(fixes[idx]["ISO_TIME"])-__import__("datetime").datetime.fromisoformat(fixes[back]["ISO_TIME"])).total_seconds()/3600,1)}
    return None
request=urllib.request.Request(BASE,headers={"User-Agent":"cyclone-game-ibtracs-audit/1.0"})
with urllib.request.urlopen(request,timeout=120) as response:
    content=response.read().decode("utf-8-sig")
read=csv.DictReader(io.StringIO(content))
allfix={}
for row in read:
    sid=row.get("SID")
    if not sid or sid=="SID" or not row.get("ISO_TIME"):continue
    if sid in set(map_ids.values()):allfix.setdefault(sid,[]).append(row)
results={}
for event,record in catalogue.items():
    sid=map_ids.get(event)
    output={"event_id":event,"storm_name":record["storm_name"],"ibtracs_sid":sid,"status":None,"crossings":[]}
    if not sid:
        output["status"]="NO_IBTRACS_MATCH"
    elif sid not in allfix:
        output["status"]="SID_NOT_FOUND"
    else:
        fixes=sorted(allfix[sid],key=lambda x:x["ISO_TIME"])
        for i in range(len(fixes)-1):
            a,b=fixes[i],fixes[i+1]
            if numeric(a.get("LANDFALL"))!=0:continue
            if crossing(a,b):
                intensity=wind_before(fixes,i)
                output["crossings"].append({"start_utc":a["ISO_TIME"],"end_utc":b["ISO_TIME"],
                  "last_offshore_lat":numeric(a["LAT"]),"last_offshore_lon":numeric(a["LON"]),
                  "landfall_flag":a["LANDFALL"],"wind":intensity})
        output["status"]="MAINLAND_CROSSING" if output["crossings"] else "NO_MAINLAND_CROSSING_FOUND"
    results[event]=output
out={"method":"IBTrACS v04r01 SI basin, last available RSMC La Réunion wind before mainland Madagascar centre crossing; USA 1-minute fallback; no averaging-period conversions","source_url":BASE,"events":results}
target=ROOT/"data/ibtracs_prelandfall_audit.json"
target.write_text(json.dumps(out,indent=2)+"\n")
print(f"Audited {len(results)} records; mainland crossings: {sum(bool(x['crossings']) for x in results.values())}; no SID: {sum(x['status']=='NO_IBTRACS_MATCH' for x in results.values())}")
