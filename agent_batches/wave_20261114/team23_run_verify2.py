#!/usr/bin/env python3
"""Verify team23 groupssor-SA + groupsorin fresh codes (one session, shorter spaced retries)."""
import json, sys, time, requests, re, html
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114")
from team23_verify import og_title

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

def verify_fast(sess, code):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(3):
        try:
            r = sess.get(url, headers=UA, timeout=60, allow_redirects=True)
            if r.status_code == 429:
                return ("pending", "", "HTTP 429")
            if r.status_code != 200:
                time.sleep(2); continue
            t = og_title(r.text)
            if t:
                return ("live", html.unescape(t), "")
            time.sleep(2 + attempt * 2)
        except requests.RequestException as e:
            time.sleep(2 + attempt * 2)
            last = str(e)
    return ("dead", "", "empty og:title after 3 attempts")

def main():
    todo = {}
    gs = json.load(open(f"{WD}/team23_groupssor_sa.json"))
    for c, d in gs.items():
        todo[c] = {"dir_name": d.get("name"), "api_category": d.get("category"),
                   "country": d.get("country"), "page": "https://www.groupssor.com/", "site": "groupssor.com"}
    try:
        gi = json.load(open(f"{WD}/team23_groupsorin_fresh.json"))
        for c, d in gi.items():
            if c not in todo:
                todo[c] = {"dir_name": d.get("name"), "api_category": d.get("category_dir"),
                           "country": "", "page": d.get("page"), "site": "groupsor.in"}
    except FileNotFoundError:
        print("groupsorin fresh not ready; groupssor only")
    print("to verify:", len(todo))
    sess = requests.Session()
    results = {}
    try:
        results = json.load(open(f"{WD}/team23_verify2_results.json"))
    except Exception:
        pass
    for i, code in enumerate(todo):
        if code in results:
            continue
        st, title, err = verify_fast(sess, code)
        results[code] = {"status": st, "og_title": title, "err": err, **todo[code]}
        print(f"{i+1}/{len(todo)} {code} {st} | {title!r}", flush=True)
        json.dump(results, open(f"{WD}/team23_verify2_results.json", "w"), ensure_ascii=False, indent=1)
        time.sleep(0.5)
    print("done")

if __name__ == "__main__":
    main()
