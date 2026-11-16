#!/usr/bin/env python3
"""Merge wave 20261116 parent-adjudicated clean set into groups.json.
Parent clean = coordinator clean (10,735) - 18 parent-screen drops - 1 spot-dead = 10,716.
- Appends with slugs via generate.py's slugify(name, gid), gid = new index.
- Updates .existing_codes.json (sorted) and dedup_codes.pkl (set).
- Verifies counts before/after; backs up groups.json first."""
import json, re, os, pickle, shutil

SITE = '/home/hatch/workspace/whatsapp-groups-site'
WAVE = os.path.join(SITE, 'agent_batches', 'wave_20261116')

def slugify(name, gid):
    s = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:50]
    return f"{s}-{gid}" if s else f"group-{gid}"

clean = json.load(open(os.path.join(WAVE, 'wave_20261116_clean_parent.json')))
groups = json.load(open(os.path.join(SITE, 'groups.json')))
before = len(groups)
print('groups.json before:', before)
print('clean to merge:', len(clean))

existing_codes = {g['invite'].rstrip('/').split('/')[-1] for g in groups if g.get('invite')}
union = set(json.load(open(os.path.join(SITE, '.existing_codes.json'))))
leaks = [c for c in clean if c['invite'].split('/')[-1] in existing_codes or c['invite'].split('/')[-1] in union]
assert not leaks, f"LEAKS at merge time: {leaks[:10]} ({len(leaks)})"
seen = set()
for c in clean:
    code = c['invite'].split('/')[-1]
    assert code not in seen, f"dup in clean: {code}"
    seen.add(code)
# schema check
for c in clean:
    assert c.get('name') and c.get('invite') and c['invite'].startswith('https://chat.whatsapp.com/')
    assert c.get('category') and c.get('description')

shutil.copy(os.path.join(SITE, 'groups.json'), os.path.join(WAVE, 'groups.json.bak-20261116-premerge'))
new_entries = []
for i, c in enumerate(clean):
    gid = before + i
    new_entries.append({
        'name': c['name'],
        'category': c['category'],
        'description': c['description'],
        'image': c.get('image', ''),
        'invite': c['invite'],
        'country': c.get('country', ''),
        'slug': slugify(c['name'], gid),
    })
groups.extend(new_entries)
json.dump(groups, open(os.path.join(SITE, 'groups.json'), 'w'), indent=1, ensure_ascii=False)
after = len(json.load(open(os.path.join(SITE, 'groups.json'))))
print('groups.json after:', after)
assert after == before + len(clean), 'COUNT MISMATCH after merge'

new_codes = sorted(union | {c['invite'].split('/')[-1] for c in clean})
json.dump(new_codes, open(os.path.join(SITE, '.existing_codes.json'), 'w'))
pickle.dump(set(new_codes), open(os.path.join(SITE, 'dedup_codes.pkl'), 'wb'))
print('.existing_codes.json now:', len(new_codes))
print('MERGE OK:', before, '->', after)
