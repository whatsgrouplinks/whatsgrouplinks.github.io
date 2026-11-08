#!/usr/bin/env python3
"""Check pasted card names (stdin, one per line: 'idx|name') against Nov-3 harvested names.
Prints 'NEW' or 'KNOWN' per line. Also loads code sets for code dedupe (mode=code)."""
import json, re, sys

W03 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/'
W04 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/'

def norm(s):
    return re.sub(r'\s+', ' ', s.strip().lower())

def load_names():
    names = set()
    for f in ['team39R-brazil.json', 'team39R-unverified-pending.json', 'team39b-unverified-pending.json']:
        try:
            for x in json.load(open(W03 + f)):
                n = x.get('name', '')
                if n: names.add(norm(n))
        except Exception as e:
            print('load fail', f, e, file=sys.stderr)
    return names

def load_codes():
    codes = set(json.load(open(W04 + 'dedupe_union.json')))
    for f in ['team39R-brazil.json', 'team39R-unverified-pending.json', 'team39b-unverified-pending.json']:
        try:
            for x in json.load(open(W03 + f)):
                m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', x.get('invite', ''))
                if m: codes.add(m.group(1))
        except Exception as e:
            print('load fail', f, e, file=sys.stderr)
    return codes

mode = sys.argv[1] if len(sys.argv) > 1 else 'name'
if mode == 'name':
    names = load_names()
    print(f'nov3 names: {len(names)}', file=sys.stderr)
    for line in sys.stdin:
        line = line.rstrip('\n')
        if not line: continue
        idx, nm = (line.split('|', 1) + [''])[:2]
        print(f"{idx}|{'KNOWN' if norm(nm) in names else 'NEW'}|{nm}")
elif mode == 'code':
    codes = load_codes()
    print(f'exclusion codes: {len(codes)}', file=sys.stderr)
    for line in sys.stdin:
        c = line.strip()
        if c: print(f"{c}|{'DUP' if c in codes else 'FRESH'}")
