#!/usr/bin/env python3
"""team30: mine groupizo.com fresh detail pages (sitemap lastmod >= 2026-11-12).
Detail page -> h1 name, JSON-LD breadcrumb country (pos2) + category (pos3).
Then /verify/<slug> -> chat.whatsapp.com code. Banked incrementally.
"""
import json, re, time, sys, glob
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}

def fresh_urls():
    urls = []
    for f in sorted(glob.glob(WAVE + "team30-gz-sitemap-*.xml")):
        t = open(f, encoding="utf-8", errors="ignore").read()
        for u, m in re.findall(r"<url>\s*<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", t):
            if m >= "2026-11-12":
                urls.append((u, m))
    # dedupe, keep max lastmod
    d = {}
    for u, m in urls:
        d[u] = max(m, d.get(u, ""))
    return sorted(d.items(), key=lambda kv: -len(kv[0]) and kv[1], reverse=True)

def parse_detail(html):
    name = ""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    if m:
        name = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    country = category = ""
    for jm in re.finditer(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(jm.group(1))
        except Exception:
            continue
        nodes = d.get("@graph", [d]) if isinstance(d, dict) else []
        for node in nodes:
            if isinstance(node, dict) and node.get("@type") == "BreadcrumbList":
                items = node.get("itemListElement", [])
                if len(items) >= 2:
                    country = items[1].get("name", "")
                if len(items) >= 3:
                    category = items[2].get("name", "")
    return name, country, category

def main():
    items = fresh_urls()
    print("fresh urls:", len(items), flush=True)
    sess = requests.Session()
    sess.headers.update(UA)
    out_path = WAVE + "team30-mined-raw.json"
    mined = []
    try:
        mined = json.load(open(out_path))
        print("resuming with", len(mined), "already mined", flush=True)
    except Exception:
        pass
    done_slugs = {m["slug"] for m in mined}
    fails = []
    for i, (url, lastmod) in enumerate(items):
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        if slug in done_slugs:
            continue
        rec = {"url": url, "slug": slug, "lastmod": lastmod}
        try:
            r = sess.get(url, timeout=60)
            if r.status_code != 200:
                rec["error"] = "detail http %d" % r.status_code
                fails.append(rec)
                mined.append(rec)
                continue
            name, country, category = parse_detail(r.text)
            rec.update({"name": name, "country_name": country, "category_raw": category})
            time.sleep(0.4)
            rv = sess.get("https://groupizo.com/verify/" + slug, timeout=60)
            if rv.status_code != 200:
                rec["error"] = "verify http %d" % rv.status_code
            else:
                codes = re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})", rv.text)
                rec["code"] = codes[0] if codes else ""
                if not codes:
                    rec["error"] = "no code on verify page"
            mined.append(rec)
        except Exception as e:
            rec["error"] = "transport:%s" % type(e).__name__
            fails.append(rec)
            mined.append(rec)
        done_slugs.add(slug)
        if (i + 1) % 25 == 0:
            json.dump(mined, open(out_path, "w"), indent=1, ensure_ascii=False)
            ncode = sum(1 for m in mined if m.get("code"))
            print(f"{i+1}/{len(items)} mined={len(mined)} codes={ncode} fails={len(fails)}", flush=True)
        time.sleep(0.5)
    json.dump(mined, open(out_path, "w"), indent=1, ensure_ascii=False)
    ncode = sum(1 for m in mined if m.get("code"))
    print("DONE mined:", len(mined), "with code:", ncode, "fails:", len(fails), flush=True)
    print("fail sample:", fails[:10], flush=True)

if __name__ == "__main__":
    main()
