#!/usr/bin/env python3
"""Team15 (wave 20261105): linkado.app resume harvest.
Slice: (a) team09 13 new categories (team09_scratch_ids.json),
(b) team10 amizade (team10-page-sets.json, 150 pages, 1982 unique gids).
Detail pages -> codes -> dedupe vs wave_20261105 dedupe_union.json -> verify
via chat.whatsapp.com og:title (keep-alive sessions, 4 workers).
Outputs in wave_20261105/: team15-linkado.json (verified),
team15-unverified-pending.json, team15-leads.json.
"""
import json, re, html, time, os, sys, random
from concurrent.futures import ThreadPoolExecutor, as_completed

WAVE04 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104'
WAVE05 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
BASE = 'https://linkado.app'
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
OGT = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
OGT2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)
OGD = re.compile(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
PPS = re.compile(r'https://pps\.whatsapp\.net/[^\s"\'&]+')

CAT_MAP = {'carros': 'Other', 'cidades': 'Regional', 'comprar-e-venda': 'Buy-Sell',
           'figurinhas': 'Funny', 'fitness': 'Health', 'lgbt': 'Community',
           'moda-e-beleza': 'Other', 'musica': 'Music', 'namoro': 'Friendship',
           'series': 'Movies', 'status': 'Entertainment', 'games': 'Gaming',
           'tecnologia': 'Technology', 'amizade': 'Friendship'}

CAT_KEYWORDS = {'carros': 'car lovers sharing car photos, models and automotive chat',
    'cidades': 'people from the same Brazilian city connecting and chatting',
    'comprar-e-venda': 'buying and selling with deals, offers and classifieds',
    'figurinhas': 'funny sticker sharing and meme exchange',
    'fitness': 'fitness, workouts, gym tips and healthy living',
    'lgbt': 'LGBTQ+ community friendship and support',
    'moda-e-beleza': 'fashion, beauty tips and style trends',
    'musica': 'music fans sharing songs, playlists and artists',
    'namoro': 'dating, romance and meeting new people',
    'series': 'TV series fans discussing episodes and shows',
    'status': 'WhatsApp status ideas, quotes and daily messages',
    'games': 'gamers chatting about games, news and gameplay',
    'tecnologia': 'technology, gadgets and tech news chat',
    'amizade': 'friendship, meeting new friends and friendly chat'}

# HARD blocks only: porn/xxx, scam/fraud/HYIP/crypto-pump/money-mule/counterfeit/satta/drugs, minor-sexualising, name-is-URL.
PORN_RES = [re.compile(p, re.I) for p in [
    r'pornhub', r'\bxxx\b', r'\bnude[sz]?\b', r'sex[\s_-]?video', r'\bescort\b',
    r'call[\s_-]?girl', r'\bfuck\b', r'\bdick\b', r'\bpussy\b', r'\bboobs?\b',
    r'\banal\b', r'\bbokep\b', r'putaria', r'\bnudes\b', r'🔞', r'🍆', r'🍑', r'💦',
    r'👅', r'🥵', r'vazad[oa]s?', r'conte[úu]do adulto', r'\bsexo\b.*(video|foto|nua|nu\b)',
    r'pack\s*(de\s*)?(fotos|videos|nudes)', r'onlyfans', r'\bsex\s?chat\b']]
SCAM_RES = [re.compile(p, re.I) for p in [
    r'\bhyip\b', r'crypto[\s_-]?pump', r'money[\s_-]?mule', r'\bcounterfeit\b',
    r'\bsatta\b', r'\bmatka\b', r'ganhe dinheiro f[áa]cil', r'dinheiro gr[áa]tis.*(pix|invest)',
    r'\b(fraude|golpe)\b.*(pix|cart[ãa]o)', r'venda de (drogas|maconha|coca[íi]na)',
    r'\bdrogas\b', r'compra de (seguidores|curtidas)']]
MINOR_RES = [re.compile(p, re.I) for p in [
    r'adolescente.*(sex|nua?|foto|video)', r'(sex|nua?|foto|video).*adolescente',
    r'\bmenor(es)?\b.*(sex|nua?|foto|video)', r'(sex|nua?|foto|video).*\bmenor(es)?\b',
    r'crian[cç]a.*(sex|nua?)', r'\b1[2-7]\s?anos\b.*(sex|nua?|foto)',
    r'novinha.*(sex|nua?|foto|video|pack)', r'\bteen\b.*(sex|nude|porn)']]

def og_title(h):
    m = OGT.search(h) or OGT2.search(h)
    return html.unescape(m.group(1)).strip() if m else ''

def clean_name(raw, cat_slug):
    t = raw or ''
    t = re.sub(r'^Grupo de WhatsApp\s+', '', t, flags=re.I)
    t = re.sub(r'\s*[-–—]\s*(Amizade|Namoro|Carros|Cidades|Games|Música|Musica|Series|Séries|Status|Fitness|LGBT|Tecnologia|Moda e Beleza|Comprar e Venda|Figurinhas)\s*$', '', t, flags=re.I)
    t = re.sub(r'\s+', ' ', t).strip(' -–—')
    return t

def is_blocked(name):
    if not name: return 'empty-name'
    if re.search(r'https?://|www\.|\.com\b|\.app\b', name): return 'name-is-url'
    if any(r.search(name) for r in PORN_RES): return 'porn-xxx'
    if any(r.search(name) for r in SCAM_RES): return 'scam-drug'
    if any(r.search(name) for r in MINOR_RES): return 'minor-sexualising'
    return None

def make_desc(title, cat_slug):
    key = CAT_KEYWORDS.get(cat_slug, 'chat and friendship')
    t = title.strip()[:80].replace('"', '')
    return f'"{t}" is a Brazilian WhatsApp group for {key}, open to members across Brazil.'

def load_jobs():
    jobs = {}  # gid -> cat_slug
    d9 = json.load(open(os.path.join(WAVE04, 'team09_scratch_ids.json')))
    for cat, v in d9.items():
        for gid in v['ids']:
            jobs[gid] = cat
    d10 = json.load(open(os.path.join(WAVE04, 'team10-page-sets.json')))
    for page, ids in d10.items():
        for gid in ids:
            jobs.setdefault(gid, 'amizade')
    return jobs

import requests
_sessions = {}
def sess_for(w):
    if w not in _sessions:
        s = requests.Session(); s.headers.update(UA); _sessions[w] = s
    return _sessions[w]

def detail_job(args):
    wid, gid, cat = args
    s = sess_for(wid)
    for attempt in range(3):
        try:
            r = s.get(f'{BASE}/grupo/{gid}', timeout=60)
            if r.status_code != 200:
                time.sleep(2); continue
            t = r.text
            if 'chat.whatsapp.com/channel' in t and 'chat.whatsapp.com/' not in t.replace('chat.whatsapp.com/channel', ''):
                return {'gid': gid, 'cat': cat, 'err': 'channel-only'}
            m = CODE_RE.search(t)
            if not m:
                return {'gid': gid, 'cat': cat, 'err': 'no-code'}
            code = m.group(1)
            title = og_title(t)
            md = OGD.search(t)
            desc = html.unescape(md.group(1)).strip() if md else ''
            imgs = PPS.findall(t)
            return {'gid': gid, 'cat': cat, 'code': code, 'title': title, 'desc': desc,
                    'image': imgs[0] if imgs else ''}
        except Exception as e:
            try: s.close()
            except Exception: pass
            _sessions[wid] = requests.Session(); _sessions[wid].headers.update(UA); s = _sessions[wid]
            time.sleep(3)
    return {'gid': gid, 'cat': cat, 'err': 'transport-failure'}

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'detail'
    ckpt_p = os.path.join(WAVE05, 'team15_detail_ckpt.json')
    if mode == 'detail':
        jobs = load_jobs()
        print(f'Total unique gids: {len(jobs)}', flush=True)
        ckpt = json.load(open(ckpt_p)) if os.path.exists(ckpt_p) else {}
        todo = [(i, g, c) for i, (g, c) in enumerate(sorted(jobs.items())) if g not in ckpt]
        print(f'Already checkpointed: {len(ckpt)}, todo: {len(todo)}', flush=True)
        done = 0
        with ThreadPoolExecutor(max_workers=16) as ex:
            futs = {ex.submit(detail_job, (i % 16, g, c)): g for i, g, c in todo}
            for f in as_completed(futs):
                d = f.result()
                ckpt[d['gid']] = d
                done += 1
                if done % 100 == 0:
                    json.dump(ckpt, open(ckpt_p, 'w'), ensure_ascii=False)
                    print(f'  detail {done}/{len(todo)} ckpt={len(ckpt)}', flush=True)
        json.dump(ckpt, open(ckpt_p, 'w'), ensure_ascii=False)
        n_code = sum(1 for v in ckpt.values() if v.get('code'))
        n_err = {e: sum(1 for v in ckpt.values() if v.get('err') == e) for e in set(v.get('err') for v in ckpt.values() if v.get('err'))}
        print(f'DETAIL DONE: {len(ckpt)} pages, {n_code} with codes, errors: {n_err}', flush=True)
    elif mode == 'build':
        ckpt = json.load(open(ckpt_p))
        union = set(json.load(open(os.path.join(WAVE05, 'dedupe_union.json'))))
        print(f'Union size: {len(union)}', flush=True)
        seen, cands, stats = set(), [], {'dup-union': 0, 'dup-within': 0, 'blocked': 0, 'no-title': 0}
        blocked_examples = []
        for gid, v in sorted(ckpt.items()):
            if not v.get('code'): continue
            code = v['code']
            if code in union: stats['dup-union'] += 1; continue
            if code in seen: stats['dup-within'] += 1; continue
            seen.add(code)
            name = clean_name(v.get('title') or '', v['cat'])
            blk = is_blocked(name)
            if blk:
                stats['blocked'] += 1
                if len(blocked_examples) < 20: blocked_examples.append({'code': code, 'name': name, 'why': blk})
                continue
            if not name: stats['no-title'] += 1; continue
            cands.append({'code': code, 'name': name, 'cat': v['cat'],
                          'src_desc': v.get('desc') or '', 'image': v.get('image') or '', 'gid': gid})
        print('CANDIDATES:', len(cands), 'stats:', stats, flush=True)
        print('blocked examples:', json.dumps(blocked_examples, ensure_ascii=False)[:1500], flush=True)
        json.dump(cands, open(os.path.join(WAVE05, 'team15_candidates.json'), 'w'), ensure_ascii=False)
        json.dump({'stats': stats, 'blocked_examples': blocked_examples},
                  open(os.path.join(WAVE05, 'team15_build_stats.json'), 'w'), ensure_ascii=False)

if __name__ == '__main__':
    main()
