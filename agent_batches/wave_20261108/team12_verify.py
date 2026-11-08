#!/usr/bin/env python3
"""Team 12 stage 2: verify candidate invite codes live against chat.whatsapp.com,
apply content filters, build verified/pending records, write the 3 output files + leads.
Rate limit: max 3 parallel, >=0.6s between check starts (global lock)."""
import json, re, os, html, time, threading, subprocess
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}
union = set(json.load(open(os.path.join(WAVE, 'dedupe_union.json'))))
data = json.load(open(os.path.join(WAVE, 'team12-candidates.json')))
cands = data['candidates']

GENERIC = {'whatsapp group', 'join this group on whatsapp', 'whatsapp', ''}
ADULT_EMOJI = set('🥵🍆🍑🔞💦👅👄💋')
SCAM_RE = re.compile(r'bitfinex|paypal.?loader|counterfeit|fake (money|currency|note)|escort|call.?girl|callgirl|money.?mule|buy cvv|cloned card', re.I)
PORN_RE = re.compile(r'\b(xxx|porno|porn|sexo|hentai|onlyfans)\b', re.I)

CATMAP = {
 'amistad': 'Friendship', 'amor': 'Friendship', 'solteros': 'Friendship',
 'amore': 'Friendship', 'amizades': 'Friendship', 'amor-e-romance': 'Friendship',
 'namoro': 'Friendship',
 'bailar': 'Entertainment', 'peliculas': 'Entertainment', 'películas': 'Entertainment',
 'musica': 'Entertainment', 'música': 'Entertainment', 'anime': 'Entertainment',
 'k-pop': 'Entertainment', 'rock': 'Entertainment', 'youtube': 'Entertainment',
 'animes-e-desenhos': 'Entertainment', 'filmes-e-series': 'Entertainment',
 'musicas': 'Entertainment', 'videos': 'Entertainment', 'novelas': 'Entertainment',
 'bbb': 'Entertainment', 'fas': 'Entertainment', 'geeks': 'Entertainment',
 'instagram': 'Community & Social', 'gays': 'Community & Social',
 'lgbt': 'Community & Social', 'cidades': 'Community & Social',
 'cultivo': 'Community & Social', 'moda-e-beleza': 'Community & Social',
 'redes-sociais': 'Community & Social', 'links': 'Community & Social',
 'carros-e-motos': 'Community & Social',
 'humor': 'Funny', 'stickers': 'Funny', 'memes': 'Funny',
 'figurinhas-e-stickers': 'Funny', 'status': 'Funny',
 'free-fire': 'Gaming', 'free fire': 'Gaming', 'gamers': 'Gaming',
 'rol': 'Gaming', 'roleplay': 'Gaming', 'jogos': 'Gaming',
 'futbol': 'Sports', 'fútbol': 'Sports', 'esportes': 'Sports', 'futebol': 'Sports',
 'senderismo': 'Travel',
 'politica': 'News', 'política': 'News', 'noticias': 'News',
 'negocios': 'Business', 'empreendedorismo': 'Business',
 'religion': 'Islamic', 'religión': 'Islamic', 'religiao': 'Islamic',
 'educacion': 'Education', 'educación': 'Education', 'educativo': 'Education',
 'estudos': 'Education', 'ciencias': 'Education', 'fisica': 'Education',
 'empleo': 'Jobs', 'trabajo': 'Jobs', 'vagas-de-emprego': 'Jobs', 'profissoes': 'Jobs',
 'salud': 'Health', 'emagrecimento': 'Health',
 'tecnologia': 'Technology', 'technology': 'Technology',
 'cocina': 'Cooking', 'receitas': 'Cooking',
 'poesia': 'Poetry', 'poesía': 'Poetry', 'frases-e-mensagens': 'Poetry',
 'criptomonedas': 'Crypto', 'cripto': 'Crypto',
 'ventas': 'Buy & Sell', 'compra venta': 'Buy & Sell', 'compra-venta': 'Buy & Sell',
 'compras-e-vendas': 'Buy & Sell',
 'deportes': 'Sports', 'juegos': 'Gaming',
 'ganhar-seguidores': 'Online Earning',
}
def canon_cat(raw):
    if not raw:
        return None
    r = raw.strip().lower()
    if r in CATMAP:
        return CATMAP[r]
    for k, v in CATMAP.items():
        if k in r:
            return v
    return None

