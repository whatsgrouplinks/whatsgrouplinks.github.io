#!/usr/bin/env python3
"""Wave 20261111 coordinator finalization pass.
1. Drops BTK6Vvs3TEu6oW7joHtiY9 from clean — coordinator spot-verify found
   og:title + banked name/description are a sports-betting recruitment group
   ('BETS1GREEN APOSTA', 'Do you like making sports bets? Come with us').
2. Restores the 5 team09 schema-error codes (empty banked names) using the
   og:titles fetched in coordinator_verify_20261111.py — all 5 live, clean.
3. Re-validates the final clean file (union leaks, schema, dupes).
"""
import json, os, re, html as H

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111'
SITE = '/home/hatch/workspace/whatsapp-groups-site'
union = set(json.load(open(os.path.join(SITE, '.existing_codes.json'))))

clean = json.load(open(os.path.join(WAVE_DIR, 'wave_20261111_clean.json')))
teams = json.load(open(os.path.join(WAVE_DIR, 'wave_20261111_clean_teams.json')))
excluded = json.load(open(os.path.join(WAVE_DIR, 'wave_20261111_excluded.json')))
state = json.load(open(os.path.join(WAVE_DIR, 'coordinator_verify_state_20261111.json')))

# 1. drop betting group found by spot-verify
code = 'BTK6Vvs3TEu6oW7joHtiY9'
hit = [c for c in clean if c['invite'].rsplit('/', 1)[-1] == code]
assert len(hit) == 1
rec = hit[0]
clean = [c for c in clean if c['invite'].rsplit('/', 1)[-1] != code]
teams.pop(code, None)
excluded.append({'team': 4, 'code': code, 'name': rec['name'],
                 'reason': 'scam:betting — sports-betting recruitment group (coordinator spot-verify: og:title BETS1GREEN APOSTA; desc invites sports betting)'})
print('dropped betting group:', code)

# 2. restore the 5 schema-error codes with og:title names
for r in state['schema_codes']:
    c = r['code']
    assert r['status'] == 'live', r
    name = H.unescape(r['og_title'])
    name = re.sub(r'\s+', ' ', name).strip()[:100]
    assert name, c
    assert c not in union, c
    assert not any(x['invite'].rsplit('/', 1)[-1] == c for x in clean), c
    clean.append({'name': name, 'category': 'Community & Social', 'country': '',
                  'description': f'Join {name}, a WhatsApp group for community & social.',
                  'invite': f'https://chat.whatsapp.com/{c}'})
    teams[c] = 9
    print('restored schema-error code:', c, '->', name)

# 3. re-validate
codes = [c['invite'].rsplit('/', 1)[-1] for c in clean]
assert len(codes) == len(set(codes)), 'dup codes in clean!'
leaks = [c for c in codes if c in union]
assert not leaks, leaks
CANON = {'Gaming','Education','Online Earning','Community & Social','Business','Friendship',
         'Finance','Buy Sell','Islamic','Entertainment','Jobs','Technology','Funny','Sports',
         'Health','News','Crypto','Cooking','Poetry','Travel','Scholarship','Freelance',
         'Real Estate'}
bad = [c for c in clean if c['category'] not in CANON or not c['name'] or not c['description']]
assert not bad, bad
print('validation OK: clean', len(clean), 'union leaks 0, schema errors 0, dupes 0')

json.dump(clean, open(os.path.join(WAVE_DIR, 'wave_20261111_clean.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(teams, open(os.path.join(WAVE_DIR, 'wave_20261111_clean_teams.json'), 'w'), indent=1)
json.dump(excluded, open(os.path.join(WAVE_DIR, 'wave_20261111_excluded.json'), 'w'), indent=1, ensure_ascii=False)
# remove the 5 restored codes from schema errors
errs = json.load(open(os.path.join(WAVE_DIR, 'wave_20261111_schema_err.json')))
restored_codes = {r['code'] for r in state['schema_codes']}
errs = [e for e in errs if e['item'].get('invite', '').rsplit('/', 1)[-1] not in restored_codes]
json.dump(errs, open(os.path.join(WAVE_DIR, 'wave_20261111_schema_err.json'), 'w'), indent=1, ensure_ascii=False)
print('schema errors remaining:', len(errs), 'excluded now:', len(excluded))
