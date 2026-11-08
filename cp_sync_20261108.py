#!/usr/bin/env python3
"""Sync the wave-20261108 deploy change set from the build dir to wgl-deploy
via plain copy (rsync breaks with 'Broken pipe' on this VM).
Reads agent_batches/wave_20261108/deploy_changes_20261108.json.
Skips files whose dest already matches the expected SHA; deletes listed
deletions. Retries EPERM per file.
Usage: python3 cp_sync_20261108.py
"""
import hashlib, json, os, shutil, sys, time

SITE = '/home/hatch/workspace/whatsapp-groups-site'
DEPLOY = '/home/hatch/workspace/wgl-deploy'
CHANGES = os.path.join(SITE, 'agent_batches', 'wave_20261108',
                       'deploy_changes_20261108.json')

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
    deleted = d.get('deleted', [])
    print('to sync:', len(changed), 'to delete:', len(deleted), flush=True)
    copied, skipped, failed = 0, 0, []
    for i, c in enumerate(changed):
        src = os.path.join(SITE, c['path'])
        dst = os.path.join(DEPLOY, c['path'])
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
        if (i + 1) % 1000 == 0:
            print(f'  {i+1}/{len(changed)} copied:{copied} skipped:{skipped} failed:{len(failed)}', flush=True)
    del_failed = []
    for p in deleted:
        dst = os.path.join(DEPLOY, p)
        try:
            if os.path.exists(dst):
                os.remove(dst)
                print('  deleted:', p, flush=True)
        except Exception as e:
            del_failed.append((p, str(e)))
    print(f'DONE copied:{copied} skipped:{skipped} failed:{len(failed)} delete_failed:{len(del_failed)}', flush=True)
    if failed:
        print('FAILED:', failed[:20], flush=True)
        sys.exit(1)
    if del_failed:
        print('DELETE FAILED:', del_failed, flush=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
