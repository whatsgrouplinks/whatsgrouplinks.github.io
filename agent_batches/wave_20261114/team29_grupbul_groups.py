#!/usr/bin/env python3
"""team29: fetch all grupbul group pages found in re-check, extract names + /redirect URLs,
attempt redirect resolution."""
import json, re, os, time
from team29_lib import S, fetch

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
pages = json.load(open(os.path.join(WAVE, "team29-grupbul-pages.json")))
gids = {}
for cat, d in pages.items():
    for g in d["union"]:
        gids[g] = cat
gids["621903"] = "carried-team21"
gids["419221"] = "carried-team21"

out = []
for gid, cat in sorted(gids.items()):
    url = f"https://grupbul.com/group/{gid}"
    try:
        r = fetch(url)
        html_text = r.text
        # group name: <title> or h1
        m = re.search(r'<title>(.*?)</title>', html_text, re.S | re.I)
        title = re.sub(r'\s+', ' ', m.group(1)).strip() if m else ""
        reds = sorted(set(re.findall(r'/redirect/(\d+)/(\d+)', html_text)))
        codes = sorted(set(re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})', html_text)))
        out.append({"gid": gid, "category": cat, "http": r.status_code,
                    "title": title, "redirects": [f"/redirect/{a}/{b}" for a, b in reds],
                    "direct_codes": codes})
        print(gid, cat, r.status_code, "|", title[:70], "| redirects:", len(reds), "codes:", codes, flush=True)
    except Exception as e:
        out.append({"gid": gid, "category": cat, "error": repr(e)})
        print(gid, "ERROR", repr(e), flush=True)
    time.sleep(1.5)

json.dump(out, open(os.path.join(WAVE, "team29-grupbul-groups.json"), "w"), indent=1)
print("saved", len(out), "group pages")
