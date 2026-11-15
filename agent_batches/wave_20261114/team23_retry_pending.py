#!/usr/bin/env python3
"""Retry the 65 HTTP-429 pending codes after cooldown; stop early if 429 persists."""
import json, sys, time, requests
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114")
from team23_run_verify2 import verify_fast

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
res = json.load(open(f"{WD}/team23_verify2_results.json"))
pending = [c for c, v in res.items() if v.get("status") == "pending"]
print("pending to retry:", len(pending))
sess = requests.Session()
out = {}
consec429 = 0
for i, code in enumerate(pending):
    st, title, err = verify_fast(sess, code)
    out[code] = {"status": st, "og_title": title, "err": err, **{k: v for k, v in res[code].items() if k not in ("status", "og_title", "err")}}
    print(f"{i+1}/{len(pending)} {code} {st} | {title!r} | {err}", flush=True)
    if st == "pending":
        consec429 += 1
        if consec429 >= 5:
            print("5 consecutive 429s — stopping retry pass, rest stay pending")
            break
    else:
        consec429 = 0
    json.dump(out, open(f"{WD}/team23_verify2_retry.json", "w"), ensure_ascii=False, indent=1)
    time.sleep(2)
print("retry done, resolved:", len(out))
