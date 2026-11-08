#!/usr/bin/env python3
"""Team15 verify: chat.whatsapp.com og:title liveness, 4 workers, keep-alive."""
import json, re, html, time, os, random, sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

WAVE05 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
OGT = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
OGT2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)
PORN_RES = [re.compile(p, re.I) for p in [
    r'pornhub', r'\bxxx\b', r'\bnude[sz]?\b', r'sex[\s_-]?video', r'\bescort\b',
    r'call[\s_-]?girl', r'\bfuck\b', r'\bdick\b', r'\bpussy\b', r'\bboobs?\b',
    r'\banal\b', r'\bbokep\b', r'putaria', r'\bnudes\b', r'🔞', r'🍆', r'🍑', r'💦',
    r'👅', r'🥵', r'vazad[oa]s?', r'conte[úu]do adulto', r'onlyfans', r'\bsex\s?chat\b']]
SCAM_RES = [re.compile(p, re.I) for p in [
    r'\bhyip\b', r'crypto[\s_-]?pump', r'money[\s_-]?mule', r'\bcounterfeit\b',
    r'\bsatta\b', r'\bmatka\b', r'venda de (drogas|maconha|coca[íi]na)', r'\bdrogas\b']]
MINOR_RES = [re.compile(p, re.I) for p in [
    r'adolescente.*(sex|nua?|foto|video)', r'(sex|nua?|foto|video).*adolescente',
    r'\bmenor(es)?\b.*(sex|nua?|foto|video)', r'(sex|nua?|foto|video).*\bmenor(es)?\b',
    r'crian[cç]a.*(sex|nua?)', r'novinha.*(sex|nua?|foto|video|pack)', r'\bteen\b.*(sex|nude|porn)']]

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

def og_title(h):
    m = OGT.search(h) or OGT2.search(h)
    return html.unescape(m.group(1)).strip() if m else ''

def is_blocked(name):
    if not name: return 'empty'
    if re.search(r'https?://|www\.|\.com\b', name): return 'name-is-url'
    if re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', name): return 'personal-email'
    if re.search(r'\+\d[\d\s()\-]{8,}\d', name): return 'personal-phone'
    if any(r.search(name) for r in PORN_RES): return 'porn-xxx'
    if any(r.search(name) for r in SCAM_RES): return 'scam-drug'
    if any(r.search(name) for r in MINOR_RES): return 'minor-sexualising'
    return None

def make_desc(title, cat_slug):
    key = CAT_KEYWORDS.get(cat_slug, 'chat and friendship')
    t = re.sub(r'\s+', ' ', title.strip())[:80].replace('"', '')
    return f'"{t}" is a Brazilian WhatsApp group for {key}, open to members across Brazil.'

_sessions = {}
def sess_for(w):
    if w not in _sessions:
        s = requests.Session(); s.headers.update(UA); _sessions[w] = s
    return _sessions[w]

def verify_job(args):
    wid, cand = args
    s = sess_for(wid)
    code = cand['code']
    time.sleep(random.uniform(0.5, 2.0))
    for attempt in range(3):
        try:
            r = s.get(f'https://chat.whatsapp.com/{code}', timeout=60)
            if r.status_code == 429:
                time.sleep(180)
                continue
            title = og_title(r.text)
            return {'code': code, 'og': title, 'status': r.status_code}
        except Exception as e:
            try: s.close()
            except Exception: pass
            _sessions[wid] = requests.Session(); _sessions[wid].headers.update(UA); s = _sessions[wid]
            time.sleep(5)
    return {'code': code, 'og': '', 'status': 0, 'err': 'transport-failure'}

def main():
    cands = json.load(open(os.path.join(WAVE05, 'team15_candidates.json')))
    ckpt_p = os.path.join(WAVE05, 'team15_verify_ckpt.json')
    ckpt = json.load(open(ckpt_p)) if os.path.exists(ckpt_p) else {}
    by_code = {c['code']: c for c in cands}
    todo = [c for c in cands if c['code'] not in ckpt]
    print(f'Candidates: {len(cands)}, already verified: {len(ckpt)}, todo: {len(todo)}', flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(verify_job, (i % 4, c)): c['code'] for i, c in enumerate(todo)}
        for f in as_completed(futs):
            d = f.result()
            ckpt[d['code']] = d
            done += 1
            if done % 200 == 0:
                json.dump(ckpt, open(ckpt_p, 'w'), ensure_ascii=False)
                print(f'  verify {done}/{len(todo)}', flush=True)
    json.dump(ckpt, open(ckpt_p, 'w'), ensure_ascii=False)
    verified, pending, blocked = [], [], []
    for code, c in by_code.items():
        v = ckpt.get(code, {})
        og = (v.get('og') or '').strip()
        if og:
            blk = is_blocked(og)
            if blk:
                blocked.append({'code': code, 'name': og, 'note': f'blocked-verified-title: {blk}'})
                continue
            name = og
            verified.append({'name': name, 'category': CAT_MAP[c['cat']],
                             'country': 'BR',
                             'description': make_desc(name, c['cat']),
                             'invite': f'https://chat.whatsapp.com/{code}',
                             'image': ''})
        else:
            note = 'transport-failure' if v.get('err') else 'empty og:title (dead or unverifiable)'
            pending.append({'code': code, 'name': c['name'], 'note': note})
    json.dump(verified, open(os.path.join(WAVE05, 'team15-linkado.json'), 'w'), ensure_ascii=False)
    json.dump(pending, open(os.path.join(WAVE05, 'team15-unverified-pending.json'), 'w'), ensure_ascii=False)
    stats = {'candidates': len(cands), 'verified': len(verified), 'pending': len(pending),
             'blocked_on_verified_title': len(blocked),
             'pending_transport': sum(1 for p in pending if p['note'] == 'transport-failure')}
    json.dump({'stats': stats, 'blocked_verified': blocked},
              open(os.path.join(WAVE05, 'team15_verify_stats.json'), 'w'), ensure_ascii=False)
    print('VERIFY DONE:', stats, flush=True)

if __name__ == '__main__':
    main()
