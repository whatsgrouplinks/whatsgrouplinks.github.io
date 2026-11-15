#!/usr/bin/env python3
"""team29: one retry round for 429-pending codes after a cooldown."""
import json, os, time
from team29_lib import verify_code

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
CKPT = os.path.join(WAVE, "team29-verify.jsonl")
named = json.load(open(os.path.join(WAVE, "team29-fresh-named.json")))
recs = [json.loads(l) for l in open(CKPT)]
pend = [r for r in recs if r["status"] == "pending"]
print("pending to retry:", len(pend), flush=True)
print("cooling down 300s...", flush=True)
time.sleep(300)
kept = [r for r in recs if r["status"] != "pending"]
with open(CKPT, "w") as f:
    for r in kept:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
for i, r in enumerate(pend):
    code = r["code"]
    status, title, http = verify_code(code, attempts=3)
    rec = {"code": code, "status": status, "title": title, "http": http,
           "name_guess": named[code]["name_guess"], "sources": named[code]["sources"],
           "retry": "429-cooldown-retry"}
    with open(CKPT, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[{i+1}/{len(pend)}] {code} {status} {http} {title[:70]!r}", flush=True)
    time.sleep(3)
print("DONE", flush=True)
