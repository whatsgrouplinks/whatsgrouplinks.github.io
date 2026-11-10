#!/usr/bin/env python3
"""Team 13: verify the 2 surviving invites via chat.whatsapp.com og:title.
Also follow the /group/<uid> redirect once to record the detail-page format."""
import json, re, subprocess, time, os

WORK = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
RAW = os.path.join(WORK, "team13_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

cands = json.load(open(os.path.join(RAW, "candidates_notag.json")))
# SHEYI = named scam, dropped on sight, never verified
DROP_SCAM = {"HYxIXc2kv6CJG7TW5CrHSn": "SHEYI airdrop — named scam/money-mule pattern in task rules"}

def curl_og(code, attempt=0):
    url = f"https://chat.whatsapp.com/{code}"
    out = os.path.join(RAW, f"check_{code}.html")
    r = subprocess.run(["curl", "-s", "-m", "15", "-A", UA, "-L", url, "-o", out, "-w", "%{http_code}|%{size_download}"],
                       capture_output=True, text=True)
    http, size = (r.stdout.strip().split("|") + ["", ""])[:2]
    title = ""
    try:
        html = open(out, encoding="utf-8", errors="ignore").read()
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
        if not m:
            m = re.search(r"<title>([^<]*)</title>", html)
        title = (m.group(1).strip() if m else "")
    except Exception as e:
        title = f"READ_ERROR {e}"
    return {"code": code, "http": http, "size": size, "og_title": title, "attempt": attempt}

results = {}
for c in cands:
    code = c["code"]
    if code in DROP_SCAM:
        print(f"DROP {code}: {DROP_SCAM[code]} (not verified)", flush=True)
        continue
    res = curl_og(code)
    print(f"CHECK {code}: http={res['http']} size={res['size']} og:title={res['og_title']!r}", flush=True)
    # retry once if empty title but http 200
    if res["http"] == "200" and not res["og_title"]:
        time.sleep(3)
        res = curl_og(code, attempt=1)
        print(f"RETRY {code}: http={res['http']} size={res['size']} og:title={res['og_title']!r}", flush=True)
    results[code] = res
    time.sleep(1)

# detail-page redirect follow (one shot)
r = subprocess.run(["curl", "-s", "-m", "20", "-A", UA, "-L",
                    "https://groupjoin.link/group/n6qj7rvo4fx9je86bi82",
                    "-o", os.path.join(RAW, "detail1_follow.html"), "-w", "%{http_code}|%{url_effective}|%{size_download}"],
                   capture_output=True, text=True)
print("DETAIL_FOLLOW:", r.stdout.strip(), flush=True)

json.dump(results, open(os.path.join(RAW, "verify.json"), "w"), indent=1)
print("VERIFY_DONE", flush=True)
