#!/usr/bin/env python3
"""Verify wave_20261029 banked candidates (pending + fresh) in THIS run's sandbox.
Parallel curl, incremental state, og:title aliveness check. Writes parent_verified_20261029.json."""
import json, re, os, glob, html, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed

WAVE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(WAVE))
GROUPS = os.path.join(SITE, 'groups.json')
CODES_JSON = os.path.join(SITE, '.existing_codes.json')
STATE = os.path.join(WAVE, 'parent_verify_20261031_state.json')
OUT = os.path.join(WAVE, 'parent_verified_20261029.json')

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)')
OG_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', re.I)
PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b', re.I)
ADULT_EMOJI = set('🥵🍆🍑🔞💦👅👄💋')

def union():
    g = json.load(open(GROUPS))
    gc = {CODE_RE.search((x.get('invite') or '')).group(1)
          for x in g if CODE_RE.search(x.get('invite') or '')}
    ec = set(json.load(open(CODES_JSON)))
    return gc | ec

def check(code):
    try:
        p = subprocess.run(
            ['curl', '-sL', '--max-time', '20', '-A',
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
             'https://chat.whatsapp.com/' + code],
            capture_output=True, text=True, timeout=25)
        if p.returncode != 0:
            return None
        m = OG_RE.search(p.stdout or '')
        t = html.unescape(m.group(1)).strip() if m else ''
        if t.lower().startswith("couldn't look up"):
            return ''
        return t
    except Exception:
        return None

def item_of(code, src):
    """find the original item dict for a code across pending+fresh files"""
    return src.get(code)

def main():
    U = union()
    print('union:', len(U), flush=True)
    src = {}  # code -> item (prefer items with more fields)
    order = []
    for fn in sorted(glob.glob(os.path.join(WAVE, 'team*-unverified-pending.json'))) + \
              sorted(glob.glob(os.path.join(WAVE, 'team*-fresh-*.json'))):
        try:
            data = json.load(open(fn))
        except Exception as e:
            print('SKIP', fn, e, flush=True); continue
        lst = data if isinstance(data, list) else data.get('items', data.get('groups', []))
        for it in lst:
            inv = (it.get('invite') or '').strip()
            m = CODE_RE.search(inv)
            if not m:
                # pending files may store bare codes
                raw = (it.get('code') or it.get('invite_code') or '').strip()
                if raw and re.fullmatch(r'[A-Za-z0-9]{20,24}', raw):
                    it = dict(it); it['invite'] = 'https://chat.whatsapp.com/' + raw
                    m = CODE_RE.search(it['invite'])
            if not m:
                continue
            c = m.group(1)
            if '/invite/' in inv:
                continue  # channel format excluded per Oct 30 precedent
            if c in U:
                continue  # already in site
            if c not in src:
                src[c] = it; order.append(c)
            else:
                # prefer richer record
                if len(json.dumps(it)) > len(json.dumps(src[c])):
                    src[c] = it
    print('unique fresh codes to check:', len(order), flush=True)

    state = json.load(open(STATE)) if os.path.exists(STATE) else {'done': {}, 'live': [], 'dead': [], 'retry': []}
    done = state['done']
    todo = [c for c in order if c not in done]
    print('remaining:', len(todo), flush=True)

    def save():
        json.dump(state, open(STATE, 'w'))

    def one(c):
        t = check(c)
        return c, t

    live, dead, retry = list(state['live']), list(state['dead']), list(state['retry'])
    n = 0
    with ThreadPoolExecutor(max_workers=24) as ex:
        futs = {ex.submit(one, c): c for c in todo}
        for f in as_completed(futs):
            c, t = f.result()
            n += 1
            if t is None:
                # transport failure: one retry inline
                t = check(c)
            if t is None:
                retry.append(c); done[c] = 'retry'
            elif t:
                it = dict(src[c])
                it['verified_og_title'] = t
                live.append(it); done[c] = 'live'
            else:
                dead.append(c); done[c] = 'dead'
            if n % 200 == 0:
                state.update(live=live, dead=dead, retry=retry)
                save()
                print(f'{n}/{len(todo)} live={len(live)} dead={len(dead)}', flush=True)
    state.update(live=live, dead=dead, retry=retry)
    save()

    # content screening on live items
    kept, drops = [], {'porn': 0, 'adult_emoji': 0, 'bad': 0, 'nodata': 0}
    for it in live:
        text = ' '.join(str(it.get(k, '')) for k in ('name', 'description', 'category')) + ' ' + it.get('verified_og_title', '')
        if PORN_RE.search(text):
            drops['porn'] += 1; continue
        if any(e in text for e in ADULT_EMOJI):
            drops['adult_emoji'] += 1; continue
        if not it.get('name') or not it.get('invite'):
            drops['bad'] += 1; continue
        if not it.get('verified_og_title'):
            drops['nodata'] += 1; continue
        kept.append(it)
    json.dump(kept, open(OUT, 'w'), ensure_ascii=False)
    print('FINAL live:', len(live), 'dead:', len(dead), 'retry:', len(retry),
          'kept:', len(kept), 'drops:', drops, flush=True)

main()
