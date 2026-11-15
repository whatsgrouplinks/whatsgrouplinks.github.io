#!/usr/bin/env python3
"""Merge wave 20261114 parent-clean batch into groups.json.
- Baseline 83,643
- REMOVE FIXIB8ohQzKAALAwNu1jTO ('NOVAS AMIZADES', merged Nov 12): parent curl
  2026-11-14 verified live og:title 'NUDS NA DESCRICAO' (nudes promotion)
  -> hard-porn/xxx removal rule applies. Code STAYS in the dedupe union.
  (The other 11 wave12 weak-signal codes re-checked LIVE on 2026-11-14 — the
  earlier empty og:title verdicts were an intermittent-serving artifact; NOT removed.)
- ADD 2,158 parent-clean items (coordinator clean; parent spot-verify 35/35 live,
  controls PASS; team24's 7 borderline kept per narrow hard-porn-only rule).
- Expected final total: 83,643 - 1 + 2,158 = 85,800.
- Union rebuilt as old union | post-merge groups.json codes | clean codes
  (heals the wave13 gap flagged by the coordinator; removed code stays in union).
"""
import json, pickle, shutil

BUILD = "/home/hatch/workspace/whatsapp-groups-site/"
WAVE = BUILD + "agent_batches/wave_20261114/"

groups = json.load(open(BUILD + "groups.json"))
print("baseline:", len(groups))
assert len(groups) == 83643, len(groups)

shutil.copyfile(BUILD + "groups.json", WAVE + "groups.json.bak-20261114-premerge")

REMOVE_CODE = "FIXIB8ohQzKAALAwNu1jTO"
removed = [g for g in groups if g["invite"].rstrip("/").split("/")[-1] == REMOVE_CODE]
assert len(removed) == 1, removed
print("removing:", removed[0]["name"], removed[0]["invite"])
groups = [g for g in groups if g["invite"].rstrip("/").split("/")[-1] != REMOVE_CODE]

new = json.load(open(WAVE + "wave_20261114_clean.json"))
print("new items:", len(new))
assert len(new) == 2158, len(new)

union = json.load(open(BUILD + ".existing_codes.json"))
union_set = set(union)
print("union before:", len(union_set))
new_codes = [c["invite"].rstrip("/").split("/")[-1] for c in new]
assert len(set(new_codes)) == len(new_codes), "dup codes in new batch"
leaks = [c for c in new_codes if c in union_set]
assert not leaks, f"union leaks: {leaks[:5]}"
existing = {g["invite"].rstrip("/").split("/")[-1] for g in groups}
assert not (set(new_codes) & existing), "overlap with groups.json"

for c in new:
    assert isinstance(c.get("name"), str) and c["name"].strip(), c
    assert isinstance(c.get("category"), str) and c["category"].strip(), c
    assert c["invite"].startswith("https://chat.whatsapp.com/"), c
    assert isinstance(c.get("description"), str) and c["description"].strip(), c

groups.extend(new)
print("final total:", len(groups))
assert len(groups) == 85800, len(groups)
assert len({g["invite"].rstrip("/").split("/")[-1] for g in groups}) == len(groups)

json.dump(groups, open(BUILD + "groups.json", "w"), ensure_ascii=False)

union_set.update(new_codes)
union_set.update(g["invite"].rstrip("/").split("/")[-1] for g in groups)
assert REMOVE_CODE in union_set
union = sorted(union_set)
print("union size:", len(union))
json.dump(union, open(BUILD + ".existing_codes.json", "w"))
pickle.dump(union_set, open(BUILD + "dedup_codes.pkl", "wb"))
print("MERGE OK: 83643 - 1 removed + 2158 added = 85800")
