#!/usr/bin/env python3
"""Team09 stage 2 (v2): checkpointed, resumable, gentle.
Reads team09_scratch_ids.json -> detail pages -> codes -> og:title verify.
Checkpoints: team09_ckpt_detail.json (gid->record), team09_ckpt_verified.json.
Pending (incl. detail transport failures): team09-unverified-pending.json
Verified: team09-linkado-newcats.json
"""
import requests, re, json, time, os, html, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104')
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
OG_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
OG_RE2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)

CAT_MAP = {'carros':'Other','cidades':'Regional','comprar-e-venda':'Buy-Sell',
           'figurinhas':'Funny','fitness':'Health','lgbt':'Community',
           'moda-e-beleza':'Other','musica':'Music','namoro':'Friendship',
           'series':'Movies','status':'Entertainment','games':'Gaming',
           'tecnologia':'Technology'}

PORN_RES = [re.compile(p, re.I) for p in [
    r'pornhub', r'\bxxx\b', r'\bnude[sz]?\b', r'sex[\s_-]?video', r'escort',
    r'call[\s_-]?girl', r'\bfuck\b', r'\bdick\b', r'\bpussy\b', r'\bboobs?\b',
    r'\banal\b', r'\bbokep\b', r'مزا دینے', r'مزہ دینے', r'🔞', r'🍆', r'🍑', r'💦',
    r'👅', r'👄', r'💋', r'🥵']]
ADULT_RES = [re.compile(p, re.I) for p in [
    r'\b18\s?\+', r'\+18', r'adulto', r'adult', r'putaria', r'sexo\s',
    r'\bhot\b.*(foto|video)', r'nudes']]
MINOR_RES = [re.compile(p, re.I) for p in [
    r'adolescente', r'\bteen\b', r'menor(es)?\b', r'\b1[2-7]\s?[-–]\s?1[2-7]\b',
    r'\b1[3-7]\s?anos', r'crian[cç]a']]

def load(p, default):
    fp = os.path.join(WAVE, p)
    return json.load(open(fp)) if os.path.exists(fp) else default

def save(p, obj):
    json.dump(obj, open(os.path.join(WAVE, p), 'w'), ensure_ascii=False)

def new_session():
    s = requests.Session(); s.headers.update(UA); return s

_sessions = {}
def sess_for(worker):
    if worker not in _sessions: _sessions[worker] = new_session()
    return _sessions[worker]

def og_title(h):
    m = OG_RE.search(h) or OG_RE2.search(h)
    return html.unescape(m.group(1)).strip() if m else ''

def is_porn(t): return any(r.search(t) for r in PORN_RES) or any(r.search(t) for r in ADULT_RES)
def is_minor(t): return any(r.search(t) for r in MINOR_RES)

def make_desc(title, cat, src_desc):
    if src_desc and len(src_desc) >= 40:
        d = re.sub(r'https?://\S+|linkado\.app', '', src_desc, flags=re.I).strip()
        d = re.sub(r'\s+', ' ', d)
        if len(d) >= 40: return d[:280]
    key = {'carros':'car lovers sharing car photos, models and automotive chat',
           'cidades':'people from the same Brazilian city connecting and chatting',
           'comprar-e-venda':'buying and selling with deals, offers and classifieds',
           'figurinhas':'funny sticker sharing and meme exchange',
           'fitness':'fitness, workouts, gym tips and healthy living',
           'lgbt':'LGBTQ+ community friendship and support',
           'moda-e-beleza':'fashion, beauty tips and style trends',
           'musica':'music fans sharing songs, playlists and artists',
           'namoro':'dating, romance and meeting new people',
           'series':'TV series fans discussing episodes and shows',
           'status':'WhatsApp status ideas, quotes and daily messages',
           'games':'gamers chatting about games, news and gameplay',
           'tecnologia':'technology, gadgets and tech news chat'}.get(cat, 'chat and friendship')
    return f'"{title.strip()[:80]}" is a Brazilian WhatsApp group for {key}, open to members across Brazil.'

def detail_job(args):
    wid, gid, cat = args
    s = sess_for('d%d' % wid)
    h = ''
    for i in range(3):
        try:
            r = s.get(f'https://linkado.app/grupo/{gid}', timeout=20)
            if r.status_code == 200: h = r.text; break
            if r.status_code == 429:
                time.sleep(30); continue
        except Exception:
            _sessions.pop('d%d' % wid, None); s = sess_for('d%d' % wid)
        time.sleep(4)
    time.sleep(4)  # gentle pacing
    if not h: return (gid, cat, None, 'transport')
    codes = CODE_RE.findall(h)
    if not codes: return (gid, cat, None, 'nocode')
    m = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S | re.I)
    name = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''
    m2 = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', h, re.I | re.S)
    desc = html.unescape(m2.group(1)).strip() if m2 else ''
    return (gid, cat, {'code': codes[0], 'name': name, 'desc': desc}, 'ok')

def verify_job(args):
    wid, code = args
    s = sess_for('v%d' % wid)
    for i in range(2):
        try:
            r = s.get(f'https://chat.whatsapp.com/{code}', timeout=25)
            if r.status_code == 429:
                time.sleep(20); continue
            return (code, og_title(r.text))
        except Exception:
            _sessions.pop('v%d' % wid, None); s = sess_for('v%d' % wid)
            time.sleep(3)
    return (code, 'transport')

