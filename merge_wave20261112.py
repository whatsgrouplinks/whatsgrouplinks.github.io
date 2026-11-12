#!/usr/bin/env python3
"""Merge wave 20261112 parent-clean batch into groups.json.
- Baseline 76,448
- REMOVE DiPrrTG7xdKB58iUQBk11l ('LGBT COVEN', merged Nov 11): live og:title
  verified by parent curl 2026-11-12 = 'novinhos libertinos' + fire/18+ emoji
  (minor-suggestive sexual content) -> hard-porn/xxx removal rule applies.
  Code STAYS in the dedupe union so it can never be re-added.
- ADD 7,196 parent-clean items (7,316 coordinator clean minus 120 casino/slots
  signal-platform groups dropped by parent adjudication).
- Expected final total: 76,448 - 1 + 7,196 = 83,643.
"""
import json, pickle, shutil, sys

BUILD = "/home/hatch/workspace/whatsapp-groups-site/"
WAVE = BUILD + "agent_batches/wave_20261112/"

groups = json.load(open(BUILD + "groups.json"))
print("baseline:", len(groups))
assert len(groups) == 76448, len(groups)

shutil.copyfile(BUILD + "groups.json", WAVE + "groups.json.bak-20261112-premerge")

REMOVE_CODE = "DiPrrTG7xdKB58iUQBk11l"
removed = [g for g in groups if g["invite"].rstrip("/").split("/")[-1] == REMOVE_CODE]
assert len(removed) == 1, removed
print("removing:", removed[0]["name"], removed[0]["invite"])
groups = [g for g in groups if g["invite"].rstrip("/").split("/")[-1] != REMOVE_CODE]

new = json.load(open(WAVE + "wave_20261112_clean_parent.json"))
print("new items:", len(new))
assert len(new) == 7196, len(new)

union = json.load(open(BUILD + ".existing_codes.json"))
union_set = set(union)
new_codes = [c["invite"].rstrip("/").split("/")[-1] for c in new]
assert len(set(new_codes)) == len(new_codes), "dup codes in new batch"
leaks = [c for c in new_codes if c in union_set]
assert not leaks, f"union leaks: {leaks[:5]}"
existing = {g["invite"].rstrip("/").split("/")[-1] for g in groups}
assert not (set(new_codes) & existing), "overlap with groups.json"

# schema check on new items
for c in new:
    assert isinstance(c.get("name"), str) and c["name"].strip(), c
    assert isinstance(c.get("category"), str) and c["category"].strip(), c
    assert c["invite"].startswith("https://chat.whatsapp.com/"), c
    assert isinstance(c.get("description"), str) and c["description"].strip(), c

groups.extend(new)
print("final total:", len(groups))
assert len(groups) == 83643, len(groups)
assert len({g["invite"].rstrip("/").split("/")[-1] for g in groups}) == len(groups)

json.dump(groups, open(BUILD + "groups.json", "w"), ensure_ascii=False)

union_set.update(new_codes)
assert REMOVE_CODE in union_set
union = sorted(union_set)
print("union size:", len(union))
assert len(union) == 119266, len(union)
json.dump(union, open(BUILD + ".existing_codes.json", "w"))
pickle.dump(union_set, open(BUILD + "dedup_codes.pkl", "wb"))
print("MERGE OK: 76448 - 1 removed + 7196 added = 83643")
