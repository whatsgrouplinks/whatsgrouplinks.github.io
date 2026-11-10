#!/usr/bin/env python3
"""Team 13 fallback: no-tag API is newest-first; scan pages until created_at < 2026-11-08."""
import json, re, time, subprocess, os
from collections import Counter

WORK = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
RAW = os.path.join(WORK, "team13_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CUTOFF = "2026-11-08"

known = set(json.load(open(os.path.join(RAW, "known_union.json"))))
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)")

def fetch_page(page):
    url = f"https://api.groupjoin.link/groups?page={page}&limit=20&safeSearch=blur"
    out = f"{RAW}/notag_p{page}.json"
    for attempt in range(4):
        r = subprocess.run(["curl", "-s", "-m", "25", "-A", UA, url, "-o", out, "-w", "%{http_code}"],
                           capture_output=True, text=True)
        code = r.stdout.strip()
        try:
            d = json.load(open(out))
        except Exception:
            d = None
        if code == "200" and isinstance(d, dict) and "data" in d:
            return d["data"]
        print(f"  notag page {page} attempt {attempt+1}: http={code} retrying", flush=True)
        time.sleep(10)
    print(f"  notag page {page} FAILED", flush=True)
    return None

all_items = []
page = 1
while True:
    data = fetch_page(page)
    if data is None:
        break
    dates = [x.get("created_at", "")[:10] for x in data]
    print(f"notag page {page}: {len(data)} items, created {min(dates) if dates else '?'}..{max(dates) if dates else '?'}", flush=True)
    all_items.extend(data)
    if not dates or min(dates) < CUTOFF:
        print(f"  cutoff reached at page {page}", flush=True)
        break
    page += 1
    if page > 15:
        print("  safety cap 15 pages", flush=True)
        break
    time.sleep(4)

json.dump(all_items, open(f"{RAW}/all_notag_window.json", "w"))
print(f"total no-tag items in window scan: {len(all_items)}", flush=True)
print("category counts:", Counter((x.get("category") or {}).get("category_name") for x in all_items), flush=True)

cands, seen, exclusions = [], set(), []
for x in all_items:
    cat = ((x.get("category") or {}).get("category_name") or "").strip()
    created = (x.get("created_at") or "")[:10]
    if created < CUTOFF:
        continue
    if cat.lower() == "adult":
        exclusions.append({"code": "", "reason": f"Adult category skipped (created {created})"})
        continue
    link = x.get("link") or ""
    if "whatsapp.com/channel" in link:
        exclusions.append({"code": "", "reason": f"channel link dropped: {link[:80]}"})
        continue
    m = CODE_RE.search(link)
    if not m:
        exclusions.append({"code": "", "reason": f"no invite code in link: {link[:100]}"})
        continue
    code = m.group(1)
    if code in seen:
        continue
    seen.add(code)
    if code in known:
        exclusions.append({"code": code, "reason": "already in union (existing_codes/groups.json)"})
        continue
    cands.append({"raw": x, "code": code})

print(f"fresh non-adult candidates since Nov 8: {len(cands)}", flush=True)
json.dump(cands, open(f"{RAW}/candidates_notag.json", "w"))
json.dump(exclusions, open(f"{RAW}/exclusions_notag.json", "w"))
for c in cands:
    x = c["raw"]
    print("CAND", c["code"], "|", (x.get("category") or {}).get("category_name"), "|",
          (x.get("country") or {}).get("iso2"), "|", x.get("created_at", "")[:10], "|",
          (x.get("group_title") or "")[:70], "| desc:", (x.get("group_desc") or "")[:80].replace("\n", " "), flush=True)
print("NOTAG_DONE", flush=True)
