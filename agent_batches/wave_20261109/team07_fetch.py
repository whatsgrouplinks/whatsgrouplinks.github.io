#!/usr/bin/env python3
"""Team07 phase 1: fetch listing pages, extract chat.whatsapp.com codes + context."""
import json, re, os, html, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WAVE, "team07_raw")
os.makedirs(RAW, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

leads = json.load(open(os.path.join(WAVE, "leads_slice_07.json")))

def fetch(item):
    idx, entry = item
    url = entry["url"].replace("&amp;", "&")
    out = os.path.join(RAW, f"{idx:03d}.html")
    # skip refetch if exists and non-empty
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return idx, url, "cached", os.path.getsize(out)
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "45",
                            "-A", UA, "-o", out, "-w", "%{http_code}", url],
                           capture_output=True, text=True, timeout=60)
        code = r.stdout.strip()
        size = os.path.getsize(out) if os.path.exists(out) else 0
        return idx, url, code, size
    except Exception as e:
        return idx, url, f"ERR {e}", 0

with ThreadPoolExecutor(max_workers=6) as ex:
    results = list(ex.map(fetch, enumerate(leads)))

for idx, url, code, size in results:
    print(idx, code, size, url[:90])

json.dump([{"idx": i, "url": u, "http": c, "size": s} for i, u, c, s in results],
          open(os.path.join(WAVE, "team07_fetch_log.json"), "w"), indent=1)
print("done")
