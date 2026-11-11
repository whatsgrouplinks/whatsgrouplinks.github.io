#!/usr/bin/env python3
"""Parent-verify spot re-check for wave 20261111 clean set.
35 seeded-random clean codes + 2 controls (known-live groups.json code, fabricated code).
Rule: HTTP 200 + non-empty og:title = live; empty og:title after 2 spaced attempts = dead.
Writes parent_verify_state_20261111.json."""
import json, re, random, subprocess, time, html, os

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111'
SITE = '/home/hatch/workspace/whatsapp-groups-site'

UAS = [
 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
]

def check(code, ua_idx=0):
    url = f'https://chat.whatsapp.com/{code}'
    try:
        r = subprocess.run(['curl', '-s', '--max-time', '30', '-A', UAS[ua_idx % len(UAS)], url],
                           capture_output=True, text=True, timeout=35)
        body = r.stdout or ''
        m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
        title = html.unescape(m.group(1)).strip() if m else ''
        return {'http': 200 if body else 0, 'title': title}
    except Exception as e:
        return {'http': 0, 'title': '', 'err': str(e)}

def verify_one(code):
    a = check(code, 0)
    if a['http'] == 0 or a['title'] == '':
        time.sleep(12)
        b = check(code, 1)
        if b['title']:
            a = b
        elif b['http'] != 0:
            a = {'http': b['http'], 'title': '', 'attempts': 2}
        else:
            a = {**a, 'attempts': 2}
    return a

clean = json.load(open(os.path.join(WAVE, 'wave_20261111_clean.json')))
random.seed(20261111)
sample = random.sample(clean, 35)
# controls: known-live code from groups.json + fabricated code
groups = json.load(open(os.path.join(SITE, 'groups.json')))
live_ctrl = groups[0]['invite'].split('/')[-1]
jobs = [{'set': 'clean-spot', 'code': it['invite'].split('/')[-1], 'name': it['name']} for it in sample]
jobs.append({'set': 'control-live', 'code': live_ctrl, 'name': groups[0]['name']})
jobs.append({'set': 'control-fake', 'code': 'ZZZZZZZZZZZZZZZZZZZZZZ', 'name': 'FABRICATED'})

results = []
for i, job in enumerate(jobs):
    res = verify_one(job['code'])
    live = bool(res.get('title'))
    results.append({**job, 'result': res, 'live': live})
    print(f"{i+1}/{len(jobs)} {job['set']} {job['code']} live={live} title={res.get('title','')[:50]!r}", flush=True)

live_n = sum(1 for r in results if r['live'] and r['set'] == 'clean-spot')
print(f"clean-spot live: {live_n}/35")
print(f"control-live: {[r for r in results if r['set']=='control-live'][0]['live']}")
print(f"control-fake: {[r for r in results if r['set']=='control-fake'][0]['live']}")
json.dump(results, open(os.path.join(WAVE, 'parent_verify_state_20261111.json'), 'w'), indent=1, ensure_ascii=False)
