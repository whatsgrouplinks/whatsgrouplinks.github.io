#!/usr/bin/env python3
"""Merge wave 20261111 clean set into groups.json (repair run).
- Appends clean groups with slugs via generate.py's slugify(name, gid), gid = new index.
- image = '' (same as Nov-9 wave additions).
- Updates .existing_codes.json (sorted) and dedup_codes.pkl (set).
- Verifies counts before/after; writes a backup of groups.json first."""
import json, re, os, pickle, shutil

SITE = '/home/hatch/workspace/whatsapp-groups-site'
WAVE = os.path.join(SITE, 'agent_batches', 'wave_20261111')

def slugify(name, gid):
    s = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:50]
    return f"{s}-{gid}" if s else f"group-{gid}"

clean = json.load(open(os.path.join(WAVE, 'wave_20261111_clean.json')))
groups = json.load(open(os.path.join(SITE, 'groups.json')))
before = len(groups)
print('groups.json before:', before)
print('clean to merge:', len(clean))

# safety: re-check clean codes against current groups.json + union
existing_codes = {g['invite'].rstrip('/').split('/')[-1] for g in groups}
union = set(json.load(open(os.path.join(SITE, '.existing_codes.json'))))
leaks = [c for c in clean if c['invite'].split('/')[-1] in existing_codes or c['invite'].split('/')[-1] in union]
assert not leaks, f"LEAKS at merge time: {leaks}"
seen = set()
for c in clean:
    code = c['invite'].split('/')[-1]
    assert code not in seen, f"dup in clean: {code}"
    seen.add(code)

shutil.copy(os.path.join(SITE, 'groups.json'), os.path.join(WAVE, 'groups.json.bak-20261111-premerge'))
new_entries = []
for i, c in enumerate(clean):
    gid = before + i
    new_entries.append({
        'name': c['name'],
        'category': c['category'],
        'description': c['description'],
        'image': '',
        'invite': c['invite'],
        'country': c['country'],
        'slug': slugify(c['name'], gid),
    })
groups.extend(new_entries)
json.dump(groups, open(os.path.join(SITE, 'groups.json'), 'w'), indent=1, ensure_ascii=False)
after = len(json.load(open(os.path.join(SITE, 'groups.json'))))
print('groups.json after:', after)
assert after == before + len(clean), 'COUNT MISMATCH after merge'

# update dedup state
new_codes = sorted(union | {c['invite'].split('/')[-1] for c in clean})
json.dump(new_codes, open(os.path.join(SITE, '.existing_codes.json'), 'w'))
pickle.dump(set(new_codes), open(os.path.join(SITE, 'dedup_codes.pkl'), 'wb'))
print('.existing_codes.json now:', len(new_codes))
print('dedup_codes.pkl now:', len(set(new_codes)))
print('MERGE OK:', before, '->', after)
