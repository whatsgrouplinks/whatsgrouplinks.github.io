#!/usr/bin/env python3
"""Team27 wave 20261111: slow verifier.
LIVE iff HTTP 200 AND non-empty og:title. Retry empty-og once after a pause.
Max 3 parallel workers, >=0.5s delay between requests per worker.
Usage: python3 team27_verify.py [pool.json] [out.tsv]"""
import json, re, sys, time, os
import urllib.request
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
RAW = os.path.join(WAVE, "team27_raw")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

pool = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(WAVE, "team27_pool.json")))
codes = sorted(pool.keys())
out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(WAVE, "team27_verify.tsv")

def fetch(code, attempt):
    url = "https://chat.whatsapp.com/" + code
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", errors="ignore")
            http = r.status
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        http = e.code
    except Exception as e:
        return (code, 0, "", "transport:" + type(e).__name__)
    m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', body)
    if not m:
        m = re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:title"', body)
    title = (m.group(1).strip() if m else "")
    # save evidence html for live ones
    if http == 200 and title:
        with open(os.path.join(RAW, "verify_%s.html" % code), "w", encoding="utf-8") as f:
            f.write(body)
    return (code, http, title, "")

def check(code):
    time.sleep(0.6)
    res = fetch(code, 1)
    if res[1] == 200 and not res[2]:
        time.sleep(8)
        res2 = fetch(code, 2)
        if res2[1] == 200 and res2[2]:
            return res2
        if res2[1] == 0:
            return (code, res[1], "", "pending-transport-after-empty")
        return res2
    return res

done = {}
if os.path.exists(out_path):
    for line in open(out_path, encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 4 and parts[0] not in done:
            done[parts[0]] = parts

todo = [c for c in codes if c not in done]
print(f"total {len(codes)} already-done {len(done)} todo {len(todo)}", flush=True)
results = []
with ThreadPoolExecutor(max_workers=3) as ex:
    for i, res in enumerate(ex.map(check, todo)):
        results.append(res)
        if (i + 1) % 10 == 0:
            print(f"checked {i+1}/{len(todo)}", flush=True)
        with open(out_path, "a", encoding="utf-8") as f:
            f.write("\t".join([res[0], str(res[1]), res[2].replace("\t", " "), res[3]]) + "\n")

live = sum(1 for r in results if r[1] == 200 and r[2])
dead = sum(1 for r in results if r[1] == 200 and not r[2])
pend = sum(1 for r in results if r[1] == 0)
print(f"this run: live {live} dead {dead} transport-fail {pend}")
