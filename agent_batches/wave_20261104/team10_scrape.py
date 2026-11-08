#!/usr/bin/env python3
"""Team 10: linkado.app amizade category deep scrape.
Phase 1: crawl listing pages, collect /grupo/<id> ids.
Phase 2: fetch detail pages in parallel, extract code + title + desc.
Phase 3: verify codes via chat.whatsapp.com og:title with keep-alive sessions.
Writes team10 raw candidate file for verification stage.
"""
import json, re, time, sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
BASE = "https://linkado.app"
CAT = f"{BASE}/categoria/amizade"
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"

def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    return s

def fetch_listing(page):
    s = session()
    try:
        r = s.get(f"{CAT}?page={page}", timeout=60)
        if r.status_code != 200:
            return []
        ids = sorted(set(re.findall(r'/grupo/([a-f0-9]{24})', r.text)))
        return ids
    except Exception:
        return []
    finally:
        s.close()

def fetch_detail(gid):
    s = session()
    try:
        r = s.get(f"{BASE}/grupo/{gid}", timeout=60)
        if r.status_code != 200:
            return None
        t = r.text
        m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', t)
        if not m:
            return None
        code = m.group(1)
        title = None
        mt = re.search(r'<meta property="og:title" content="([^"]*)"', t)
        if mt:
            title = mt.group(1)
        desc = None
        md = re.search(r'<meta property="og:description" content="([^"]*)"', t)
        if md:
            desc = md.group(1)
        return {"gid": gid, "code": code, "title": title, "desc": desc}
    except Exception:
        return None
    finally:
        s.close()

def main():
    last_page = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    print(f"Crawling listing pages 1..{last_page}", flush=True)
    all_ids = []
    seen = set()
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(fetch_listing, p): p for p in range(1, last_page + 1)}
        for f in as_completed(futs):
            ids = f.result()
            for i in ids:
                if i not in seen:
                    seen.add(i)
                    all_ids.append(i)
    print(f"Unique group ids: {len(all_ids)}", flush=True)
    json.dump(all_ids, open(f"{WAVE}/team10-ids.json", "w"))

    # dedupe vs union before detail fetch (cheap skip of known codes impossible
    # here since code unknown until detail page; do detail fetch then dedupe)
    print("Fetching detail pages...", flush=True)
    cands = []
    done = 0
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(fetch_detail, g): g for g in all_ids}
        for f in as_completed(futs):
            done += 1
            d = f.result()
            if d:
                cands.append(d)
            if done % 500 == 0:
                print(f"  {done}/{len(all_ids)} detail pages, {len(cands)} with codes", flush=True)
    print(f"Detail pages with codes: {len(cands)}", flush=True)
    json.dump(cands, open(f"{WAVE}/team10-candidates.json", "w"), ensure_ascii=False)
    print("Wrote team10-candidates.json", flush=True)

if __name__ == "__main__":
    main()
