#!/usr/bin/env python3
"""TEAM 10 — retry the 21 transport-failed (pending) codes from the verify checkpoint.
Appends fresh verdicts to team10-verify-checkpoint.jsonl (build takes the LAST
record per code). Spaced retry: verify_one already does 2 attempts w/ 5s pause.
"""
import json, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '.')
from team10_pipeline import verify_one

CKPT = "team10-verify-checkpoint.jsonl"
lock = threading.Lock()
pending = []
seen = {}
for line in open(CKPT):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    seen[r["code"]] = r
pending = sorted(c for c, r in seen.items() if r["status"] == "pending")
print(f"pending codes to retry: {len(pending)}", flush=True)
results = {}
def work(code):
    rec = verify_one(code)
    with lock:
        with open(CKPT, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        results[code] = rec["status"]
        print(f"{code}: {rec['status']} http={rec.get('http')} og={rec.get('og_title','')[:40]!r}", flush=True)
    time.sleep(0.5)
    return rec
with ThreadPoolExecutor(6) as ex:
    list(ex.map(work, pending))
from collections import Counter
print("RETRY RESULT:", dict(Counter(results.values())), flush=True)
