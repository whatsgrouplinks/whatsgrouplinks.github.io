#!/usr/bin/env python3
"""team05: scrape groupwhat API for technology/gaming/sports, extract candidates."""
import json, re, sys, time, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

CATS = {179: "Technology", 80: "Gaming", 169: "Sports"}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

def extract_code(link):
    m = re.search(r'chat\.whatsapp\.com(?:/invite)?/([A-Za-z0-9_-]{10,})', link or "")
    return m.group(1) if m else None

all_groups = []
for cid, cname in CATS.items():
    d = fetch(f"https://api.groupwhat.com/wa-groups/public?categoryId={cid}&page=1&limit=50")
    total, pages = d["total"], d["totalPages"]
    print(f"{cname}: total={total} pages={pages}", flush=True)
    for page in range(1, pages + 1):
        if page > 1:
            d = fetch(f"https://api.groupwhat.com/wa-groups/public?categoryId={cid}&page={page}&limit=50")
            time.sleep(0.4)
        for g in d["groups"]:
            code = extract_code(g.get("invite_link", ""))
            if not code:
                continue  # skip channel links / missing
            country = g.get("country")
            ctry = country.get("name") if isinstance(country, dict) and country.get("name") else "International"
            all_groups.append({
                "name": (g.get("name") or "").strip(),
                "category": cname,
                "country": ctry,
                "description": (g.get("description") or "").strip(),
                "image": "",
                "code": code,
            })
    time.sleep(0.5)

# dedupe by code within source
seen = {}
for g in all_groups:
    seen.setdefault(g["code"], g)
print(f"raw entries: {len(all_groups)} | unique by code: {len(seen)}")
json.dump(list(seen.values()), open("/tmp/team05_candidates.json", "w"), ensure_ascii=False, indent=1)
print("wrote /tmp/team05_candidates.json")
