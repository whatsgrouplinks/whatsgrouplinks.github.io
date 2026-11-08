#!/usr/bin/env python3
"""Wave 20261103 final count: per-team verified/pending/leads + manifest."""
import json, re, glob, os

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103'
os.chdir(WAVE)

def code_of(item):
    inv = item.get('invite') or item.get('url') or ''
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{15,30})', inv)
    return m.group(1) if m else None

# verified files: teamNN...json excluding leads/pending/state/candidates/raw/checkpoint/scripts
VERIFIED = []
for f in sorted(glob.glob('team*.json')):
    base = os.path.basename(f)
    if any(s in base for s in ['leads', 'pending', 'state', 'candidates', 'checkpoint', 'raw', 'draft', 'result', 'fresh', 'rows', 'queue']):
        continue
    try:
        d = json.load(open(f))
    except Exception as e:
        print('UNREADABLE', f, e); continue
    if not isinstance(d, list):
        print('NONLIST', f, type(d)); continue
    codes = [code_of(x) for x in d]
    bad = sum(1 for c in codes if not c or not (20 <= len(c) <= 24))
    VERIFIED.append((f, len(d), len(set(c for c in codes if c)), bad))

PENDING = []
LEADS = []
for f in sorted(glob.glob('team*-unverified-pending.json')):
    try: PENDING.append((f, len(json.load(open(f)))))
    except Exception: pass
for f in sorted(glob.glob('team*-leads.json')):
    try: LEADS.append((f, len(json.load(open(f)))))
    except Exception: pass

print('=== VERIFIED FILES ===')
tv = 0
for f, n, u, bad in VERIFIED:
    flag = '  <-- SCHEMA/CODE ISSUES' if bad else ''
    print(f'{f:48} n={n:4} uniq={u:4} badcode={bad}{flag}')
    tv += n
print('TOTAL verified items (file sum, pre-merge):', tv)

print()
print('=== PENDING ===')
tp = 0
for f, n in PENDING:
    print(f'{f:48} n={n}'); tp += n
print('TOTAL pending:', tp)

print()
print('=== LEADS ===')
tl = 0
for f, n in LEADS:
    print(f'{f:48} n={n}'); tl += n
print('TOTAL leads:', tl)

# cross-file dup check among verified files
print()
print('=== CROSS-FILE CODE OVERLAP (verified files) ===')
seen = {}
dups = 0
for f, n, u, bad in VERIFIED:
    for x in json.load(open(f)):
        c = code_of(x)
        if not c: continue
        if c in seen:
            dups += 1
            if dups <= 10: print('DUP', c, 'in', f, 'already in', seen[c])
        else:
            seen[c] = f
print('total dup code occurrences across verified files:', dups, '| unique codes:', len(seen))
