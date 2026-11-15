#!/usr/bin/env python3
"""team29: retry pages that errored in first mining pass; merge into mined set."""
import json, re, os, time
import requests
from team29_lib import S, fetch

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})')
mined = json.load(open(os.path.join(WAVE, "team29-mined-set.json")))

RETRY = [
    "https://instantgrouplink.com/single-girl-whatsapp-group-links/",
    "https://instantgrouplink.com/usa-whatsapp-group-links/",
    "https://wagroupshub.com/page/2/",
    "https://activewagroup.com/page/2/",
    "https://whatzgrouplink.com/",
    "https://whatzgrouplink.com/jobs-whatsapp-group-links/",
    "https://whatzgrouplink.com/education-whatsapp-group-links/",
    "https://techsslash.com/",
]
for url in RETRY:
    ok = False
    for attempt in range(3):
        try:
            r = fetch(url)
            codes = sorted(set(CODE_RE.findall(r.text)))
            print(url, "HTTP", r.status_code, "codes:", len(codes), flush=True)
            for c in codes:
                idx = r.text.find(c)
                ctx = re.sub(r'\s+', ' ', r.text[max(0, idx-160):idx+30])[-200:]
                mined.setdefault(c, {"sources": [], "context": ctx})
                if url not in mined[c]["sources"]:
                    mined[c]["sources"].append(url)
            ok = True
            break
        except Exception as e:
            print(url, "attempt", attempt+1, "ERROR", type(e).__name__, flush=True)
            time.sleep(8)
    if not ok:
        print(url, "FAILED all retries", flush=True)
    time.sleep(2)

json.dump(mined, open(os.path.join(WAVE, "team29-mined-set.json"), "w"), indent=1)
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
fresh = {c: v for c, v in mined.items() if c not in union}
print("TOTAL mined:", len(mined), "FRESH:", len(fresh), flush=True)
json.dump(fresh, open(os.path.join(WAVE, "team29-fresh-raw.json"), "w"), indent=1)
