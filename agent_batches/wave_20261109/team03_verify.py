#!/usr/bin/env python3
"""Team 03 slow WhatsApp verification. curl only, >=0.6s between check starts,
max 3 parallel. LIVE = HTTP 200 + non-empty og:title. 200+empty retried twice."""
import json, re, subprocess, time, threading, html
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
lock = threading.Lock()
last = [0.0]

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "25", "-A", UA,
                            "-w", "\n%{http_code}", url],
                           capture_output=True, text=True, timeout=35)
        body = r.stdout or ""
        m = re.search(r"\n(\d{3})\s*$", body)
        http = int(m.group(1)) if m else 0
        body_only = body[:m.start()] if m else body
        og = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', body_only, re.I)
        if not og:
            og = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body_only, re.I)
        title = html.unescape(og.group(1)).strip() if og else ""
        return {"code": code, "http": http, "og_title": re.sub(r'\s+', ' ', title).strip(),
                "curl_rc": r.returncode}
    except Exception as e:
        return {"code": code, "http": 0, "og_title": "", "curl_rc": -1, "error": str(e)[:100]}

def gated(code):
    with lock:
        gap = 0.6 - (time.time() - last[0])
        if gap > 0:
            time.sleep(gap)
        last[0] = time.time()
    return check(code)

fresh = json.load(open(f"{WAVE}/team03-fresh.json"))
codes = [r["code"] for r in fresh]
print(f"verifying {len(codes)} codes", flush=True)
results = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(gated, codes):
        results[res["code"]] = res
        n = len(results)
        if n % 20 == 0:
            live = sum(1 for v in results.values() if v["http"] == 200 and v["og_title"])
            print(f"... {n}/{len(codes)} live-so-far={live}", flush=True)

# retry rounds for ambiguous (200 + empty og:title)
for rnd in (1, 2):
    amb = [c for c, v in results.items() if v["http"] == 200 and not v["og_title"]]
    if not amb:
        break
    print(f"retry round {rnd}: {len(amb)} ambiguous", flush=True)
    time.sleep(60 if rnd == 1 else 120)
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(gated, amb):
            if res["og_title"]:
                results[res["code"]] = res
                print("  resolved live:", res["code"], repr(res["og_title"][:60]), flush=True)
            else:
                results[res["code"]] = res
    json.dump(results, open(f"{WAVE}/team03-verify.json", "w"), indent=1)

json.dump(results, open(f"{WAVE}/team03-verify.json", "w"), indent=1)
live = sum(1 for v in results.values() if v["http"] == 200 and v["og_title"])
amb = sum(1 for v in results.values() if v["http"] == 200 and not v["og_title"])
dead = sum(1 for v in results.values() if v["http"] not in (0, 200))
fail = sum(1 for v in results.values() if v["http"] == 0)
print(f"DONE live={live} ambiguous-still-empty={amb} dead(http!=200)={dead} transport-fail={fail}", flush=True)
