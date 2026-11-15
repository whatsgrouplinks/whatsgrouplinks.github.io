#!/usr/bin/env python3
"""team07 resume: verify pending slice idx 120-141 (banked progress covers 0-119)."""
import json, re, time, html, os, sys
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
PENDING = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/wave_20261112_pending_all.json"
PROGRESS = os.path.join(WAVE, "team07-progress.json")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
SESSION = requests.Session()
SESSION.headers.update(UA)
TITLE_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
TITLE_RE2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)

def og_title(body):
    if not body:
        return ""
    m = TITLE_RE.search(body) or TITLE_RE2.search(body)
    return html.unescape(m.group(1)).strip() if m else ""

def fetch_once(code):
    try:
        r = SESSION.get(f"https://chat.whatsapp.com/{code}", timeout=60)
        if r.status_code == 429:
            return ("ratelimit", "", 429, "HTTP 429")
        t = og_title(r.text or "")
        if not t or t.lower() in ("whatsapp", "whatsapp group invite"):
            return ("empty", t, r.status_code, f"http={r.status_code} empty/generic og:title")
        return ("live", t, r.status_code, f"http={r.status_code}")
    except requests.exceptions.RequestException as e:
        return ("transport", "", 0, f"transport:{type(e).__name__}:{str(e)[:120]}")

def fetch_with_retries(code, attempts=3, delays=(8, 30)):
    last = None
    for i in range(attempts):
        st, title, http, note = fetch_once(code)
        last = (st, title, http, note, i + 1)
        if st == "live" or st in ("ratelimit", "transport"):
            return last
        if i < attempts - 1:
            time.sleep(delays[i] if i < len(delays) else 30)
    return last

def main():
    prog = json.load(open(PROGRESS))
    done_idx = {r["idx"] for r in prog["results"]}
    allp = json.load(open(PENDING))
    todo = []
    for idx in range(120, 142):
        if idx in done_idx:
            continue
        it = allp[idx]
        code = (it.get("invite") or "").rstrip("/").split("/")[-1]
        todo.append((idx, it, code))
    print(f"resume todo={len(todo)}", flush=True)

    def work(item):
        idx, it, code = item
        st, title, http, note, attempts = fetch_with_retries(code)
        return {"idx": idx, "code": code, "invite": f"https://chat.whatsapp.com/{code}",
                "pending_name": it.get("name") or "", "pending_category": it.get("category") or "",
                "pending_country": it.get("country") or "", "pending_description": it.get("description") or "",
                "source_team_file": it.get("_team_file") or "", "prev_reason": it.get("reason") or "",
                "status": st, "og_title": title, "http": http, "note": note, "attempts": attempts}

    results = {r["code"]: r for r in prog["results"]}
    BATCH = 11
    for b in range(0, len(todo), BATCH):
        chunk = todo[b:b + BATCH]
        with ThreadPoolExecutor(max_workers=2) as ex:
            for res in ex.map(work, chunk):
                results[res["code"]] = res
                print(f"[{res['idx']}] {res['code']} {res['status']} {res['og_title'][:60]!r} ({res['note']})", flush=True)
        json.dump({"controls": prog["controls"], "done": len(results), "todo": 142,
                   "dupes_union": prog["dupes_union"], "dupes_within": prog["dupes_within"],
                   "results": sorted(results.values(), key=lambda r: r["idx"])},
                  open(PROGRESS, "w"), indent=1, ensure_ascii=False)
        print(f"--- batch done; banked {len(results)}/142 ---", flush=True)
        if b + BATCH < len(todo):
            time.sleep(6)
    print("RESUME ALL DONE", flush=True)

if __name__ == "__main__":
    main()
