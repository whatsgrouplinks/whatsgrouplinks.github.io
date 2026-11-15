#!/usr/bin/env python3
"""team07 wave_20261114: re-verify pending slice 0-141 with spaced, low concurrency."""
import json, re, time, html, os, sys
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
PENDING = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/wave_20261112_pending_all.json"
UNION = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
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
    if not m:
        return ""
    t = html.unescape(m.group(1)).strip()
    return t

def fetch_once(code):
    """Returns (status, ogtitle, http_code, note). status in live/empty/ratelimit/transport."""
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = SESSION.get(url, timeout=60)
        if r.status_code == 429:
            return ("ratelimit", "", 429, "HTTP 429")
        body = r.text or ""
        t = og_title(body)
        if not t or t.lower() in ("whatsapp", "whatsapp group invite"):
            return ("empty", t, r.status_code, f"http={r.status_code} empty/generic og:title")
        return ("live", t, r.status_code, f"http={r.status_code}")
    except requests.exceptions.RequestException as e:
        return ("transport", "", 0, f"transport:{type(e).__name__}:{str(e)[:120]}")

def fetch_with_retries(code, attempts=3, delays=(8, 30)):
    """Empty -> spaced retry. 429/transport -> return immediately as pending-type."""
    last = None
    for i in range(attempts):
        st, title, http, note = fetch_once(code)
        last = (st, title, http, note, i + 1)
        if st == "live":
            return last
        if st in ("ratelimit", "transport"):
            return last
        # empty: retry after delay unless last attempt
        if i < attempts - 1:
            time.sleep(delays[i] if i < len(delays) else 30)
    return last

def main():
    allp = json.load(open(PENDING))
    assert len(allp) == 285, len(allp)
    slice_items = allp[0:142]
    union = set(json.load(open(UNION)))
    print(f"slice={len(slice_items)} union={len(union)}", flush=True)

    # ---- CONTROLS ----
    st, title, http, note, n = fetch_with_retries("KrDwdK8EIkB6vgauHg5M7N", attempts=2, delays=(5,))
    ctrl_live = (st == "live" and title == "JAY - PHP & Python Full Stack Developer")
    print(f"CONTROL live: status={st} title={title!r} http={http} PASS={ctrl_live}", flush=True)
    st2, title2, http2, note2, n2 = fetch_with_retries("ZzZzZzZzZzZzZzZzZzZzZzZz", attempts=2, delays=(5,))
    ctrl_fake = (st2 == "empty" and title2 == "")
    print(f"CONTROL fabricated: status={st2} title={title2!r} http={http2} PASS={ctrl_fake}", flush=True)
    controls = {"live_control": {"code": "KrDwdK8EIkB6vgauHg5M7N", "status": st, "og_title": title, "http": http,
                                  "expected": "JAY - PHP & Python Full Stack Developer", "pass": ctrl_live},
                "fabricated_control": {"code": "ZzZzZzZzZzZzZzZzZzZzZzZz", "status": st2, "og_title": title2,
                                       "http": http2, "expected_empty": True, "pass": ctrl_fake}}
    if not (ctrl_live and ctrl_fake):
        json.dump({"controls": controls, "fatal": "controls failed, stopped"}, open(os.path.join(WAVE, "team07-controls.json"), "w"), indent=1, ensure_ascii=False)
        print("CONTROLS FAILED - STOPPING", flush=True)
        sys.exit(2)
    json.dump({"controls": controls}, open(os.path.join(WAVE, "team07-controls.json"), "w"), indent=1, ensure_ascii=False)

    # ---- SLICE PREP: dedupe vs union + within team ----
    results = {}
    dupes_union, dupes_within = [], []
    seen = set()
    todo = []
    for idx, it in enumerate(slice_items):
        code = (it.get("invite") or "").rstrip("/").split("/")[-1]
        if not code:
            continue
        if code in union:
            dupes_union.append({"idx": idx, "code": code, "name": it.get("name")})
            continue
        if code in seen:
            dupes_within.append({"idx": idx, "code": code, "name": it.get("name")})
            continue
        seen.add(code)
        todo.append((idx, it, code))
    print(f"todo={len(todo)} dupes_union={len(dupes_union)} dupes_within={len(dupes_within)}", flush=True)

    def work(item):
        idx, it, code = item
        st, title, http, note, attempts = fetch_with_retries(code)
        return {"idx": idx, "code": code, "invite": f"https://chat.whatsapp.com/{code}",
                "pending_name": it.get("name") or "", "pending_category": it.get("category") or "",
                "pending_country": it.get("country") or "", "pending_description": it.get("description") or "",
                "source_team_file": it.get("_team_file") or "", "prev_reason": it.get("reason") or "",
                "status": st, "og_title": title, "http": http, "note": note, "attempts": attempts}

    # batches of 12, max 2 workers, pause between batches
    BATCH = 12
    for b in range(0, len(todo), BATCH):
        chunk = todo[b:b + BATCH]
        with ThreadPoolExecutor(max_workers=2) as ex:
            for res in ex.map(work, chunk):
                results[res["code"]] = res
                print(f"[{res['idx']}] {res['code']} {res['status']} {res['og_title'][:60]!r} ({res['note']})", flush=True)
        # bank partial progress
        json.dump({"controls": controls, "done": len(results), "todo": len(todo),
                   "dupes_union": dupes_union, "dupes_within": dupes_within,
                   "results": list(results.values())},
                  open(PROGRESS, "w"), indent=1, ensure_ascii=False)
        print(f"--- batch done {b + len(chunk)}/{len(todo)}; banked progress ---", flush=True)
        if b + BATCH < len(todo):
            time.sleep(6)

    json.dump({"controls": controls, "done": len(results), "todo": len(todo),
               "dupes_union": dupes_union, "dupes_within": dupes_within,
               "results": list(results.values())},
              open(PROGRESS, "w"), indent=1, ensure_ascii=False)
    print("ALL DONE", flush=True)

if __name__ == "__main__":
    main()
