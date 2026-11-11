#!/usr/bin/env python3
"""Team 13 wave 20261111: slow-verify the 2 fresh candidates via chat.whatsapp.com og:title.
Control code first (known-live from Nov-10 run), then candidates, retry-on-empty-og after a pause."""
import json, re, subprocess, time, os

WORK = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
RAW = os.path.join(WORK, "team13_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OG = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG2 = re.compile(r"og:title[^>]*content=\"([^\"]*)\"", re.I)

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    out = f"{RAW}/check_{code}.html"
    r = subprocess.run(["curl", "-s", "-L", "-m", "30", "-A", UA, url, "-o", out, "-w", "%{http_code}"],
                       capture_output=True, text=True)
    http = r.stdout.strip()
    try:
        html = open(out, encoding="utf-8", errors="ignore").read()
    except Exception:
        html = ""
    m = OG.search(html) or OG2.search(html)
    title = m.group(1).strip() if m else ""
    return http, title

cands = json.load(open(f"{RAW}/candidates.json"))
results = {}

# control code (known live, Nov-10 run)
http, title = check("KrDwdK8EIkB6vgauHg5M7N")
print(f"CONTROL KrDwdK8EIkB6vgauHg5M7N: http={http} og:title={title!r}", flush=True)
results["control"] = {"http": http, "og_title": title}
time.sleep(2)

for c in cands:
    code = c["code"]
    http, title = check(code)
    print(f"{code}: attempt1 http={http} og:title={title!r}", flush=True)
    if not title:
        time.sleep(8)
        http2, title2 = check(code)
        print(f"{code}: attempt2 http={http2} og:title={title2!r}", flush=True)
        if not title2:
            time.sleep(15)
            http3, title3 = check(code)
            print(f"{code}: attempt3 http={http3} og:title={title3!r}", flush=True)
            http, title = http3, title3
        else:
            http, title = http2, title2
    results[code] = {"http": http, "og_title": title, "raw": c["raw"]}
    time.sleep(2)

json.dump(results, open(f"{RAW}/verify.json", "w"), ensure_ascii=False, indent=1)
print("VERIFY_DONE", flush=True)
