#!/usr/bin/env python3
"""team14: verify mined codes via chat.whatsapp.com og:title, dedupe, screen, categorize.
Uses ONE requests.Session (keep-alive) per task spec. Controls run first."""
import json, re, time, html, os, sys

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UNION = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"

import requests

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}

TITLE_RE = re.compile(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\'](.*?)["\']', re.S | re.I)
TITLE_RE2 = re.compile(r'<meta[^>]*content=["\'](.*?)["\'][^>]*property=["\']og:title["\']', re.S | re.I)

def og_title(html_text):
    m = TITLE_RE.search(html_text) or TITLE_RE2.search(html_text)
    if not m:
        return ""
    return html.unescape(m.group(1)).strip()

GENERIC = {"", "whatsapp", "whatsapp group", "whatsapp group invite", "join this group on whatsapp"}

def check_code(sess, code, retries=3):
    """returns (status, title) status in live/dead/pending"""
    last_err = ""
    for attempt in range(retries):
        try:
            r = sess.get(f"https://chat.whatsapp.com/{code}", timeout=75)
            if r.status_code == 429:
                return "pending", f"HTTP 429 (attempt {attempt+1})"
            if r.status_code != 200:
                last_err = f"HTTP {r.status_code}"
                time.sleep(15 * (attempt + 1))
                continue
            t = og_title(r.text)
            if t and t.lower() not in GENERIC:
                return "live", t
            # empty/generic title: spaced retry
            last_err = f"empty og:title (attempt {attempt+1})"
            if attempt < retries - 1:
                time.sleep(20 * (attempt + 1))
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:80]}"
            if attempt < retries - 1:
                time.sleep(20 * (attempt + 1))
    if "429" in last_err or "Timeout" in last_err or "Proxy" in last_err or "Connection" in last_err:
        return "pending", last_err
    return "dead", last_err

# ---------- load data ----------
union = set(json.load(open(UNION)))
ckpt = json.load(open(f"{WAVE}/team14-fetch-checkpoint.json"))
raw = ckpt["raw"]  # code -> {name, tags, src_grupo, rel_grupo}
print(f"raw unique codes: {len(raw)}; union: {len(union)}", flush=True)

sess = requests.Session()
sess.headers.update(UA)

# ---------- controls FIRST ----------
ctrl_live, ctrl_live_t = check_code(sess, "KrDwdK8EIkB6vgauHg5M7N", retries=2)
print(f"CONTROL live: {ctrl_live} title={ctrl_live_t!r}", flush=True)
ctrl_fab, ctrl_fab_t = check_code(sess, "ZzZzZzZzZzZzZzZzZzZzZzZz", retries=2)
print(f"CONTROL fabricated: {ctrl_fab} info={ctrl_fab_t!r}", flush=True)
if not (ctrl_live == "live" and ctrl_live_t == "JAY - PHP & Python Full Stack Developer"):
    print("CONTROL FAIL: live control did not return expected title - STOPPING", flush=True)
    sys.exit(2)
if ctrl_fab != "dead":
    print("CONTROL FAIL: fabricated code did not come back dead - STOPPING", flush=True)
    sys.exit(2)
print("CONTROLS PASS", flush=True)

# ---------- dedupe + verify ----------
results = {"live": {}, "dead": [], "pending": [], "dupes": []}
out_path = f"{WAVE}/team14-verify-checkpoint.json"
if os.path.exists(out_path):
    results = json.load(open(out_path))
    print(f"resumed verify: live={len(results['live'])} dead={len(results['dead'])} pending={len(results['pending'])} dupes={len(results['dupes'])}", flush=True)

seen_done = set(results["live"]) | set(results["dead"]) | {p["code"] for p in results["pending"]} | set(results["dupes"])
fresh = [c for c in raw if c not in union and c not in seen_done]
print(f"fresh codes to verify: {len(fresh)} (dupes vs union so far: {len([c for c in raw if c in union])})", flush=True)

for i, code in enumerate(fresh):
    if code in union:
        results["dupes"].append(code)
        continue
    status, info = check_code(sess, code)
    if status == "live":
        results["live"][code] = {"title": info, "dir_name": raw[code]["name"],
                                 "tags": raw[code]["tags"], "src_grupo": raw[code]["src_grupo"],
                                 "rel_grupo": raw[code]["rel_grupo"]}
    elif status == "dead":
        results["dead"].append(code)
    else:
        results["pending"].append({"code": code, "reason": info})
    if (i + 1) % 10 == 0:
        print(f"verified {i+1}/{len(fresh)} live={len(results['live'])} dead={len(results['dead'])} pending={len(results['pending'])}", flush=True)
        json.dump(results, open(out_path, "w"), ensure_ascii=False)
    time.sleep(2)

json.dump(results, open(out_path, "w"), ensure_ascii=False)
print(f"VERIFY DONE live={len(results['live'])} dead={len(results['dead'])} pending={len(results['pending'])} dupes={len(results['dupes'])}", flush=True)
