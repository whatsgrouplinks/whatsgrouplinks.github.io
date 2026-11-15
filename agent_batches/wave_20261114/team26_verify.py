#!/usr/bin/env python3
"""team26 verifier: one keep-alive Session per worker thread; og:title is the live signal."""
import json, re, sys, time, html
import requests
from concurrent.futures import ThreadPoolExecutor

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.S)

def make_session():
    s = requests.Session()
    s.headers.update(UA)
    return s

def fetch_title(session, code):
    r = session.get(f'https://chat.whatsapp.com/{code}', timeout=75)
    m = TITLE_RE.search(r.text)
    title = html.unescape(m.group(1)).strip() if m else ''
    return r.status_code, title

def verify_one(code):
    s = make_session()
    try:
        for attempt in range(3):
            try:
                status, title = fetch_title(s, code)
            except Exception as e:
                return {'code': code, 'status': 'pending', 'reason': f'{type(e).__name__}: {e}', 'title': ''}
            if status == 429:
                return {'code': code, 'status': 'pending', 'reason': 'HTTP 429', 'title': ''}
            if title:
                return {'code': code, 'status': 'live', 'reason': '', 'title': title}
            if attempt < 2:
                time.sleep(35)
        return {'code': code, 'status': 'dead', 'reason': 'empty og:title x3', 'title': ''}
    finally:
        s.close()

if __name__ == '__main__':
    items = json.load(open(sys.argv[1]))
    codes = [it['code'] for it in items]
    out = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, res in enumerate(ex.map(verify_one, codes)):
            out.append(res)
            print(f"{i+1}/{len(codes)} {res['code']} {res['status']} {res['title'][:60]!r} {res['reason']}", flush=True)
    json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r['status'] for r in out))
