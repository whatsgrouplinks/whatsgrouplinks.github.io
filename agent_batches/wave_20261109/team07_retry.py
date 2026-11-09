#!/usr/bin/env python3
"""Team07 phase 4b: ONE retry round over ambiguous codes (200 + empty og:title).
Writes team07_verify_retry.jsonl. Spaced apart from pass 1; same slow checker."""
import json, re, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUT = os.path.join(WAVE, "team07_verify_retry.jsonl")

verify = {}
for line in open(os.path.join(WAVE, "team07_verify.jsonl"), encoding="utf-8"):
    try:
        v = json.loads(line)
        verify[v["code"]] = v
    except Exception:
        pass
amb = [c for c, v in verify.items() if v.get("http") == "200" and not v.get("og_title")]
done = set()
if os.path.exists(OUT):
    for line in open(OUT, encoding="utf-8"):
        try:
            done.add(json.loads(line)["code"])
        except Exception:
            pass
todo = [c for c in amb if c not in done]
print(f"ambiguous={len(amb)} already-retried={len(done)} todo={len(todo)}", flush=True)

def parse(body, prop):
    m = re.search(r'<meta[^>]+property=["\']' + prop + r'["\'][^>]+content=["\']([^"\']*)', body)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']' + prop + r'["\']', body)
    return m.group(1).strip() if m else ""

def check(code):
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "25", "-A", UA,
                            "-o", "-", "-w", "\n%{http_code}", f"https://chat.whatsapp.com/{code}"],
                           capture_output=True, text=True, timeout=35)
        lines = r.stdout.rsplit("\n", 1)
        http = lines[-1].strip() if len(lines) > 1 else "000"
        body = lines[0] if len(lines) > 1 else r.stdout
        return {"code": code, "http": http, "og_title": parse(body, "og:title"),
                "og_desc": parse(body, "og:description"), "attempt": 2, "transport_error": False}
    except Exception as e:
        return {"code": code, "http": "000", "og_title": "", "og_desc": "",
                "attempt": 2, "transport_error": True, "err": str(e)[:100]}

def worker(code):
    res = check(code)
    time.sleep(0.6)
    return res

n = 0
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(worker, todo):
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(res, ensure_ascii=False) + "\n")
        n += 1
        if n % 100 == 0:
            print(f"retried {n}/{len(todo)}", flush=True)
recov = sum(1 for line in open(OUT, encoding="utf-8") if json.loads(line).get("og_title"))
print(f"retry done: {n} checked, {recov} recovered a title", flush=True)
