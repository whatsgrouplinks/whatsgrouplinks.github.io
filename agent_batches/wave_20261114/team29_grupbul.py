#!/usr/bin/env python3
"""team29 grupbul re-check: fetch category pages, extract gids, diff vs Nov-13 baseline."""
import json, re, os, time
from team29_lib import S, fetch, og_title

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
CATS = {
    "chat-friendship": "https://grupbul.com/en/category/whatsapp/15/chat-friendship",
    "food": "https://grupbul.com/en/category/whatsapp/53/food",
    "job-postings": "https://grupbul.com/en/category/whatsapp/9/job-postings",
    "sport": "https://grupbul.com/en/category/whatsapp/4/sport",
}
BASELINE = {
    "chat-friendship": {"count": 27, "known": set()},
    "food": {"count": 0, "known": set()},
    "job-postings": {"count": 3, "known": {"320563", "503833", "977190"}},
    "sport": {"count": 1, "known": {"113756"}},
}
KNOWN_ALL = {"621903", "419221", "320563", "503833", "977190", "113756"}

result = {}
for cat, base in CATS.items():
    gids = {}
    for page in (1, 2):
        url = base if page == 1 else base + "?page=2"
        try:
            r = fetch(url)
            found = set(re.findall(r'/group/(\d+)', r.text))
            # also grab names near links
            gids[page] = sorted(found)
            print(cat, "p%d" % page, "HTTP", r.status_code, "gids:", len(found), flush=True)
        except Exception as e:
            print(cat, "p%d ERROR" % page, repr(e), flush=True)
            gids[page] = []
        time.sleep(2)
    allg = set(gids.get(1, [])) | set(gids.get(2, []))
    result[cat] = {"pages": gids, "union": sorted(allg),
                   "baseline_count": BASELINE[cat]["count"],
                   "new_gids": sorted(allg - KNOWN_ALL - BASELINE[cat]["known"]),
                   "removed_vs_known": sorted(BASELINE[cat]["known"] - allg)}
    print(cat, "union", len(allg), "new-vs-known:", result[cat]["new_gids"], flush=True)

json.dump(result, open(os.path.join(WAVE, "team29-grupbul-pages.json"), "w"), indent=1)
print("saved team29-grupbul-pages.json")
