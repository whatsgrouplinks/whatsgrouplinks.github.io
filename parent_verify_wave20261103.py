#!/usr/bin/env python3
"""Parent verification for wave_20261103 banked team files.
Dedupe against current union, liveness-check via og:title (keep-alive session),
porn/adult screen, output parent_verified.json. Incremental state survives restarts.
Usage: python3 parent_verify_wave20261103.py"""
import json, re, os, sys, html, threading
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.join(BASE, 'agent_batches', 'wave_20261103')
OUT = os.path.join(WAVE, 'parent_verified.json')
STATE = os.path.join(WAVE, 'parent_verify_state.json')
PENDING = os.path.join(WAVE, 'parent_verify_pending_transport.json')

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
OG_RE = re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', re.I)

PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal|bokep)\b', re.I)
PORN_URDU_RE = re.compile(r'مزا\s?دینے|مزہ\s?دینے', re.I)
ADULT_EMOJI = set('🥵🍆🍑🔞💦👅👄💋')

SKIP_FILES = {'team30b-groupsinvite.json',        # 100% dup of team30
              'team46b-crypto-earning-extra.json',  # 100% dup of team46
              'team16-verified-raw.json',            # 100% dup of team16-igrupos-conosur
              'team41b-germany.json'}               # strict subset of team41-germany
IGNORE_SUBSTR = ('-leads', '-pending', '-state', '-progress', '-probe', '-mule',
                 '-candidates', '-tails', 'parent', 'team14_merged', 'team11_postfix')

def code_of(invite):
    m = CODE_RE.search(invite or '')
    return m.group(1) if m else None

def og_title(text):
    m = OG_RE.search(text or '')
    if not m:
        return ''
    return html.unescape(m.group(1)).strip()

def adult_screen(name, desc):
    t = f"{name} {desc}"
    if PORN_RE.search(t):
        return 'porn-regex'
    if PORN_URDU_RE.search(t):
        return 'porn-urdu'
    if any(e in t for e in ADULT_EMOJI):
        return 'adult-emoji'
    return None

_tls = threading.local()
def session():
    s = getattr(_tls, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
        _tls.s = s
    return s

def check_live(item):
    """Return (verdict, og_name): live / dead / transport."""
    url = item['invite']
    try:
        r = session().get(url, timeout=45, allow_redirects=True)
    except (requests.Timeout, requests.ConnectionError):
        return 'transport', ''
    except Exception:
        return 'transport', ''
    try:
        return ('live' if og_title(r.text) else 'dead'), og_title(r.text)
    except Exception:
        return 'transport', ''

def main():
    union = set(json.load(open(os.path.join(BASE, 'agent_batches', 'wave_20261104', 'dedupe_union.json'))))
    print('union:', len(union), flush=True)

    files = [f for f in sorted(os.listdir(WAVE)) if f.startswith('team') and f.endswith('.json')
             and f not in SKIP_FILES and not any(s in f for s in IGNORE_SUBSTR)]
    print('team files:', len(files), flush=True)

    seen = {}
    for f in files:
        try:
            items = json.load(open(os.path.join(WAVE, f)))
        except Exception as e:
            print('ERR', f, e); continue
        if not isinstance(items, list):
            continue
        for it in items:
            if not isinstance(it, dict):
                continue
            code = code_of(it.get('invite'))
            name = (it.get('name') or '').strip()
            if not code or not name:
                continue
            if code not in seen:
                seen[code] = it
    # add the Nov-3 retries file
    try:
        for it in json.load(open(os.path.join(WAVE, 'parent_verified_retries.json'))):
            code = code_of(it.get('invite'))
            if code and code not in seen:
                seen[code] = it
    except Exception as e:
        print('retries file err:', e)
    print('unique codes across team files:', len(seen), flush=True)

    fresh = {c: it for c, it in seen.items() if c not in union}
    print('fresh vs union:', len(fresh), flush=True)

    # load prior state
    done = {}
    if os.path.exists(STATE):
        try:
            done = json.load(open(STATE))
            print('resumed state:', len(done), flush=True)
        except Exception:
            pass
    pending = []
    if os.path.exists(PENDING):
        try:
            pending = json.load(open(PENDING))
        except Exception:
            pass

    codes = [c for c in fresh if c not in done]
    print('to check:', len(codes), flush=True)

    stats = {'live': 0, 'dead': 0, 'transport': 0, 'porn': 0, 'bad': 0}
    lock = threading.Lock()
    since_save = [0]

    def save():
        with lock:
            tmp = STATE + '.tmp'
            json.dump(done, open(tmp, 'w'))
            os.replace(tmp, STATE)
            json.dump(pending, open(PENDING + '.tmp', 'w'))
            os.replace(PENDING + '.tmp', PENDING)

    def work(code):
        it = fresh[code]
        verdict, ogname = check_live(it)
        with lock:
            if verdict == 'live':
                name = ogname if (not it.get('name') or len(ogname) > len(it.get('name',''))) else it['name']
                it = dict(it); it['name'] = name[:120]
                flag = adult_screen(it.get('name',''), it.get('description',''))
                if flag:
                    stats['porn'] += 1
                    done[code] = 'porn:' + flag
                else:
                    stats['live'] += 1
                    done[code] = 'live'
            elif verdict == 'dead':
                stats['dead'] += 1
                done[code] = 'dead'
            else:
                stats['transport'] += 1
                pending.append({'code': code, 'invite': it.get('invite'), 'note': 'transport'})
                done[code] = 'transport'
            since_save[0] += 1
            if since_save[0] >= 200:
                since_save[0] = 0
        if since_save[0] == 0:
            save()

    with ThreadPoolExecutor(max_workers=30) as ex:
        list(ex.map(work, codes))
    save()

    live_items = []
    for c, it in fresh.items():
        if done.get(c) == 'live':
            out = {'name': (it.get('name') or '')[:120],
                   'category': it.get('category') or 'Community & Social',
                   'country': it.get('country') or 'International',
                   'description': it.get('description') or '',
                   'invite': it.get('invite'),
                   'image': it.get('image') or ''}
            live_items.append(out)
    json.dump(live_items, open(OUT, 'w'), ensure_ascii=False)
    print('STATS', stats, flush=True)
    print('LIVE OUTPUT:', len(live_items), '->', OUT, flush=True)
    print('PENDING TRANSPORT:', len(pending), flush=True)

if __name__ == '__main__':
    main()
