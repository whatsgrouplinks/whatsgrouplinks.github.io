#!/usr/bin/env python3
"""WGL Data-API deploy — stage 1: compute change set vs repo HEAD tree.
Saves agent_batches/wave_20261105/deploy_changes_leg1.json"""
import os, json, hashlib, subprocess, time

SITE = '/home/hatch/workspace/whatsapp-groups-site'
OUT = os.path.join(SITE, 'agent_batches', 'wave_20261105', 'deploy_changes_leg1.json')
MANAGED_DIRS = ('groups', 'category', 'blog', 'assets')
ROOT_FILES = ('about.html', 'batch_a_fresh.txt', 'blog.html', 'categories.html',
              'contact.html', 'groups.json', 'index.html', 'privacy.html',
              'robots.txt', 'sitemap-groups-1.xml', 'sitemap-groups-2.xml',
              'sitemap-main.xml', 'sitemap.xml', 'submit.html', 'terms.html')

def token():
    u = subprocess.run(['git', '-C', '/home/hatch/workspace/wgl-deploy',
                        'config', '--get', 'remote.origin.url'],
                       capture_output=True, text=True).stdout.strip()
    return u.split(':')[2].split('@')[0]

def api(path, method='GET', data=None):
    body = json.dumps(data).encode() if data else None
    import tempfile
    for attempt in range(4):
        try:
            cmd = ['curl', '-s', '--max-time', '300', '-X', method,
                   '-H', 'Authorization: Bearer ' + token(),
                   '-H', 'Accept: application/vnd.github+json',
                   '-H', 'Content-Type: application/json']
            if body:
                cmd += ['--data-binary', '@-']
            cmd += [f'https://api.github.com{path}']
            p = subprocess.run(cmd, input=body, capture_output=True, timeout=320)
            out = p.stdout.decode()
            return json.loads(out or '{}')
        except Exception as e:
            print(f'api {path} attempt {attempt+1} failed: {str(e)[:120]}', flush=True)
            time.sleep(5 + attempt * 5)
    raise RuntimeError(f'api {path} failed after 4 attempts')

def blob_sha(path):
    with open(path, 'rb') as f:
        data = f.read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest(), len(data)

def load_repo_tree_local():
    """Repo blob map from the local git object DB (wgl-deploy HEAD == remote HEAD).
    Avoids the 14MB recursive-tree API response, which the egress proxy now
    truncates at ~11.8MB on every attempt."""
    import re
    tree_file = os.path.join(SITE, 'agent_batches', 'wave_20261105', 'repo_tree_96a70567.txt')
    repo = {}
    with open(tree_file) as f:
        for line in f:
            m = re.match(r'^\d+ blob ([0-9a-f]{40})\t(.+)$', line.rstrip('\n'))
            if m:
                repo[m.group(2)] = m.group(1)
    return repo

def main():
    ref = api('/repos/whatsgrouplinks/whatsgrouplinks.github.io/git/ref/heads/main')
    head = ref['object']['sha']
    print('remote HEAD:', head[:8], flush=True)
    if head != '96a70567374cdc5ca7c06766d76d3b9500626bfd':
        raise RuntimeError(f'remote HEAD moved to {head[:8]} — local tree file is stale, aborting')
    repo = load_repo_tree_local()
    print('repo blobs:', len(repo), flush=True)

    build = {}
    for d in MANAGED_DIRS:
        base = os.path.join(SITE, d)
        for root, _, files in os.walk(base):
            for f in files:
                p = os.path.join(root, f)
                rel = os.path.relpath(p, SITE)
                build[rel] = p
    for f in ROOT_FILES:
        p = os.path.join(SITE, f)
        if os.path.exists(p):
            build[f] = p
    print('build files:', len(build), flush=True)

    changed, samesha = [], {}
    for rel, p in build.items():
        sha, size = blob_sha(p)
        samesha[rel] = sha
        if repo.get(rel) != sha:
            changed.append({'path': rel, 'sha': sha, 'size': size,
                            'local': p, 'new': rel not in repo})
    deleted = [rel for rel in repo
               if rel not in build and rel.split('/')[0] in MANAGED_DIRS]
    print('changed:', len(changed), 'deleted:', len(deleted), flush=True)
    for _a in range(12):
        try:
            json.dump({'head': head, 'changed': changed, 'deleted': deleted,
                       'shas': samesha}, open(OUT, 'w'))
            break
        except PermissionError:
            print(f'save attempt {_a+1} EPERM, retrying...', flush=True)
            time.sleep(10)
    else:
        raise PermissionError('could not save deploy_changes_leg1.json after 12 attempts')
    print('saved', OUT, flush=True)
    # summary by category
    from collections import Counter
    print(Counter(('new' if c['new'] else 'modified') for c in changed), flush=True)

if __name__ == '__main__':
    main()
