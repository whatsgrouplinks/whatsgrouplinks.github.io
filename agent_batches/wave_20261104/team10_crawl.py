#!/usr/bin/env python3
"""Team10 listing crawler: pages 1..150, 90s timeout, 3 attempts/page, per-page record."""
import json, re, time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"

def fetch_listing(page):
    for attempt in range(3):
        s = requests.Session()
        s.headers.update({"User-Agent": UA})
        try:
            r = s.get("https://linkado.app/categoria/amizade?page=%d" % page, timeout=90)
            if r.status_code == 200:
                ids = sorted(set(re.findall(r'/grupo/([a-f0-9]{24})', r.text)))
                return (page, ids, None)
            if r.status_code == 429:
                time.sleep(10)
        except Exception as e:
            time.sleep(5)
        finally:
            s.close()
    return (page, [], "failed")

def main():
    print("Crawling 150 listing pages...", flush=True)
    per_page = {}
    all_ids = []
    seen = set()
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(fetch_listing, p): p for p in range(1, 151)}
        done = 0
        for f in as_completed(futs):
            page, ids, err = f.result()
            done += 1
            per_page[str(page)] = {"n": len(ids), "err": err}
            for i in ids:
                if i not in seen:
                    seen.add(i); all_ids.append(i)
            if done % 25 == 0:
                print("  %d/150 pages, %d unique ids" % (done, len(all_ids)), flush=True)
    json.dump(all_ids, open(WAVE + "/team10-ids.json", "w"))
    json.dump(per_page, open(WAVE + "/team10-pages.json", "w"))
    failed = [p for p, v in per_page.items() if v["err"]]
    print("TOTAL_IDS=%d FAILED_PAGES=%d (%s)" % (len(all_ids), len(failed), ",".join(sorted(failed, key=int))), flush=True)

if __name__ == "__main__":
    main()
