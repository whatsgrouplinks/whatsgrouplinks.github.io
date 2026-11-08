#!/usr/bin/env python3
"""TEAM 13 pipeline: probe tails via groupjoin.link API, extract, dedupe, verify."""
import json, re, time, html, os, sys, random
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")

def api_q(tag, page, attempts=4, timeout=45):
    last = None
    for i in range(attempts):
        try:
            r = requests.get("https://api.groupjoin.link/groups",
                params={"tag": tag, "page": page, "limit": 20, "safeSearch": "blur"},
                headers={"User-Agent": UA, "Accept": "application/json"}, timeout=timeout)
            d = r.json()
            return d
        except Exception as e:
            last = e
            time.sleep(2 + i * 3)
    print(f"  API FAIL tag={tag} p{page}: {last}", flush=True)
    return None

union = set(json.load(open(f"{WAVE}/dedupe_union.json")))
print(f"union: {len(union)} codes", flush=True)

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})")

# --- bound discovery: money true end + tail probes ---
probes = {"money": list(range(100, 108)) + [211, 212, 213, 214],
          "education": [32, 76, 77],
          "business": [85]}
results = {}
for tag, pages in probes.items():
    print(f"== {tag} ==", flush=True)
    for p in pages:
        d = api_q(tag, p)
        if d is None:
            results[(tag, p)] = None
        else:
            n = len(d.get("data", []))
            results[(tag, p)] = (n, d.get("total"), d.get("totalPages"))
            print(f"  p{p}: records={n} total={d.get('total')} totalPages={d.get('totalPages')}", flush=True)
        time.sleep(1.0)

json.dump({f"{t}:{p}": v for (t, p), v in results.items()},
          open(f"{WAVE}/team13-probe-results.json", "w"), indent=1)
print("probe done", flush=True)
