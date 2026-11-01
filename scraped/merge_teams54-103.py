#!/usr/bin/env python3
"""Merge team54-103 WhatsApp group scrapes into groups.json (code-level dedup)."""
import json, re, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
GROUPS = os.path.join(BASE, '..', 'groups.json')
MERGED_LOG = os.path.join(BASE, 'merged.log')

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)', re.IGNORECASE)

def code_of(url):
    if not url or not isinstance(url, str):
        return None
    u = url.strip().rstrip('/')
    if 'chat.whatsapp.com' not in u.lower():
        return None
    m = CODE_RE.search(u)
    return m.group(1) if m else None

def load_file(path):
    raw = open(path).read().strip()
    if not raw:
        return []
    try:
        d = json.loads(raw)
        return d if isinstance(d, list) else [d]
    except Exception as e:
        # try JSONL
        out = []
        for line in raw.split('\n'):
            line = line.strip()
            if line:
                out.append(json.loads(line))
        return out

def clean_name(name):
    n = str(name or '').strip()
    n = re.sub(r'https?://\S+', '', n)
    n = re.sub(r'(?:www\.)?youtube\.com/\S+', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    n = n.strip('[],|:;')
    return n[:120] if n else 'WhatsApp Group'

def clean_desc(desc):
    d = str(desc or '').strip()
    d = re.sub(r'https?://chat\.whatsapp\.com/\S+', 'this group', d)
    d = re.sub(r'\s+', ' ', d).strip()
    return d[:300]

# Order: team54 .. team103, then recovered extras
files = []
for n in range(54, 104):
    for f in sorted(os.listdir(BASE)):
        m = re.match(r'team%d-.*\.json$' % n, f)
        if m:
            files.append(f)
extra = 'team80-recovered-invite.json'
if os.path.exists(os.path.join(BASE, extra)) and extra not in files:
    files.append(extra)

main = json.load(open(GROUPS))
existing = set()
skipped_bad = 0
for e in main:
    c = code_of(e.get('invite', ''))
    if c:
        existing.add(c)
    else:
        skipped_bad += 1

added = 0
added_per_file = {}
bad_invites = 0
xteam_dups = 0

for f in files:
    path = os.path.join(BASE, f)
    try:
        recs = load_file(path)
    except Exception as e:
        print('SKIP %s: %s' % (f, e), file=sys.stderr)
        continue
    n0 = 0
    for r in recs:
        if not isinstance(r, dict):
            continue
        c = code_of(r.get('invite', ''))
        if not c:
            bad_invites += 1
            continue
        if c in existing:
            xteam_dups += 1
            continue
        entry = {
            'name': clean_name(r.get('name', 'WhatsApp Group')),
            'category': str(r.get('category', 'General')).strip()[:40] or 'General',
            'description': clean_desc(r.get('description', '')),
            'image': '',
            'invite': 'https://chat.whatsapp.com/' + c,
        }
        main.append(entry)
        existing.add(c)
        added += 1
        n0 += 1
    added_per_file[f] = n0

json.dump(main, open(GROUPS, 'w'), ensure_ascii=False, indent=0)

with open(MERGED_LOG, 'a') as log:
    for f in files:
        log.write(f + '\n')

print('files merged:', len(files))
print('added:', added)
print('cross-team/existing dups skipped:', xteam_dups)
print('invalid invites skipped:', bad_invites)
print('final groups.json count:', len(main))
per = {f: added_per_file[f] for f in sorted(added_per_file)}
print(json.dumps(per, indent=0))