def main():
    ids_data = load('team09_scratch_ids.json', {})
    union = set(load('dedupe_union.json', []))
    ckpt = load('team09_ckpt_detail.json', {})          # gid -> record or {"status":...}
    jobs, seen = [], set()
    for cat, v in ids_data.items():
        for gid in v.get('ids', []):
            if gid in ckpt or (cat, gid) in seen: continue
            seen.add((cat, gid)); jobs.append((0, gid, cat))
    print('detail jobs remaining:', len(jobs), 'checkpointed:', len(ckpt), flush=True)

    porn_drops = minor_drops = trans_fail = nocode = 0
    since_save = 0
    NW = 3
    with ThreadPoolExecutor(max_workers=NW) as ex:
        futs = {ex.submit(detail_job, (i % NW, g, c)): (g, c) for i, (_, g, c) in enumerate(jobs)}
        for f in as_completed(futs):
            g, c = futs[f]
            try: gid, cat, info, status = f.result()
            except Exception as e:
                ckpt[g] = {'status': 'error', 'cat': c}; continue
            if status == 'transport':
                trans_fail += 1; ckpt[gid] = {'status': 'transport', 'cat': cat}
            elif status == 'nocode':
                nocode += 1; ckpt[gid] = {'status': 'nocode', 'cat': cat}
            else:
                blob = info['name'] + ' ' + info['desc']
                if is_porn(blob): porn_drops += 1; ckpt[gid] = {'status': 'porn', 'cat': cat}
                elif is_minor(blob): minor_drops += 1; ckpt[gid] = {'status': 'minor', 'cat': cat}
                elif info['code'] in union: ckpt[gid] = {'status': 'dupe', 'cat': cat}
                else: ckpt[gid] = {'status': 'ok', 'cat': cat, 'code': info['code'],
                                   'name': info['name'], 'desc': info['desc']}
            since_save += 1
            if since_save >= 50:
                save('team09_ckpt_detail.json', ckpt); since_save = 0
    save('team09_ckpt_detail.json', ckpt)
    print('detail done. ok/nocode/transport/porn/minor:',
          sum(1 for v in ckpt.values() if v.get('status')=='ok'), nocode, trans_fail,
          porn_drops, minor_drops, flush=True)

    # ---- verify phase ----
    verified = load('team09_ckpt_verified.json', [])   # list of items
    done_codes = {it['invite'].rsplit('/',1)[-1] for it in verified}
    pend = load('team09_ckpt_pending.json', [])
    pend_codes = {p['code'] for p in pend}
    todo = []
    for gid, rec in ckpt.items():
        if rec.get('status') != 'ok': continue
        code = rec['code']
        if code in done_codes or code in pend_codes: continue
        # dedupe codes within batch: keep first gid
        todo.append((rec['cat'], gid, code, rec))
    # intra-batch code dedupe
    seen_c, vjobs = set(), []
    for cat, gid, code, rec in todo:
        if code in seen_c or code in union: continue
        seen_c.add(code); vjobs.append((cat, gid, code, rec))
    print('verify jobs:', len(vjobs), 'already verified:', len(verified), flush=True)

    NVW = 6
    with ThreadPoolExecutor(max_workers=NVW) as ex:
        futs = {ex.submit(verify_job, (i % NVW, code)): (cat, gid, code, rec)
                for i, (cat, gid, code, rec) in enumerate(vjobs)}
        n = 0
        for f in as_completed(futs):
            cat, gid, code, rec = futs[f]
            title = f.result()[1]
            n += 1
            if title in ('transport', 'rate-limited'):
                pend.append({'code': code, 'gid': gid, 'cat': cat,
                             'note': 'transport failure' if title=='transport' else 'rate-limited'})
            elif not title:
                pass  # dead link, drop silently
            else:
                if is_porn(title + ' ' + rec['name']): porn_drops += 1; continue
                if is_minor(title + ' ' + rec['name']): minor_drops += 1; continue
                name = (rec['name'] or title)[:120]
                verified.append({'name': name, 'category': CAT_MAP.get(cat, 'Other'),
                                 'country': 'BR',
                                 'description': make_desc(name, cat, rec['desc'])[:280],
                                 'invite': f'https://chat.whatsapp.com/{code}', 'image': ''})
            if n % 100 == 0:
                save('team09_ckpt_verified.json', verified); save('team09_ckpt_pending.json', pend)
                print('verify progress', n, 'verified', len(verified), flush=True)
    save('team09_ckpt_verified.json', verified); save('team09_ckpt_pending.json', pend)

    # detail transport failures also banked as pending for next wave
    for gid, rec in ckpt.items():
        if rec.get('status') == 'transport' and not any(p.get('gid')==gid for p in pend):
            pend.append({'code': '', 'gid': gid, 'cat': rec.get('cat',''),
                         'note': 'detail fetch transport failure (linkado.app rate-limited); retry /grupo/'+gid})
    save('team09_ckpt_pending.json', pend)

    save('team09-linkado-newcats.json', verified)
    save('team09-unverified-pending.json',
         [{'name':'(pending)','category':'Other','country':'BR','description':'pending verification',
           'invite':('https://chat.whatsapp.com/'+p['code']) if p['code'] else '',
           'image':'','note':p['note'],'gid':p.get('gid','')} for p in pend])
    print('FINAL verified:', len(verified), 'pending:', len(pend),
          'porn_drops:', porn_drops, 'minor_drops:', minor_drops, flush=True)

if __name__ == '__main__':
    main()
