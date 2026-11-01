#!/usr/bin/env python3
"""Parent verification for wave 20261026 coordinator output.
Collects invite-bearing items from team*-unverified-pending.json + team*-fresh-*.json,
dedupes against current groups.json + .existing_codes.json, curl-verifies
(HTTP success + non-empty og:title), writes parent_* outputs in this dir.
Run only after the coordinator has finished writing all team files.
"""
import json, glob, os, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.expanduser('~/workspace/whatsapp-groups-site')
WAVE = os.path.join(BASE, 'agent_batches/wave_20261026')

groups = json.load(open(os.path.join(BASE, 'groups.json')))
gcode = set()
for g in groups:
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)', g.get('invite', ''))
    if m:
        gcode.add(m.group(1))
existing = set(json.load(open(os.path.join(BASE, '.existing_codes.json'))))

uniq = {}
for f in sorted(glob.glob(os.path.join(WAVE, 'team*.json'))):
    if 'parent_' in f:
        continue
    try:
        d = json.load(open(f))
    except Exception as e:
        print('SKIP unreadable', f, e)
        continue
    if isinstance(d, dict):
        d = d.get('items') or []
    for it in d:
        if not isinstance(it, dict):
            continue
        inv = it.get('invite', '')
        m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)', inv)
        if m and m.group(1) not in gcode and m.group(1) not in existing:
            uniq.setdefault(m.group(1), it)
print(f"FRESH TO VERIFY: {len(uniq)}")

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

def check(it):
    url = it['invite']
    for _ in range(2):
        try:
            p = subprocess.run(['curl', '-s', '-L', '--max-time', '20', '-A', UA, url],
                               capture_output=True, text=True, timeout=30)
            html = p.stdout or ''
            m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
            title = m.group(1).strip() if m else ''
            if p.returncode == 0 and title:
                return (it, 'live')
            if p.returncode == 0 and not title:
                return (it, 'dead')
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return (it, 'uncheckable')

with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(check, list(uniq.values())))
live = [i for i, s in results if s == 'live']
dead = [i for i, s in results if s == 'dead']
unk = [i for i, s in results if s == 'uncheckable']
print(f"LIVE: {len(live)} DEAD: {len(dead)} UNCHECKABLE: {len(unk)}")
json.dump(live, open(os.path.join(WAVE, 'parent_verified.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(dead, open(os.path.join(WAVE, 'parent_dead.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(unk, open(os.path.join(WAVE, 'parent_uncheckable.json'), 'w'), ensure_ascii=False, indent=1)
for i in dead[:20]:
    print("DEAD:", i.get('name'), i.get('invite'))
for i in unk[:20]:
    print("UNK:", i.get('name'), i.get('invite'))
