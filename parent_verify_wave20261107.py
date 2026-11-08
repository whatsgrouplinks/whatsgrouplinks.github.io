#!/usr/bin/env python3
"""Parent verification for wave 20261107 (run 2026-11-07).
Verifies the coordinator's clean file (1,159 team-verified) + the 182 pending
codes + the 83 team09 groupizo candidates (slow re-verify leg: team09's rapid
sequential check returned all-empty og:title, likely a WhatsApp rate-limit
artefact) against the CURRENT union (groups.json 68,294 + .existing_codes.json).
Uses the settled slow checker: keep-alive requests.Session, 3 workers (per
wave-20261107 method note: above 3-4 parallel workers transport-error bursts
spike), 0.7s delay, ONE retry on empty og:title (fresh session + 8s pause).
Adult screen: PORN_RE + PORN_URDU_RE + ADULT_EMOJI (task set only:
🥵🍆🍑🔞💦👅👄💋 — NOT 🥰) on og-enriched name + description, PLUS extended
terms on og:title and name/desc. Generic og:title ("WhatsApp Group" etc.)
counts as dead. Team09 categories canonical-mapped; empty descriptions filled.
Incremental state every 100 items. Outputs parent_verified_wave20261107.json.
Usage: python3 parent_verify_wave20261107.py
"""
import json, re, os, time, html, threading
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.join(BASE, 'agent_batches', 'wave_20261107')
CLEAN = os.path.join(WAVE, 'wave_20261107_verified_clean.json')
PENDING = os.path.join(WAVE, 'wave_20261107_pending_all.json')
TEAM09 = os.path.join(WAVE, 'team09-groupizo-unverified-candidates.json')
OUT_STATE = os.path.join(WAVE, 'parent_verify_state.json')
OUT_VERIFIED = os.path.join(WAVE, 'parent_verified_wave20261107.json')
OUT_PENDING = os.path.join(WAVE, 'parent_verify_pending_transport.json')

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
OG_RE = re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', re.I)
PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal|bokep)\b', re.I)
PORN_URDU_RE = re.compile(r'مزا\s?دینے|مزہ\s?دینے', re.I)
ADULT_EMOJI = set('🥵🍆🍑🔞💦👅👄💋')
EXT_RE = re.compile(r'\b(hookup|hook-up|sexy|sexx?y?\s?(video|girl|bhabhi|aunty)|adults?\s?only|18\s?\+|adult\s?(group|chat|video|dating))\b', re.I)
GENERIC_OG = {'whatsapp group', 'whatsapp group invite', 'join this group on whatsapp', 'whatsapp'}
WORKERS = 3
DELAY = 0.7
RETRY_PAUSE = 8.0
SESSION_ROTATE_EVERY = 40

CATMAP = {
    '': 'Community & Social', 'Buy Sell': 'Buy & Sell', 'buy-sell': 'Buy & Sell',
    'buysell': 'Buy & Sell', 'Religious': 'Islamic', 'religious': 'Islamic',
    'Movies': 'Entertainment', 'movies': 'Entertainment', 'Shopping': 'Buy & Sell',
    'Digital Marketing': 'Business', 'education': 'Education', 'jobs': 'Jobs',
    'entertainment': 'Entertainment', 'islamic': 'Islamic', 'news': 'News',
    'sports': 'Sports', 'technology': 'Technology', 'health': 'Health',
    'business': 'Business', 'gaming': 'Gaming', 'friendship': 'Friendship',
    'online earning': 'Online Earning', 'finance': 'Finance', 'funny': 'Funny',
    'games': 'Gaming', 'crypto': 'Crypto', 'poetry': 'Poetry', 'travel': 'Travel',
}

def code_of(invite):
    m = CODE_RE.search(invite or '')
    return m.group(1) if m else None

def og_title(text):
    m = OG_RE.search(text or '')
    return html.unescape(m.group(1)).strip() if m else ''

def adult_screen(name, desc, og=''):
    t = f"{name} {desc} {og}"
    if PORN_RE.search(t) or PORN_URDU_RE.search(t):
        return 'porn-regex'
    if any(e in t for e in ADULT_EMOJI):
        return 'adult-emoji'
    if EXT_RE.search(t):
        return 'porn-extended'
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
        try: st['s'].close()
        except Exception: pass
        st['s'] = fresh_session()
        st['n'] = 0
    st['n'] += 1
    return st['s']

def fetch_once(url, session):
    try:
        r = session.get(url, timeout=45, allow_redirects=True)
    except Exception:
        return 'transport', ''
    if r.status_code != 200:
        return 'transport', ''
    t = og_title(r.text)
    if not t or t.strip().lower() in GENERIC_OG:
        return 'empty', t
    return 'live', t

