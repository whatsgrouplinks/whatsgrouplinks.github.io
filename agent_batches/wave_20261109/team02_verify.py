#!/usr/bin/env python3
"""Team 02: slow-checker verification of the 48 new codes against chat.whatsapp.com.
curl only (never python requests). 3 workers, >=0.5s pacing. Retries x3 for empty og:title."""
import json, re, subprocess, time, html, os
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OUT = f"{WAVE}/team02-verified.json"

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    attempts = []
    for attempt in range(3):
        try:
            r = subprocess.run(["curl","-s","-L","--max-time","30","-A",UA,
                                "-w","\n%{http_code}", url],
                               capture_output=True, timeout=40)
            raw = r.stdout.decode("utf-8", errors="ignore")
            lines = raw.rsplit("\n", 1)
            http = lines[1].strip() if len(lines) == 2 else "?"
            body = lines[0] if len(lines) == 2 else raw
        except Exception as e:
            http, body = "ERR", ""
        tm = re.search(r'<meta property="og:title" content="([^"]*)"', body)
        dm = re.search(r'<meta property="og:description" content="([^"]*)"', body)
        title = html.unescape(tm.group(1)).strip() if tm else ""
        desc = html.unescape(dm.group(1)).strip() if dm else ""
        attempts.append({"attempt": attempt+1, "http": http, "og_title": title, "og_desc": desc})
        if http == "200" and title:
            break
        time.sleep(4)  # spaced retry
    time.sleep(0.6)
    return {"code": code, "invite": url, "attempts": attempts}

extracted = json.load(open(f"{WAVE}/team02-extracted.json"))
new = [x for x in extracted if x["status"] == "new"]

done = {}
if os.path.exists(OUT):
    for v in json.load(open(OUT)):
        done[v["code"]] = v

def save():
    json.dump(list(done.values()), open(OUT, "w"), ensure_ascii=False, indent=1)

todo = [x for x in new if x["code"] not in done]
print(f"to verify: {len(todo)} (already done {len(done)})", flush=True)
n = 0
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(check, [x["code"] for x in todo]):
        n += 1
        last = res["attempts"][-1]
        print(f"[{n}/{len(todo)}] {res['code']} http={last['http']} og={last['og_title']!r}", flush=True)
        done[res["code"]] = res
        if n % 8 == 0:
            save()
save()
live = sum(1 for v in done.values() if v["attempts"][-1]["http"]=="200" and v["attempts"][-1]["og_title"])
print(f"DONE verified={len(done)} live={live}")
