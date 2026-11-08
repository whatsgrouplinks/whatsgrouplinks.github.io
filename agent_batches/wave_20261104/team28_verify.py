#!/usr/bin/env python3
"""Team 28: verify candidate codes via og:title (keep-alive session, threaded)."""
import json, re, html, sys
import requests
from concurrent.futures import ThreadPoolExecutor

WORK = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
OG_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
OG_RE2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)

def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    return s

SESSIONS = {}

def og_title(code):
    import threading
    tid = threading.get_ident()
    s = SESSIONS.get(tid)
    if s is None:
        s = make_session()
        SESSIONS[tid] = s
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = s.get(url, timeout=50, allow_redirects=True)
        m = OG_RE.search(r.text) or OG_RE2.search(r.text)
        if m:
            t = html.unescape(m.group(1)).strip()
            return ("ok", t)
        return ("empty", "")
    except Exception as e:
        return ("transport", str(e)[:80])

def main():
    c1 = json.load(open(f"{WORK}/team28-candidates.json"))
    c2 = json.load(open(f"{WORK}/team28-candidates2.json"))
    allc = c1 + c2
    # dedupe within batch
    seen = {}
    for c in allc:
        if c["code"] not in seen:
            seen[c["code"]] = c
    cand = list(seen.values())
    print(f"verifying {len(cand)} candidates")
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for c, (st, title) in zip(cand, ex.map(lambda x: og_title(x["code"]), cand)):
            c["vstatus"], c["og"] = st, title
            results.append(c)
    json.dump(results, open(f"{WORK}/team28-verified-raw.json", "w"), ensure_ascii=False, indent=1)
    ok = sum(1 for c in results if c["vstatus"] == "ok" and c["og"])
    empty = sum(1 for c in results if c["vstatus"] in ("empty", "ok") and not c["og"])
    trans = sum(1 for c in results if c["vstatus"] == "transport")
    print(f"live={ok} dead(empty)={empty} transport={trans}")

main()
