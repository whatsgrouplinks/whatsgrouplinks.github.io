#!/usr/bin/env python3
"""Verify igrupos retry candidates. Prints one JSON line per code to stdout:
{"code":..., "st":200|"timeout"|"error"|"429", "t":"og:title or ''"}"""
import json, re, html, sys, threading
from concurrent.futures import ThreadPoolExecutor
import requests

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
WORKERS = 16
TIMEOUT = 45

def og_title(page):
    for m in re.finditer(r'<meta[^>]*>', page, re.I):
        tag = m.group(0)
        if re.search(r'property=["\']og:title["\']', tag, re.I):
            cm = re.search(r'content=["\'](.*?)["\']', tag, re.I | re.S)
            if cm:
                return html.unescape(cm.group(1)).strip()
            return ''
    return ''

def main():
    cands = json.load(open('_team35_candidates.json'))
    # resume: skip codes already in _v_done.json
    done = set()
    try:
        done = set(json.load(open('_v_done.json')))
    except Exception:
        pass
    todo = [c for c in cands if c['code'] not in done]
    print('TOVERIFY ' + str(len(todo)), flush=True)
    stop429 = threading.Event()
    lock = threading.Lock()
    out = sys.stdout

    def worker(chunk):
        s = requests.Session()
        s.headers.update({'User-Agent': UA})
        for c in chunk:
            code = c['code']
            if stop429.is_set():
                rec = {'code': code, 'st': '429skip', 't': ''}
            else:
                try:
                    r = s.get('https://chat.whatsapp.com/' + code, timeout=TIMEOUT)
                    if r.status_code == 429:
                        stop429.set()
                        rec = {'code': code, 'st': '429', 't': ''}
                    elif r.status_code == 200:
                        rec = {'code': code, 'st': 200, 't': og_title(r.text)}
                    else:
                        rec = {'code': code, 'st': r.status_code, 't': ''}
                except requests.exceptions.Timeout:
                    rec = {'code': code, 'st': 'timeout', 't': ''}
                except Exception:
                    rec = {'code': code, 'st': 'error', 't': ''}
                    try:
                        s.close()
                    except Exception:
                        pass
                    s = requests.Session()
                    s.headers.update({'User-Agent': UA})
            with lock:
                out.write(json.dumps(rec, ensure_ascii=True) + '\n')

    chunks = [todo[i::WORKERS] for i in range(WORKERS)]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(worker, chunks))
    out.flush()

if __name__ == '__main__':
    main()
