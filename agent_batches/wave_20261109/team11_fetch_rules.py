#!/usr/bin/env python3
"""Team 11 wave 20261109: fetch groupsinvite.link /group/rules/<slug>/ for
enum entries 1001-2671 (0-based indices 1000..2670). Uses curl only.
Saves incrementally to team11_gi_rules.json in the wave dir."""
import json, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
OUT = os.path.join(WAVE, "team11_gi_rules.json")
ENUM = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team13_state/gi_enum.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')

enum = json.load(open(ENUM))
slugs = list(enum.keys())[1000:2671]
print("target slugs:", len(slugs), "first:", slugs[0], "last:", slugs[-1], flush=True)

state = {}
if os.path.exists(OUT):
    state = json.load(open(OUT))
    print("resuming, already have:", len(state), flush=True)
lock = threading.Lock()

def fetch_one(slug):
    with lock:
        # skip only if we already have a code or a channel verdict
        if slug in state and (state[slug].get("code") or state[slug].get("channel")):
            return "cached"
    url = "https://groupsinvite.link/group/rules/%s/" % slug
    code, is_channel, http_code, size = "", False, 0, 0
    tmp = "/tmp/team11_gi_page_%s.html" % threading.current_thread().name.replace(" ", "_")
    for attempt in range(2):
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA,
                                "-o", tmp, "-w", "%{http_code}",
                                url], capture_output=True, text=True, timeout=45)
            http_code = int((r.stdout or "0").strip() or 0)
            body = open(tmp, encoding="utf-8", errors="ignore").read() if os.path.exists(tmp) else ""
            size = len(body)
            if http_code == 200 and size > 5000:
                is_channel = "whatsapp.com/channel/" in body
                codes = CODE_RE.findall(body)
                code = "" if is_channel else (codes[0] if codes else "")
                break
            time.sleep(3)
        except Exception:
            time.sleep(4)
    with lock:
        rec = dict(enum[slug])
        rec["code"] = code
        rec["all_codes"] = codes if 'codes' in dir() else []
        rec["channel"] = is_channel
        rec["http"] = http_code
        rec["bytes"] = size
        state[slug] = rec
        json.dump(state, open(OUT, "w"), ensure_ascii=False)
    return "ok %s -> %s" % (slug, "CHANNEL" if is_channel else (code if code else "NO-CODE"))

# Re-fetch entries saved with empty code (pre-fix regex missed /invite/ form).
todo = [s for s in slugs if s not in state or (not state[s].get("code") and not state[s].get("channel"))]
print("to fetch:", len(todo), flush=True)
n = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch_one, s): s for s in todo}
    for f in futs:
        try:
            res = f.result()
        except Exception as e:
            res = "ERR %s %s" % (futs[f], e)
        n += 1
        if n % 100 == 0:
            print(n, res, "state:", len(state), flush=True)
        time.sleep(0.05)
have = sum(1 for v in state.values() if v.get("code"))
chan = sum(1 for v in state.values() if v.get("channel"))
print("DONE fetched=%d with_code=%d channel=%d no_code=%d" % (len(state), have, chan, len(state)-have-chan), flush=True)
