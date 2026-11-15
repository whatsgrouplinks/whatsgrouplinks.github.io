#!/usr/bin/env python3
"""team26 verifier v2: phase A single attempt for all codes (logs to file, banks partials);
phase B retries only empties, 2 spaced retries. One keep-alive Session per worker thread."""
import json, re, sys, time, html
import requests
from concurrent.futures import ThreadPoolExecutor

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.S)
LOG = open('team26_verify.log', 'a', buffering=1)

def make_session():
    s = requests.Session()
    s.headers.update(UA)
    return s

def fetch_title(session, code):
    r = session.get(f'https://chat.whatsapp.com/{code}', timeout=60)
    m = TITLE_RE.search(r.text)
    title = html.unescape(m.group(1)).strip() if m else ''
    return r.status_code, title

def attempt(code, session):
    try:
        status, title = fetch_title(session, code)
    except Exception as e:
        return 'pending', '', f'{type(e).__name__}: {e}'
    if status == 429:
        return 'pending', '', 'HTTP 429'
    if title:
        return 'live', title, ''
    return 'empty', '', 'empty og:title'

def run_phase(codes, phase, retries, sleep_s):
    out = {}
    def work(code):
        s = make_session()
        try:
            status, title, reason = attempt(code, s)
            for a in range(retries):
                if status != 'empty':
                    break
                time.sleep(sleep_s)
                status, title, reason = attempt(code, s)
            rec = {'code': code, 'status': status, 'title': title, 'reason': reason}
            LOG.write(f"{phase} {code} {status} {title[:70]!r} {reason}\n")
            return rec
        finally:
            s.close()
    with ThreadPoolExecutor(max_workers=6) as ex:
        for rec in ex.map(work, codes):
            out[rec['code']] = rec
    return out

if __name__ == '__main__':
    items = json.load(open(sys.argv[1]))
    codes = [it['code'] for it in items]
    phaseA = run_phase(codes, 'A', 0, 0)
    json.dump(list(phaseA.values()), open('team26_verify_phaseA.json', 'w'), ensure_ascii=False, indent=1)
    empties = [c for c, r in phaseA.items() if r['status'] == 'empty']
    print(f"phase A done: live={sum(1 for r in phaseA.values() if r['status']=='live')} empty={len(empties)} pending={sum(1 for r in phaseA.values() if r['status']=='pending')}", flush=True)
    final = dict(phaseA)
    if empties:
        phaseB = run_phase(empties, 'B', 2, 25)
        for c, r in phaseB.items():
            if r['status'] == 'live':
                final[c] = r
            elif r['status'] == 'pending':
                final[c] = r
            else:
                final[c] = {'code': c, 'status': 'dead', 'title': '', 'reason': 'empty og:title x3'}
    json.dump(list(final.values()), open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r['status'] for r in final.values()))
