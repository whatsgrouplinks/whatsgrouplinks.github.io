"""Team24 wave 20261112: dedupe mined candidates vs .existing_codes.json union.
Writes team24_fresh12.json ({code: {code, page, name}}) for codes NOT in the union.
Also reports counts and how many mined codes were already known.
"""
import json

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
cands = json.load(open(W + "team24_candidates12.json"))
fresh = {}
known = 0
for code, v in cands.items():
    if code in existing:
        known += 1
    else:
        fresh[code] = v
json.dump(fresh, open(W + "team24_fresh12.json", "w"), indent=1, ensure_ascii=False)
print(f"mined unique codes: {len(cands)}")
print(f"already in union: {known}")
print(f"fresh (not in union): {len(fresh)}")
named = sum(1 for v in fresh.values() if v.get("name"))
print(f"fresh with name: {named}, without name: {len(fresh)-named}")
for code, v in fresh.items():
    print(" ", code, repr(v.get("name", ""))[:80], v.get("page", ""))
