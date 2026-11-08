#!/usr/bin/env python3
"""Leg-1 re-verification for wave 20261105 (run 2026-11-06).
Re-checks the 5,713 state1-dead codes never re-checked + 1 transport + 1 no-verdict code.
Uses curl (independent stack from the urllib passes) with Chrome UA; LIVE iff HTTP 200
and a non-empty og:title. Porn screen on the og:title (same regexes as parent_verify_wave.py).
Incremental state saved every 100 items. Spot-check mode: pass a JSON list file as argv[1]
and it checks only those codes, printing the live rate.
"""
import json, re, html, os, sys, subprocess, threading
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261105')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG_RE2 = re.compile(r"<meta\s+property='og:title'\s+content='([^']*)'", re.I)
PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal|orgasm|cumshot|blowjob)\b', re.I)
ADULT_EMOJI_RE = re.compile('[\U0001f97a\U0001f346\U0001f348\U0001f4a6\U0001f445\U0001f444\U0001f48b\U0001f51e]')
LOCK = threading.Lock()

def check_live(code):
    url = 'https://chat.whatsapp.com/' + code
    try:
        p = subprocess.run(['curl', '-sS', '-L', '--max-time', '25', '-A', UA, url],
                           capture_output=True, text=True, timeout=35)
        data = p.stdout or ''
        m = OG_RE.search(data) or OG_RE2.search(data)
        if not m:
            return ('dead', '')
        title = html.unescape(m.group(1)).strip()
        if not title:
            return ('dead', '')
        if PORN_RE.search(title):
            return ('porn:porn-regex', title)
        if ADULT_EMOJI_RE.search(title):
            return ('porn:adult-emoji', title)
        return ('live', title)
    except Exception as e:
        return ('transport', str(e)[:80])

def main():
    codes = json.load(open(sys.argv[1]))
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    spot = out_path is None
    state = {}
    if out_path and os.path.exists(out_path):
        state = json.load(open(out_path))
        print('resumed state:', len(state), flush=True)
    todo = [c for c in codes if c not in state]
    print('to check:', len(todo), 'of', len(codes), flush=True)
    done = [0]
    def work(code):
        v = check_live(code)
        with LOCK:
            state[code] = v
            done[0] += 1
            if out_path and done[0] % 100 == 0:
                json.dump(state, open(out_path, 'w'))
                print(f'  progress {done[0]}/{len(todo)}', flush=True)
        return v
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(work, todo))
    if out_path:
        json.dump(state, open(out_path, 'w'))
    from collections import Counter
    print('STATS', dict(Counter(v[0] for v in state.values())), flush=True)
    if spot:
        live = sum(1 for v in state.values() if v[0] == 'live')
        print(f'SPOTCHECK live {live}/{len(state)} = {live/len(state)*100:.1f}%', flush=True)

if __name__ == '__main__':
    main()