def check_live(item):
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
    groups = json.load(open(os.path.join(BASE, 'groups.json')))
    union = set()
    for g in groups:
        c = code_of(g.get('invite', ''))
        if c: union.add(c)
    try:
        union |= set(json.load(open(os.path.join(BASE, '.existing_codes.json'))))
    except Exception as e:
        print('existing_codes load failed:', e, flush=True)
    print('union codes:', len(union), 'groups.json groups:', len(groups), flush=True)

    clean = json.load(open(CLEAN))
    pending = []
    try:
        pending = json.load(open(PENDING))
    except Exception as e:
        print('pending load failed:', e, flush=True)
    t9raw = []
    try:
        t9raw = json.load(open(TEAM09))
    except Exception as e:
        print('team09 load failed:', e, flush=True)
    t9 = []
    for it in t9raw:
        code = it.get('code') or ''
        if not code:
            m = CODE_RE.search(it.get('invite') or '')
            code = m.group(1) if m else ''
        if not code or len(code) != 22:
            continue
        inv = f"https://chat.whatsapp.com/{code}"
        cat = CATMAP.get((it.get('category') or '').strip(), (it.get('category') or '').strip() or 'Community & Social')
        t9.append({'name': it.get('name') or '', 'category': cat,
                   'country': it.get('country') or 'International',
                   'description': it.get('description') or '',
                   'invite': inv, 'image': it.get('image') or ''})
    print('team09 normalized:', len(t9), flush=True)
    seen = {}
    for it in clean:
        c = code_of(it.get('invite'))
        if c and c not in seen:
            seen[c] = it
    for it in pending:
        c = code_of(it.get('invite'))
        if c and c not in seen:
            seen[c] = it
    for it in t9:
        c = code_of(it.get('invite'))
        if c and c not in seen:
            seen[c] = it
    print('candidates:', len(seen), '(clean', len(clean), '+ pending', len(pending), '+ team09', len(t9), ')', flush=True)
    fresh = {c: it for c, it in seen.items() if c not in union}
    print('fresh vs union:', len(fresh), '| dup vs union:', len(seen) - len(fresh), flush=True)

    done = {}
    if os.path.exists(OUT_STATE):
        try:
            done = json.load(open(OUT_STATE))
            print('resumed state:', len(done), flush=True)
        except Exception:
            pass
    pend_out = []
    if os.path.exists(OUT_PENDING):
        try: pend_out = json.load(open(OUT_PENDING))
        except Exception: pass
    codes = [c for c in fresh if c not in done]
    print('to check:', len(codes), flush=True)
    stats = {'live': 0, 'dead': 0, 'transport': 0, 'porn': 0}
    lock = threading.Lock()
    since_save = [0]
    def save():
        with lock:
            tmp = OUT_STATE + '.tmp'
            json.dump(done, open(tmp, 'w'))
            os.replace(tmp, OUT_STATE)
            json.dump(pend_out, open(OUT_PENDING + '.tmp', 'w'))
            os.replace(OUT_PENDING + '.tmp', OUT_PENDING)
    def work(code):
        it = fresh[code]
        verdict, og = check_live(it)
        with lock:
            if verdict == 'live':
                name = og if (not it.get('name') or len(og) > len(it.get('name', ''))) else it['name']
                flag = adult_screen(name, it.get('description', ''), og)
                if flag:
                    stats['porn'] += 1
                    done[code] = ['porn:' + flag, og]
                else:
                    stats['live'] += 1
                    done[code] = ['live', og]
            elif verdict == 'dead':
                stats['dead'] += 1
                done[code] = ['dead', '']
            else:
                stats['transport'] += 1
                pend_out.append({'code': code, 'invite': it.get('invite'), 'note': 'transport'})
                done[code] = ['transport', '']
            since_save[0] += 1
            if since_save[0] >= 100:
                since_save[0] = 0
        if since_save[0] == 0:
            save()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, codes))
    save()
    live_items = []
    for c, it in fresh.items():
        v = done.get(c)
        if not (isinstance(v, list) and v[0] == 'live'):
            continue
        og = v[1] if len(v) > 1 else ''
        name = it.get('name') or ''
        if og and len(og) > len(name):
            name = og
        if not name or name.strip().lower() in GENERIC_OG:
            continue
        cat = CATMAP.get((it.get('category') or '').strip(), (it.get('category') or '').strip() or 'Community & Social')
        desc = it.get('description') or ''
        if not desc.strip():
            desc = f"Join the {name} WhatsApp group for {cat.lower()} discussions and updates."
        live_items.append({'name': name[:120],
                           'category': cat,
                           'country': it.get('country') or 'International',
                           'description': desc,
                           'invite': it.get('invite'),
                           'image': it.get('image') or ''})
    json.dump(live_items, open(OUT_VERIFIED, 'w'), ensure_ascii=False)
    print('PARENT VERIFY STATS', stats, flush=True)
    print('TOTAL LIVE:', len(live_items), '->', OUT_VERIFIED, flush=True)
    print('PENDING TRANSPORT:', len(pend_out), flush=True)

if __name__ == '__main__':
    main()
