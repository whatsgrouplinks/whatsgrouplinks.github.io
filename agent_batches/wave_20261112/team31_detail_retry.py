#!/usr/bin/env python3
"""TEAM31 phase 3: retry CF-blocked detail pages once, then compile fresh-code pool with names."""
import json, re, time, os
import requests
from concurrent.futures import ThreadPoolExecutor
from html import unescape

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
RAW = os.path.join(WAVE, "team31_raw", "detail")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})")

fetched = json.load(open(os.path.join(WAVE, "team31_detail_fetch.json")))
blocked = [u for u, v in fetched.items() if v["status"] == 200 and v["len"] < 20000 and len(v["codes"]) == 0]
print("blocked detail pages to retry:", len(blocked), flush=True)

def fetch_one(url):
    s = requests.Session()
    for i in range(2):
        try:
            r = s.get(url, headers=UA, timeout=60)
            fn = re.sub(r"[^A-Za-z0-9]+", "_", url.replace("https://", ""))[:80] + ".html"
            open(os.path.join(RAW, fn), "w", encoding="utf-8").write(r.text)
            codes = list(dict.fromkeys(CODE_RE.findall(r.text)))
            print(f"OK {r.status_code} len={len(r.text)} codes={len(codes)} {url}", flush=True)
            return {"url": url, "status": r.status_code, "codes": codes, "len": len(r.text)}
        except Exception as e:
            print(f"FAIL try{i+1} {url} :: {str(e)[:100]}", flush=True)
            time.sleep(8)
    return {"url": url, "status": "transport-fail", "codes": [], "len": 0}

results = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(fetch_one, blocked):
        results[res["url"]] = res
json.dump(results, open(os.path.join(WAVE, "team31_detail_retry.json"), "w"), indent=1)
print("retry done:", sum(len(v["codes"]) for v in results.values()), "codes", flush=True)

# ---- compile pool: names = last "Join <name>" before each invite href ----
def names_from_html(html, source_url, default_cat):
    out = {}
    # find all anchor texts containing Join ... followed by href chat.whatsapp.com/CODE
    for m in re.finditer(r"(?:Join|JOIN)\s+([^<]{1,80}?)\s*(?:</[^>]+>\s*)?<a[^>]*href=\"https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})", html):
        name = re.sub(r"\s+", " ", unescape(m.group(1))).strip(" –-:—\t")
        out[m.group(2)] = name
    # fallback: plain-text "Join X" then href nearby (shopping page pattern has text then <a href>)
    for m in re.finditer(r"Join\s+([^<\n]{1,80}?)\s*[-–:]*\s*<a[^>]*href=\"https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})", html):
        name = re.sub(r"\s+", " ", unescape(m.group(1))).strip(" –-:—\t")
        out.setdefault(m.group(2), name)
    return out

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
pool = {}  # code -> {name, source, category_hint}
# shopping page
shop = open(os.path.join(WAVE, "team31_raw", "whatsagroupslinks_com_category_shopping_groups_.html"), encoding="utf-8", errors="ignore").read()
for code, name in names_from_html(shop, "shopping", "Buy & Sell").items():
    pool.setdefault(code, {"name": name, "source": "https://whatsagroupslinks.com/category/shopping-groups/", "cat_hint": "Buy & Sell"})
# all detail pages (both fetch rounds)
for fn in os.listdir(RAW):
    if not fn.endswith(".html") or fn.startswith("whatsagroupslinks_com_category_") or fn.startswith("www_") or fn.startswith("go_"):
        continue
    html = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read()
    slug = fn.replace("whatsagroupslinks_com_", "").replace("_.html", "").replace("_", "-")
    src = "https://whatsagroupslinks.com/" + slug + "/"
    for code, name in names_from_html(html, src, "").items():
        pool.setdefault(code, {"name": name, "source": src, "cat_hint": ""})
# also any code in detail htmls missed by name regex (bare hrefs)
for fn in os.listdir(RAW):
    if not fn.endswith(".html"):
        continue
    html = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read()
    for code in CODE_RE.findall(html):
        pool.setdefault(code, {"name": "", "source": "detail-html:" + fn, "cat_hint": ""})

fresh = {c: v for c, v in pool.items() if c not in union}
print("pool total:", len(pool), "fresh:", len(fresh), "in-union:", len(pool) - len(fresh), flush=True)
json.dump(pool, open(os.path.join(WAVE, "team31_pool.json"), "w"), indent=1)
json.dump(fresh, open(os.path.join(WAVE, "team31_fresh.json"), "w"), indent=1)
for c, v in sorted(fresh.items()):
    print(" FRESH", c, "|", repr(v["name"][:70]), "|", v["source"][:70], flush=True)
