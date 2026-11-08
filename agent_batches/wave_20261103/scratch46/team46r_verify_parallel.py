#!/usr/bin/env python3
"""TEAM 46R parallel crypto/earning verifier (8 workers, fresh conn/request, stop on 429)."""
import json, re, time, html, os, threading
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
OG = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.S | re.I)
OG2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.S | re.I)

stop_event = threading.Event()
lock = threading.Lock()
done = {}        # code -> 'ok'|'dead'|'transport'|'rate-limited'
verified = []    # {'code','name','srcname'}
pending = []     # rate-limited / transport

def og_title(code):
    url = f'https://chat.whatsapp.com/{code}'
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=25)
    except Exception:
        return ('transport', None)
    if r.status_code == 429:
        return ('rate-limited', None)
    m = OG.search(r.text) or OG2.search(r.text)
    title = html.unescape(m.group(1)).strip() if m else ''
    return ('ok', title) if title else ('dead', None)

def worker(chunk):
    for p in chunk:
        if stop_event.is_set():
            with lock:
                if p['code'] not in done:
                    done[p['code']] = 'rate-limited'
                    pending.append({'code': p['code'], 'name': p.get('name',''), 'note': 'rate-limited (halted)'})
            continue
        status, title = og_title(p['code'])
        with lock:
            done[p['code']] = status
            if status == 'ok':
                verified.append({'code': p['code'], 'name': title, 'srcname': p.get('name','')})
            elif status == 'rate-limited':
                pending.append({'code': p['code'], 'name': p.get('name',''), 'note': 'rate-limited'})
                stop_event.set()
                print('RATE LIMITED — halting', flush=True)
            elif status == 'transport':
                pending.append({'code': p['code'], 'name': p.get('name',''), 'note': 'transport failure'})
            if len(done) % 40 == 0:
                json.dump({'done': done, 'pending': pending},
                          open(os.path.join(BASE, 'team46r_verify_state.json'), 'w'))
                print(f'progress: {len(done)} verified={len(verified)}', flush=True)
        time.sleep(0.6)

def main():
    pool = json.load(open(os.path.join(BASE, 'team46r_pool.json')))
    if os.path.exists(os.path.join(BASE, 'team46r_verify_state.json')):
        st = json.load(open(os.path.join(BASE, 'team46r_verify_state.json')))
        done.update(st['done']); pending.extend(st['pending'])
        pool = [p for p in pool if p['code'] not in done]
    print(f'to check: {len(pool)}', flush=True)
    n = 8
    chunks = [pool[i::n] for i in range(n)]
    with ThreadPoolExecutor(max_workers=n) as ex:
        list(ex.map(worker, chunks))
    json.dump({'done': done, 'pending': pending}, open(os.path.join(BASE, 'team46r_verify_state.json'), 'w'))
    json.dump(verified, open(os.path.join(BASE, 'team46r_verified_raw.json'), 'w'), ensure_ascii=False)
    ok = sum(1 for v in done.values() if v == 'ok')
    print(f'DONE: checked={len(done)} ok={ok} dead={sum(1 for v in done.values() if v=="dead")} '
          f'transport={sum(1 for v in done.values() if v=="transport")} ratelimited={sum(1 for v in done.values() if v=="rate-limited")}',
          flush=True)

if __name__ == '__main__':
    main()
