#!/usr/bin/env python3
"""Coordinator live spot re-check: sample verified codes from the clean file,
GET chat.whatsapp.com/<code> with browser UA (plain, then ?_fb_noscript=1
fallback on empty og:title). 4 workers, 30s timeout. Writes sample_recheck.json."""
import json, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261107")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OG = re.compile(r'og:title[^>]*content="([^"]*)"')

clean = json.load(open(os.path.join(WAVE, "wave_20261107_verified_clean.json")))
prov = json.load(open(os.path.join(WAVE, "wave_20261107_verified_clean_provenance.json")))
# sample: up to 2 per team file, deterministic (first items in clean order per team)
by_team = {}
for e in clean:
    code = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})", e["invite"]).group(1)
    by_team.setdefault(prov[code], []).append((code, e["name"]))
sample = []
for team in sorted(by_team):
    sample.extend(by_team[team][:2])
print("sample size:", len(sample))

def check(item):
    code, name = item
    for variant in ("", "?_fb_noscript=1"):
        try:
            r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "30",
                                f"https://chat.whatsapp.com/{code}{variant}"],
                               capture_output=True, text=True, timeout=40)
            m = OG.search(r.stdout or "")
            title = (m.group(1) if m else "").strip()
            if title:
                return {"code": code, "name": name, "live": True,
                        "method": "plain" if variant == "" else "fb_noscript",
                        "og_title": title[:120]}
        except Exception as ex:
            return {"code": code, "name": name, "live": False, "method": "transport-error",
                    "og_title": "", "error": str(ex)[:100]}
    return {"code": code, "name": name, "live": False, "method": "empty-og-title-both-variants",
            "og_title": ""}

with ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(check, sample))
live = [r for r in results if r["live"]]
print(f"live: {len(live)}/{len(results)}")
print("plain:", sum(1 for r in live if r["method"] == "plain"),
      "fb_noscript-only:", sum(1 for r in live if r["method"] == "fb_noscript"))
for r in results:
    if not r["live"]:
        print("NOT-LIVE:", r["code"], r["name"][:50], r["method"])
with open(os.path.join(WAVE, "sample_recheck.json"), "w") as f:
    json.dump({"sample_size": len(sample), "live": len(live),
               "live_plain": sum(1 for r in live if r["method"] == "plain"),
               "live_fb_noscript_only": sum(1 for r in live if r["method"] == "fb_noscript"),
               "results": results}, f, indent=1, ensure_ascii=False)
