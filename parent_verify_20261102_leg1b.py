#!/usr/bin/env python3
"""Parent verification for leg 1 of wave 20261102: banked wave_20261031 pending items.
Method: curl invite URL, require HTTP 2xx + non-empty og:title (invite_link_type_v2 strict:
og:title present and non-empty). Dedupes against union of groups.json codes +
.existing_codes.json. Porn filter: hard-porn keywords only; adult emojis flagged.
Never deletes/banks uncheckable (transport failures) — they are logged for a retry pass.
"""
import json, re, html, subprocess, os, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
_STATE_LOCK = threading.Lock()

SITE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.join(SITE, 'agent_batches', 'wave_20261031')
OUT = os.path.join(SITE, 'agent_batches', 'wave_20261102', 'parent_verified_leg1b.json')
STATE = os.path.join(SITE, 'agent_batches', 'wave_20261102', 'parent_verify_leg1b_state.json')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

PORN_RE = re.compile(r'\b(porn|xxx|hardcore|hentai|bhabhi\s*sex|adult\s*sex|sex\s*video|blue\s*film|18\+\s*(sex|porn)|nude\s*sex|escort)\b|🔞.{0,20}(sex|porn)|girls?\s*sex\s*video', re.I)
ADULT_EMOJI_RE = re.compile(r'[🥵🔞🍑🍆💦]')
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9\-_]{20,24})')

os.makedirs(os.path.dirname(OUT), exist_ok=True)

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

def classify(item):
    url = item.get('invite', '') or ''
    for _ in range(2):
        try:
            code, title = fetch(url)
        except Exception as e:
            return 'transport', str(e)
        if code == '000':
            continue
        if code.startswith('2') and title:
            return 'live', title
        if code.startswith('2'):
            return 'dead', 'empty og:title'
        return 'dead', 'http ' + code
    return 'transport', 'curl 000 x2'

def main():
    items = []
    import glob
    for f in sorted(glob.glob(os.path.join(BATCH, 'team*-unverified-pending.json'))):
        try:
            d = json.load(open(f))
            for it in (d if isinstance(d, list) else list(d.values())):
                if isinstance(it, dict) and it.get('invite'):
                    it['_src'] = os.path.basename(f); items.append(it)
        except Exception as e:
            print('ERR', f, e)
    print('loaded pending:', len(items), flush=True)
    union = load_union(); print('union codes:', len(union), flush=True)
    seen, fresh = set(), []
    for it in items:
        m = CODE_RE.search(it.get('invite', ''))
        c = m.group(1) if m else ''
        if not c or c in union or c in seen: continue
        seen.add(c); it['_code'] = c; fresh.append(it)
    print('fresh to check:', len(fresh), flush=True)
    try:
        state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    except Exception:
        state = {}
    live, dead, transport, dropped = [], [], [], []
    def work(it):
        c = it['_code']
        with _STATE_LOCK:
            if c in state: return c, list(state[c])
        status, detail = classify(it)
        with _STATE_LOCK:
            state[c] = [status, detail]
            return c, list(state[c])
    n = 0
    with ThreadPoolExecutor(max_workers=25) as ex:
        futs = {ex.submit(work, it): it for it in fresh}
        for f in as_completed(futs):
            it = futs[f]; c, (status, detail) = f.result(); n += 1
            name = (it.get('name') or '').strip()
            if status == 'live':
                if PORN_RE.search(name + ' ' + (it.get('description') or '')):
                    dropped.append((c, 'porn')); continue
                if ADULT_EMOJI_RE.search(name):
                    dropped.append((c, 'adult-emoji')); continue
                if not name: dropped.append((c, 'empty-name')); continue
                it['_ogtitle'] = detail
                if 'http' in name.lower() or 'https' in name.lower():
                    it['name'] = detail[:120]
                live.append(it)
            elif status == 'dead': dead.append((c, detail))
            else: transport.append((c, detail))
            if n % 25 == 0:
                with _STATE_LOCK:
                    snap = dict(state)
                json.dump(snap, open(STATE, 'w'))
                print('progress %d/%d' % (n, len(fresh)), flush=True)
    with _STATE_LOCK:
        snap = dict(state)
    json.dump(snap, open(STATE, 'w'))
    for it in live: it.pop('_src', None); it.pop('_code', None); it.pop('_ogtitle', None)
    json.dump(live, open(OUT, 'w'), ensure_ascii=False)
    print('LIVE:', len(live), 'DEAD:', len(dead), 'TRANSPORT:', len(transport), 'DROPPED:', len(dropped), flush=True)
    print('dropped:', dropped[:20], flush=True)
    print('transport:', transport[:20], flush=True)

main()
