#!/usr/bin/env python3
"""Team07 phase 4: slow-verify chat.whatsapp.com codes with curl (max 3 parallel)."""
import json, re, os, subprocess, time, sys
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUT = os.path.join(WAVE, "team07_verify.jsonl")

recs = json.load(open(os.path.join(WAVE, "team07_screened.json")))
done = {}
if os.path.exists(OUT):
    for line in open(OUT, encoding="utf-8"):
        try:
            r = json.loads(line)
            done[r["code"]] = r
        except Exception:
            pass
todo = [r for r in recs if r["code"] not in done]
print(f"total {len(recs)} already done {len(done)} todo {len(todo)}", flush=True)

def parse_title(body):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', body)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body)
    t = m.group(1) if m else ""
    return t.strip()

def parse_desc(body):
    m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)', body)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:description["\']', body)
    return (m.group(1).strip() if m else "")

def check(rec, attempt=1):
    code = rec["code"]
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "25", "-A", UA,
                            "-o", "-", "-w", "\n%{http_code}", url],
                           capture_output=True, text=True, timeout=35)
        out = r.stdout
        lines = out.rsplit("\n", 1)
        http = lines[-1].strip() if len(lines) > 1 else "000"
        body = lines[0] if len(lines) > 1 else out
        title = parse_title(body)
        desc = parse_desc(body)
        return {"code": code, "http": http, "og_title": title, "og_desc": desc,
                "attempt": attempt, "transport_error": False}
    except Exception as e:
        return {"code": code, "http": "000", "og_title": "", "og_desc": "",
                "attempt": attempt, "transport_error": True, "err": str(e)[:100]}

def worker(rec):
    res = check(rec)
    time.sleep(0.6)
    return res

results = []
with ThreadPoolExecutor(max_workers=3) as ex:
    for i, res in enumerate(ex.map(worker, todo)):
        results.append(res)
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(res, ensure_ascii=False) + "\n")
        if (i + 1) % 100 == 0:
            print(f"checked {i+1}/{len(todo)}", flush=True)

live = [r for r in results if r["http"] == "200" and r["og_title"]]
amb = [r for r in results if r["http"] == "200" and not r["og_title"]]
dead = [r for r in results if r["http"] not in ("200", "000")]
pend = [r for r in results if r["http"] == "000"]
print(f"pass1: live={len(live)} ambiguous={len(amb)} dead={len(dead)} transport-fail={len(pend)}", flush=True)
json.dump({"live": len(live), "ambiguous": len(amb), "dead": len(dead), "transport_fail": len(pend)},
          open(os.path.join(WAVE, "team07_verify_pass1.json"), "w"))
