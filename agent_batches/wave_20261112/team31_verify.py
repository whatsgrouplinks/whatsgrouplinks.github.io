#!/usr/bin/env python3
"""TEAM31 verify: 97 fresh codes, 4 workers, warm session, spaced retry for transport failures."""
import json, re, time, os
import requests
from concurrent.futures import ThreadPoolExecutor
from html import unescape

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}

def og_title(html):
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
    if m: return unescape(m.group(1)).strip()
    m = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html)
    return unescape(m.group(1)).strip() if m else ""

def check(args):
    code, session = args
    try:
        r = session.get(f"https://chat.whatsapp.com/{code}", headers=UA, timeout=75)
        t = og_title(r.text)
        return {"code": code, "status": "live" if t else "dead", "og": t, "http": r.status_code}
    except Exception as e:
        return {"code": code, "status": "transport", "og": "", "error": str(e)[:150]}

fresh = json.load(open(os.path.join(WAVE, "team31_fresh.json")))
codes = sorted(fresh.keys())
print("to verify:", len(codes), flush=True)

# one session per worker via thread-local
import threading
local = threading.local()
def get_s():
    if not hasattr(local, "s"):
        local.s = requests.Session()
    return local.s

def run(code):
    return check((code, get_s()))

results = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for i, res in enumerate(ex.map(run, codes)):
        results[res["code"]] = res
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(codes)}", flush=True)
            json.dump(results, open(os.path.join(WAVE, "team31_verify_pass1.json"), "w"), indent=1)

pend = [c for c, r in results.items() if r["status"] == "transport"]
print("pass1:", sum(1 for r in results.values() if r["status"]=="live"), "live,",
      sum(1 for r in results.values() if r["status"]=="dead"), "dead,",
      len(pend), "transport", flush=True)
if pend:
    print("pausing 30s then retrying transport failures...", flush=True)
    time.sleep(30)
    with ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(run, pend):
            results[res["code"]] = res
    pend2 = [c for c, r in results.items() if r["status"] == "transport"]
    print("pass2 transport remaining:", len(pend2), flush=True)
json.dump(results, open(os.path.join(WAVE, "team31_verify.json"), "w"), indent=1)
for c, r in sorted(results.items()):
    print(f"  {r['status'].upper():9s} {c} | og={r['og'][:80]!r}", flush=True)
