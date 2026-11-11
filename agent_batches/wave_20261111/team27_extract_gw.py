#!/usr/bin/env python3
"""Team27: extract groupwa.link wagd cards + virenial_yt (0 codes) into pool2."""
import json, re, os, html, sys

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
RAW = os.path.join(WAVE, "team27_raw")
UNION = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
POOL1 = set(json.load(open(os.path.join(WAVE, "team27_pool.json"))).keys())

CATMAP = {"jobs": "Jobs", "education": "Education", "gaming": "Gaming",
          "news": "News", "islamic": "Islamic", "sports": "Sports",
          "health": "Health", "movies": "Entertainment", "cricket": "Sports",
          "online-earning": "Online Earning", "gallery": "Community & Social"}

CARD_RE = re.compile(
    r'<div class="wagd-card"[^>]*data-name="([^"]*)"[^>]*data-cat="([^"]*)"[^>]*data-desc="([^"]*)"[^>]*data-link="https://chat\.whatsapp\.com/([A-Za-z0-9]{22})"',
    re.S)

out = {}
for fname in sorted(os.listdir(RAW)):
    if not fname.startswith("gw_") or not fname.endswith(".html"):
        continue
    slug = fname[3:-5]
    raw = open(os.path.join(RAW, fname), encoding="utf-8", errors="ignore").read()
    for m in CARD_RE.finditer(raw):
        name, cat, desc, code = (html.unescape(x) for x in m.groups())
        name = name.strip()
        if name.lower() in ("whatsapp group", ""):
            name = ""
        cat = CATMAP.get(slug, cat if cat in CATMAP.values() else "Community & Social")
        if code not in out:
            out[code] = {"name": name, "category": cat, "country": "",
                         "description": desc.strip()[:200],
                         "invite": "https://chat.whatsapp.com/" + code,
                         "source": fname}
fresh = {c: v for c, v in out.items() if c not in UNION and c not in POOL1}
print(f"groupwa total unique: {len(out)}; fresh (not union, not pool1): {len(fresh)}; "
      f"in-union: {len([c for c in out if c in UNION])}; in-pool1: {len([c for c in out if c in POOL1])}", file=sys.stderr)
json.dump(fresh, open(os.path.join(WAVE, "team27_pool2.json"), "w"), ensure_ascii=False, indent=1)
for c, v in sorted(fresh.items()):
    print(c, "|", v["category"], "|", repr(v["name"])[:60], "|", v["description"][:60], "|", v["source"])
