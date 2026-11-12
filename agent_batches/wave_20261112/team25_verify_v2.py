#!/usr/bin/env python3
"""TEAM25 v2 wave_20261112: re-verify team20's 15 pending wglfinder codes.
CORRECTED RULE (proven by controls 2026-11-12): WhatsApp now serves
og:description="WhatsApp Group Invite" on EVERY invite page (live AND dead).
LIVE = non-empty og:title only. DEAD = HTTP 200 + empty og:title (+ default
static.whatsapp.net og:image). og:description is NEVER a live signal.
Controls: live control must show a real og:title; fabricated must show EMPTY og:title.
"""
import json, re, time, html
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
IMG_RE = re.compile(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']*)["\']', re.I)

def check(code):
    url = "https://chat.whatsapp.com/" + code
    try:
        r = S.get(url, timeout=75)
        h = r.text or ""
        m = TITLE_RE.search(h)
        title = html.unescape(m.group(1)).strip() if m else ""
        im = IMG_RE.search(h)
        img = html.unescape(im.group(1))[:80] if im else ""
        default_img = "static.whatsapp.net" in img
        if title:
            return "live", title, f"HTTP {r.status_code} og:title img={'default' if default_img else 'group-photo'}"
        return "dead", "", f"HTTP {r.status_code} EMPTY og:title img={'default' if default_img else 'group-photo'}"
    except requests.exceptions.Timeout:
        return "transport", "", "read/connect timeout"
    except requests.exceptions.RequestException as e:
        return "transport", "", f"{type(e).__name__}: {str(e)[:120]}"

def log(rec):
    with open(CKPT, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def main():
    pend = json.load(open(PEND_IN))
    results = {}
    print("CONTROL live KrDwdK8EIkB6vgauHg5M7N ...", flush=True)
    st, t, d = check("KrDwdK8EIkB6vgauHg5M7N")
    print(f"  -> {st} | {t[:80]} | {d}", flush=True)
    log({"phase": "control-live-v2", "code": "KrDwdK8EIkB6vgauHg5M7N", "status": st, "title": t, "detail": d})
    assert st == "live", "live control FAILED"
    time.sleep(20)
    print("CONTROL fabricated ZZZZZZZZZZZZZZZZZZZZZZ ...", flush=True)
    st, t, d = check("ZZZZZZZZZZZZZZZZZZZZZZ")
    print(f"  -> {st} | {t[:80]} | {d}", flush=True)
    log({"phase": "control-fake-v2", "code": "ZZZZZZZZZZZZZZZZZZZZZZ", "status": st, "title": t, "detail": d})
    assert st == "dead", "fake control FAILED - expected empty og:title"
    print("CONTROLS PASS: live=real title, fake=empty title. og:description ignored.", flush=True)
    time.sleep(20)

    for i, p in enumerate(pend):
        code = p["invite"].rstrip("/").split("/")[-1]
        print(f"[{i+1}/15] {code} {p['name'][:40]} ...", flush=True)
        st, t, d = check(code)
        print(f"  -> {st} | {t[:80]} | {d}", flush=True)
        results[code] = {"item": p, "pass1": {"status": st, "title": t, "detail": d}}
        log({"phase": "pass1-v2", "code": code, "status": st, "title": t, "detail": d})
        if i < len(pend) - 1:
            time.sleep(20)

    todo = [c for c, r in results.items() if r["pass1"]["status"] != "live"]
    print(f"Pass 1 done: live={15-len(todo)} non-live={len(todo)}. Cooling 180s...", flush=True)
    time.sleep(180)
    for i, code in enumerate(todo):
        p = results[code]["item"]
        print(f"[retry {i+1}/{len(todo)}] {code} {p['name'][:40]} ...", flush=True)
        st, t, d = check(code)
        print(f"  -> {st} | {t[:80]} | {d}", flush=True)
        results[code]["pass2"] = {"status": st, "title": t, "detail": d}
        log({"phase": "pass2-v2", "code": code, "status": st, "title": t, "detail": d})
        if i < len(todo) - 1:
            time.sleep(25)

    json.dump(results, open(WAVE + "team25-verify-results.json", "w"), indent=2, ensure_ascii=False)
    live = [c for c, r in results.items()
            if r["pass1"]["status"] == "live" or r.get("pass2", {}).get("status") == "live"]
    dead = [c for c, r in results.items()
            if r["pass1"]["status"] == "dead" and r.get("pass2", {}).get("status") == "dead"]
    transp = [c for c, r in results.items() if c not in live and c not in dead]
    print(f"SUMMARY live={len(live)} clean-dead(2 empties)={len(dead)} still-pending={len(transp)}", flush=True)
    print("LIVE:", live, flush=True)
    print("DEAD:", dead, flush=True)
    print("PENDING:", transp, flush=True)

if __name__ == "__main__":
    main()
