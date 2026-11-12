#!/usr/bin/env python3
"""TEAM25 wave_20261112: re-verify team20's 15 pending wglfinder codes.
Controls first; keep-alive Session; spaced requests; 1 retry per code.
Transport failures -> PENDING. LIVE = non-empty og:title (og:description fallback).
"""
import json, re, time, sys, random
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
PEND_IN = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/team20-wglfinder-pending.json"
CKPT = WAVE + "team25-progress.jsonl"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                  "Accept": "text/html,application/xhtml+xml"})

TITLE_RE = re.compile(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']*)["\']', re.I)
TITLE_RE2 = re.compile(r'<meta\s+content=["\']([^"\']*)["\']\s+property=["\']og:title["\']', re.I)
DESC_RE = re.compile(r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']*)["\']', re.I)

def og(html):
    m = TITLE_RE.search(html) or TITLE_RE2.search(html)
    t = m.group(1).strip() if m else ""
    if t:
        return t, "title"
    m = DESC_RE.search(html)
    d = m.group(1).strip() if m else ""
    return d, "description" if d else ""

def check(code):
    """Returns (status, title, detail). status in live/dead/transport."""
    url = "https://chat.whatsapp.com/" + code
    try:
        r = S.get(url, timeout=75)
        html = r.text or ""
        t, src = og(html)
        if t:
            return "live", t, f"HTTP {r.status_code} og:{src}"
        return "dead", "", f"HTTP {r.status_code} empty og"
    except requests.exceptions.Timeout:
        return "transport", "", "read/connect timeout"
    except requests.exceptions.RequestException as e:
        return "transport", "", f"{type(e).__name__}: {str(e)[:120]}"

def log(rec):
    with open(CKPT, "a") as f:
        f.write(json.dumps(rec) + "\n")

def main():
    pend = json.load(open(PEND_IN))
    results = {}
    # --- CONTROLS ---
    print("CONTROL live KrDwdK8EIkB6vgauHg5M7N ...", flush=True)
    st, t, d = check("KrDwdK8EIkB6vgauHg5M7N")
    print(f"  -> {st} | {t[:80]} | {d}", flush=True)
    log({"phase": "control-live", "code": "KrDwdK8EIkB6vgauHg5M7N", "status": st, "title": t, "detail": d})
    time.sleep(20)
    print("CONTROL fabricated ZZZZZZZZZZZZZZZZZZZZZZ ...", flush=True)
    st, t, d = check("ZZZZZZZZZZZZZZZZZZZZZZ")
    print(f"  -> {st} | {t[:80]} | {d}", flush=True)
    log({"phase": "control-fake", "code": "ZZZZZZZZZZZZZZZZZZZZZZ", "status": st, "title": t, "detail": d})
    time.sleep(20)

    # --- PASS 1 over 15 pending, 20s spacing ---
    for i, p in enumerate(pend):
        code = p["invite"].rstrip("/").split("/")[-1]
        print(f"[{i+1}/15] {code} {p['name'][:40]} ...", flush=True)
        st, t, d = check(code)
        print(f"  -> {st} | {t[:80]} | {d}", flush=True)
        results[code] = {"item": p, "pass1": {"status": st, "title": t, "detail": d}}
        log({"phase": "pass1", "code": code, "status": st, "title": t, "detail": d})
        if i < len(pend) - 1:
            time.sleep(20)

    # --- cool-down, then PASS 2 (one retry) for non-live ---
    todo = [c for c, r in results.items() if r["pass1"]["status"] != "live"]
    print(f"Pass 1 done: live={15-len(todo)} pending-retry={len(todo)}. Cooling 180s...", flush=True)
    time.sleep(180)
    for i, code in enumerate(todo):
        p = results[code]["item"]
        print(f"[retry {i+1}/{len(todo)}] {code} {p['name'][:40]} ...", flush=True)
        st, t, d = check(code)
        print(f"  -> {st} | {t[:80]} | {d}", flush=True)
        results[code]["pass2"] = {"status": st, "title": t, "detail": d}
        log({"phase": "pass2", "code": code, "status": st, "title": t, "detail": d})
        if i < len(todo) - 1:
            time.sleep(25)

    json.dump(results, open(WAVE + "team25-verify-results.json", "w"), indent=2, ensure_ascii=False)
    live = [c for c, r in results.items() if any(a["status"] == "live" for a in (r.get("pass1"), r.get("pass2")) if a)]
    dead = [c for c, r in results.items() if r["pass1"]["status"] == "dead" and r.get("pass2", {}).get("status") == "dead"]
    print(f"SUMMARY live={len(live)} clean-dead={len(dead)} still-pending={15-len(live)-len(dead)}", flush=True)
    print("LIVE:", live, flush=True)

if __name__ == "__main__":
    main()
