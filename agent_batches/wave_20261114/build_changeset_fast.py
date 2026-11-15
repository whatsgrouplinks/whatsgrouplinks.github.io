#!/usr/bin/env python3
"""Fast deploy changeset for wave 20261114 (v2): build dir -> wgl-deploy.
Same scope/exclusions as build_changeset_20261114.py.
Strategy (generate.py output for unchanged groups is byte-identical):
- groups/*.html present in both dirs: compare SIZE only; hash-verify a random
  sample of 1,000 size-equal pairs (fail loudly if any mismatch -> full hash).
  Size-differing pairs are hashed on both sides.
- All other files: hash both sides when present in both.
- New files: hashed once. Deletions: filename diff within synced scope.
Writes agent_batches/wave_20261114/deploy_changes_20261114.json
in the format cp_sync_20261114.py expects.
"""
import hashlib, json, os, random
from collections import Counter

SITE = '/home/hatch/workspace/whatsapp-groups-site'
DEPLOY = '/home/hatch/workspace/wgl-deploy'
OUT = os.path.join(SITE, 'agent_batches', 'wave_20261114',
                   'deploy_changes_20261114.json')
SKIP_DIRS = {'__pycache__', '.git'}

def blob_sha(path):
    with open(path, 'rb') as f:
        data = f.read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()

def is_excluded(rel):
    parts = rel.split(os.sep)
    if len(parts) >= 2 and parts[0] == 'agent_batches' and parts[1].startswith('wave_'):
        # wave_20261115 is mid-write by the coordinator; never sync a
        # half-written wave dir — its deliverables ship with its own deploy.
        if parts[1] == 'wave_20261115':
            return True
        return len(parts) > 3
    return False

SKIPPED = []

def safe_sha(path):
    try:
        return blob_sha(path)
    except OSError as e:
        SKIPPED.append((path, str(e)))
        return None

def collect(base):
    out = {}
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, base)
            if is_excluded(rel):
                continue
            try:
                st = os.stat(p)
            except OSError:
                continue
            out[rel] = (p, st.st_size)
    return out

print('collecting build...', flush=True)
build = collect(SITE)
print('build files:', len(build), flush=True)
print('collecting deploy...', flush=True)
dep = collect(DEPLOY)
print('deploy files:', len(dep), flush=True)

changed, deleted = [], []
size_equal_pairs = []
for rel, (p, size) in build.items():
    d = dep.get(rel)
    if d is None:
        sh=safe_sha(p)
        if sh: changed.append({'path': rel, 'sha': sh})
        continue
    dp, dsize = d
    if rel.startswith('groups/'):
        if size != dsize:
            a, b = safe_sha(p), safe_sha(dp)
            if a and b and a != b:
                changed.append({'path': rel, 'sha': a})
        else:
            size_equal_pairs.append((rel, p, dp))
    else:
        a, b = safe_sha(p), safe_sha(dp)
        if a and b and a != b:
            changed.append({'path': rel, 'sha': a})

for rel in dep:
    if rel not in build:
        deleted.append(rel)

# sample-verify size-equal group pages
random.seed(20261114)
sample = random.sample(size_equal_pairs, min(1000, len(size_equal_pairs)))
bad = [rel for rel, p, dp in sample if (lambda a,b: a and b and a != b)(safe_sha(p), safe_sha(dp))]
print('size-equal group pairs:', len(size_equal_pairs),
      'sampled:', len(sample), 'sample mismatches:', len(bad), flush=True)
if bad:
    print('SAMPLE MISMATCH — size equality is NOT safe. Aborting; run full hash.',
          bad[:10], flush=True)
    raise SystemExit(1)

print('changed:', len(changed), 'deleted:', len(deleted), flush=True)
json.dump({'changed': changed, 'deleted': deleted}, open(OUT, 'w'))
print('wrote', OUT, flush=True)
print(dict(Counter(x['path'].split('/')[0] for x in changed)))
print('deleted:', deleted[:20])
print('skipped (vanished mid-walk):', len(SKIPPED), SKIPPED[:5])
