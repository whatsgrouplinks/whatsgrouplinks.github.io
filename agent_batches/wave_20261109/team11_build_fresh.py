#!/usr/bin/env python3
"""Team 11: build team11_fresh_codes.json from team11_gi_rules.json.
Keep entries with a code, not a channel, code not in .existing_codes.json
and not in Nov 8 team13 gi codes; dedupe by code within batch (first wins).
Also writes team11_fetch_stats.json."""
import json, os
WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
rules = json.load(open(os.path.join(WAVE, "team11_gi_rules.json")))
enum = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team13_state/gi_enum.json"))
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))
gi13 = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team13_state/gi_rules.json"))
gi13_codes = {v["code"] for v in gi13.values() if v.get("code")}

# slice order = enum order indices 1000..2670
slugs = list(enum.keys())[1000:2671]
stats = {"slice_total": len(slugs), "fetched": 0, "with_code": 0, "channel": 0,
         "no_code": 0, "dup_existing": 0, "dup_nov8": 0, "dup_batch": 0, "fresh": 0}
fresh, seen = [], set()
for slug in slugs:
    rec = rules.get(slug)
    if not rec:
        continue
    stats["fetched"] += 1
    if rec.get("channel"):
        stats["channel"] += 1
        continue
    code = rec.get("code") or ""
    if not code:
        stats["no_code"] += 1
        continue
    stats["with_code"] += 1
    if code in existing:
        stats["dup_existing"] += 1
        continue
    if code in gi13_codes:
        stats["dup_nov8"] += 1
        continue
    if code in seen:
        stats["dup_batch"] += 1
        continue
    seen.add(code)
    fresh.append({"name": rec.get("name", ""), "code": code, "slug": slug,
                  "source": "groupsinvite", "category_slug": rec.get("category_slug", ""),
                  "country_slug": rec.get("country_slug", ""),
                  "description": rec.get("description", "")})
    stats["fresh"] += 1
json.dump(fresh, open(os.path.join(WAVE, "team11_fresh_codes.json"), "w"), ensure_ascii=False, indent=1)
json.dump(stats, open(os.path.join(WAVE, "team11_fetch_stats.json"), "w"), indent=1)
print(stats)
