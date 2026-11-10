#!/usr/bin/env python3
"""TEAM 06 wave 20261110 slice 6: fetch 184 listing pages, extract invite codes + names."""
import json, re, html, os, subprocess, sys, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
RAW = os.path.join(BASE, "raw")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

leads = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_06.json"))
for i, l in enumerate(leads):
    l["url"] = html.unescape(l["url"])
    l["idx"] = i

def fetch_one(l):
    i = l["idx"]; url = l["url"]
    out = os.path.join(RAW, f"p{i}.html")
    if os.path.exists(out) and os.path.getsize(out) > 100:
        return (i, url, "cached", os.path.getsize(out))
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "30",
                            "--connect-timeout", "10", "-A", UA,
                            "-o", out, "-w", "%{http_code}", url],
                           capture_output=True, text=True, timeout=40)
        code = r.stdout.strip()
        sz = os.path.getsize(out) if os.path.exists(out) else 0
        return (i, url, code, sz)
    except Exception as e:
        return (i, url, f"ERR:{e}", 0)

t0 = time.time()
results = []
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(fetch_one, leads):
        results.append(res)
        if len(results) % 40 == 0:
            print(f"{len(results)}/184 fetched in {time.time()-t0:.0f}s", flush=True)
json.dump([{"idx": i, "url": u, "http": h, "size": s} for i, u, h, s in results],
          open(os.path.join(BASE, "team06-fetch-status.json"), "w"), indent=1)
print("fetch done", len(results), f"{time.time()-t0:.0f}s")
from collections import Counter
print(Counter(str(h) for _, _, h, _ in results))
