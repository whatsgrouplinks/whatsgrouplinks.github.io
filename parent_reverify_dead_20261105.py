#!/usr/bin/env python3
"""Re-verify wave_20261105 'dead' verdicts with a rate-limit-aware checker.
BACKGROUND: the 30-worker no-delay parent run stamped 12,513 'dead', but an
8/8 random sample of those re-fetched via curl AND via fresh requests.Session
returned REAL non-empty og:titles. chat.whatsapp.com serves the same 200 page
with an EMPTY og:title under burst load (soft rate-limit shell); a dead group
returns the identical page shape, so empty-og on a 200 is ambiguous. This
script re-checks every 'dead' code slowly (6 workers, 0.5s delay, session
rotation) with ONE retry on empty (fresh session + 8s pause). Live verdicts
from the first run are kept (non-empty og:title is positive proof).
Usage: python3 parent_reverify_dead_20261105.py"""
import json, re, os, time, html, threading
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.join(BASE, 'agent_batches', 'wave_20261105')
STATE1 = os.path.join(WAVE, 'parent_verify_state.json')
OUT_STATE = os.path.join(WAVE, 'parent_reverify_state.json')
OUT_PENDING = os.path.join(WAVE, 'parent_reverify_pending.json')
OUT_VERIFIED = os.path.join(WAVE, 'parent_verified.json')

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
OG_RE = re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', re.I)
PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal|bokep)\b', re.I)
PORN_URDU_RE = re.compile(r'مزا\s?دینے|مزہ\s?دینے', re.I)
ADULT_EMOJI = set('🥵🍆🍑🔞💦👅👄💋')

WORKERS = 6
EXCLUDE_CODES = {'L0JS1dP9m2M3jjoOxfKK0z'}  # SOCRATES COMMUNITY — community invite, not a group
DELAY = 0.5
RETRY_PAUSE = 8.0
SESSION_ROTATE_EVERY = 40

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
def fresh_session():
    s = requests.Session()
    s.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
    return s

def get_session():
    st = getattr(_tls, 'st', None)
    if st is None:
        st = {'s': fresh_session(), 'n': 0}
        _tls.st = st
    if st['n'] >= SESSION_ROTATE_EVERY:
        try:
            st['s'].close()
        except Exception:
            pass
        st['s'] = fresh_session()
        st['n'] = 0
    st['n'] += 1
    return st['s']

def fetch_once(url, session):
    try:
        r = session.get(url, timeout=45, allow_redirects=True)
    except (requests.Timeout, requests.ConnectionError):
        return 'transport', ''
    except Exception:
        return 'transport', ''
    if r.status_code in (429, 403, 500, 502, 503, 504):
        return 'transport', ''
    if r.status_code != 200:
        return 'transport', ''
    return ('live' if og_title(r.text) else 'empty'), og_title(r.text)

def check_live(item):
    """(verdict, og): live / dead / transport. Empty og retried once."""
    url = item['invite']
    verdict, og = fetch_once(url, get_session())
    time.sleep(DELAY)
    if verdict == 'empty':
        time.sleep(RETRY_PAUSE)
        verdict, og = fetch_once(url, fresh_session())
        time.sleep(DELAY)
        if verdict == 'empty':
            return 'dead', ''
    return verdict, og

def main():
    state1 = json.load(open(STATE1))
    print('first-run state:', len(state1), flush=True)
    # canonical team items (manifest-exact, same as parent verify run 2)
    files = []
    for _l in open(os.path.join(WAVE, 'manifest.txt')):
        _m = re.search(r'(team\d+-[\w\-\.]+\.json): count=(\d+)', _l)
        if _m:
            files.append(_m.group(1))
    files = sorted(set(files))
    seen = {}
    for f in files:
        items = json.load(open(os.path.join(WAVE, f)))
        for it in items:
            if not isinstance(it, dict):
                continue
            code = code_of(it.get('invite'))
            if not code or not (it.get('name') or '').strip():
                continue
            if code in EXCLUDE_CODES:
                continue
            if code not in seen:
                seen[code] = it
    print('unique codes:', len(seen), flush=True)

    keep_live = {c for c, v in state1.items() if v == 'live'}
    keep_porn = {c: v for c, v in state1.items() if v.startswith('porn')}
    to_check = [c for c in seen if c not in keep_live and c not in keep_porn]
    print('keep live:', len(keep_live), '| keep porn:', len(keep_porn),
          '| to re-check:', len(to_check), flush=True)

    done = {}
    if os.path.exists(OUT_STATE):
        try:
            done = json.load(open(OUT_STATE))
            print('resumed reverify state:', len(done), flush=True)
        except Exception:
            pass
    pending = []
    if os.path.exists(OUT_PENDING):
        try:
            pending = json.load(open(OUT_PENDING))
        except Exception:
            pass

    codes = [c for c in to_check if c not in done]
    print('remaining:', len(codes), flush=True)
    stats = {'live': 0, 'dead': 0, 'transport': 0}
    lock = threading.Lock()
    since_save = [0]

    def save():
        with lock:
            tmp = OUT_STATE + '.tmp'
            json.dump(done, open(tmp, 'w'))
            os.replace(tmp, OUT_STATE)
            json.dump(pending, open(OUT_PENDING + '.tmp', 'w'))
            os.replace(OUT_PENDING + '.tmp', OUT_PENDING)

    def work(code):
        it = seen[code]
        verdict, og = check_live(it)
        with lock:
            if verdict == 'live':
                # adult screen on og-enriched name
                name = og if (not it.get('name') or len(og) > len(it.get('name', ''))) else it['name']
                flag = adult_screen(name, it.get('description', ''))
                if flag:
                    done[code] = ['porn:' + flag, og]
                else:
                    stats['live'] += 1
                    done[code] = ['live', og]
            elif verdict == 'dead':
                stats['dead'] += 1
                done[code] = ['dead', '']
            else:
                stats['transport'] += 1
                pending.append({'code': code, 'invite': it.get('invite'), 'note': 'transport'})
                done[code] = ['transport', '']
            since_save[0] += 1
            if since_save[0] >= 200:
                since_save[0] = 0
        if since_save[0] == 0:
            save()

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, codes))
    save()

    # assemble parent_verified.json: live from run 1 + live from re-verify
    live_items = []
    for c, it in seen.items():
        v1 = state1.get(c)
        v2 = done.get(c)
        is_live = (v1 == 'live') or (isinstance(v2, list) and v2[0] == 'live')
        if not is_live:
            continue
        og = v2[1] if (isinstance(v2, list) and len(v2) > 1 and v2[1]) else ''
        name = it.get('name') or ''
        if og and len(og) > len(name):
            name = og
        out = {'name': name[:120],
               'category': it.get('category') or 'Community & Social',
               'country': it.get('country') or 'International',
               'description': it.get('description') or '',
               'invite': it.get('invite'),
               'image': it.get('image') or ''}
        live_items.append(out)
    json.dump(live_items, open(OUT_VERIFIED, 'w'), ensure_ascii=False)
    print('REVERIFY STATS', stats, flush=True)
    print('TOTAL LIVE (run1 + reverify):', len(live_items), '->', OUT_VERIFIED, flush=True)
    print('PENDING TRANSPORT:', len(pending), flush=True)

if __name__ == '__main__':
    main()
