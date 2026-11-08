#!/usr/bin/env python3
"""WGL Data-API deploy — stage 3: trees + commits + ref update, <=250 entries each.
Reads deploy_changes.json + deploy_blobs.json. Saves deploy_commits.json."""
import os, json, subprocess, time

SITE = '/home/hatch/workspace/whatsapp-groups-site'
WAVE = os.path.join(SITE, 'agent_batches', 'wave_20261104')
CHANGES = os.path.join(WAVE, 'deploy_changes.json')
BLOBS = os.path.join(WAVE, 'deploy_blobs.json')
OUT = os.path.join(WAVE, 'deploy_commits.json')
REPO = 'whatsgrouplinks/whatsgrouplinks.github.io'
CHUNK = 250

def token():
    u = subprocess.run(['git', '-C', '/home/hatch/workspace/wgl-deploy',
                        'config', '--get', 'remote.origin.url'],
                       capture_output=True, text=True).stdout.strip()
    return u.split(':')[2].split('@')[0]
T = token()

def gh(path, method='GET', data=None):
    for attempt in range(5):
        try:
            p = subprocess.run(
                ['curl', '-s', '--max-time', '120', '-X', method,
                 '-H', 'Authorization: Bearer ' + T,
                 '-H', 'Accept: application/vnd.github+json',
                 '-H', 'Content-Type: application/json']
                + (['--data-binary', '@-'] if data is not None else [])
                + [f'https://api.github.com/repos/{REPO}{path}'],
                input=(json.dumps(data).encode() if data is not None else None),
                capture_output=True, timeout=140)
            r = json.loads(p.stdout.decode() or '{}')
            if isinstance(r, dict) and r.get('message') and 'sha' not in r and 'ref' not in r and 'tree' not in r:
                time.sleep(5 + attempt * 5); continue
            return r
        except Exception as e:
            time.sleep(5 + attempt * 5)
    raise RuntimeError('gh failed: ' + path)

def main():
    d = json.load(open(CHANGES))
    blobs = json.load(open(BLOBS))
    missing = [c['path'] for c in d['changed'] if c['path'] not in blobs]
    if missing:
        print('BLOBS MISSING for', len(missing), 'files — run stage 2 first', flush=True)
        return
    # order: new group pages, new category pages, modified category, root last
    def key(c):
        p = c['path']
        if p.startswith('groups/') and c['new']: return (0, p)
        if p.startswith('category/') and c['new']: return (1, p)
        if p.startswith('category/'): return (2, p)
        return (3, p)
    ordered = sorted(d['changed'], key=key)
    chunks = [ordered[i:i + CHUNK] for i in range(0, len(ordered), CHUNK)]
    print('chunks:', len(chunks), flush=True)

    state = {'commits': []}
    if os.path.exists(OUT):
        state = json.load(open(OUT))
        print('resuming at commit', len(state['commits']), flush=True)
    done_chunks = len(state['commits'])

    head = gh('/git/ref/heads/main')['object']['sha']
    commit_sha = head
    tree_sha = gh(f'/git/commits/{commit_sha}')['tree']['sha']
    if done_chunks:
        commit_sha = state['commits'][-1]['commit']
        tree_sha = state['commits'][-1]['tree']
    # sanity: remote must not have moved under us
    if not done_chunks and head != d['head']:
        print('REMOTE MOVED:', d['head'][:8], '->', head[:8], 'ABORT', flush=True)
        return

    total_new = sum(1 for c in d['changed'] if c['new'])
    for i, ch in enumerate(chunks):
        if i < done_chunks:
            continue
        entries = [{'path': c['path'], 'mode': '100644', 'type': 'blob',
                    'sha': blobs[c['path']]} for c in ch]
        t = gh('/git/trees', 'POST', {'base_tree': tree_sha, 'tree': entries})
        while 'sha' not in t:  # blob replication lag -> retry
            print('tree 422, retrying', flush=True); time.sleep(15)
            t = gh('/git/trees', 'POST', {'base_tree': tree_sha, 'tree': entries})
        tree_sha = t['sha']
        last = (i == len(chunks) - 1)
        if last:
            msg = ('Add 1,734 new verified groups (46,925 -> 48,659 total); '
                   'wave 20261103 banked, parent-verified')
        else:
            msg = f'WGL deploy part {i+1}/{len(chunks)}: new group/category pages'
        cm = gh('/git/commits', 'POST', {'message': msg, 'tree': tree_sha,
                                         'parents': [commit_sha]})
        commit_sha = cm['sha']
        for _ in range(6):
            try:
                gh('/git/ref/heads/main', 'PATCH', {'sha': commit_sha})
            except RuntimeError:
                pass
            cur = gh('/git/ref/heads/main')['object']['sha']
            if cur == commit_sha:
                break
            time.sleep(10)
        else:
            print('REF UPDATE FAILED for chunk', i, flush=True)
            state['commits'].append({'chunk': i, 'commit': commit_sha,
                                     'tree': tree_sha, 'files': len(ch),
                                     'ref_updated': False})
            json.dump(state, open(OUT + '.tmp', 'w')); os.replace(OUT + '.tmp', OUT)
            return
        state['commits'].append({'chunk': i, 'commit': commit_sha,
                                 'tree': tree_sha, 'files': len(ch),
                                 'ref_updated': True})
        json.dump(state, open(OUT + '.tmp', 'w')); os.replace(OUT + '.tmp', OUT)
        print(f'chunk {i+1}/{len(chunks)} committed {commit_sha[:8]} ({len(ch)} files)', flush=True)
    print('FINAL COMMIT:', commit_sha, flush=True)

if __name__ == '__main__':
    main()
