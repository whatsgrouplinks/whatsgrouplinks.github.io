#!/usr/bin/env python3
"""Wave 20261116 — PHASE 3: verify the queue myself via chat.whatsapp.com og:title.
Pass 1 over all queue codes (8 workers, 30s timeout), checkpointed.
Pass 2 retries empty-title codes once after a delay (5 workers).
429 / transport errors -> pending.
"""
import json, os, re, time, html, threading
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
TITLE_RE3 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:title"', re.I)

_tls = threading.local()
def session():
    if not hasattr(_tls, "s"):
        _tls.s = requests.Session()
    return _tls.s

def fetch(code):
    url = "https://chat.whatsapp.com/" + code
    try:
        r = session().get(url, headers=UA, timeout=30)
        if r.status_code == 429:
            return {"code": code, "status": "pending", "title": "", "err": "HTTP 429"}
        if r.status_code != 200:
            return {"code": code, "status": "pending", "title": "",
                    "err": f"HTTP {r.status_code}"}
        body = r.text[:65536]
        m = TITLE_RE.search(body) or TITLE_RE2.search(body) or TITLE_RE3.search(body)
        title = html.unescape(m.group(1)).strip() if m else ""
        if title and title.lower() not in GENERIC:
            return {"code": code, "status": "live", "title": title, "err": ""}
        return {"code": code, "status": "empty", "title": "", "err": "empty-title"}
    except requests.exceptions.Timeout:
        return {"code": code, "status": "pending", "title": "", "err": "timeout"}
    except Exception as e:
        return {"code": code, "status": "pending", "title": "",
                "err": f"{type(e).__name__}: {str(e)[:80]}"}

def run_pass(codes, workers, outpath, label):
    done = 0
    counts = {"live": 0, "empty": 0, "pending": 0}
    with open(outpath, "a", encoding='utf-8') as fh:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for res in ex.map(fetch, codes):
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
                fh.flush()
                counts[res["status"]] = counts.get(res["status"], 0) + 1
                done += 1
                if done % 500 == 0:
                    print(f"{label}: {done}/{len(codes)} {counts}", flush=True)
    print(f"{label} DONE: {counts}", flush=True)
    return counts

def main():
    queue = json.load(open(os.path.join(OUT, "verify_queue.json"), encoding='utf-8'))
    codes = [q["code"] for q in queue]
    print("queue size:", len(codes), flush=True)
    # controls first
    print("controls:", fetch("KrDwdK8EIkB6vgauHg5M7N"), fetch("ZzZzZzZzZzZzZzZzZzZzZzZz"), flush=True)
    # resume support: skip codes already in pass1 file
    p1 = os.path.join(OUT, "verify_pass1.jsonl")
    seen = set()
    if os.path.exists(p1):
        for line in open(p1, encoding='utf-8'):
            try:
                seen.add(json.loads(line)["code"])
            except Exception:
                pass
    todo = [c for c in codes if c not in seen]
    print("pass1 todo:", len(todo), "already done:", len(seen), flush=True)
    if todo:
        run_pass(todo, 8, p1, "pass1")
    # pass 2: retry empties once after a delay
    empties, pendings = [], []
    for line in open(p1, encoding='utf-8'):
        r = json.loads(line)
        if r["status"] == "empty":
            empties.append(r["code"])
        elif r["status"] == "pending":
            pendings.append(r["code"])
    print("pass1 empties:", len(empties), "pendings:", len(pendings), flush=True)
    p2 = os.path.join(OUT, "verify_pass2.jsonl")
    seen2 = set()
    if os.path.exists(p2):
        for line in open(p2, encoding='utf-8'):
            try:
                seen2.add(json.loads(line)["code"])
            except Exception:
                pass
    retry = [c for c in empties if c not in seen2]
    print("pass2 retrying:", len(retry), "after 60s delay", flush=True)
    if retry:
        time.sleep(60)
        run_pass(retry, 5, p2, "pass2")
    print("ALL DONE", flush=True)

if __name__ == "__main__":
    main()
