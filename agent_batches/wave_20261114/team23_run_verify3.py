#!/usr/bin/env python3
"""Verify the 16 groupslink.pk fresh codes (runs AFTER verify2 finishes)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114")
from team23_run_verify2 import verify_fast
import requests

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
fresh = json.load(open(f"{WD}/team23_groupslinkpk_fresh.json"))
sess = requests.Session()
results = {}
try:
    results = json.load(open(f"{WD}/team23_verify3_results.json"))
except Exception:
    pass
for i, (code, d) in enumerate(fresh.items()):
    if code in results:
        continue
    st, title, err = verify_fast(sess, code)
    results[code] = {"status": st, "og_title": title, "err": err,
                      "dir_name": d.get("name"), "page": d.get("page"), "site": "groupslink.pk",
                      "country": "PK", "api_category": ""}
    print(f"{i+1}/{len(fresh)} {code} {st} | {title!r}", flush=True)
    json.dump(results, open(f"{WD}/team23_verify3_results.json", "w"), ensure_ascii=False, indent=1)
    time.sleep(0.5)
print("done")
