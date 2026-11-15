#!/usr/bin/env python3
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114")
from team23_verify import verify
import requests

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
raw = json.load(open(f"{WD}/team23_raw.json"))
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
fresh = [c for c in raw if c not in union]

sess = requests.Session()
results = {}
for i, code in enumerate(fresh):
    st, title, err = verify(sess, code)
    results[code] = {"status": st, "og_title": title, "err": err,
                      "dir_name": raw[code]["name"], "page": raw[code]["page"], "site": raw[code]["site"]}
    print(f"{i+1}/{len(fresh)} {code} {st} | {title!r}")
    json.dump(results, open(f"{WD}/team23_verify_results.json", "w"), ensure_ascii=False, indent=1)
    time.sleep(1)
print("done")
