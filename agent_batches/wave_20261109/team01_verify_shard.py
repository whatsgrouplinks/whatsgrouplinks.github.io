#!/usr/bin/env python3
"""Team 01 - verify a shard of fresh codes (run up to 3 shards in parallel). Usage: verify_shard.py <codes.json> <out.json>"""
import json, os, re, subprocess, sys, time, html as htmlmod

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
codes_path, out_path = sys.argv[1], sys.argv[2]
fresh = json.load(open(codes_path))  # code -> listing url

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(3):
        try:
            r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "25",
                                "-o", "-", "-w", "\n%{http_code}", url],
                               capture_output=True, text=True, timeout=40)
            out = r.stdout
            http = out.rsplit("\n", 1)[-1].strip()
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
        if http == "200" and title:
            return {"code": code, "status": "live", "http": 200, "title": title,
                    "description": desc, "attempts": attempt + 1}
        if http == "200" and not title:
            time.sleep(5)
            continue
        if http in ("500", "502", "503", "429") and attempt < 1:
            time.sleep(5)
            continue
        return {"code": code, "status": "dead", "http": http, "title": title,
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
        json.dump(results, open(out_path, "w"), indent=1)
json.dump(results, open(out_path, "w"), indent=1)
live = [r for r in results if r["status"] == "live"]
print(f"DONE shard {out_path}: LIVE={len(live)} TOTAL={len(results)}")
