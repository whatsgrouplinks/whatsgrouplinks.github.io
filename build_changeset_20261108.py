#!/usr/bin/env python3
"""Build the deploy change set for wave 20261108: compare every file in the
build dir against the wgl-deploy repo HEAD tree by git blob SHA.
Writes agent_batches/wave_20261108/deploy_changes_20261108.json with
{changed: [{path, sha}], deleted: [path]}.
Usage: python3 build_changeset_20261108.py
"""
import hashlib, json, os, subprocess

SITE = '/home/hatch/workspace/whatsapp-groups-site'
DEPLOY = '/home/hatch/workspace/wgl-deploy'
OUT = os.path.join(SITE, 'agent_batches', 'wave_20261108',
                   'deploy_changes_20261108.json')

SKIP_TOP = {'.git'}

def blob_sha(path):
    with open(path, 'rb') as f:
        data = f.read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()

def main():
    tree = subprocess.run(['git', 'ls-tree', '-r', 'HEAD'],
                          cwd=DEPLOY, capture_output=True, text=True,
                          check=True).stdout
    repo = {}
    for line in tree.splitlines():
        # "<mode> blob <sha>\t<path>"
        meta, path = line.split('\t', 1)
        repo[path] = meta.split()[2]
    print('repo tracked files:', len(repo), flush=True)

    changed, on_disk = [], set()
    for root, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in SKIP_TOP]
        for fn in files:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, SITE)
            on_disk.add(rel)
            sha = blob_sha(full)
            if repo.get(rel) != sha:
                changed.append({'path': rel, 'sha': sha})
    deleted = sorted(p for p in repo if p not in on_disk)
    print('changed/new:', len(changed), 'deleted:', len(deleted), flush=True)
    for d in deleted:
        print('  DELETE:', d, flush=True)
    json.dump({'changed': changed, 'deleted': deleted}, open(OUT, 'w'))
    print('wrote', OUT, flush=True)

if __name__ == '__main__':
    main()
