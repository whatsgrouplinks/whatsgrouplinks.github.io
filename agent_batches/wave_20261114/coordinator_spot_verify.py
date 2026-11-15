#!/usr/bin/env python3
"""Coordinator spot-verification for wave 20261114 Part A.
Fetches live og:title for a list of codes with a keep-alive session.
LIVE = non-empty, non-generic og:title. Retries empty titles 2x spaced.
Writes wave_20261114/coordinator_spot_verify.json
"""
import json, re, time, sys
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

import requests

def fetch_title(session, code, tries=3):
    url = f"https://chat.whatsapp.com/{code}"
    last = {"http": None, "title": "", "err": ""}
    for attempt in range(tries):
        try:
            r = session.get(url, headers=UA, timeout=90)
            last["http"] = r.status_code
            m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
            if not m:
                m = re.search(r"<meta\s+property='og:title'\s+content='([^']*)'", r.text)
            title = m.group(1) if m else ""
            title = title.replace("&amp;", "&").strip()
            last["title"] = title
            if title:
                return last
            last["err"] = "empty og:title"
        except Exception as e:
            last["err"] = f"{type(e).__name__}: {str(e)[:120]}"
        if attempt < tries - 1:
            time.sleep(15)
    return last

def check(args):
    code, label = args
    s = requests.Session()
    try:
        res = fetch_title(s, code)
    finally:
        s.close()
    res["code"] = code
    res["label"] = label
    res["verdict"] = "LIVE" if res["title"] else ("PENDING" if res["http"] in (429, None) and res["err"] and "empty" not in res["err"] else "DEAD")
    return res

def main():
    targets = json.load(open(f"{WAVE}/coordinator_spot_targets.json"))
    items = [(t["code"], t["label"]) for t in targets]
    print(f"spot-checking {len(items)} codes ...", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        for res in ex.map(check, items):
            results.append(res)
            print(f"{res['code']} [{res['label']}] http={res['http']} verdict={res['verdict']} title={res['title']!r} err={res['err']}", flush=True)
    json.dump(results, open(f"{WAVE}/coordinator_spot_verify.json", "w"), indent=1, ensure_ascii=False)
    live = sum(1 for r in results if r["verdict"] == "LIVE")
    print(f"DONE live={live} dead={sum(1 for r in results if r['verdict']=='DEAD')} pending={sum(1 for r in results if r['verdict']=='PENDING')}")

if __name__ == "__main__":
    main()
