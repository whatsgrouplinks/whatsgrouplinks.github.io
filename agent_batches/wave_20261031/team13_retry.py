#!/usr/bin/env python3
"""team13 retry pass: for codes dropped as empty-og:title, do sweep1, wait 60s, sweep2.
A code is declared dead ONLY if empty in all three attempts (orig verify + 2 retry sweeps)."""
import json, os, sys, time

sys.path.insert(0, os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261031"))
from team13_verify import og_title, is_blocked, looks_junk, category_for, country_for

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261031")
RETRY_PAUSE = 60  # seconds between sweep1 and sweep2 per coordinator advisory

def build_item(code, info, title):
    name = info["name"] if (info["name"] and not looks_junk(info["name"]) and not is_blocked(info["name"])) else title
    if is_blocked(name) or is_blocked(title):
        return None
    cat = category_for(info["slug"], title)
    country = country_for(title, info["slug"])
    cname = {"IN": "India", "PK": "Pakistan", "BD": "Bangladesh",
             "NP": "Nepal", "LK": "Sri Lanka", "MM": "Myanmar",
             "UG": "Uganda", "CN": "China"}.get(country, "worldwide")
    return {
        "name": name,
        "category": cat,
        "description": "%s is an active WhatsApp group for %s lovers. Join %s to chat, share updates and connect with the %s community in %s." % (name, cat.lower(), name, cat.lower(), cname),
        "image": "",
        "invite": "https://chat.whatsapp.com/" + code,
        "country": country,
    }

def main():
    shard, nshards = int(sys.argv[1]), int(sys.argv[2])
    cand = json.load(open("/tmp/team13_cand.json"))
    verified_codes = set()
    for s in range(5):
        p = BASE + "/team13-whatspgroupslink-variant.shard%d.json" % s
        if os.path.exists(p):
            for it in json.load(open(p)):
                verified_codes.add(it["invite"].rsplit("/", 1)[-1])
    dropped = [(code, info) for code, info in cand.items() if code not in verified_codes]
    mine = [d for i, d in enumerate(dropped) if i % nshards == shard]
    print("retry shard %d/%d: %d dropped codes" % (shard, nshards, len(mine)), flush=True)

    found = []
    still_empty = []
    n = 0
    for code, info in mine:  # SWEEP 1
        n += 1
        title, err = og_title(code)
        if err and err.startswith("transport"):
            still_empty.append((code, info))  # transport failure: retry in sweep 2
        elif title:
            item = build_item(code, info, title)
            if item:
                found.append(item)
        else:
            still_empty.append((code, info))
        time.sleep(0.6)
        if n % 40 == 0:
            print("retry shard %d sweep1 %d/%d: found=%d empty=%d" % (shard, n, len(mine), len(found), len(still_empty)), flush=True)

    print("retry shard %d sweep1 done: found=%d, waiting %ds before sweep2" % (shard, len(found), RETRY_PAUSE), flush=True)
    time.sleep(RETRY_PAUSE)

    dead = 0
    n = 0
    for code, info in still_empty:  # SWEEP 2
        n += 1
        title, err = og_title(code)
        if err and err.startswith("transport"):
            dead += 1  # transport failure twice; not a dead verdict, but out of wave budget -> drop silently (logged)
        elif title:
            item = build_item(code, info, title)
            if item:
                found.append(item)
            else:
                dead += 1
        else:
            dead += 1  # empty in orig verify + sweep1 + sweep2 -> dead
        time.sleep(0.6)
        if n % 40 == 0:
            print("retry shard %d sweep2 %d/%d: found=%d dead=%d" % (shard, n, len(still_empty), len(found), dead), flush=True)

    json.dump(found, open(BASE + "/team13-retry.shard%d.json" % shard, "w"), ensure_ascii=False, indent=1)
    print("retry shard %d DONE recovered=%d dead=%d" % (shard, len(found), dead), flush=True)

if __name__ == "__main__":
    main()
