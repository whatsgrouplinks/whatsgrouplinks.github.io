#!/usr/bin/env python3
"""TEAM31 phase 2: fetch whatsagroupslinks detail posts + retry CF-challenged category pages + cazajobz wp-json."""
import json, re, time, os
import requests
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
RAW = os.path.join(WAVE, "team31_raw", "detail")
os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})")

posts = json.load(open(os.path.join(WAVE, "team31_detail_posts.json")))
# keep only *-whatsapp-group-links/ slugs (group lists), drop blog articles/pages
detail = sorted([u for u in posts if re.search(r"whatsapp-group-links?/?$", u)])
print("detail posts:", len(detail), flush=True)

cf_retry = [f"https://whatsagroupslinks.com/category/{c}/" for c in
            ["fashion","finance","gaming-groups","health","lifestyle","news","social-media","sports","study-groups","technology"]]
extra = ["https://www.whatsapplink.cazajobz.com/wp-json/wp/v2/posts/814",
         "https://go.tuxmat.com/total-ask/bahrain-whatsapp-group-links-2024-join-now-1767648724"]

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
            print(f"FAIL try{i+1} {url} :: {str(e)[:120]}", flush=True)
            time.sleep(8)
    return {"url": url, "status": "transport-fail", "codes": [], "len": 0}

results = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(fetch_one, detail):
        results[res["url"]] = res
json.dump(results, open(os.path.join(WAVE, "team31_detail_fetch.json"), "w"), indent=1)
print("phase2a done:", sum(len(v["codes"]) for v in results.values()), "codes total", flush=True)

results2 = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(fetch_one, cf_retry + extra):
        results2[res["url"]] = res
json.dump(results2, open(os.path.join(WAVE, "team31_retry_fetch.json"), "w"), indent=1)
print("phase2b done", flush=True)
