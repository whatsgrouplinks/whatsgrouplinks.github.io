#!/usr/bin/env python3
"""Team16 wave 20261105 — PHASE 2 verify candidates via chat.whatsapp.com og:title.
Control code must return non-empty og:title first, else everything -> pending.
Checkpoints to team16_verify_ckpt.json every 25 items (wave dir, NOT /tmp).
Writes team16-groupjoin.json, team16-unverified-pending.json, team16-leads.json.
"""
import re, json, time, random, html, os, sys, subprocess, threading
from concurrent.futures import ThreadPoolExecutor

WORK = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
CONTROL = 'KrDwdK8EIkB6vgauHg5M7N'
STOP = threading.Event()   # set on sustained 429

def og_title(code):
    """Returns (og_title or None, http_code, note)."""
    url = f'https://chat.whatsapp.com/{code}'
    try:
        p = subprocess.run(
            ['curl', '-sL', '-A', UA, '--max-time', '20', '-w', '\n%{http_code}', url],
            capture_output=True, timeout=35)
        out = p.stdout.decode('utf-8', 'ignore')
        lines = out.rsplit('\n', 1)
        http = lines[1].strip() if len(lines) > 1 else ''
        body = lines[0] if len(lines) > 1 else out
        m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
        title = html.unescape(m.group(1)).strip() if m else None
        return title, http, ''
    except Exception as e:
        return None, '', f'error:{e}'

def verify_one(entry):
    code = entry['_code']
    time.sleep(random.uniform(0.5, 2.0))
    if STOP.is_set():
        return entry, None, 'stopped-429'
    title, http, note = og_title(code)
    if http == '429':
        time.sleep(180)
        title, http, note = og_title(code)
        if http == '429':
            STOP.set()
            return entry, None, 'http-429-after-backoff'
    if title:
        return entry, title, ''
    if http == '429':
        return entry, None, 'http-429'
    if http and http != '200':
        return entry, None, f'http-{http}'
    return entry, None, 'empty-og:title'

def main():
    data = json.load(open(f'{WORK}/team16_candidates.json'))
    cands = data['candidates']
    print(f'verifying {len(cands)} candidates', flush=True)
    title, http, _ = og_title(CONTROL)
    print(f'CONTROL {CONTROL}: http={http} og:title={title!r}', flush=True)
    if not title:
        pending = [{'code': c['_code'], 'name': c.get('name') or None,
                    'note': 'verification-blocked: control code also empty og:title'} for c in cands]
        json.dump([], open(f'{WORK}/team16-groupjoin.json', 'w'), ensure_ascii=False, indent=1)
        json.dump(pending, open(f'{WORK}/team16-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
        print('VERIFICATION BLOCKED - control empty', flush=True)
        return
    import importlib.util
    spec = importlib.util.spec_from_file_location('gj', f'{WORK}/team16_harvest.py')
    gj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gj)
    verified, pending, blocked_og = [], [], []
    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for entry, og, note in ex.map(verify_one, cands):
            if og:
                rec = {'title': og, 'desc': entry.get('_desc_raw') or '', 'tags': ''}
                reason = gj.blocked_reason(rec)
                if reason:
                    blocked_og.append({'code': entry['_code'], 'name': og, 'reason': f'og:title-blocked:{reason}'})
                else:
                    e = {k: entry[k] for k in ('name', 'category', 'country', 'description', 'invite', 'image')}
                    if not e['name']:
                        e['name'] = gj.clean_text(og)
                    if not e['name']:
                        pending.append({'code': entry['_code'], 'name': og, 'note': 'empty-name-after-clean'})
                    else:
                        verified.append(e)
            else:
                pending.append({'code': entry['_code'], 'name': entry.get('name') or None,
                                'note': note or 'empty-og:title'})
            done += 1
            if done % 25 == 0:
                print(f'progress done={done} verified={len(verified)} pending={len(pending)} blocked_og={len(blocked_og)} stop429={STOP.is_set()}', flush=True)
                json.dump({'verified': verified, 'pending': pending, 'blocked_og': blocked_og, 'done': done},
                          open(f'{WORK}/team16_verify_ckpt.json', 'w'), ensure_ascii=False, indent=1)
    out = [{k: v[k] for k in ('name', 'category', 'country', 'description', 'invite', 'image')} for v in verified]
    json.dump(out, open(f'{WORK}/team16-groupjoin.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(f'{WORK}/team16-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(blocked_og, open(f'{WORK}/team16_blocked_by_ogtitle.json', 'w'), ensure_ascii=False, indent=1)
    json.dump({'verified': verified, 'pending': pending, 'blocked_og': blocked_og, 'done': done},
              open(f'{WORK}/team16_verify_ckpt.json', 'w'), ensure_ascii=False, indent=1)
    print(f'VERIFY DONE verified={len(out)} pending={len(pending)} blocked_by_ogtitle={len(blocked_og)}', flush=True)

if __name__ == '__main__':
    main()
