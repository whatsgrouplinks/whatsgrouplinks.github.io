#!/usr/bin/env python3
"""Retry wave2 'uncheckable' links. Input: wave2_retry_oct18.json.
Appends newly-ok to wave2_verified_oct18.json; updates wave2_state.json."""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor

SITE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SITE)
from check_links import check_link

IN_FILE = os.path.join(SITE, 'wave2_retry_oct18.json')
OUT_FILE = os.path.join(SITE, 'wave2_verified_oct18.json')
STATE_FILE = os.path.join(SITE, 'wave2_state.json')
WORKERS = int(os.environ.get('VERIFY_WORKERS', '25'))

def generic_name(n):
    n = (n or '').strip()
    return (not n) or n.startswith('WhatsApp Group ') or len(n) < 4

def main():
    cands = json.load(open(IN_FILE))
    state = json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {}
    verified = json.load(open(OUT_FILE)) if os.path.exists(OUT_FILE) else []
    print(f'Retrying {len(cands)} links with {WORKERS} workers...', flush=True)
    ok, dead, uncheck = 0, 0, 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(check_link, c['invite']): c for c in cands}
        for fut in futs:
            c = futs[fut]
            try:
                status, detail = fut.result()
            except Exception as e:
                status, detail = 'uncheckable', str(e)[:50]
            state[c['invite']] = status
            if status == 'ok':
                ok += 1
                if generic_name(c.get('name')) and detail and len(detail) > 3:
                    c['name'] = detail
                verified.append(c)
            elif status == 'dead':
                dead += 1
            else:
                uncheck += 1
    json.dump(state, open(STATE_FILE, 'w'))
    json.dump(verified, open(OUT_FILE, 'w'), ensure_ascii=False)
    print(f'RETRY DONE: ok={ok} dead={dead} uncheck={uncheck} '
          f'total verified={len(verified)}', flush=True)

if __name__ == '__main__':
    main()
