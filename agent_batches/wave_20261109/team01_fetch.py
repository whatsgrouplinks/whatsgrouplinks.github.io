#!/usr/bin/env python3
"""Team 01 wave 20261109 - step 1: fetch listing pages, extract invite codes."""
import json, os, re, subprocess, sys, time

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WAVE, "team01_raw")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

leads = json.load(open(os.path.join(WAVE, "leads_slice_01.json")))
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

CODE_RE = re.compile(r"chat\.whatsapp\.com(?:/|\\u002f|\\/|%2F)+([A-Za-z0-9_\-]{8,})")

def fetch(url, outpath):
    r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "30",
                        "-o", outpath, "-w", "%{http_code} %{size_download}", url],
                       capture_output=True, text=True)
    return r.stdout.strip()

results = []
seen_new = {}  # code -> first listing url
for i, lead in enumerate(leads):
    url = lead["url"]
    fn = os.path.join(RAW, f"p{i:03d}.html")
    status = ""
    if os.path.exists(fn) and os.path.getsize(fn) > 500:
        status = "cached"
    else:
        status = fetch(url, fn)
        time.sleep(0.4)
    try:
        html = open(fn, encoding="utf-8", errors="ignore").read()
    except Exception:
        html = ""
    codes = set()
    for m in CODE_RE.finditer(html):
        c = m.group(1)
        # strip trailing junk: codes are <=22 chars; if match ran into adjacent word, trim to 22
        # but keep shorter codes intact (min 8). Only trim when >22.
        if len(c) > 22:
            c = c[:22]
        # drop obvious non-codes
        if c.lower() in ("invite",):
            continue
        codes.add(c)
    fresh = [c for c in codes if c not in existing]
    for c in fresh:
        seen_new.setdefault(c, url)
    results.append({"idx": i, "url": url, "source": lead.get("source", ""),
                    "fetch": status, "bytes": len(html),
                    "codes_found": len(codes), "fresh": len(fresh),
                    "fresh_codes": sorted(fresh)})
    print(f"{i:3d} {status} bytes={len(html)} codes={len(codes)} fresh={len(fresh)} {url}", flush=True)

json.dump(results, open(os.path.join(WAVE, "team01_fetch_log.json"), "w"), indent=1)
json.dump({c: u for c, u in sorted(seen_new.items())},
          open(os.path.join(WAVE, "team01_fresh_codes.json"), "w"), indent=1)
print("TOTAL fresh unique codes:", len(seen_new))
print("TOTAL pages:", len(results))
