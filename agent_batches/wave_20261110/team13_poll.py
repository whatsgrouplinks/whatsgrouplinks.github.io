#!/usr/bin/env python3
"""Team 13: poll groupjoin.link API tag=onlynew pages 1-40, extract candidates
created >= 2026-11-08, non-Adult, dedupe vs union, verify invite links."""
import json, re, time, subprocess, os, sys
from collections import Counter

WORK = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
RAW = os.path.join(WORK, "team13_raw")
os.makedirs(RAW, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CUTOFF = "2026-11-08"

ec = json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"))
known = set(ec)
g = json.load(open("/home/hatch/workspace/whatsapp-groups-site/groups.json"))
pat = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)")
n_groups_codes = 0
for item in g:
    m = pat.search(item.get("invite", "") or "")
    if m:
        known.add(m.group(1))
        n_groups_codes += 1
print(f"existing_codes={len(ec)} groups_invite_codes={n_groups_codes} union={len(known)}", flush=True)
json.dump(sorted(known), open(os.path.join(RAW, "known_union.json"), "w"))

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)")

def fetch_page(page):
    url = f"https://api.groupjoin.link/groups?tag=onlynew&page={page}&limit=20&safeSearch=blur"
    out = f"{RAW}/p{page}.json"
    for attempt in range(3):
        r = subprocess.run(["curl", "-s", "-m", "25", "-A", UA, url, "-o", out, "-w", "%{http_code}"],
                           capture_output=True, text=True)
        code = r.stdout.strip()
        try:
            d = json.load(open(out))
        except Exception:
            d = None
        if code == "200" and isinstance(d, dict) and "data" in d:
            return d["data"]
        print(f"  page {page} attempt {attempt+1}: http={code} retrying", flush=True)
        time.sleep(8)
    print(f"  page {page} FAILED after 3 attempts", flush=True)
    return None

all_items = []
for p in range(1, 41):
    data = fetch_page(p)
    if data is None:
        continue
    print(f"page {p}: {len(data)} items, created "
          f"{min((x.get('created_at','')[:10] for x in data), default='?')}.."
          f"{max((x.get('created_at','')[:10] for x in data), default='?')}", flush=True)
    all_items.extend(data)
    time.sleep(4)

json.dump(all_items, open(f"{RAW}/all_onlynew.json", "w"))
print(f"total items collected: {len(all_items)}", flush=True)
print("category counts:", Counter((x.get("category") or {}).get("category_name") for x in all_items), flush=True)
print("created_at date counts:", Counter(x.get("created_at", "")[:10] for x in all_items).most_common(15), flush=True)

cands = []
seen = set()
exclusions = []
for x in all_items:
    cat = ((x.get("category") or {}).get("category_name") or "").strip()
    if cat.lower() == "adult":
        continue
    created = (x.get("created_at") or "")[:10]
    if created < CUTOFF:
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
        continue
    cands.append({"raw": x, "code": code})

print(f"fresh candidates (new since Nov 8, non-adult, not in union): {len(cands)}", flush=True)
json.dump(cands, open(f"{RAW}/candidates.json", "w"))
json.dump(exclusions, open(f"{RAW}/exclusions_stage1.json", "w"))
for c in cands:
    x = c["raw"]
    print("CAND", c["code"], (x.get("category") or {}).get("category_name"),
          (x.get("country") or {}).get("iso2"), x.get("created_at", "")[:10],
          (x.get("group_title") or "")[:70], flush=True)
print("POLL_DONE", flush=True)
