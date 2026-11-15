"""Retry pending (HTTP 429) codes from the state file with fewer workers.
Usage: team05_retry_pending.py <workers>"""
import json, re, html, os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

def og_title(h):
    m = re.search(r'<meta property="og:title" content="([^"]*)"', h or '')
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
    sess = get_sess()
    last_err = ''
    for attempt in range(3):
        try:
            r = sess.get(f'https://chat.whatsapp.com/{code}', timeout=75)
            if r.status_code == 429:
                time.sleep(20)
                last_err = 'HTTP 429'
                continue
            t = og_title(r.text)
            if t:
                return ('live', t, '')
            last_err = f'HTTP {r.status_code} empty og:title'
            time.sleep(8 + attempt * 8)
        except Exception as e:
            last_err = f'{type(e).__name__}: {e}'
            time.sleep(8 + attempt * 8)
    if 'Connect' in last_err or 'Timeout' in last_err or 'Proxy' in last_err or 'SSLError' in last_err or 'RemoteDisconnected' in last_err or 'ChunkedEncoding' in last_err or 'ConnectionError' in last_err or '429' in last_err:
        return ('pending', None, last_err)
    if 'empty og:title' in last_err:
        return ('dead', None, last_err)
    return ('pending', None, last_err)

def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    state_path = os.path.join(WAVE, 'team05_verified_p61_160.json.state.json')
    done = json.load(open(state_path, encoding='utf-8'))
    todo = [r for r in done.values() if r['status'] == 'pending']
    print(f'retrying {len(todo)} pending codes, {workers} workers', flush=True)
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
            if n[0] % 10 == 0:
                with open(state_path, 'w', encoding='utf-8') as f:
                    json.dump(done, f, ensure_ascii=False)
                print(f'{n[0]}/{len(todo)} live={sum(1 for r in done.values() if r["status"]=="live")} dead={sum(1 for r in done.values() if r["status"]=="dead")} pending={sum(1 for r in done.values() if r["status"]=="pending")}', flush=True)
        time.sleep(1.5)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, todo))
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(done, f, ensure_ascii=False)
    with open(os.path.join(WAVE, 'team05_verified_p61_160.json'), 'w', encoding='utf-8') as f:
        json.dump(list(done.values()), f, ensure_ascii=False, indent=1)
    live = sum(1 for r in done.values() if r['status'] == 'live')
    dead = sum(1 for r in done.values() if r['status'] == 'dead')
    pend = sum(1 for r in done.values() if r['status'] == 'pending')
    print(f'DONE live={live} dead={dead} pending={pend} total={len(done)}', flush=True)

if __name__ == '__main__':
    main()
