#!/usr/bin/env python3
"""Team 04 resume verifier — curl-based, resumes from checkpoint files."""
import json, re, subprocess, time, threading, os
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261108")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
GENERIC = {"whatsapp group", "join this group on whatsapp", "whatsapp", "join group", ""}

prog = json.load(open(os.path.join(WAVE, "team04-progress.json")))
candidates = prog["candidates"]

def code_of(r):
    m = re.search(r"chat.whatsapp.com/([A-Za-z0-9]{22})", r["invite"])
    return m.group(1)

done_v = json.load(open(os.path.join(WAVE, "team04-leads-harvest-d.json")))
done_p = json.load(open(os.path.join(WAVE, "team04-leads-harvest-d-pending.json")))
decided = {code_of(r) for r in done_v + done_p}
todo = [c for c in candidates if c not in decided]
print(f"resume: {len(candidates)} candidates, {len(decided)} decided, {len(todo)} to check", flush=True)

lock = threading.Lock()
last = [0.0]

def check(code):
    rec = candidates[code]
    with lock:
        gap = 0.6 - (time.time() - last[0])
        if gap > 0:
            time.sleep(gap)
        last[0] = time.time()
    for attempt in range(2):
        try:
            p = subprocess.run(
                ["curl", "-sS", "-m", "30", "-A", UA, "-L",
                 "-w", "\n%{http_code}", f"https://chat.whatsapp.com/{code}"],
                capture_output=True, text=True, timeout=45)
            out = p.stdout or ""
            if "\n" in out:
                body, sc = out.rsplit("\n", 1)
                sc = int(sc.strip()) if sc.strip().isdigit() else 0
            else:
                body, sc = out, 0
            if sc == 0:
                if attempt == 0:
                    time.sleep(5)
                    continue
                return ("pending", code)
            if sc != 200:
                if sc in (429, 500, 502, 503) and attempt == 0:
                    time.sleep(5)
                    continue
                if sc in (429, 500, 502, 503):
                    return ("pending", code)
                return ("dead", code)
            m = re.search(r'property="og:title"\s+content="([^"]*)"', body) or \
                re.search(r'content="([^"]*)"\s+property="og:title"', body)
            title = (m.group(1).strip() if m else "")
            if title and title.lower() not in GENERIC:
                return ("live", code)
            if attempt == 0:
                time.sleep(8)
                continue
            return ("dead", code)
        except Exception:
            if attempt == 0:
                time.sleep(5)
                continue
            return ("pending", code)
    return ("dead", code)

results = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(check, c): c for c in todo}
    n = 0
    for f in futs:
        results[futs[f]] = f.result()
        n += 1
        if n % 50 == 0:
            v = list(done_v) + [candidates[c] for c, r in results.items() if r[0] == "live"]
            pp = list(done_p) + [dict(candidates[c], reason="transport") for c, r in results.items() if r[0] == "pending"]
            json.dump(v, open(os.path.join(WAVE, "team04-leads-harvest-d.json"), "w"), ensure_ascii=False)
            json.dump(pp, open(os.path.join(WAVE, "team04-leads-harvest-d-pending.json"), "w"), ensure_ascii=False)
            print(f"  checked {n}/{len(todo)} this run, verified total {len(v)}", flush=True)

VERIFIED = list(done_v) + [candidates[c] for c, r in results.items() if r[0] == "live"]
PENDING = list(done_p) + [dict(candidates[c], reason="transport") for c, r in results.items() if r[0] == "pending"]
DEAD = sum(1 for r in results.values() if r[0] == "dead")

seen = set(); leads_out = []
for l in prog["new_leads"]:
    if l["url"] not in seen:
        seen.add(l["url"]); leads_out.append(l)

def w(name, data):
    for i in range(5):
        try:
            with open(os.path.join(WAVE, name), "w") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=1)
            return True
        except OSError as e:
            print(f"  write {name} failed ({e}), retry {i+1}", flush=True)
            time.sleep(2)
    return False

w("team04-leads-harvest-d.json", VERIFIED)
w("team04-leads-harvest-d-pending.json", PENDING)
w("team04-leads-harvest-d-leads.json", leads_out)
print(f"DONE verified={len(VERIFIED)} pending={len(PENDING)} dead_this_run={DEAD} leads={len(leads_out)}", flush=True)
print("FAILED TAGS:", json.dumps(prog["failed_tags"]), flush=True)
