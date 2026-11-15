#!/usr/bin/env python3
"""team29: mine overflow sites' newest pages; extract chat.whatsapp.com codes (incl /invite/)."""
import json, re, os, time
from team29_lib import S, fetch

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UNION = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
union = set(json.load(open(UNION)))
print("union size:", len(union), flush=True)

URLS = [
    # groupwa.link
    "https://groupwa.link/",
    "https://groupwa.link/jobs/",
    "https://groupwa.link/education/",
    "https://groupwa.link/cricket/",
    "https://groupwa.link/business/",
    "https://groupwa.link/entertainment/",
    "https://groupwa.link/page/2/",
    "https://groupwa.link/jobs/page/2/",
    # instantgrouplink
    "https://instantgrouplink.com/",
    "https://instantgrouplink.com/single-girl-whatsapp-group-links/",
    "https://instantgrouplink.com/tamil-whatsapp-group-links/",
    "https://instantgrouplink.com/usa-whatsapp-group-links/",
    "https://instantgrouplink.com/sri-lanka-whatsapp-group-links/",
    # wagroupshub / activewagroup
    "https://wagroupshub.com/",
    "https://wagroupshub.com/page/2/",
    "https://activewagroup.com/",
    "https://activewagroup.com/page/2/",
    # whatzgrouplink
    "https://whatzgrouplink.com/football-whatsapp-group-links/",
    "https://whatzgrouplink.com/",
    "https://whatzgrouplink.com/cricket-whatsapp-group-links/",
    "https://whatzgrouplink.com/jobs-whatsapp-group-links/",
    "https://whatzgrouplink.com/girls-whatsapp-group-links/",
    "https://whatzgrouplink.com/education-whatsapp-group-links/",
    # techsslash
    "https://techsslash.com/kenya-whatsapp-group-links/",
    "https://techsslash.com/",
]

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})')

mined = {}  # code -> {sources:[], contexts:[]}
for url in URLS:
    try:
        r = fetch(url)
        codes = CODE_RE.findall(r.text)
        uniq = sorted(set(codes))
        print(url, "HTTP", r.status_code, "codes:", len(uniq), flush=True)
        for c in uniq:
            # context: 80 chars before the code occurrence
            idx = r.text.find(c)
            ctx = re.sub(r'\s+', ' ', r.text[max(0, idx-160):idx+30])[-200:]
            mined.setdefault(c, {"sources": [], "context": ctx})
            if url not in mined[c]["sources"]:
                mined[c]["sources"].append(url)
    except Exception as e:
        print(url, "ERROR", repr(e), flush=True)
    time.sleep(1.5)

json.dump(mined, open(os.path.join(WAVE, "team29-mined-set.json"), "w"), indent=1)
fresh = {c: v for c, v in mined.items() if c not in union}
dupes = {c: v for c, v in mined.items() if c in union}
print("TOTAL mined:", len(mined), "dupes vs union:", len(dupes), "FRESH:", len(fresh), flush=True)
for c in sorted(fresh):
    print("FRESH", c, mined[c]["sources"], "|", mined[c]["context"][-120:], flush=True)
json.dump(fresh, open(os.path.join(WAVE, "team29-fresh-raw.json"), "w"), indent=1)
