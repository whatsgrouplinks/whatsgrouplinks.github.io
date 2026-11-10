#!/usr/bin/env python3
"""Aggregate wave 20261110 pending + leads files (repair run)."""
import json, glob, os

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110'

# --- pending: all *-pending.json, tag with team ---
pending = []
for f in sorted(glob.glob(os.path.join(WAVE, '*-pending.json'))):
    base = os.path.basename(f)
    team = base.split('-')[0]  # teamNN
    try:
        items = json.load(open(f))
    except Exception as e:
        print('PENDING READ FAIL', f, e); continue
    if not isinstance(items, list):
        continue
    for it in items:
        if isinstance(it, dict):
            it = dict(it)
            it.setdefault('_team_file', base)
            pending.append(it)
print('pending total:', len(pending))
json.dump(pending, open(os.path.join(WAVE, 'wave_20261110_pending_all.json'), 'w'), indent=1, ensure_ascii=False)

# --- leads: all *-leads.json, unique URLs ---
leads = set()
for f in sorted(glob.glob(os.path.join(WAVE, '*-leads.json'))):
    try:
        items = json.load(open(f))
    except Exception as e:
        print('LEADS READ FAIL', f, e); continue
    if not isinstance(items, list):
        continue
    for it in items:
        if isinstance(it, dict):
            u = it.get('url') or it.get('source') or ''
            if u:
                leads.add(u)
print('unique lead URLs:', len(leads))
json.dump(sorted(leads), open(os.path.join(WAVE, 'wave_20261110_leads_all.json'), 'w'), indent=1, ensure_ascii=False)
print('wrote wave_20261110_pending_all.json and wave_20261110_leads_all.json')
