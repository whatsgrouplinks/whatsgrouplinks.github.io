#!/usr/bin/env python3
"""Sync the leg-1 deploy change set from the build dir to wgl-deploy via plain
copy (rsync breaks with 'Broken pipe' on this VM; cp uses plain file I/O).
Reads agent_batches/wave_20261106/deploy_changes_leg2.json (17,103 files).
Skips files already identical (same size + mtime within 1s + same git blob SHA
is too slow to check for all; size+mtime is enough given the partial rsync
already copied most files byte-identical). Retries EPERM per file.
Usage: python3 cp_sync_leg1.py
"""
import json, os, shutil, sys, time, hashlib

SITE = '/home/hatch/workspace/whatsapp-groups-site'
DEPLOY = '/home/hatch/workspace/wgl-deploy'
CHANGES = os.path.join(SITE, 'agent_batches', 'wave_20261106', 'deploy_changes_leg2.json')

def blob_sha(path):
    with open(path, 'rb') as f:
        data = f.read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()

def copy_retry(src, dst, tries=8):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for a in range(tries):
        try:
            shutil.copy2(src, dst)
            return True
        except PermissionError:
            time.sleep(2)
    return False

def main():
    d = json.load(open(CHANGES))
    changed = d['changed']
    print('to sync:', len(changed), flush=True)
    copied, skipped, failed = 0, 0, []
    for i, c in enumerate(changed):
        src = os.path.join(SITE, c['path'])
        dst = os.path.join(DEPLOY, c['path'])
        # skip if dest already matches the expected SHA
        if os.path.exists(dst):
            try:
                if blob_sha(dst) == c['sha']:
                    skipped += 1
                    continue
            except Exception:
                pass
        if copy_retry(src, dst):
            copied += 1
        else:
            failed.append(c['path'])
        if (i + 1) % 2000 == 0:
            print(f'  {i+1}/{len(changed)} copied:{copied} skipped:{skipped} failed:{len(failed)}', flush=True)
    print(f'DONE copied:{copied} skipped:{skipped} failed:{len(failed)}', flush=True)
    if failed:
        print('FAILED:', failed[:20], flush=True)
        json.dump(failed, open(os.path.join(SITE, 'agent_batches', 'wave_20261106', 'cp_sync_failed.json'), 'w'))
        sys.exit(1)

if __name__ == '__main__':
    main()
