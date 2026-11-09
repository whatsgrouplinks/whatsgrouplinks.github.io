#!/usr/bin/env python3
"""Team 20 - verify remaining codes (incremental writes; resumes from existing files)."""
import json, os, re, subprocess, time, html
WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OUT = os.path.join(WAVE, "team20_verified.json")

cands = json.load(open(os.path.join(WAVE, "team20_to_verify.json")))
results = {}
if os.path.exists(OUT):
    try:
        results = json.load(open(OUT))
    except Exception:
        results = {}

def parse_og(path):
    try:
        s = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return "", ""
    m = re.search(r'<meta property="og:title" content="([^"]*)"', s)
    t = html.unescape(m.group(1)).strip() if m else ""
    m2 = re.search(r'<meta property="og:description" content="([^"]*)"', s)
    d = html.unescape(m2.group(1)).strip() if m2 else ""
    return t, d

def og_check(code):
    url = f"https://chat.whatsapp.com/{code}"
    http, title, desc = "", "", ""
    for attempt in (1, 2, 3):
        out = os.path.join(WAVE, f"team20_verify_{code}.html")
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "30", "-A", UA,
                            "-o", out, "-w", "%{http_code}", url],
                           capture_output=True, text=True, timeout=40)
        http = (r.stdout or "").strip()
        title, desc = parse_og(out)
        if http == "200" and title:
            return {"http": http, "og_title": title, "og_desc": desc,
                    "attempts": attempt, "verdict": "LIVE"}
        time.sleep(3)
    return {"http": http, "og_title": title, "og_desc": desc, "attempts": 3,
            "verdict": "DEAD" if http != "200" else "AMBIGUOUS-EMPTY-TITLE"}

for code in sorted(cands):
    if code in results and results[code].get("verdict") == "LIVE":
        continue
    # reuse an already-downloaded file with non-empty og:title
    f = os.path.join(WAVE, f"team20_verify_{code}.html")
    if os.path.exists(f):
        t, d = parse_og(f)
        if t:
            rec = dict(cands[code]); rec.update({"http": "200", "og_title": t, "og_desc": d,
                                                 "attempts": 1, "verdict": "LIVE"})
            results[code] = rec
            print(code, "LIVE (cached)", repr(t[:50]), flush=True)
            json.dump(results, open(OUT, "w"), indent=1, ensure_ascii=False)
            continue
    v = og_check(code)
    rec = dict(cands[code]); rec.update(v)
    results[code] = rec
    print(code, v["verdict"], "http=", v["http"], "og=", repr(v["og_title"][:60]), "src=", rec["source"], flush=True)
    json.dump(results, open(OUT, "w"), indent=1, ensure_ascii=False)
    time.sleep(1.0)

print("LIVE:", sum(1 for r in results.values() if r["verdict"] == "LIVE"))
print("DEAD:", sum(1 for r in results.values() if r["verdict"] == "DEAD"))
print("AMBIG:", sum(1 for r in results.values() if r["verdict"].startswith("AMBIG")))
