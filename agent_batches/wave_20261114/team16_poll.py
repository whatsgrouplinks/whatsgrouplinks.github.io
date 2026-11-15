#!/usr/bin/env python3
"""team16 groupjoin.link newest poll — wave 20261114.
Polls https://api.groupjoin.link/groups?page=N&limit=20&safeSearch=blur
(newest-first, no tag param). Saves raw JSON, prints a compact table.
Cutoff from team17 (Nov 13): fresh = created_at > 2026-11-12 16:26:43.
"""
import json, sys, time, requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
BASE = "https://api.groupjoin.link/groups"
OUT = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/team16-api-raw.json"

s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "application/json, text/plain, */*",
                  "Referer": "https://groupjoin.link/"})

def fetch_page(n, tries=4):
    for i in range(tries):
        try:
            r = s.get(BASE, params={"page": n, "limit": 20, "safeSearch": "blur"},
                      timeout=60)
            if r.status_code == 200:
                return r.json()
            print(f"page {n}: HTTP {r.status_code} (try {i+1})", flush=True)
        except Exception as e:
            print(f"page {n}: transport error {e!r} (try {i+1})", flush=True)
        time.sleep(6)
    return None

raw = {}
for n in (1, 2):
    data = fetch_page(n)
    if data is None:
        print(f"FAILED page {n}", flush=True)
        continue
    raw[f"page{n}"] = data
    time.sleep(5)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(raw, f, ensure_ascii=False, indent=1)

def items_of(data):
    if isinstance(data, dict):
        for k in ("data", "groups", "items", "results"):
            if isinstance(data.get(k), list):
                return data[k]
        return []
    return data if isinstance(data, list) else []

for n in (1, 2):
    data = raw.get(f"page{n}")
    if not data:
        continue
    items = items_of(data)
    print(f"=== page {n}: {len(items)} items; top-level keys: "
          f"{list(data.keys()) if isinstance(data, dict) else 'list'} ===", flush=True)
    for it in items:
        if not isinstance(it, dict):
            print("  NON-DICT:", repr(it)[:200]); continue
        print("  | ".join([
            str(it.get("created_at") or it.get("createdAt") or "?"),
            str(it.get("title") or it.get("name") or "?")[:60],
            "cat=" + str(it.get("category") or it.get("category_name") or "?"),
            "ctry=" + str(it.get("country") or it.get("country_code") or "?"),
            "uid=" + str(it.get("group_uid") or it.get("uid") or it.get("id") or "?"),
            "link=" + str(it.get("link") or it.get("invite_link") or it.get("whatsapp_link") or "?")[:70],
        ]), flush=True)
print("saved", OUT)
