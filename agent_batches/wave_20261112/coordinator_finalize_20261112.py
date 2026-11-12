#!/usr/bin/env python3
"""Wave 20261112 coordinator finalize — spot-verify drops + name fixes.
Spot-check: 43 sampled, 42 live, 1 dead, 0 pending.
- DROP dead: t30 KzJBW7FX9Ng44olQ6Ibz6D 'Pakistan Mall' (empty og:title x2).
- NAME FIXES (banked name was a directory listing-page title, not the group
  name; og:title is the real group name):
  - t06 KuEzkA15lu1CX8y4H1MrOd: 'Malaysia WhatsApp Group Links 2026 – Jobs,
    Students & Community (Verified)' -> 'Bachelor in Accounting (SFMCH/ SBSCH)'
  - t06 GKeNQz9jXIC80FoHF410CM: '1850+ Entertainment WhatsApp Group Links
    2026 | Join Now' -> 'Zambia investment' (generic investment name, kept;
    flagged in manifest)
  - t01 JaQbUSDjTS4E6pOx9UJpja: truncated 'INVESTIDOR INTELIGENT...' ->
    'Investidor inteligente #2'
Descriptions re-templated to 'Join <name>, ...' after each rename.
"""
import json, html, os

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112'
clean = json.load(open(os.path.join(WAVE_DIR, 'wave_20261112_clean.json')))
teams = json.load(open(os.path.join(WAVE_DIR, 'wave_20261112_clean_teams.json')))
state = json.load(open(os.path.join(WAVE_DIR, 'coordinator_verify_state_20261112.json')))

DROP = ['KzJBW7FX9Ng44olQ6Ibz6D']
FIX = {
    'KuEzkA15lu1CX8y4H1MrOd': 'Bachelor in Accounting (SFMCH/ SBSCH)',
    'GKeNQz9jXIC80FoHF410CM': 'Zambia investment',
    'JaQbUSDjTS4E6pOx9UJpja': 'Investidor inteligente #2',
}
drops = []
out = []
for it in clean:
    code = it['invite'].split('/')[-1]
    if code in DROP:
        drops.append({'code': code, 'team': teams.get(code), 'name': it['name'],
                      'reason': 'coordinator spot-verify: dead (empty og:title on 2 spaced checks)'})
        print('DROPPED dead:', code, it['name'])
        continue
    if code in FIX:
        old = it['name']
        it['name'] = html.unescape(FIX[code])
        it['description'] = f"Join {it['name']}, a WhatsApp group listed under {it['category']}."
        print(f"RENAMED {code}: {old!r} -> {it['name']!r}")
    out.append(it)

json.dump(out, open(os.path.join(WAVE_DIR, 'wave_20261112_clean.json'), 'w'), indent=1, ensure_ascii=False)
json.dump({c['invite'].split('/')[-1]: teams[c['invite'].split('/')[-1]] for c in out},
          open(os.path.join(WAVE_DIR, 'wave_20261112_clean_teams.json'), 'w'), indent=1)
json.dump(drops, open(os.path.join(WAVE_DIR, 'wave_20261112_spotverify_drops.json'), 'w'), indent=1, ensure_ascii=False)
state['drops'] = drops
json.dump(state, open(os.path.join(WAVE_DIR, 'coordinator_verify_state_20261112.json'), 'w'), indent=1, ensure_ascii=False)
print('clean now:', len(out), '| dropped:', len(drops))