def norm_flag(flag):
    if not flag:
        return None
    f = flag.strip().lower()
    if f in ('world', 'world24', 'mundo', 'wd'):
        return 'International'
    f = f[:-2] if f.endswith('24') else f
    if len(f) == 2 and f.isalpha():
        return f.upper()
    return None

def clean_text(s):
    s = html.unescape(s or '')
    s = s.replace('-' * 3, ' ').replace('-------', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def has_adult_emoji(s):
    return any(e in (s or '') for e in ADULT_EMOJI)

# De-obfuscate fancy-unicode titles for filter checks only (display name untouched):
# NFKD folds mathematical bold/italic to ASCII; homoglyph map folds Greek/Cyrillic lookalikes.
import unicodedata
_HOMO = str.maketrans({'α': 'a', 'ε': 'e', 'ι': 'i', 'ο': 'o', 'ρ': 'p', 'τ': 't',
                       'υ': 'u', 'χ': 'x', 'η': 'n', 'ɳ': 'n', 'ƚ': 't', 'я': 'r',
                       '∂': 'd', 'к': 'k', 'с': 'c', 'а': 'a', 'е': 'e', 'о': 'o',
                       'р': 'p', 'х': 'x', 'у': 'y', 'ñ': 'n', '0': 'o', '1': 'i'})
def deobfuscate(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s.translate(_HOMO).lower()

# ---------- live verification ----------
_lock = threading.Lock()
_last = [0.0]
def check_live(code):
    """Returns (status, og_title): status in live/dead/transport/ambiguous-after-retry."""
    def once():
        global _last
        with _lock:
            wait = 0.6 - (time.time() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
        try:
            with requests.Session() as s:
                r = s.get('https://chat.whatsapp.com/' + code, headers=UA, timeout=25)
            m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
            title = html.unescape(m.group(1)).strip() if m else ''
            return ('http', r.status_code, title)
        except Exception as e:
            return ('err', None, str(e)[:120])
    st, code_, title = once()
    if st == 'err':
        st2, code2, title2 = once()
        if st2 == 'err':
            return 'transport', ''
        st, code_, title = st2, code2, title2
    if code_ != 200:
        return 'dead', title
    if not title or title.strip().lower() in GENERIC:
        time.sleep(3)
        st2, code2, title2 = once()
        if st2 == 'err':
            return 'transport', ''
        if code2 == 200 and title2 and title2.strip().lower() not in GENERIC:
            return 'live', title2
        return 'dead', title2
    return 'live', title

# candidates to verify: fresh codes only (not in union), deduped by code
todo = {}
for c in cands:
    if c['in_union']:
        continue
    todo.setdefault(c['code'], c)
print(f'verifying {len(todo)} fresh codes (igrupos + ongrupos)...', flush=True)
# pilot codes already verified live earlier this run — trust those results, skip re-check
PILOT_LIVE = {'LCjcnVaBMRc6OrEqrExKsd': '⚚ 𝕎𝕒𝕫𝕒𝕔𝕙𝕒𝕥 𝔻𝕚𝕧𝕖𝕣𝕤𝕚ó𝕟 𝔾𝕒𝕣𝕒𝕟𝕥𝕚𝕫𝕒𝕕𝕒 ⚚',
              'B5j4NSW4LAUGWaV5zMQJ7M': 'Legião Efoteboll 🏴‍☠️🎮'}
results = {}
for code, t in PILOT_LIVE.items():
    if code in todo:
        results[code] = ('live', t)
        print(f'pilot {code}: live (already checked)', flush=True)
rest = [c for c in todo if c not in results]
# resume from checkpoint if present
CKPT = os.path.join(WAVE, 'team12-verify-checkpoint.json')
if os.path.exists(CKPT):
    ck = json.load(open(CKPT))
    for code, v in ck.items():
        if code in todo and code not in results:
            results[code] = (v[0], v[1])
    rest = [c for c in rest if c not in results]
    print(f'resumed from checkpoint: {len(results)} already verified, {len(rest)} left', flush=True)
t0 = time.time()
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(check_live, code): code for code in rest}
    done_n = 0
    for f in futs:
        code = futs[f]
        try:
            results[code] = f.result()
        except Exception as e:
            results[code] = ('transport', '')
        done_n += 1
        if done_n % 25 == 0:
            print(f'  verified {done_n}/{len(rest)} in {time.time()-t0:.0f}s', flush=True)
            json.dump({k: list(v) for k, v in results.items()}, open(CKPT, 'w'), ensure_ascii=False)
    json.dump({k: list(v) for k, v in results.items()}, open(CKPT, 'w'), ensure_ascii=False)
print(f'verification done: {len(results)} codes in {time.time()-t0:.0f}s', flush=True)
from collections import Counter
print(Counter(v[0] for v in results.values()), flush=True)

# ---------- ongrupos detail enrichment for live codes ----------
def fetch_on_detail(slug):
    try:
        r = subprocess.run(['curl', '-sS', '-m', '40', '-L', '-A', UA['User-Agent'],
                            f'https://ongrupos.com/grupo/{slug}'],
                           capture_output=True, timeout=50)
        h = r.stdout.decode('utf-8', errors='replace')
    except Exception:
        return {}
    t = re.sub(r'<script.*?</script>', '', h, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(re.sub(r'\s+', ' ', t))
    m = re.search(r'Grupo de WhatsApp (.+?) Tags', t)
    name = m.group(1).strip() if m else ''
    tags = re.search(r'Tags \d+ (.+?) ' + re.escape(name[:20]) if name else r'Tags \d+ (.+?) Grupo destinado', t)
    tagstr = tags.group(1).strip() if tags else ''
    dm = re.search(re.escape(name[:25]) + r' (.+?) Esse grupo', t) if name else None
    desc = dm.group(1).strip() if dm else ''
    return {'name': name, 'tags': tagstr, 'desc': desc, 'text': t[:800]}

# ---------- build records ----------
def build_pending(cand, code):
    name = clean_text(cand.get('title') or '') or 'WhatsApp Group'
    cat = canon_cat(cand.get('category_raw') or '') or 'Community & Social'
    return {'name': name, 'category': cat, 'country': 'International',
            'description': f"Join {name}, a WhatsApp group listed under {cat}.",
            'invite': f'https://chat.whatsapp.com/{code}', 'image': '', 'reason': 'transport'}

def build_verified(cand, code, og):
    src = cand['source']
    if src == 'igrupos':
        name = clean_text(cand.get('title') or '')
        cat = canon_cat(cand.get('category_raw') or '')
        if not cat:
            # fall back to tag source label
            for s in cand.get('sources', []):
                if s.startswith('tag-'):
                    cat = canon_cat(s[4:])
                    break
        cat = cat or 'Community & Social'
        desc = clean_text(cand.get('detail_desc') or cand.get('desc') or '')
        country = cand.get('country_hint') or norm_flag(cand.get('flag') or '') or 'International'
        if not name:
            name = clean_text(og)
    else:
        det = fetch_on_detail(code)
        name = clean_text(det.get('name') or '')
        tagstr = det.get('tags') or ''
        cat = None
        for tok in re.split(r'\s+', tagstr):
            cat = canon_cat(tok)
            if cat:
                break
        if not cat:
            for s in cand.get('sources', []):
                cat = canon_cat(s)
                if cat:
                    break
        cat = cat or 'Community & Social'
        desc = clean_text(det.get('desc') or '')
        country = 'BR'
        if not name:
            name = clean_text(og)
    if not name:
        dropped['no-name'] += 1
        return None
    if has_adult_emoji(name) or has_adult_emoji(desc) or has_adult_emoji(og):
        dropped['adult-emoji'] += 1
        return None
    blob = deobfuscate(name) + ' ' + deobfuscate(desc) + ' ' + deobfuscate(og)
    if SCAM_RE.search(blob):
        dropped['scam'] += 1
        return None
    if PORN_RE.search(blob):
        dropped['porn-keyword'] += 1
        return None
    if len(name) > 100:
        name = name[:100].rstrip()
    if not desc or len(desc) < 15:
        desc = f'Join {name}, a WhatsApp group listed under {cat}.'
    if len(desc) > 300:
        desc = desc[:300].rstrip()
    # name mismatch guard: if live og:title shares no token>=4 chars with listing name, prefer og:title
    def toks(s):
        return set(w for w in re.findall(r'[A-Za-z0-9]{4,}', (s or '').lower()))
    og_clean = clean_text(og)
    if og_clean and name and toks(og_clean) and not (toks(name) & toks(og_clean)):
        name = og_clean[:100]
    return {'name': name, 'category': cat, 'country': country,
            'description': desc, 'invite': f'https://chat.whatsapp.com/{code}', 'image': ''}

verified, pending = [], []
dropped = Counter()
for code, cand in todo.items():
    status, og = results.get(code, ('dead', ''))
    if status == 'transport':
        pending.append(build_pending(cand, code))
        continue
    if status != 'live':
        continue
    rec = build_verified(cand, code, og)
    if rec is None:
        continue
    verified.append(rec)

print('dropped:', dict(dropped), flush=True)
print(f'verified: {len(verified)}, pending: {len(pending)}', flush=True)

json.dump(verified, open(os.path.join(WAVE, 'team12-igrupos-ongrupos.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(pending, open(os.path.join(WAVE, 'team12-igrupos-ongrupos-pending.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- leads: listing pages fetched/known, minus already-banked ----------
import glob as _glob
banked = set()
for f in _glob.glob(os.path.join(WAVE, 'leads_slice_*.json')):
    for x in json.load(open(f)):
        banked.add(x.get('url', ''))
for f in _glob.glob(os.path.join(WAVE, 'team12-*.json')):
    pass
leads = []
def add_lead(url, label):
    if url in banked:
        return
    if any(l['url'] == url for l in leads):
        return
    leads.append({'url': url, 'source': label})
add_lead('https://www.igrupos.com/', 'igrupos-home')
add_lead('https://www.igrupos.com/whatsapp', 'igrupos-whatsapp-p1')
for p in (2, 3, 4, 5):
    add_lead(f'https://www.igrupos.com/whatsapp/{p}', 'igrupos-whatsapp-p%d' % p)
for cc in ['AD','AR','BO','BR','CL','CO','CR','CU','DO','EC','ES','GT','MX','PA','PE','PY','SV','US','UY','VE']:
    add_lead(f'https://www.igrupos.com/ciudades/{cc}/whatsapp', f'igrupos-country-{cc}')
for t in ['amor','anime','bailar','gamers','gays','humor','instagram','k-pop','musica',
          'peliculas','politica','rock','rol','roleplay','senderismo','solteros','stickers','youtube']:
    add_lead(f'https://www.igrupos.com/tag/whatsapp/{t}', f'igrupos-tag-{t}')
for s in ['sortnew', 'sorttoday', 'sortweek', 'sortmonth', 'sortall']:
    add_lead(f'https://www.igrupos.com/whatsapp/{s}', f'igrupos-{s}')
for city in ['chicago', 'berwyn-illinois', 'cicero', 'elmwood-park', 'forest-park',
             'lockport-illinois', 'oak-park-illinois', 'stickney']:
    add_lead(f'https://www.igrupos.com/whatsapp/{city}', f'igrupos-city-{city}')
add_lead('https://ongrupos.com/', 'ongrupos-home')
for cu in re.findall(r'<loc>(https://ongrupos\.com/categoria/[^<]+)</loc>',
                     open('/tmp/on_cat.xml', encoding='utf-8', errors='ignore').read()):
    add_lead(cu, 'ongrupos-cat-' + cu.rsplit('/', 1)[-1])
json.dump(leads, open(os.path.join(WAVE, 'team12-igrupos-ongrupos-leads.json'), 'w'), ensure_ascii=False, indent=1)
print(f'leads: {len(leads)} (banked/excluded: checked against slices)', flush=True)
print('DONE', flush=True)
