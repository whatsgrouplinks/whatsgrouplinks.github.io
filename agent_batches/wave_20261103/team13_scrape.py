#!/usr/bin/env python3
"""TEAM 13: groupjoin.link residual TAILS - money (212+), education (75+), business (218+)."""
import json, re, time, html, os, sys, random
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")

def fetch(url, timeout=30):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return r.text

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})")

union = set(json.load(open(f"{WAVE}/dedupe_union.json")))
print(f"union codes: {len(union)}", flush=True)

# --- Phase 1: bound discovery ---
TAG_URL = "https://www.groupjoin.link/tag/{tag}/?page={page}&limit=20&safeSearch=blur"
tasks = {"money": 212, "education": 75, "business": 218}

# per-tag: list of dicts {code, name, page, tag}
found = []
bounds = {}
for tag, start in tasks.items():
    empty = 0
    last_page = start - 1
    page = start
    while empty < 2 and page < start + 40:
        url = TAG_URL.format(tag=tag, page=page)
        try:
            html_text = fetch(url)
        except Exception as e:
            print(f"[{tag}] page {page} fetch fail: {e}", flush=True)
            bounds[tag] = {"last_ok_page": last_page, "note": f"fetch fail at {page}: {e}"}
            break
        codes = CODE_RE.findall(html_text)
        # crude record count: count code occurrences as proxy
        if len(codes) < 3:
            empty += 1
            print(f"[{tag}] page {page}: ~0 records ({len(codes)} code hits), empty_streak={empty}", flush=True)
        else:
            empty = 0
            last_page = page
            # extract (name, code) pairs from listing cards if possible
            names = extract_names_codes(html_text)
            for code, name in names:
                if len(code) < 20 or len(code) > 24:
                    continue
                found.append({"code": code, "name": name, "page": page, "tag": tag})
            print(f"[{tag}] page {page}: {len(codes)} code hits, {len(names)} name/code pairs", flush=True)
        page += 1
        time.sleep(0.7)
    bounds[tag] = {"last_page_with_records": last_page, "stopped_at_page": page}
    print(f"[{tag}] BOUND: last page with records = {last_page}", flush=True)

json.dump(bounds, open(f"{WAVE}/team13-bounds.json", "w"), indent=1)
print(f"total candidates: {len(found)}", flush=True)
