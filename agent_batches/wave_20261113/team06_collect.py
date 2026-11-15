#!/usr/bin/env python3
"""team06 linkado collector: fetch listing pages, extract invite codes + metadata."""
import json, re, sys, time, os
from concurrent.futures import ThreadPoolExecutor
import urllib.request

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception as e:
        return None

def parse(html, url):
    if not html:
        return None
    codes = re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_\-]{15,})", html)
    title = ""
    m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    if m: title = m.group(1).strip()
    if not title:
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        if m: title = re.sub(r"\s+", " ", m.group(1)).strip()
    # category hints: linkado pages often show category text; grab meta keywords/description
    desc = ""
    m = re.search(r'<meta (?:name|property)="(?:description|og:description)" content="([^"]*)"', html)
    if m: desc = m.group(1).strip()
    return {"url": url, "title": title, "codes": sorted(set(codes)), "desc": desc[:300]}

def main(start, end):
    urls = open(os.path.join(WAVE, "team06_urls.txt")).read().splitlines()
    batch = urls[start:end]
    out_path = os.path.join(WAVE, f"team06_pages_{start}_{end}.json")
    results = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, res in enumerate(ex.map(lambda u: parse(fetch(u), u), batch)):
            if res is not None:
                results.append(res)
            if (i + 1) % 50 == 0:
                with open(out_path, "w") as f:
                    json.dump(results, f, ensure_ascii=False, indent=1)
                print(f"{i+1}/{len(batch)} fetched, {len(results)} ok, {sum(1 for r in results if r['codes'])} with codes, {time.time()-t0:.0f}s", flush=True)
    with open(out_path, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"DONE {start}-{end}: {len(results)} pages, {sum(1 for r in results if r['codes'])} with codes")

if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
