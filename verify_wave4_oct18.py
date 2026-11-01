#!/usr/bin/env python3
"""Phase 1B: Verify queued candidate links (parallel, resumable).
Input: wave4_new_oct18.json. Output: wave4_verified_oct18.json (only 'ok' links).
Upgrades generic names from og:title.
"""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

SITE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SITE)
from check_links import check_link, CANARY_URL

IN_FILE = os.path.join(SITE, 'wave4_new_oct18.json')
OUT_FILE = os.path.join(SITE, 'wave4_verified_oct18.json')
STATE_FILE = os.path.join(SITE, 'wave4_state.json')
WORKERS = int(os.environ.get('VERIFY_WORKERS', '60'))
SAVE_EVERY = 2000
CANARY_EVERY = 10000

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except Exception:
            return {}
    return {}

def save_state(s):
    tmp = STATE_FILE + '.tmp'
    json.dump(s, open(tmp, 'w'))
    os.replace(tmp, STATE_FILE)

def generic_name(n):
    n = (n or '').strip()
    return (not n) or n.startswith('WhatsApp Group ') or len(n) < 4

def main():
    cands = json.load(open(IN_FILE))
    state = load_state()
    pending = [c for c in cands if c['invite'] not in state]
    print(f'Verifying {len(pending)} links ({len(cands)-len(pending)} resumed) '
          f'with {WORKERS} workers...', flush=True)

    ok, dead, uncheck = 0, 0, 0
    done = 0
    t0 = time.time()
    verified = []
    # reload previously verified ok records
    prev = {}
    if os.path.exists(OUT_FILE):
        try:
            for c in json.load(open(OUT_FILE)):
                prev[c['invite']] = c
        except Exception:
            pass
    verified = list(prev.values())
    ok = len(verified)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(check_link, c['invite']): c for c in pending}
        for fut in futs:
            c = futs[fut]
            done += 1
            try:
                status, detail = fut.result()
            except Exception as e:
                status, detail = 'uncheckable', str(e)[:50]
            state[c['invite']] = status
            if status == 'ok':
                ok += 1
                if generic_name(c.get('name')) and detail and len(detail) > 3:
                    c['name'] = detail
                    if not c.get('description'):
                        c['description'] = (f'Join {detail}, a WhatsApp group listed '
                                            f'under {c.get("category","Community & Social")}.')
                verified.append(c)
            elif status == 'dead':
                dead += 1
            else:
                uncheck += 1
            if done % 5000 == 0 or done == len(pending):
                el = time.time() - t0
                print(f'  {done}/{len(pending)} ok={ok} dead={dead} '
                      f'uncheck={uncheck} {el:.0f}s', flush=True)
            if done % SAVE_EVERY == 0:
                save_state(state)
                json.dump(verified, open(OUT_FILE, 'w'), ensure_ascii=False)
            if done % CANARY_EVERY == 0:
                cs, _ = check_link(CANARY_URL)
                if cs != 'ok':
                    print(f'CANARY FAILED ({cs}) — aborting, nothing lost.', flush=True)
                    save_state(state)
                    json.dump(verified, open(OUT_FILE, 'w'), ensure_ascii=False)
                    return

    save_state(state)
    json.dump(verified, open(OUT_FILE, 'w'), ensure_ascii=False)
    el = (time.time() - t0) / 60
    print(f'\nDONE in {el:.1f} min: ok={ok} dead={dead} uncheck={uncheck} '
          f'-> {OUT_FILE}', flush=True)

if __name__ == '__main__':
    main()
