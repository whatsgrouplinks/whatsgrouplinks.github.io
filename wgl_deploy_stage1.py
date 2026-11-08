#!/usr/bin/env python3
"""WGL Data-API deploy — stage 1: compute change set vs repo HEAD tree.
Saves agent_batches/wave_20261104/deploy_changes.json"""
import os, json, hashlib, subprocess

SITE = '/home/hatch/workspace/whatsapp-groups-site'
OUT = os.path.join(SITE, 'agent_batches', 'wave_20261104', 'deploy_changes.json')
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
    import urllib.request
    req = urllib.request.Request('https://api.github.com' + path,
                                 data=json.dumps(data).encode() if data else None,
                                 headers={'Authorization': 'Bearer ' + token(),
                                          'Accept': 'application/vnd.github+json',
                                          'Content-Type': 'application/json'},
                                 method=method)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def blob_sha(path):
    with open(path, 'rb') as f:
        data = f.read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest(), len(data)

def main():
    ref = api('/repos/whatsgrouplinks/whatsgrouplinks.github.io/git/ref/heads/main')
    head = ref['object']['sha']
    print('remote HEAD:', head[:8], flush=True)
    tree = api(f'/repos/whatsgrouplinks/whatsgrouplinks.github.io/git/trees/{head}?recursive=1')
    repo = {t['path']: t['sha'] for t in tree['tree'] if t['type'] == 'blob'}
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
    json.dump({'head': head, 'changed': changed, 'deleted': deleted,
               'shas': samesha}, open(OUT, 'w'))
    print('saved', OUT, flush=True)
    # summary by category
    from collections import Counter
    print(Counter(('new' if c['new'] else 'modified') for c in changed), flush=True)

if __name__ == '__main__':
    main()
