#!/usr/bin/env python3
"""TEAM 39 Brazil: ongrupos.com category crawl -> verify -> final JSON files."""
import requests, re, html, json, time, random
from concurrent.futures import ThreadPoolExecutor

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'Connection': 'close'}

union = set(json.load(open(WAVE + 'dedupe_union.json')))

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

DESC_TPL = {
 'Friendship': 'A friendly Brazilian WhatsApp group to meet new people, chat daily and make real friendships across Brazil.',
 'Girls': 'A Brazilian WhatsApp group for singles and friendly dating conversation — meet new people and chat in a respectful space.',
 'Entertainment': 'A fun Brazilian WhatsApp group sharing entertaining content, conversations and laughs with members from all over Brazil.',
 'Other': 'A Brazilian WhatsApp community group to chat, share updates and connect with people who share the same interests.',
 'Regional': 'A Brazilian WhatsApp group for people from the same city and region — local chat, news and new friendships.',
 'Education': 'A Brazilian WhatsApp study group to share materials, tips and help each other learn and prepare for exams.',
 'Buy-Sell': 'A Brazilian WhatsApp group for buying and selling — find offers, deals and trade with members across Brazil.',
 'Health': 'A Brazilian WhatsApp group focused on health and wellness — tips, motivation and mutual support from Brazilian members.',
 'Business': 'A Brazilian WhatsApp group for entrepreneurs and business networking — share opportunities and grow together.',
 'Sports': 'A Brazilian WhatsApp group for Brazilian sports fans — talk about matches, teams and results with fellow supporters.',
 'Funny': 'A hilarious Brazilian WhatsApp group full of memes, jokes and funny videos to brighten your day.',
 'Movies': 'A Brazilian WhatsApp group for movie and series lovers — discuss films, share recommendations and chat about cinema.',
 'Gaming': 'A Brazilian WhatsApp group for gamers — squad up, share tips and talk about your favorite games with Brazilian players.',
 'Music': 'A Brazilian WhatsApp group for music lovers — share songs, discover new artists and chat about Brazilian music.',
 'Jobs': 'A Brazilian WhatsApp group sharing job openings and work opportunities across Brazil — find vacancies and career tips.',
 'Food': 'A Brazilian WhatsApp group for food lovers — share recipes, cooking tips and delicious ideas with Brazilian members.',
 'Technology': 'A Brazilian WhatsApp group for tech enthusiasts — discuss gadgets, apps, programming and the latest technology news.',
 'News': 'A Brazilian WhatsApp group sharing Brazilian news and daily updates — stay informed with headlines and discussions.',
}

PORN = ['porn','pornhub','xxx','nude','sex video','escort','call girl','fuck','dick','pussy','boobs','anal',
        'pornô','porno','putaria','novinha','pelada','🔞','🍆','🍑','🥵','💦','👅','👄','💋']

