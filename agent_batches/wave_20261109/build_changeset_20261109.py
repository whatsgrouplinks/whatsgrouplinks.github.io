#!/usr/bin/env python3
"""Build deploy changeset for wave 20261109: build dir -> wgl-deploy via blob-SHA diff.
Excludes: .git, __pycache__, and agent_batches/wave_20261109 raw HTML dump dirs
(team*_raw, team17_raw etc. — 511MB of fetched-page evidence; kept in the build
dir only, not pushed to the live repo). All wave deliverables (teamNN-*.json,
summaries, manifest, clean/pending/leads/excluded, verify scripts/state) ARE synced.
"""
import hashlib, json, os

SITE='/home/hatch/workspace/whatsapp-groups-site'
DEPLOY='/home/hatch/workspace/wgl-deploy'
OUT=os.path.join(SITE,'agent_batches','wave_20261109','deploy_changes_20261109.json')
SKIP_DIRS={'__pycache__','.git'}
RAW_PREFIX='agent_batches/wave_20261109/'

def blob_sha(path):
    with open(path,'rb') as f: data=f.read()
    return hashlib.sha1(b'blob %d\0'%len(data)+data).hexdigest()

def is_raw_dump(rel):
    if not rel.startswith(RAW_PREFIX): return False
    rest=rel[len(RAW_PREFIX):]
    first=rest.split('/')[0]
    return first.endswith('_raw') or first=='team17_raw' or '_raw' in first

changed=[]; total=0
for root,dirs,files in os.walk(SITE):
    dirs[:]=[d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        p=os.path.join(root,fn); rel=os.path.relpath(p,SITE); total+=1
        if is_raw_dump(rel): continue
        dst=os.path.join(DEPLOY,rel)
        try: sha=blob_sha(p)
        except Exception as e:
            print('READ FAIL',rel,e); continue
        if not os.path.exists(dst):
            changed.append({'path':rel,'sha':sha}); continue
        try:
            if blob_sha(dst)!=sha: changed.append({'path':rel,'sha':sha})
        except Exception as e:
            print('DEPLOY READ FAIL',rel,e); changed.append({'path':rel,'sha':sha})
# deletions: deploy files not in build (excluding .git and excluded raw dumps)
deploy_files=set()
for root,dirs,files in os.walk(DEPLOY):
    dirs[:]=[d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        deploy_files.add(os.path.relpath(os.path.join(root,fn),DEPLOY))
build_files=set()
for root,dirs,files in os.walk(SITE):
    dirs[:]=[d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        rel=os.path.relpath(os.path.join(root,fn),SITE)
        if not is_raw_dump(rel): build_files.add(rel)
deleted=sorted(deploy_files-build_files)
print('scanned:',total,'changed:',len(changed),'deleted:',len(deleted))
print('deleted:',deleted[:20])
json.dump({'changed':changed,'deleted':deleted},open(OUT,'w'),indent=1)
print('wrote',OUT)
