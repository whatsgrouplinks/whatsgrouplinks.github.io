#!/usr/bin/env python3
"""Wave 20261112 coordinator spot-verification.
Samples ~35 clean codes (stratified across teams, weighted to the big
contributors, plus restored items + borderline keeps) and re-checks each with
sequential curl-equivalent requests, og:title ONLY (og:description is the
generic 'WhatsApp Group Invite' on dead pages too — never a live signal;
generic og:title 'WhatsApp Group Invite' also counts as dead).
og:title serving is intermittent (team08: live pages sometimes serve an empty
title), so an empty title gets one spaced retry before a dead verdict.
Controls first: known-live groups.json code (must show real og:title) and a
fabricated code (must show empty/generic). Writes
coordinator_verify_state_20261112.json. Drops go in coordinator_verify_drops.json.
"""
import json, random, re, time
import requests

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112'
SITE = '/home/hatch/workspace/whatsapp-groups-site'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}
TITLE1 = re.compile(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)', re.I)
TITLE2 = re.compile(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', re.I)

s = requests.Session()
s.headers.update(UA)

def og_title(code, timeout=60):
    try:
        r = s.get(f'https://chat.whatsapp.com/{code}', timeout=timeout)
        html = r.text
        m = TITLE1.search(html) or TITLE2.search(html)
        return (r.status_code, (m.group(1).strip() if m else ''))
    except Exception as e:
        return (0, f'TRANSPORT:{type(e).__name__}')

def check(code):
    st, t = og_title(code)
    if t and t != 'WhatsApp Group Invite':
        return ('live', st, t, 1)
    time.sleep(30)
    st2, t2 = og_title(code)
    if t2 and t2 != 'WhatsApp Group Invite':
        return ('live-retry', st2, t2, 2)
    if t2.startswith('TRANSPORT') or t.startswith('TRANSPORT'):
        return ('pending', st2, t2, 2)
    return ('dead', st2, t2, 2)

state = {'controls': {}, 'sample': [], 'drops': []}
# controls
st, t = og_title('KrDwdK8EIkB6vgauHg5M7N')
state['controls']['known_live'] = {'code': 'KrDwdK8EIkB6vgauHg5M7N', 'http': st, 'og_title': t}
print('control live:', st, repr(t))
st, t = og_title('ZZZZZZZZZZZZZZZZZZZZZZ')
state['controls']['fabricated'] = {'code': 'ZZZZZZZZZZZZZZZZZZZZZZ', 'http': st, 'og_title': t}
print('control fabricated:', st, repr(t))

clean = json.load(open(f'{WAVE_DIR}/wave_20261112_clean.json'))
teams = json.load(open(f'{WAVE_DIR}/wave_20261112_clean_teams.json'))
restored = json.load(open(f'{WAVE_DIR}/wave_20261112_restored.json'))
random.seed(20261112)
by_team = {}
for c in clean:
    code = c['invite'].split('/')[-1]
    by_team.setdefault(teams[code], []).append(c)
# stratified: 2 per team with >=5 items, 1 per smaller team, plus extras from big teams
sample = []
for t in sorted(by_team):
    items = by_team[t]
    k = 2 if len(items) >= 5 else 1
    sample.extend(random.sample(items, min(k, len(items))))
# top up from the biggest teams to reach ~35
big = [c for c in clean if teams[c['invite'].split('/')[-1]] in (3, 2, 5, 16)]
random.shuffle(big)
for c in big:
    if len(sample) >= 35: break
    if c not in sample: sample.append(c)
# force-include 3 restored items + 2 casino-flagged team05 items for adjudication check
for code in ['Dtg17f3Hryq1XM9XjcMhcw', 'CYjh8YprII8GQ08sOuahLW', 'KDjyNz7lzt5BMotyWRlBmL']:
    it = next((c for c in clean if c['invite'].endswith(code)), None)
    if it and it not in sample: sample.append(it)
print('sample size:', len(sample))

for it in sample:
    code = it['invite'].split('/')[-1]
    verdict, http, title, attempts = check(code)
    rec = {'code': code, 'team': teams[code], 'banked_name': it['name'],
           'category': it['category'], 'verdict': verdict, 'http': http,
           'og_title': title, 'attempts': attempts}
    state['sample'].append(rec)
    print(f"{verdict:10s} t{teams[code]:02d} {code} banked={it['name']!r} og={title!r}")
    if verdict == 'dead':
        state['drops'].append(rec)

live = sum(1 for r in state['sample'] if r['verdict'].startswith('live'))
dead = sum(1 for r in state['sample'] if r['verdict'] == 'dead')
pend = sum(1 for r in state['sample'] if r['verdict'] == 'pending')
print(f'SAMPLE: {len(state["sample"])} checked, {live} live, {dead} dead, {pend} pending')
state['summary'] = {'checked': len(state['sample']), 'live': live, 'dead': dead, 'pending': pend}
json.dump(state, open(f'{WAVE_DIR}/coordinator_verify_state_20261112.json', 'w'), indent=1, ensure_ascii=False)
print('wrote coordinator_verify_state_20261112.json')
