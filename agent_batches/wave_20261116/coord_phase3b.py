#!/usr/bin/env python3
"""Wave 20261116 — PHASE 3b: resume verification with stream reads + auto-throttle.
- Fetches remaining queue codes (stream, read <=48KB, close early).
- 3 workers, 0.5s post-fetch delay; if 429 rate in last 100 > 15%, sleep 180s.
- Then retries ALL pending (429/timeout) codes once.
- Then retries empty-title codes once (pass2).
Checkpoints appended to verify_pass1b.jsonl / verify_retry429.jsonl / verify_pass2.jsonl.
"""
import json, os, re, time, html, threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = "/home/hatch/workspace/whatsapp-groups-site"
OUT = os.path.join(BASE, "agent_batches/wave_20261116")
GENERIC = {"", "whatsapp group invite", "whatsapp", "join group on whatsapp",
           "whatsapp group", "invite", "group invite"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
TITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
TITLE_RE2 = re.compile(r"<meta\s+property='og:title'\s+content='([^']*)'", re.I)

_tls = threading.local()
def sess():
    if not hasattr(_tls, "s"):
        _tls.s = requests.Session()
    return _tls.s

_recent = deque(maxlen=100)
_lock = threading.Lock()

def fetch(code):
    try:
        r = sess().get("https://chat.whatsapp.com/" + code, headers=UA,
                       timeout=30, stream=True)
        if r.status_code == 429:
            r.close()
            res = {"code": code, "status": "pending", "title": "", "err": "HTTP 429"}
        elif r.status_code != 200:
            r.close()
            res = {"code": code, "status": "pending", "title": "",
                   "err": f"HTTP {r.status_code}"}
        else:
            body = b""
            for chunk in r.iter_content(chunk_size=8192):
                body += chunk
                if len(body) >= 49152:
                    break
            r.close()
            m = TITLE_RE.search(body.decode('utf-8', 'ignore')) or \
                TITLE_RE2.search(body.decode('utf-8', 'ignore'))
            title = html.unescape(m.group(1)).strip() if m else ""
            if title and title.lower() not in GENERIC:
                res = {"code": code, "status": "live", "title": title, "err": ""}
            else:
                res = {"code": code, "status": "empty", "title": "", "err": "empty-title"}
    except requests.exceptions.Timeout:
        res = {"code": code, "status": "pending", "title": "", "err": "timeout"}
    except Exception as e:
        res = {"code": code, "status": "pending", "title": "",
               "err": f"{type(e).__name__}:{str(e)[:60]}"}
    with _lock:
        _recent.append(1 if res["status"] == "pending" and res["err"] == "HTTP 429" else 0)
        if len(_recent) >= 100 and sum(_recent) > 15:
            print("THROTTLE: 429 rate high, sleeping 180s", flush=True)
            _recent.clear()
            time.sleep(180)
    time.sleep(0.5)
    return res

def run_batch(codes, outpath, label, workers=3):
    done = 0
    counts = {"live": 0, "empty": 0, "pending": 0}
    already = set()
    if os.path.exists(outpath):
        for line in open(outpath, encoding='utf-8'):
            try:
                already.add(json.loads(line)["code"])
            except Exception:
                pass
    todo = [c for c in codes if c not in already]
    print(f"{label}: {len(todo)} to fetch ({len(already)} already done)", flush=True)
    with open(outpath, "a", encoding='utf-8') as fh:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for res in ex.map(fetch, todo):
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
                fh.flush()
                counts[res["status"]] = counts.get(res["status"], 0) + 1
                done += 1
                if done % 500 == 0:
                    print(f"{label}: {done}/{len(todo)} {counts}", flush=True)
    print(f"{label} DONE: {counts}", flush=True)
    return counts

def load_results(*paths):
    out = {}
    for p in paths:
        if os.path.exists(p):
            for line in open(p, encoding='utf-8'):
                try:
                    r = json.loads(line)
                    out[r["code"]] = r
                except Exception:
                    pass
    return out

def main():
    queue = json.load(open(os.path.join(OUT, "verify_queue.json"), encoding='utf-8'))
    qcodes = [q["code"] for q in queue]
    p1 = os.path.join(OUT, "verify_pass1.jsonl")
    p1b = os.path.join(OUT, "verify_pass1b.jsonl")
    # 1. remaining pass1
    seen = set(load_results(p1).keys())
    remaining = [c for c in qcodes if c not in seen]
    if remaining:
        run_batch(remaining, p1b, "pass1b", workers=5)
    # 2. retry all pendings once
    allres = load_results(p1, p1b)
    pendings = [c for c, r in allres.items() if r["status"] == "pending"]
    print("pendings to retry:", len(pendings), flush=True)
    if pendings:
        time.sleep(60)
        run_batch(pendings, os.path.join(OUT, "verify_retry429.jsonl"), "retry429", workers=12)
    # 3. retry empties once
    allres = load_results(p1, p1b, os.path.join(OUT, "verify_retry429.jsonl"))
    empties = [c for c, r in allres.items() if r["status"] == "empty"]
    print("empties to retry (pass2):", len(empties), flush=True)
    if empties:
        time.sleep(60)
        run_batch(empties, os.path.join(OUT, "verify_pass2.jsonl"), "pass2", workers=20)
    print("PHASE 3b ALL DONE", flush=True)

if __name__ == "__main__":
    main()
