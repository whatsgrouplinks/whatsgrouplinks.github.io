"""Verify fresh codes with persistent sessions (one per worker thread).
LIVE only if NON-EMPTY, NON-GENERIC og:title (html-unescaped).
Empty og:title -> retry up to 3x spaced. HTTP 429 / transport failure -> PENDING.
Usage: team05_verify.py <fresh.json> <tag> [workers]"""
import json, re, html, os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
GENERIC = {'whatsapp group invite', 'whatsapp group link', 'whatsapp group'}

def og_title(h):
    m = re.search(r'<meta property="og:title" content="([^"]*)"', h or '')
    return html.unescape(m.group(1)).strip() if m else ''

def og_desc(h):
    m = re.search(r'<meta property="og:description" content="([^"]*)"', h or '')
    return html.unescape(m.group(1)).strip() if m else ''

_thread_local = threading.local()

def get_sess():
    s = getattr(_thread_local, 'sess', None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        _thread_local.sess = s
    return s

def check_one(code):
    """Returns (status, og_title_or_None, reason). status in live/dead/pending."""
    sess = get_sess()
    last_err = ''
    for attempt in range(3):
        try:
            r = sess.get(f'https://chat.whatsapp.com/{code}', timeout=75)
            if r.status_code == 429:
                return ('pending', None, 'HTTP 429')
            t = og_title(r.text)
            if t:
                return ('live', t, '')
            # empty title: spaced retry
            last_err = f'HTTP {r.status_code} empty og:title'
            time.sleep(6 + attempt * 6)
        except Exception as e:
            last_err = f'{type(e).__name__}: {e}'
            if '429' in str(e) or 'Too Many' in str(e):
                return ('pending', None, last_err)
            time.sleep(6 + attempt * 6)
    # after 3 empty/failed attempts: transport-ish failures -> pending, clean empties -> dead
    if 'Connect' in last_err or 'Timeout' in last_err or 'Proxy' in last_err or 'SSLError' in last_err or 'RemoteDisconnected' in last_err or 'ChunkedEncoding' in last_err or 'ConnectionError' in last_err:
        return ('pending', None, last_err)
    if 'empty og:title' in last_err:
        return ('dead', None, last_err)
    return ('pending', None, last_err)

def main():
    fresh_file, tag = sys.argv[1], sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fresh = json.load(open(os.path.join(WAVE, fresh_file), encoding='utf-8'))
    out_path = os.path.join(WAVE, f'team05_verified_{tag}.json')
    state_path = out_path + '.state.json'
    done = {}
    if os.path.exists(state_path):
        done = json.load(open(state_path, encoding='utf-8'))
        print(f'resuming: {len(done)} already done', flush=True)
    todo = [f for f in fresh if f['code'] not in done]
    print(f'verifying {len(todo)} codes, {workers} workers', flush=True)
    lock = threading.Lock()
    n = [0]

    def work(item):
        status, title, reason = check_one(item['code'])
        rec = dict(item)
        rec['status'] = status
        rec['og_title'] = title or ''
        rec['verify_reason'] = reason
        with lock:
            done[item['code']] = rec
            n[0] += 1
            if n[0] % 25 == 0:
                with open(state_path, 'w', encoding='utf-8') as f:
                    json.dump(done, f, ensure_ascii=False)
                print(f'{n[0]}/{len(todo)} live={sum(1 for r in done.values() if r["status"]=="live")} dead={sum(1 for r in done.values() if r["status"]=="dead")} pending={sum(1 for r in done.values() if r["status"]=="pending")}', flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, todo))
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(list(done.values()), f, ensure_ascii=False, indent=1)
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(done, f, ensure_ascii=False)
    live = sum(1 for r in done.values() if r['status'] == 'live')
    dead = sum(1 for r in done.values() if r['status'] == 'dead')
    pend = sum(1 for r in done.values() if r['status'] == 'pending')
    print(f'DONE live={live} dead={dead} pending={pend} total={len(done)}', flush=True)

if __name__ == '__main__':
    main()
