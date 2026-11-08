#!/usr/bin/env python3
"""TEAM 08: ongrupos.com Brazil — full 41-category re-crawl + new-post check.
Nov-3 (team39/team39R) covered 24/40 categories; remaining 16 + recheck across all.
Dedupe: wave_20261104 union + team39R/team39b outputs (verified+pending) so no double-coverage.
"""
import requests, re, html, json, time
from concurrent.futures import ThreadPoolExecutor

BASE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/'
W04 = BASE + 'wave_20261104/'
W03 = BASE + 'wave_20261103/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

CATMAP = {
 'amizades':'Friendship','amor-e-romance':'Girls','animes-e-desenhos':'Entertainment','bbb':'Entertainment',
 'carros-e-motos':'Other','cidades':'Regional','ciencias':'Education','compras-e-vendas':'Buy-Sell',
 'cultivo':'Other','educativo':'Education','emagrecimento':'Health','empreendedorismo':'Business',
 'esportes':'Sports','estudos':'Education','fas':'Entertainment','figurinhas-e-stickers':'Funny',
 'filmes-e-series':'Movies','fisica':'Education','frases-e-mensagens':'Funny','free-fire':'Gaming',
 'futebol':'Sports','ganhar-seguidores':'Business','gays':'Friendship','geeks':'Technology',
 'jogos':'Gaming','lgbt':'Friendship','links':'Other','memes':'Funny','moda-e-beleza':'Other',
 'musicas':'Music','namoro':'Girls','negocios':'Business','novelas':'Entertainment','profissoes':'Jobs',
 'receitas':'Food','redes-sociais':'Business','religiao':'Other','status':'Funny','tecnologia':'Technology',
 'vagas-de-emprego':'Jobs','videos':'Entertainment',
}

PORN = ['porn','pornhub','xxx','nude','sex video','escort','call girl','fuck','dick','pussy','boobs','anal',
        'pornô','porno','putaria','novinha','pelada','🔞','🍆','🍑','🥵','💦','👅','👄','💋']

def clean(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    return re.sub(r'\s+', ' ', s).strip()

def is_porn(text):
    tl = text.lower()
    return any(p in tl for p in [x.lower() for x in PORN]) or ('18' in tl and any(w in tl for w in ['figurinh','stick','sticker']))

sess = requests.Session()
sess.headers.update(UA)

def get(url, timeout=50):
    return sess.get(url, timeout=timeout)

def crawl():
    items = {}          # code -> {name, desc_pt, cat(label), slug}
    for slug, label in CATMAP.items():
        page = 1
        while True:
            url = f'https://ongrupos.com/categoria/{slug}' + (f'?page={page}' if page > 1 else '')
            try:
                t = get(url).text
            except Exception as e:
                print('CATFAIL', slug, page, repr(e)[:90], flush=True); break
            cards = re.findall(r'href="https://ongrupos\.com/grupo/([A-Za-z0-9]{20,24})">(.*?)</a>', t, re.S)
            fresh = 0
            for code, inner in cards:
                if code in items: continue
                nm = re.search(r'class="titleGrupo"[^>]*>(.*?)</h3>', inner, re.S)
                ds = re.search(r'class="descGrupo"[^>]*>(.*?)</p>', inner, re.S)
                name = clean(nm.group(1))[:120] if nm else ''
                desc = clean(ds.group(1))[:300] if ds else ''
                items[code] = {'name': name, 'desc_pt': desc, 'label': label, 'slug': slug}
                fresh += 1
            print(f'{slug} p{page}: {len(cards)} cards, +{fresh} (total {len(items)})', flush=True)
            if not re.search(r"\?page=%d['\"]" % (page + 1), t): break
            page += 1
            time.sleep(0.25)
    return items

RATE_LIMITED = False

def verify(code):
    global RATE_LIMITED
    if RATE_LIMITED: return ('rl', '')
    for attempt in (1, 2):
        try:
            r = get('https://chat.whatsapp.com/' + code, timeout=55)
            if r.status_code == 429:
                RATE_LIMITED = True
                return ('rl', '')
            m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            title = html.unescape(m.group(1)).strip() if m else ''
            return ('ok', title)
        except Exception as e:
            if attempt == 2: return ('fail', repr(e)[:60])
            time.sleep(2)
    return ('fail', 'x')

def main():
    union = set(json.load(open(W04 + 'dedupe_union.json')))
    print('union', len(union), flush=True)
    prev = {}
    for f in ['team39R-brazil.json', 'team39R-unverified-pending.json', 'team39b-unverified-pending.json']:
        try:
            d = json.load(open(W03 + f))
            for x in d:
                m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', x['invite'])
                if m: prev[m.group(1)] = f
        except Exception as e:
            print('prev load fail', f, e, flush=True)
    print('prev nov3 codes', len(prev), flush=True)

    print('crawling...', flush=True)
    items = crawl()
    json.dump(items, open(W04 + 'team08_crawl_raw.json', 'w'), ensure_ascii=False)
    print(f'TOTAL {len(items)}', flush=True)

    cand, porn, perinfo, dup_union, dup_prev = [], 0, 0, 0, 0
    for code, d in items.items():
        if code in union: dup_union += 1; continue
        if code in prev: dup_prev += 1; continue
        blob = (d['name'] + ' ' + d['desc_pt'])
        if is_porn(blob): porn += 1; continue
        if re.search(r'\d{2,3}\s?\d{4,5}[-. ]?\d{4}', blob) or '@' in blob: perinfo += 1; continue
        cand.append((code, d))
    print(f'candidates {len(cand)} dup_union {dup_union} dup_prev {dup_prev} porn {porn} perinfo {perinfo}', flush=True)
    json.dump([{'code': c, 'd': d} for c, d in cand], open(W04 + 'team08_candidates.json', 'w'), ensure_ascii=False)

    def vf(cd):
        code, d = cd
        st, title = verify(code)
        return (code, d, st, title)

    verified, pending = [], []
    rl_hit = False
    with ThreadPoolExecutor(max_workers=10) as ex:
        n = 0
        for code, d, st, title in ex.map(vf, cand):
            n += 1
            if st == 'rl': rl_hit = True
            if n % 50 == 0: print(f'verified {n}/{len(cand)}', flush=True)
            if st == 'ok' and title:
                if title.lower().strip() in ('só falta colocar um nome',): continue
                name = d['name'] or title
                verified.append({'code': code, 'd': d, 'og': title, 'name': name})
            elif st in ('fail', 'rl'):
                pending.append({'name': d['name'], 'category': d['label'], 'country': 'BR',
                    'invite': 'https://chat.whatsapp.com/' + code, 'image': '',
                    'note': 'rate-limited' if st == 'rl' else 'transport failure',
                    'pt_desc': d['desc_pt']})
    if rl_hit: print('RATE LIMITED — remaining banked as pending', flush=True)
    json.dump(verified, open(W04 + 'team08_verified_raw.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(W04 + 'team08-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
    print(f'DONE verified={len(verified)} pending={len(pending)}', flush=True)

if __name__ == '__main__':
    main()
