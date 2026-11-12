#!/usr/bin/env python3
"""Team19: confirm page 2 holds nothing fresher than yesterday's newest (2026-11-11 05:12:31)."""
import json, subprocess, time, os
RAW="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team19_raw"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
time.sleep(4)
out=f"{RAW}/notag_p2.json"
for attempt in range(4):
    r=subprocess.run(["curl","-s","-m","30","-A",UA,"https://api.groupjoin.link/groups?page=2&limit=20&safeSearch=blur","-o",out,"-w","%{http_code}"],capture_output=True,text=True)
    try: d=json.load(open(out))
    except Exception: d=None
    if r.stdout.strip()=="200" and isinstance(d,dict) and "data" in d: break
    print("page2 attempt",attempt+1,"http=",r.stdout.strip(),flush=True); time.sleep(10)
else:
    print("PAGE2_FAILED"); raise SystemExit(1)
data=d["data"]
dates=[x.get("created_at","")[:10] for x in data]
print(f"page2: {len(data)} items, created {min(dates)}..{max(dates)}")
print("page2 max created_at:", max(x.get("created_at","") for x in data))
print("any > 2026-11-11 05:12:31 ?", any(x.get("created_at","")>"2026-11-11 05:12:31" for x in data))
for x in data[:5]:
    print(" ",x.get("created_at","")[:19],"|",((x.get("category") or {}).get("category_name")),"|",x.get("group_title","")[:50])
print("PAGE2_DONE")
