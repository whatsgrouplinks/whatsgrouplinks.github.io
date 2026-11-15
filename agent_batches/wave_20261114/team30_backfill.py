#!/usr/bin/env python3
"""team30 backfill: re-fetch groupizo detail pages for mined rows missing
category/country; extract category from meta description ('listed under X')
and country/category from JSON-LD breadcrumb; unescape entities."""
import json, re, time
import requests
from html import unescape

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

def parse(html):
    cat = country = ""
    m = re.search(r'<meta name="description" content="([^"]*)"', html)
    if m:
        d = unescape(m.group(1))
        mm = re.search(r"listed under (.+?) on Groupizo", d)
        if mm:
            cat = mm.group(1).strip()
    bc_country = bc_cat = ""
    for jm in re.finditer(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            dd = json.loads(jm.group(1))
        except Exception:
            continue
        nodes = dd.get("@graph", [dd]) if isinstance(dd, dict) else []
        for node in nodes:
            if isinstance(node, dict) and node.get("@type") == "BreadcrumbList":
                items = node.get("itemListElement", [])
                if len(items) >= 2:
                    bc_country = unescape(items[1].get("name", ""))
                if len(items) >= 3:
                    bc_cat = unescape(items[2].get("name", ""))
    if not cat:
        cat = bc_cat
    if not country:
        country = bc_country
    return cat, country

def main():
    path = WAVE + "team30-mined-raw.json"
    mined = json.load(open(path))
    todo = [m for m in mined if not m.get("category_raw")]
    print("backfill todo:", len(todo), flush=True)
    sess = requests.Session()
    sess.headers.update(UA)
    for i, m in enumerate(todo):
        try:
            r = sess.get(m["url"], timeout=60)
            if r.status_code == 200:
                cat, country = parse(r.text)
                m["category_raw"] = cat
                m["country_name"] = country
                if not m.get("name"):
                    mm = re.search(r"<h1[^>]*>(.*?)</h1>", r.text, re.S)
                    if mm:
                        m["name"] = re.sub(r"<[^>]+>", "", mm.group(1)).strip()
        except Exception as e:
            print("ERR", m["slug"], e, flush=True)
        if (i + 1) % 25 == 0:
            json.dump(mined, open(path, "w"), indent=1, ensure_ascii=False)
            print(f"{i+1}/{len(todo)}", flush=True)
        time.sleep(0.4)
    json.dump(mined, open(path, "w"), indent=1, ensure_ascii=False)
    print("DONE still missing:", sum(1 for m in mined if not m.get("category_raw")), flush=True)
    from collections import Counter
    print("categories:", Counter(m.get("category_raw", "") for m in mined).most_common(20))
    print("countries:", Counter(m.get("country_name", "") for m in mined).most_common(15))

if __name__ == "__main__":
    main()
