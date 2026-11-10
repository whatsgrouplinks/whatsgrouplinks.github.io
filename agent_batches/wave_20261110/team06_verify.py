#!/usr/bin/env python3
"""TEAM 06 wave 20261110 slice 6: dedupe vs union, prescreen, verify fresh codes."""
import json, re, os, subprocess, time, threading, html
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
VDIR = os.path.join(BASE, "verify")
os.makedirs(VDIR, exist_ok=True)

# ---- union ----
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
groups = json.load(open("/home/hatch/workspace/whatsapp-groups-site/groups.json"))
g_codes = set()
for g in groups:
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', g.get("invite", ""))
    if m:
        g_codes.add(m.group(1))
union = existing | g_codes
print(f"union: existing={len(existing)} groups={len(g_codes)} total={len(union)}")

ext = json.load(open(os.path.join(BASE, "team06-extracted.json")))
print(f"extracted unique codes: {len(ext)}")

ADULT_RE = re.compile(r'(\U0001F51E|\U0001F975|sexy|sexual|\bsex\b|porn|xxx|nude|naked|escort|hookup|erotic|call\s*girl|callgirl|adult|18\+|18 plus|hot\s*sex)', re.I)
SCAM_RE = re.compile(r'(b-?love|blove|forsage|shey(i|y)\b|airdrop|paypal\s*loader|bitfinex|counterfeit\s*currency|carding|crypto[ -]?doubling|double\s*(your|the)\s*(money|bitcoin|btc|crypto|usdt)|money[ -]?doubling|double\s*income)', re.I)

def screen(name):
    if not name:
        return None
    if ADULT_RE.search(name):
        return "adult"
    if SCAM_RE.search(name):
        return "scam"
    return None

fresh = []
exclusions = []
dropped_adult_page = 0
for rec in ext:
    code = rec["code"]
    if code in union:
        continue
    if rec.get("adult_page"):
        exclusions.append({"code": code, "reason": "adult-category page (groupjoin.link Adult) — never verified"})
        dropped_adult_page += 1
        continue
    why = screen(rec.get("name") or "")
    if why:
        exclusions.append({"code": code, "reason": f"prescreen {why}: name={rec.get('name')!r}"})
        continue
    fresh.append(rec)
print(f"fresh after dedupe+prescreen: {len(fresh)} (adult-page dropped: {dropped_adult_page}, excluded: {len(exclusions)})")
json.dump(fresh, open(os.path.join(BASE, "team06-fresh.json"), "w"), indent=1)
json.dump(exclusions, open(os.path.join(BASE, "team06-exclusions-prescreen.json"), "w"), indent=1)

# ---- verify ----
start_lock = threading.Lock()
last_start = [0.0]

def paced_start():
    with start_lock:
        now = time.time()
        wait = 0.6 - (now - last_start[0])
        if wait > 0:
            time.sleep(wait)
        last_start[0] = time.time()

def verify_once(code):
    paced_start()
    out = os.path.join(VDIR, f"{code}.html")
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "15",
                            "--connect-timeout", "8", "--compressed",
                            "-A", UA, "-o", out, "-w", "%{http_code}",
                            f"https://chat.whatsapp.com/{code}"],
                           capture_output=True, text=True, timeout=25)
        http = r.stdout.strip()
        if not http.isdigit():
            return {"code": code, "http": None, "title": None, "transport_error": (r.stderr or "no http status")[:200]}
        title = None
        if os.path.exists(out):
            s = open(out, encoding="utf-8", errors="ignore").read()
            m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', s) or \
                re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:title"', s)
            if m:
                title = html.unescape(m.group(1)).strip()
        return {"code": code, "http": int(http), "title": title or None, "transport_error": None}
    except Exception as e:
        return {"code": code, "http": None, "title": None, "transport_error": str(e)[:200]}

def run_pass(codes, tag):
    results = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(verify_once, c): c for c in codes}
        done = 0
        for f in futs:
            r = f.result()
            results[r["code"]] = r
            done += 1
            if done % 50 == 0:
                print(f"  {tag}: {done}/{len(codes)}", flush=True)
    return results

t0 = time.time()
print("pass 1: verifying", len(fresh))
p1 = run_pass([r["code"] for r in fresh], "pass1")
live, dead, pending = {}, {}, {}
for code, r in p1.items():
    if r["transport_error"] is not None or r["http"] is None:
        pending[code] = r
    elif r["http"] == 200 and r["title"]:
        live[code] = r
    else:
        dead[code] = r
print(f"pass1: live={len(live)} empty-title={len(dead)} transport-fail={len(pending)} in {time.time()-t0:.0f}s")

# retries for empty-title (2 spaced retries) and transport failures (1 retry)
for attempt in (2, 3):
    retry_codes = list(dead.keys()) + list(pending.keys())
    if not retry_codes:
        break
    print(f"pass {attempt}: retrying {len(retry_codes)} (dead+pending), spacing 20s first")
    time.sleep(20)
    pr = run_pass(retry_codes, f"pass{attempt}")
    for code, r in pr.items():
        if r["transport_error"] is not None or r["http"] is None:
            pending[code] = r
            dead.pop(code, None)
        elif r["http"] == 200 and r["title"]:
            live[code] = r
            dead.pop(code, None)
            pending.pop(code, None)
        else:
            dead[code] = r
            pending.pop(code, None)
    print(f"after pass {attempt}: live={len(live)} dead={len(dead)} pending={len(pending)}")

out = {"live": live, "dead": dead, "pending": pending,
       "exclusions_prescreen": exclusions, "union_size": len(union)}
json.dump(out, open(os.path.join(BASE, "team06-verify.json"), "w"), indent=1)
print(f"FINAL live={len(live)} dead={len(dead)} pending={len(pending)}")
