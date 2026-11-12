#!/usr/bin/env python3
"""Build deploy changeset for wave 20261112: build dir -> wgl-deploy via blob-SHA diff.
Excludes: .git, __pycache__, and any SUBDIRECTORY inside agent_batches/wave_*/
(raw HTML dumps, verify/ page dumps, scratch dirs, team*_work fetch evidence —
wave dirs in the deploy repo contain only top-level deliverable files, matching
the wave-20261112 convention). All wave deliverables (teamNN-*.json, summaries,
manifest, clean/pending/leads/excluded, verify scripts/state) ARE synced.
"""
import hashlib, json, os

SITE = '/home/hatch/workspace/whatsapp-groups-site'
DEPLOY = '/home/hatch/workspace/wgl-deploy'
OUT = os.path.join(SITE, 'agent_batches', 'wave_20261112', 'deploy_changes_20261112.json')
SKIP_DIRS = {'__pycache__', '.git'}

def blob_sha(path):
    with open(path, 'rb') as f:
        data = f.read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()

def is_excluded(rel):
    parts = rel.split(os.sep)
    # inside a wave dir, only top-level files are synced (3 parts: agent_batches/wave_XXX/file)
    if len(parts) >= 2 and parts[0] == 'agent_batches' and parts[1].startswith('wave_'):
        return len(parts) > 3
    return False

changed = []
total = 0
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, SITE)
        total += 1
        if is_excluded(rel):
            continue
        dst = os.path.join(DEPLOY, rel)
        try:
            sha = blob_sha(p)
        except Exception as e:
            print('READ FAIL', rel, e)
            continue
        if not os.path.exists(dst):
            changed.append({'path': rel, 'sha': sha})
            continue
        try:
            if blob_sha(dst) != sha:
                changed.append({'path': rel, 'sha': sha})
        except Exception as e:
            print('DEPLOY READ FAIL', rel, e)
            changed.append({'path': rel, 'sha': sha})

deploy_files = set()
for root, dirs, files in os.walk(DEPLOY):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        rel = os.path.relpath(os.path.join(root, fn), DEPLOY)
        if not is_excluded(rel):
            deploy_files.add(rel)
build_files = set()
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        rel = os.path.relpath(os.path.join(root, fn), SITE)
        if not is_excluded(rel):
            build_files.add(rel)
deleted = sorted(deploy_files - build_files)
print('scanned:', total, 'changed:', len(changed), 'deleted:', len(deleted))
print('deleted:', deleted[:20])
json.dump({'changed': changed, 'deleted': deleted}, open(OUT, 'w'), indent=1)
print('wrote', OUT)
