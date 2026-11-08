#!/usr/bin/env python3
"""Parent verification for wave_20261102 fresh teams.
Loads teamNN-*.json verified files (excl. pending/leads), dedupes against union,
curl-verifies each invite (HTTP 2xx + non-empty og:title), screens porn/adult/scam.
"""
import json, re, html, subprocess, os, glob, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

SITE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.join(SITE, 'agent_batches', 'wave_20261102')
OUT = os.path.join(WAVE, 'parent_verified_wave20261102.json')
STATE = os.path.join(WAVE, 'parent_verify_fresh_state.json')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
LOCK = threading.Lock()

PORN_RE = re.compile(r'\b(porn|pornhub|xxx|hardcore|hentai|nudes?|sex\s?video|blue\s?film|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b', re.I)
ADULT_EMOJI_RE = re.compile(r'[🥵🔞🍑🍆💦]')
SCAM_RE = re.compile(r'counterfeit|fake\s*(currency|money|notes?)|money\s*mule|receiver\s*and\s*loader|passcode|phish|click\s*here\s*to\s*claim|bitfinexinvest', re.I)
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9\-_]{20,24})')

def load_union():
    codes = set()
    gj = json.load(open(os.path.join(SITE, 'groups.json')))
    for g in gj:
        m = CODE_RE.search(g.get('invite', '') or '')
        if m: codes.add(m.group(1))
    ex = json.load(open(os.path.join(SITE, '.existing_codes.json')))
    codes.update(ex if isinstance(ex, list) else list(ex))
    return codes

def fetch(url):
    p = subprocess.run(['curl', '-s', '-L', '--max-time', '20', '-A', UA,
                        '-w', '\n%{http_code}', url],
                       capture_output=True, timeout=30)
    body = p.stdout.decode('utf-8', errors='ignore')
    lines = body.rsplit('\n', 1)
    code = lines[1].strip() if len(lines) == 2 else '000'
    t = lines[0]
    m = re.search(r'og:title[^>]*?content="([^"]*)"', t)
    title = html.unescape(m.group(1)).strip() if m else None
    return code, title

def classify(url):
    for _ in range(2):
        try:
            code, title = fetch(url)
        except Exception:
            return 'transport', 'exception'
        if code == '000':
            continue
        if code.startswith('2') and title:
            return 'live', title
        if code.startswith('2'):
            return 'dead', 'empty og:title'
        return 'dead', 'http ' + code
    return 'transport', 'curl 000 x2'

def main():
    files = [f for f in sorted(glob.glob(os.path.join(WAVE, 'team*.json')))
             if '-unverified-pending' not in f and '-leads' not in f]
    items = []
    for f in files:
        try:
            d = json.load(open(f))
            for it in (d if isinstance(d, list) else list(d.values())):
                if isinstance(it, dict) and it.get('invite'):
                    it['_src'] = os.path.basename(f); items.append(it)
        except Exception as e:
            print('ERR', f, e)
    print('loaded team items:', len(items), 'from', len(files), 'files', flush=True)
    union = load_union(); print('union codes:', len(union), flush=True)
    seen, fresh = set(), []
    ndup_union = ndup_wave = nbad = 0
    for it in items:
        m = CODE_RE.search(it.get('invite', ''))
        c = m.group(1) if m else ''
        if not c: nbad += 1; continue
        if c in union: ndup_union += 1; continue
        if c in seen: ndup_wave += 1; continue
        seen.add(c); it['_code'] = c; fresh.append(it)
    print('fresh to check:', len(fresh), 'dup-union:', ndup_union, 'dup-wave:', ndup_wave, 'bad:', nbad, flush=True)
    try:
        state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    except Exception:
        state = {}
    live, dead, transport, dropped = [], [], [], []
    def work(it):
        c = it['_code']
        with LOCK:
            if c in state: return c, list(state[c])
        status, detail = classify(it['invite'])
        with LOCK:
            state[c] = [status, detail]
            return c, list(state[c])
    n = 0
    with ThreadPoolExecutor(max_workers=30) as ex:
        futs = {ex.submit(work, it): it for it in fresh}
        for f in as_completed(futs):
            it = futs[f]; c, (status, detail) = f.result(); n += 1
            name = (it.get('name') or '').strip()
            txt = name + ' ' + (it.get('description') or '')
            if status == 'live':
                if PORN_RE.search(txt): dropped.append((c, 'porn')); continue
                if ADULT_EMOJI_RE.search(name): dropped.append((c, 'adult-emoji')); continue
                if SCAM_RE.search(txt): dropped.append((c, 'scam')); continue
                if not name:
                    if detail and len(detail) > 1: it['name'] = detail[:120]
                    else: dropped.append((c, 'empty-name')); continue
                if 'http' in name.lower(): it['name'] = detail[:120] if detail else name
                it['_ogtitle'] = detail
                live.append(it)
            elif status == 'dead': dead.append((c, detail))
            else: transport.append((c, detail))
            if n % 100 == 0:
                with LOCK: snap = dict(state)
                json.dump(snap, open(STATE, 'w'))
                print('progress %d/%d (live %d)' % (n, len(fresh), len(live)), flush=True)
    with LOCK: snap = dict(state)
    json.dump(snap, open(STATE, 'w'))
    for it in live: it.pop('_src', None); it.pop('_code', None); it.pop('_ogtitle', None)
    json.dump(live, open(OUT, 'w'), ensure_ascii=False)
    print('LIVE:', len(live), 'DEAD:', len(dead), 'TRANSPORT:', len(transport), flush=True)
    from collections import Counter
    print('dropped:', dict(Counter(r for _, r in dropped)), flush=True)
    print('transport codes:', [c for c, _ in transport][:10], flush=True)

main()
