#!/usr/bin/env python3
"""TEAM 46R crypto/earning verifier. Reads team46r_pool.json, verifies via chat.whatsapp.com og:title."""
import json, re, time, html, sys, os
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
OG = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.S | re.I)
OG2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.S | re.I)

def og_title(code):
    url = f'https://chat.whatsapp.com/{code}'
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=25)
    except Exception as e:
        return ('transport', None)
    if r.status_code == 429:
        return ('rate-limited', None)
    m = OG.search(r.text) or OG2.search(r.text)
    title = html.unescape(m.group(1)).strip() if m else ''
    if title:
        return ('ok', title)
    return ('dead', None)

def main():
    pool = json.load(open(os.path.join(BASE, 'team46r_pool.json')))
    done_state = os.path.join(BASE, 'team46r_verify_state.json')
    state = {'done': {}, 'pending': []}
    if os.path.exists(done_state):
        state = json.load(open(done_state))
    done = state['done']
    pending = state['pending']

    verified, dead, transp = [], 0, []
    started = len(done)
    for p in pool:
        code = p['code']
        if code in done:
            continue
        status, title = og_title(code)
        if status == 'rate-limited':
            pending.append({'code': code, 'name': p.get('name',''), 'note': 'rate-limited'})
            done[code] = 'rate-limited'
            break  # stop verifying for this wave per brief
        elif status == 'transport':
            transp.append({'code': code, 'name': p.get('name',''), 'note': 'transport failure'})
            done[code] = 'transport'
        elif status == 'dead':
            dead += 1
            done[code] = 'dead'
        else:
            verified.append({'code': code, 'name': title, 'srcname': p.get('name','')})
            done[code] = 'ok'
        time.sleep(0.7)
        if len(done) % 40 == 0:
            json.dump(state := {'done': done, 'pending': pending + transp}, open(done_state, 'w'))
            print(f'progress: {len(done)}/{len(pool)} verified={len(verified)} dead={dead} transport={len(transp)}', flush=True)

    json.dump({'done': done, 'pending': pending + transp}, open(done_state, 'w'))
    json.dump(verified, open(os.path.join(BASE, 'team46r_verified_raw.json'), 'w'), ensure_ascii=False)
    print(f'DONE: checked={len(done)} verified={len(verified)} dead={dead} transport={len(transp)} pending_rate_limited={len(pending)}', flush=True)

if __name__ == '__main__':
    main()
