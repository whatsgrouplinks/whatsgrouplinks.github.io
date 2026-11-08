"""Team 13: build appgrouplink candidate pool.
- Today's re-fetch (ag_raw.json): all (name, code, slug) with code not in union.
- Nov 4 legacy (team18_raw.json): codes not in union, not in today's fetch,
  that were never-attempted or rate-limited-pending on Nov 4.
Dedupe by code (today's record wins). Writes team13_state/candidates_ag.json.
"""
import json, os

WORK = os.path.dirname(os.path.abspath(__file__))
WAVE8 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108"
WAVE4 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"

union = set(json.load(open(os.path.join(WAVE8, "dedupe_union.json"))))
print("union:", len(union))

cands = {}  # code -> {name, code, slug, source}

# today's fetch first (preferred records)
ag = json.load(open(os.path.join(WORK, "ag_raw.json")))
n_today = 0
for slug, v in ag["pages"].items():
    for name, code in v.get("pairs", []):
        if len(code) < 20 or len(code) > 24:
            continue
        if code in union:
            continue
        if code not in cands:
            cands[code] = {"name": name, "code": code, "slug": slug, "source": "appgrouplink"}
            n_today += 1
print("today fresh vs union:", n_today)

# Nov 4 legacy: verified + pending sets
v4 = json.load(open(os.path.join(WAVE4, "team18_verified_raw.json")))
p4 = json.load(open(os.path.join(WAVE4, "team18_pending_raw.json")))
vc = {it["code"] for it in v4}
pc = {it["code"] for it in p4}
raw4 = json.load(open(os.path.join(WAVE4, "team18_raw.json")))
n_leg = 0
for slug, v in raw4["pages"].items():
    for name, code in v.get("pairs", []):
        if code in union or code in cands:
            continue
        if code in vc:
            continue  # verified Nov 4 but not in union (28) — was dropped in merge; recheck? include as legacy
        if code in pc or True:
            # never-attempted (521) + rate-limited pending (495) + verified-not-in-union (28)
            cands[code] = {"name": name, "code": code, "slug": slug, "source": "appgrouplink-nov4"}
            n_leg += 1
print("legacy added:", n_leg)
print("total AG candidates:", len(cands))
json.dump(list(cands.values()), open(os.path.join(WORK, "candidates_ag.json"), "w"), ensure_ascii=False)
