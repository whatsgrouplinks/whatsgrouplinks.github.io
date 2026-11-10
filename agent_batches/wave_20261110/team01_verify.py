#!/usr/bin/env python3
"""Team 01 wave 20261110 slice 1 - verify fresh codes (3 parallel, >=0.55s start spacing, 15s timeout)."""
import json, os, re, subprocess, time, html as htmlmod, threading
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site"
WAVE = os.path.join(BASE, "agent_batches/wave_20261110")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

fresh = json.load(open(os.path.join(WAVE, "team01_fresh_codes.json")))
ctx = json.load(open(os.path.join(WAVE, "team01_context.json")))

# --- prefix-collapse: drop truncated variants (RSC payload truncates inviteUrls) ---
codes = sorted(fresh.keys())
keep = []
dropped = []
for c in codes:
    if any(o != c and o.startswith(c) for o in codes):
        dropped.append((c, "prefix-of-longer-extracted-code"))
        continue
    keep.append(c)
# E51z* has no 22-char form anywhere in raw files -> truncated artifact, drop
for c in list(keep):
    if c.startswith("E51zHCiU0i"):
        dropped.append((c, "truncated-code-no-full-form-in-any-raw-file"))
        keep.remove(c)
print("verify set:", len(keep), "dropped artifacts:", dropped, flush=True)
json.dump({"kept": keep, "dropped_artifacts": dropped},
          open(os.path.join(WAVE, "team01_verify_set.json"), "w"), indent=1)

lock = threading.Lock()
last_start = [0.0]

def check_once(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "15",
                            "-o", "-", "-w", "\n%{http_code}", url],
                           capture_output=True, text=True, timeout=25)
        out = r.stdout
        http = out.rsplit("\n", 1)[-1].strip()
        body = out[:out.rfind("\n")]
        if not http.isdigit():
            return {"http": None, "title": "", "desc": "", "transport": True}
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', body)
        if not m:
            m = re.search(r'<meta\s+content="([^"]*)"\s+property="og:title"', body)
        title = htmlmod.unescape(m.group(1)).strip() if m else ""
        md = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', body)
        if not md:
            md = re.search(r'<meta\s+content="([^"]*)"\s+property="og:description"', body)
        desc = htmlmod.unescape(md.group(1)).strip() if md else ""
        return {"http": http, "title": title, "desc": desc, "transport": False}
    except Exception as e:
        return {"http": None, "title": "", "desc": "", "transport": True, "error": str(e)}

def check(code):
    # spaced-start rate limit
    with lock:
        now = time.time()
        wait = 0.55 - (now - last_start[0])
        if wait > 0:
            time.sleep(wait)
        last_start[0] = time.time()
    first = check_once(code)
    if first["transport"]:
        # one spaced retry for transport failures
        time.sleep(3)
        second = check_once(code)
        if second["transport"]:
            return {"code": code, "status": "pending", "reason": "transport-fail-no-http-status",
                    "error": second.get("error", ""), "attempts": 2}
        first = second
    if first["http"] == "200" and first["title"]:
        return {"code": code, "status": "live", "http": 200, "title": first["title"],
                "description": first["desc"], "attempts": 1}
    if first["http"] == "200" and not first["title"]:
        time.sleep(5)
        second = check_once(code)
        if second.get("transport"):
            return {"code": code, "status": "pending", "reason": "transport-fail-on-retry", "attempts": 2}
        if second["http"] == "200" and second["title"]:
            return {"code": code, "status": "live", "http": 200, "title": second["title"],
                    "description": second["desc"], "attempts": 2}
        return {"code": code, "status": "dead", "http": "200-empty-title",
                "title": "", "description": "", "attempts": 2}
    if first["http"] in ("429", "500", "502", "503"):
        time.sleep(8)
        second = check_once(code)
        if second.get("transport"):
            return {"code": code, "status": "pending", "reason": "transport-fail-on-retry", "attempts": 2}
        if second["http"] == "200" and second["title"]:
            return {"code": code, "status": "live", "http": 200, "title": second["title"],
                    "description": second["desc"], "attempts": 2}
        return {"code": code, "status": "dead", "http": second["http"] or first["http"],
                "title": second.get("title", ""), "description": second.get("desc", ""), "attempts": 2}
    return {"code": code, "status": "dead", "http": first["http"],
            "title": first.get("title", ""), "description": first.get("desc", ""), "attempts": 1}

results = []
t0 = time.time()
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(check, keep):
        res["listing_url"] = fresh.get(res["code"], "")
        res["ctx"] = ctx.get(res["code"], {})
        results.append(res)
        print(f"{len(results)}/{len(keep)} {res['code']} {res['status']} http={res.get('http')} title={res.get('title','')[:60]!r} [{time.time()-t0:.0f}s]", flush=True)
        if len(results) % 5 == 0:
            json.dump(results, open(os.path.join(WAVE, "team01_verify_partial.json"), "w"), indent=1, ensure_ascii=False)

json.dump(results, open(os.path.join(WAVE, "team01_verify.json"), "w"), indent=1, ensure_ascii=False)
live = [r for r in results if r["status"] == "live"]
dead = [r for r in results if r["status"] == "dead"]
pend = [r for r in results if r["status"] == "pending"]
print(f"LIVE={len(live)} DEAD={len(dead)} PENDING={len(pend)} TOTAL={len(results)} ELAPSED={time.time()-t0:.0f}s")
