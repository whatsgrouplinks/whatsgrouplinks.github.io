#!/usr/bin/env python3
"""WGL Data-API deploy — stage 3b: manual chunked commits with direct curl + visible errors.
Usage: python3 wgl_deploy_stage3b.py [start_chunk]"""
import os, json, subprocess, sys, time

SITE = '/home/hatch/workspace/whatsapp-groups-site'
WAVE = os.path.join(SITE, 'agent_batches', 'wave_20261104')
CHANGES = os.path.join(WAVE, 'deploy_changes_leg2.json')
BLOBS = os.path.join(WAVE, 'deploy_blobs_leg2.json')
OUT = os.path.join(WAVE, 'deploy_commits_leg2.json')
REPO = 'whatsgrouplinks/whatsgrouplinks.github.io'
CHUNK = 250

def token():
    u = subprocess.run(['git', '-C', '/home/hatch/workspace/wgl-deploy',
                        'config', '--get', 'remote.origin.url'],
                       capture_output=True, text=True).stdout.strip()
    return u.split(':')[2].split('@')[0]
T = token()

def api(path, method='GET', data=None, timeout=90):
    body = json.dumps(data).encode() if data is not None else None
    p = subprocess.run(
        ['curl', '-s', '--max-time', str(timeout), '-X', method,
         '-H', 'Authorization: Bearer ' + T,
         '-H', 'Accept: application/vnd.github+json',
         '-H', 'Content-Type: application/json']
        + (['--data-binary', '@-'] if body else [])
        + [f'https://api.github.com/repos/{REPO}{path}'],
        input=body, capture_output=True, timeout=timeout + 20)
    out = p.stdout.decode()
    try:
        return json.loads(out or '{}'), p.returncode
    except Exception:
        return {'_raw': out[:300], '_rc': p.returncode}, p.returncode

def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    d = json.load(open(CHANGES))
    blobs = json.load(open(BLOBS))
    def key(c):
        p = c['path']
        if p.startswith('groups/') and c['new']: return (0, p)
        if p.startswith('category/') and c['new']: return (1, p)
        if p.startswith('category/'): return (2, p)
        return (3, p)
    ordered = sorted(d['changed'], key=key)
    chunks = [ordered[i:i + CHUNK] for i in range(0, len(ordered), CHUNK)]
    state = {'commits': []}
    if os.path.exists(OUT):
        state = json.load(open(OUT))
    done = len(state['commits'])
    start = max(start, done)
    ref, _ = api('/git/refs/heads/main')
    commit_sha = ref['object']['sha']
    cm, _ = api(f'/git/commits/{commit_sha}')
    tree_sha = cm['tree']['sha']
    if done:
        commit_sha = state['commits'][-1]['commit']
        tree_sha = state['commits'][-1]['tree']
        print('resuming: last commit', commit_sha[:8], flush=True)
    for i in range(start, len(chunks)):
        ch = chunks[i]
        entries = [{'path': c['path'], 'mode': '100644', 'type': 'blob',
                    'sha': blobs[c['path']]} for c in ch]
        for attempt in range(6):
            t, rc = api('/git/trees', 'POST', {'base_tree': tree_sha, 'tree': entries}, 120)
            if t.get('sha'): break
            print(f'chunk {i}: tree attempt {attempt} failed:', str(t)[:150], flush=True)
            time.sleep(10)
        else:
            print(f'chunk {i}: TREE FAILED, aborting', flush=True); return
        tree_sha = t['sha']
        last = (i == len(chunks) - 1)
        msg = ('Add 1,450 new verified groups (48,659 -> 50,109 total); wave 20261104 fresh, parent-verified'
               if last else f'WGL deploy part {i+1}/{len(chunks)}: new group/category pages')
        cm2, rc = api('/git/commits', 'POST', {'message': msg, 'tree': tree_sha, 'parents': [commit_sha]}, 120)
        if not cm2.get('sha'):
            print(f'chunk {i}: COMMIT FAILED:', str(cm2)[:200], flush=True); return
        commit_sha = cm2['sha']
        ok = False
        for attempt in range(8):
            r, rc = api('/git/refs/heads/main', 'PATCH', {'sha': commit_sha}, 90)
            time.sleep(2)
            cur, _ = api('/git/refs/heads/main')
            if cur.get('object', {}).get('sha') == commit_sha:
                ok = True; break
            print(f'chunk {i}: ref attempt {attempt} not yet moved:', str(r)[:120], flush=True)
            time.sleep(8)
        if not ok:
            print(f'chunk {i}: REF UPDATE FAILED', flush=True); return
        state['commits'].append({'chunk': i, 'commit': commit_sha, 'tree': tree_sha,
                                 'files': len(ch), 'ref_updated': True})
        json.dump(state, open(OUT + '.tmp', 'w')); os.replace(OUT + '.tmp', OUT)
        print(f'chunk {i+1}/{len(chunks)} OK {commit_sha[:8]} ({len(ch)} files)', flush=True)
    print('FINAL:', commit_sha, flush=True)

if __name__ == '__main__':
    main()
