#!/usr/bin/env python3
"""WGL Data-API deploy — stage 2: parallel blob uploads via curl.
Saves agent_batches/wave_20261105/deploy_blobs_leg1.json incrementally."""
import os, json, base64, subprocess, threading, time
from concurrent.futures import ThreadPoolExecutor

SITE = '/home/hatch/workspace/whatsapp-groups-site'
WAVE = os.path.join(SITE, 'agent_batches', 'wave_20261105')
CHANGES = os.path.join(WAVE, 'deploy_changes_leg1.json')
BLOBS = os.path.join(WAVE, 'deploy_blobs_leg1.json')
REPO = 'whatsgrouplinks/whatsgrouplinks.github.io'
WORKERS = 30

def token():
    u = subprocess.run(['git', '-C', '/home/hatch/workspace/wgl-deploy',
                        'config', '--get', 'remote.origin.url'],
                       capture_output=True, text=True).stdout.strip()
    return u.split(':')[2].split('@')[0]
T = token()

def upload(c):
    with open(c['local'], 'rb') as f:
        data = f.read()
    body = json.dumps({'content': base64.b64encode(data).decode(),
                       'encoding': 'base64'})
    for attempt in range(4):
        try:
            p = subprocess.run(
                ['curl', '-s', '--max-time', '180', '-X', 'POST',
                 '-H', 'Authorization: Bearer ' + T,
                 '-H', 'Accept: application/vnd.github+json',
                 '-H', 'Content-Type: application/json',
                 '--data-binary', '@-',
                 f'https://api.github.com/repos/{REPO}/git/blobs'],
                input=body.encode(), capture_output=True, timeout=200)
            r = json.loads(p.stdout.decode() or '{}')
            sha = r.get('sha')
            if sha:
                return c['path'], sha, sha == c['sha'], None
            err = r.get('message', p.stdout.decode()[:120])
        except Exception as e:
            err = str(e)[:120]
        time.sleep(5 + attempt * 5)
    return c['path'], None, False, err

def main():
    d = json.load(open(CHANGES))
    changed = d['changed']
    done = {}
    if os.path.exists(BLOBS):
        done = json.load(open(BLOBS))
        print('resuming, already have:', len(done), flush=True)
    todo = [c for c in changed if done.get(c['path']) != c['sha']]
    print('to upload:', len(todo), flush=True)
    lock = threading.Lock()
    n = [0]; fails = []
    def save():
        with lock:
            for _a in range(12):
                try:
                    tmp = BLOBS + '.tmp'
                    json.dump(done, open(tmp, 'w'))
                    os.replace(tmp, BLOBS)
                    return
                except PermissionError:
                    time.sleep(5)
            print('WARNING: blob-state save failed after retries (in-memory kept)', flush=True)
    def work(c):
        path, sha, match, err = upload(c)
        with lock:
            n[0] += 1
            if sha:
                done[path] = sha
                if not match:
                    fails.append((path, 'sha-mismatch'))
            else:
                fails.append((path, err))
            if n[0] % 25 == 0:
                print(f'{n[0]}/{len(todo)} fails:{len(fails)}', flush=True)
        if n[0] % 25 == 0:
            save()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, todo))
    save()
    print('DONE uploaded:', len(done), 'fails:', len(fails), flush=True)
    for f in fails[:20]:
        print('FAIL', f, flush=True)

if __name__ == '__main__':
    main()
