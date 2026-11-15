#!/usr/bin/env python3
"""team29: verify all fresh codes vs WhatsApp, checkpointed (resume-safe)."""
import json, os, time
from team29_lib import S, verify_code

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
CKPT = os.path.join(WAVE, "team29-verify.jsonl")
named = json.load(open(os.path.join(WAVE, "team29-fresh-named.json")))
done = {}
if os.path.exists(CKPT):
    for line in open(CKPT):
        try:
            r = json.loads(line)
            done[r["code"]] = r
        except Exception:
            pass
print("already verified:", len(done), "of", len(named), flush=True)

codes = [c for c in named if c not in done]
for i, code in enumerate(codes):
    status, title, http = verify_code(code, attempts=3)
    rec = {"code": code, "status": status, "title": title, "http": http,
           "name_guess": named[code]["name_guess"], "sources": named[code]["sources"]}
    with open(CKPT, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[{i+1}/{len(codes)}] {code} {status} {http} {title[:70]!r}", flush=True)
    time.sleep(0.6)

print("DONE", flush=True)
