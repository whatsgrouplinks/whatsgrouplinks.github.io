#!/usr/bin/env python3
"""Resilient deploy sync for WGL: cp-based, retries EPERM windows.
Usage: python3 wgl_sync_deploy.py"""
import os, sys, time, shutil

SITE = '/home/hatch/workspace/whatsapp-groups-site'
DEP = '/home/hatch/workspace/wgl-deploy'

def robust_copy(src, dst, tries=8):
    for a in range(tries):
        try:
            # read fully, write in one go (small files); python open/write
            with open(src, 'rb') as f:
                data = f.read()
            tmp = dst + '.tmpcopy'
            with open(tmp, 'wb') as f:
                f.write(data)
            os.replace(tmp, dst)
            return True
        except PermissionError:
            time.sleep(2 + a * 2)
        except OSError as e:
            if 'Operation not permitted' in str(e):
                time.sleep(2 + a * 2)
            else:
                raise
    return False

def sync_dir(d):
    src = os.path.join(SITE, d); dst = os.path.join(DEP, d)
    os.makedirs(dst, exist_ok=True)
    build_files = {}
    for root, _, files in os.walk(src):
        for f in files:
            p = os.path.join(root, f)
            build_files[os.path.relpath(p, src)] = os.path.getsize(p)
    dep_files = set()
    for root, _, files in os.walk(dst):
        for f in files:
            dep_files.add(os.path.relpath(os.path.join(root, f), dst))
    copied = failed = deleted = 0
    for rel, sz in build_files.items():
        dp = os.path.join(dst, rel)
        if rel in dep_files and os.path.getsize(dp) == sz:
            continue
        dd = os.path.dirname(dp)
        os.makedirs(dd, exist_ok=True)
        if robust_copy(os.path.join(src, rel), dp):
            copied += 1
        else:
            failed += 1
            print('FAIL-COPY', rel, flush=True)
    for rel in dep_files - set(build_files):
        try:
            os.remove(os.path.join(dst, rel)); deleted += 1
        except OSError as e:
            print('FAIL-DEL', rel, e, flush=True)
    # prune empty dirs in deploy
    for root, dirs, files in os.walk(dst, topdown=False):
        for dd in dirs:
            try:
                os.rmdir(os.path.join(root, dd))
            except OSError:
                pass
    print(d, 'copied:', copied, 'failed:', failed, 'deleted-stale:', deleted, flush=True)

def main():
    for d in ('groups', 'category', 'blog', 'assets'):
        sync_dir(d)
    import glob
    n = 0
    for f in glob.glob(os.path.join(SITE, '*.html')) + glob.glob(os.path.join(SITE, '*.xml')) + glob.glob(os.path.join(SITE, '*.txt')):
        dst = os.path.join(DEP, os.path.basename(f))
        if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(f):
            if robust_copy(f, dst):
                n += 1
            else:
                print('FAIL-COPY root', os.path.basename(f), flush=True)
    print('root files copied:', n, flush=True)
    # gate check (a): file sets identical
    for d in ('groups', 'category'):
        s = {os.path.relpath(os.path.join(r, f), os.path.join(SITE, d))
             for r, _, fs in os.walk(os.path.join(SITE, d)) for f in fs}
        t = {os.path.relpath(os.path.join(r, f), os.path.join(DEP, d))
             for r, _, fs in os.walk(os.path.join(DEP, d)) for f in fs}
        print(d, 'build:', len(s), 'deploy:', len(t), 'symdiff:', len(s ^ t), flush=True)

if __name__ == '__main__':
    main()