def clean(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    return re.sub(r'\s+', ' ', s).strip()

def get(url, timeout=30):
    return requests.get(url, headers=UA, timeout=timeout)

PAGE_CAP = 12  # bound deep outliers (amizades has 27+ pages)

def crawl():
    items = {}
    try:
        items = json.load(open('/tmp/team39_all.json'))
        print(f'resumed {len(items)} items', flush=True)
    except Exception:
        pass
    done_cats = set()
    try:
        done_cats = set(json.load(open('/tmp/team39_done_cats.json')))
    except Exception:
        pass
    for cat, label in CATMAP.items():
        if cat in done_cats:
            print(f'{cat}: skipped (done)', flush=True); continue
        page = 1
        while True:
            url = f'https://ongrupos.com/categoria/{cat}' + (f'?page={page}' if page > 1 else '')
            try:
                t = get(url).text
            except Exception as e:
                print('CATFAIL', cat, page, repr(e)[:80], flush=True); break
            cards = re.findall(r'href="https://ongrupos\.com/grupo/([A-Za-z0-9]{20,24})">(.*?)</a>', t, re.S)
            fresh = 0
            for code, inner in cards:
                if code in items: continue
                nm = re.search(r'class="titleGrupo"[^>]*>(.*?)</h3>', inner, re.S)
                ds = re.search(r'class="descGrupo"[^>]*>(.*?)</p>', inner, re.S)
                name = clean(nm.group(1))[:120] if nm else ''
                desc = clean(ds.group(1))[:300] if ds else ''
                items[code] = {'name': name, 'desc_pt': desc, 'cat': label}
                fresh += 1
            print(f'{cat} p{page}: {len(cards)} cards, +{fresh} (total {len(items)})', flush=True)
            if not re.search(r"\?page=%d['\"]" % (page + 1), t): break
            page += 1
            if page > PAGE_CAP: print(f'{cat}: capped at {PAGE_CAP}', flush=True); break
            time.sleep(0.3)
        done_cats.add(cat)
        json.dump(items, open('/tmp/team39_all.json', 'w'), ensure_ascii=False)
        json.dump(sorted(done_cats), open('/tmp/team39_done_cats.json', 'w'))
    return items

def is_porn(text):
    tl = text.lower()
    return any(p in tl for p in [x.lower() for x in PORN]) or re.search(r'\b18\s*\+|\+?\s*18\s*anos', tl) and 'figurinh' in tl

RATE_LIMITED = False

def verify(code):
    global RATE_LIMITED
    if RATE_LIMITED:
        return ('rl', '')
    for attempt in (1, 2):
        try:
            r = get('https://chat.whatsapp.com/' + code, timeout=25)
            if r.status_code == 429:
                RATE_LIMITED = True
                return ('rl', '')
            m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            title = html.unescape(m.group(1)).strip() if m else ''
            return ('ok', title)
        except Exception as e:
            if attempt == 2: return ('fail', repr(e)[:60])
    return ('fail', 'x')

def main():
    print('crawling...', flush=True)
    items = crawl()
    new = {c: v for c, v in items.items() if c not in union}
    print(f'TOTAL {len(items)} new-vs-union {len(new)}', flush=True)
    json.dump({c: v for c, v in items.items()}, open('/tmp/team39_all.json', 'w'), ensure_ascii=False)

    # content filter before verification
    cand, porn, perinfo = [], 0, 0
    for code, d in new.items():
        blob = (d['name'] + ' ' + d['desc_pt'])
        if is_porn(blob):
            porn += 1; continue
        if re.search(r'\d{2,3}\s?\d{4,5}[-. ]?\d{4}', blob) or '@' in blob:
            perinfo += 1; continue
        cand.append((code, d))
    print(f'candidates {len(cand)} porn-dropped {porn} personalinfo-dropped {perinfo}', flush=True)

    def vf(cd):
        code, d = cd
        st, title = verify(code)
        time.sleep(0.5)
        return (code, d, st, title)

    verified, pending = [], []
    rl_hit = False
    with ThreadPoolExecutor(max_workers=8) as ex:
        n = 0
        for code, d, st, title in ex.map(vf, cand):
            n += 1
            if st == 'rl':
                rl_hit = True
            if n % 50 == 0: print(f'verified {n}/{len(cand)}', flush=True)
            if st == 'ok' and title:
                if title.lower() in ('só falta colocar um nome',):
                    continue
                name = d['name'] or title
                verified.append({
                    'name': name, 'category': d['cat'], 'country': 'BR',
                    'description': DESC_TPL.get(d['cat'], DESC_TPL['Other']),
                    'invite': 'https://chat.whatsapp.com/' + code, 'image': ''})
            elif st == 'fail':
                pending.append({'name': d['name'], 'category': d['cat'], 'country': 'BR',
                    'description': DESC_TPL.get(d['cat'], DESC_TPL['Other']),
                    'invite': 'https://chat.whatsapp.com/' + code, 'image': '',
                    'note': 'transport failure'})
            elif st == 'rl':
                pending.append({'name': d['name'], 'category': d['cat'], 'country': 'BR',
                    'description': DESC_TPL.get(d['cat'], DESC_TPL['Other']),
                    'invite': 'https://chat.whatsapp.com/' + code, 'image': '',
                    'note': 'rate-limited'})
    if rl_hit: print('RATE LIMITED - remaining banked as pending', flush=True)
    json.dump(verified, open(WAVE + 'team39b-brazil.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(WAVE + 'team39b-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
    print(f'DONE verified={len(verified)} pending={len(pending)} porn={porn} perinfo={perinfo}', flush=True)

main()
