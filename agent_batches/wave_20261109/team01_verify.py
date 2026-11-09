#!/usr/bin/env python3
"""Team 01 wave 20261109 - step 2: verify fresh invite codes with slow checker (curl)."""
import json, os, re, subprocess, time, html as htmlmod

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

fresh = json.load(open(os.path.join(WAVE, "team01_fresh_codes.json")))  # code -> listing url

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(3):
        try:
            r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "25",
                                "-o", "-", "-w", "\n%{http_code}", url],
                               capture_output=True, text=True, timeout=40)
            out = r.stdout
            code_http = out.rsplit("\n", 1)[-1].strip()
            body = out[:out.rfind("\n")]
        except Exception as e:
            return {"code": code, "status": "transport-fail", "error": str(e), "attempts": attempt + 1}
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', body)
        if not m:
            m = re.search(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:title\"", body)
        title = htmlmod.unescape(m.group(1)).strip() if m else ""
        md = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', body)
        if not md:
            md = re.search(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:description\"", body)
        desc = htmlmod.unescape(md.group(1)).strip() if md else ""
        if code_http == "200" and title:
            return {"code": code, "status": "live", "http": 200, "title": title,
                    "description": desc, "attempts": attempt + 1}
        if code_http == "200" and not title:
            # ambiguous: retry spaced apart
            time.sleep(5)
            continue
        # non-200: dead (404 etc.) — one retry for 5xx/transport-ish
        if code_http in ("500", "502", "503", "429") and attempt < 1:
            time.sleep(5)
            continue
        return {"code": code, "status": "dead", "http": code_http, "title": title,
                "description": desc, "attempts": attempt + 1}
    return {"code": code, "status": "dead", "http": "200-empty-title", "title": "",
            "description": "", "attempts": 3}

results = []
codes = sorted(fresh.keys())
for i, c in enumerate(codes):
    res = check(c)
    res["listing_url"] = fresh[c]
    results.append(res)
    print(f"{i+1}/{len(codes)} {c} {res['status']} http={res.get('http')} title={res.get('title','')[:60]!r}", flush=True)
    time.sleep(0.6)
    if (i + 1) % 20 == 0:
        json.dump(results, open(os.path.join(WAVE, "team01_verify_partial.json"), "w"), indent=1)

json.dump(results, open(os.path.join(WAVE, "team01_verify.json"), "w"), indent=1)
live = [r for r in results if r["status"] == "live"]
dead = [r for r in results if r["status"] == "dead"]
tf = [r for r in results if r["status"] == "transport-fail"]
print(f"LIVE={len(live)} DEAD={len(dead)} TRANSPORT-FAIL={len(tf)} TOTAL={len(results)}")
