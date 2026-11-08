#!/usr/bin/env python3
"""Team07 Part B: re-verify team29 Nov-3 pending items (121) with keep-alive session."""
import json, re, html, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
OG_RE = re.compile(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', re.I | re.S)
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')

_tls = threading.local()
def sess():
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA})
        _tls.s = s
    return s

def verify(url):
    try:
        r = sess().get(url, timeout=60, allow_redirects=True)
        if r.status_code == 429:
            return ("rate-limited", None, r.status_code)
        m = OG_RE.search(r.text)
        title = html.unescape(m.group(1)).strip() if m else ""
        if title:
            return ("live", title, r.status_code)
        return ("dead", None, r.status_code)
    except requests.exceptions.Timeout:
        return ("transport", "timeout", None)
    except requests.exceptions.ConnectionError as e:
        return ("transport", "conn-error", None)
    except Exception as e:
        return ("transport", type(e).__name__, None)

def main():
    pend = json.load(open(f"{PREV}/team29-unverified-pending.json"))
    union = set(json.load(open(f"{WAVE}/dedupe_union.json")))
    seen = set()
    todo = []
    for it in pend:
        code = it["invite"].rstrip("/").split("/")[-1]
        if not re.fullmatch(r"[A-Za-z0-9]{20,24}", code):
            continue
        if code in union or code in seen:
            continue
        seen.add(code)
        todo.append(it)
    print(f"items: {len(pend)}, to-verify: {len(todo)}", flush=True)

    results = {}
    stop = False
    with ThreadPoolExecutor(max_workers=25) as ex:
        futs = {ex.submit(verify, it["invite"]): it for it in todo}
        for f in as_completed(futs):
            it = futs[f]
            results[it["invite"]] = f.result()

    verified, pending, dead, ratehit = [], [], 0, False
    for it in todo:
        status, detail, sc = results[it["invite"]]
        code = it["invite"].rstrip("/").split("/")[-1]
        if status == "live":
            v = {k: it[k] for k in ("name", "category", "country", "description", "invite", "image")}
            v["name"] = detail
            verified.append(v)
        elif status == "dead":
            dead += 1
        elif status == "rate-limited":
            ratehit = True
            p = {k: it[k] for k in ("name", "category", "country", "description", "invite", "image")}
            p["note"] = "rate-limited on retry 2026-11-04 — retry next wave"
            pending.append(p)
        else:
            p = {k: it[k] for k in ("name", "category", "country", "description", "invite", "image")}
            p["note"] = f"transport failure on retry 2026-11-04 ({detail})"
            pending.append(p)

    json.dump(verified, open(f"{WAVE}/team07-thewhatspgrouplink.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(f"{WAVE}/team07-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps({"verified": len(verified), "pending": len(pending),
                      "dead": dead, "ratehit": ratehit}))
if __name__ == "__main__":
    main()
