#!/usr/bin/env python3
"""team29: attempt grupbul /redirect resolution on a sample; inspect for JS target."""
import json, re, os, time
from team29_lib import S, fetch

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
groups = json.load(open(os.path.join(WAVE, "team29-grupbul-groups.json")))
# test first redirect of 5 diverse gids
sample = [g for g in groups if g["gid"] in ("621903", "419221", "320563", "113756", "175618")]
res = []
for g in sample:
    red = g["redirects"][0]
    url = "https://grupbul.com" + red
    try:
        r = S.get(url, timeout=60, allow_redirects=True)
        hist = [(h.status_code, h.headers.get("Location")) for h in r.history]
        codes = sorted(set(re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})', r.text)))
        # look for JS countdown / data-url / meta refresh
        meta = re.findall(r'url=([^"\'>]+)', r.text, re.I)
        jsurl = re.findall(r'(?:redirect|target|href|url)\s*[:=]\s*["\']([^"\']+)["\']', r.text, re.I)[:8]
        res.append({"gid": g["gid"], "redirect": red, "final_url": r.url,
                    "http": r.status_code, "history": hist, "codes": codes,
                    "meta_refresh": meta[:3], "js_urls": jsurl,
                    "len": len(r.text)})
        print(g["gid"], r.status_code, "final:", r.url, "hist:", hist,
              "codes:", codes, "meta:", meta[:3], "js:", jsurl, flush=True)
    except Exception as e:
        res.append({"gid": g["gid"], "redirect": red, "error": repr(e)})
        print(g["gid"], "ERROR", repr(e), flush=True)
    time.sleep(2)

json.dump(res, open(os.path.join(WAVE, "team29-redirect-probe.json"), "w"), indent=1)
