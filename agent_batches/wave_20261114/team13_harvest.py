#!/usr/bin/env python3
"""team13 tugrupo.online — page 4 onwards + 26 detail pages. wave_20261114."""
import json, re, time, html, os, sys
import requests

WAVE = os.path.dirname(os.path.abspath(__file__))
SITE = '/home/hatch/workspace/whatsapp-groups-site'
UNION = json.load(open(f'{SITE}/.existing_codes.json'))
union = set(UNION)
t17 = json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team17-tugrupo-online-candidates.json'))
t17codes = set(c['invite'].rsplit('/', 1)[-1] for c in t17)
leads26 = json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team17-tugrupo-online-leads.json'))
DETAIL_LEADS = [u for u in leads26 if u.startswith('https://tugrupo.online/whatsapp/') and 'query-eb715b85' not in u]
PAGE4_LEAD = 'https://tugrupo.online/whatsapp/?query-eb715b85=4'

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'}
ts = requests.Session(); ts.headers.update(UA)          # tugrupo session
vs = requests.Session(); vs.headers.update(UA)          # chat.whatsapp.com session (keep-alive)

STATE_F = f'{WAVE}/team13-state.json'
def load_state():
    try: return json.load(open(STATE_F))
    except Exception: return {'pages_done': [], 'pages_failed': [], 'listings': {}, 'detail': {}, 'verified': {}, 'pending': {}, 'dead': {}, 'excluded': {}, 'controls': {}}
def save_state(st): json.dump(st, open(STATE_F, 'w'), ensure_ascii=False, indent=1)
st = load_state()

def og_title(htmltxt):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', htmltxt, re.I | re.S)
    if not m:
        m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', htmltxt, re.I | re.S)
    return html.unescape(m.group(1)).strip() if m else ''

def verify_code(code, retries=3):
    """returns (status, ogtitle, reason) status in live/dead/pending"""
    url = f'https://chat.whatsapp.com/{code}'
    last_err = ''
    for attempt in range(retries):
        try:
            r = vs.get(url, timeout=75)
            if r.status_code == 429:
                return ('pending', '', f'HTTP 429 attempt {attempt+1}')
            t = og_title(r.text)
            if t:
                return ('live', t, f'HTTP {r.status_code}')
            last_err = f'empty og:title HTTP {r.status_code}'
        except Exception as e:
            last_err = f'{type(e).__name__}: {e}'
            # transport failure -> pending per spec (only after retries)
            if attempt == retries - 1:
                return ('pending', '', last_err)
        time.sleep(4 * (attempt + 1))
    return ('dead', '', last_err)

# ---------- CONTROLS (run first, every run until passed) ----------
if not st['controls'].get('passed'):
    print('CONTROLS...', flush=True)
    s1, t1, r1 = verify_code('KrDwdK8EIkB6vgauHg5M7N')
    print('live control:', s1, repr(t1), r1, flush=True)
    s2, t2, r2 = verify_code('ZzZzZzZzZzZzZzZzZzZzZzZz')
    print('fabricated control:', s2, repr(t2), r2, flush=True)
    st['controls'] = {'live': {'status': s1, 'og_title': t1, 'reason': r1},
                      'fabricated': {'status': s2, 'og_title': t2, 'reason': r2},
                      'passed': (s1 == 'live' and t1 == 'JAY - PHP & Python Full Stack Developer' and s2 == 'dead' and t2 == '')}
    save_state(st)
    if not st['controls']['passed']:
        print('CONTROLS FAILED — STOPPING', flush=True)
        sys.exit(2)
    print('CONTROLS PASSED', flush=True)

CATMAP = {'chat': 'Community & Social', 'juegos': 'Gaming', 'anime': 'Entertainment',
          'rol': 'Gaming', 'diversion': 'Entertainment', 'musica': 'Entertainment',
          'memes': 'Funny', 'stickers': 'Funny', 'peliculas': 'Entertainment',
          'mundial': 'Sports', 'futbol': 'Sports', 'deportes': 'Sports',
          'educacion': 'Education', 'estudio': 'Education', 'cocina': 'Cooking',
          'salud': 'Health', 'noticias': 'News', 'trabajo': 'Jobs', 'empleo': 'Jobs',
          'tecnologia': 'Technology', 'negocios': 'Business', 'finanzas': 'Finance',
          'cripto': 'Crypto', 'criptomonedas': 'Crypto', 'poesia': 'Poetry',
          'viajes': 'Travel', 'becas': 'Scholarship', 'freelance': 'Freelance',
          'islam': 'Islamic', 'religion': 'Islamic', 'compra-venta': 'Buy Sell',
          'ventas': 'Buy Sell', 'inmobiliaria': 'Real Estate', 'amistad': 'Community & Social',
          'familia': 'Community & Social', 'libros': 'Education', 'series': 'Entertainment',
          'humor': 'Funny', 'apuestas': 'Sports', 'crypto': 'Crypto', 'ganar-dinero': 'Earning',
          'dinero': 'Earning', 'ingles': 'Education', 'idiomas': 'Education'}

PORN = re.compile(r'\b(xxx|porn|porno|sexo\s*expl[ií]cito|videos\s*porno|putas|tetas|polla|verga|coño|follando?|nudes?|onlyfans|pack\s*de\s*(chicas|mujeres|nenas)|sex\s*chat|hot\s*girls?\s*(xxx|porn)?)\b', re.I)
SCAM = re.compile(r'(airdrop|binary\s*option|opciones\s*binarias|free\s*money|dinero\s*gratis|gana\s+\$?\d+\s*(al\s*d[ií]a|por\s*d[ií]a|diarios?)\s*(gratis|sin\s*inversi[oó]n)|plataformas?\s*pagantes|tigrinho|fortune\s*tiger|sinais\s*(de\s*)?(apostas?|cassino|tigre)|cassino|casino|slots?|apostas?\s*esportivas|wjbett?|bet365\s*signals?|aviator\s*signals?)', re.I)
NEG_PROHIB = re.compile(r'(prohibido|no\s+se\s+permite|sin\s+porno|no\s+porno|anti[-\s]?porno|prohibido\s+el\s+porno)', re.I)
FALSE_POS = re.compile(r'(sexta-feira|chuta|18\+)', re.I)

def screen(name, ogt):
    text = f'{name} {ogt}'
    if NEG_PROHIB.search(text):
        return None  # negated prohibition -> keep
    if PORN.search(text):
        # allow 18+ age gates on non-porn, food/fitness contexts
        if re.search(r'\b(18\+|mayores?\s+de\s+18)\b', text) and not re.search(r'\b(porn|xxx|sexo|putas|nudes?|onlyfans)\b', text, re.I):
            return None
        return 'porn/xxx content'
    if SCAM.search(text):
        return 'crypto-airdrop/binary/casino/betting scam'
    return None

def parse_listings(htmltxt):
    """return list of dicts {url, name, slugcat} from a listing page"""
    out = []
    # article cards: entry title link
    for m in re.finditer(r'<h2[^>]*class="[^"]*entry-title[^"]*"[^>]*>\s*<a[^>]*href="(https://tugrupo\.online/whatsapp/[^"]+/)"[^>]*>(.*?)</a>', htmltxt, re.S | re.I):
        url = m.group(1)
        name = html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip()
        mm = re.match(r'https://tugrupo\.online/whatsapp/([a-z0-9\-]+)/', url)
        slug = mm.group(1) if mm else ''
        out.append({'url': url, 'name': name, 'slug': slug})
    if not out:  # fallback: aria-label media links
        seen = set()
        for m in re.finditer(r'<a[^>]+class="[^"]*ct-media-container[^"]*"[^>]+href="(https://tugrupo\.online/whatsapp/[^"]+/)"[^>]*aria-label="([^"]*)"', htmltxt, re.I):
            url, name = m.group(1), html.unescape(m.group(2)).strip()
            if url in seen: continue
            seen.add(url)
            mm = re.match(r'https://tugrupo\.online/whatsapp/([a-z0-9\-]+)/', url)
            out.append({'url': url, 'name': name, 'slug': mm.group(1) if mm else ''})
    # dedupe preserving order
    ded, seen = [], set()
    for o in out:
        if o['url'] not in seen:
            seen.add(o['url']); ded.append(o)
    return ded

def is_challenge(htmltxt):
    return ('One moment, please' in htmltxt or '__cf_chl_' in htmltxt
            or 'cf-challenge' in htmltxt or 'Attention Required' in htmltxt)

def fetch_page(url, retries=4):
    for a in range(retries):
        try:
            r = ts.get(url, timeout=60)
            if r.status_code == 200 and len(r.text) > 5000 and not is_challenge(r.text):
                return r.text
            print(f'  fetch {url} -> {r.status_code} len {len(r.text)} challenge={is_challenge(r.text)}', flush=True)
        except Exception as e:
            print(f'  fetch {url} ERR {type(e).__name__}: {e}', flush=True)
        time.sleep(8 * (a + 1))
    return None

def detail_code(url):
    """fetch detail page, return (code, title, desc) or (None,...) with err in title"""
    h = fetch_page(url, retries=3)
    if not h:
        return None, '', 'fetch-fail'
    codes = re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]{15,30})', h)
    code = codes[0] if codes else None
    t = re.search(r'<title>(.*?)</title>', h, re.S | re.I)
    title = html.unescape(t.group(1)).strip() if t else ''
    return code, title, ''

def process_detail(url, name_hint='', slug_hint=''):
    """mine one detail page -> verify -> record in state. Returns True if a kept candidate resulted."""
    if url in st['detail'] and st['detail'][url].get('done'):
        return False
    code, ptitle, err = detail_code(url)
    if not code:
        st['detail'][url] = {'done': True, 'code': None, 'err': err or 'no-code-on-page'}
        save_state(st)
        print(f'  DETAIL NO-CODE {url}', flush=True)
        return False
    name = name_hint or ptitle.replace(' - TuGrupo.Online', '').replace(' | TuGrupo.Online', '').strip()
    slug = slug_hint or (re.match(r'https://tugrupo\.online/whatsapp/([a-z0-9\-]+)/', url).group(1) if re.match(r'https://tugrupo\.online/whatsapp/([a-z0-9\-]+)/', url) else '')
    st['detail'][url] = {'done': True, 'code': code, 'name': name, 'slug': slug}
    save_state(st)
    if code in union:
        print(f'  DUP-union {code} {name[:40]}', flush=True); return False
    if code in t17codes:
        print(f'  DUP-team17 {code} {name[:40]}', flush=True); return False
    if code in st['verified'] or code in st['pending'] or code in st['dead'] or code in st['excluded']:
        print(f'  DUP-team {code}', flush=True); return False
    status, ogt, reason = verify_code(code)
    if status == 'live':
        excl = screen(name, ogt)
        if excl:
            st['excluded'][code] = {'name': name, 'og_title': ogt, 'reason': excl, 'detail': url}
            print(f'  EXCLUDED {code} {excl} | {ogt[:60]}', flush=True)
        else:
            cat = CATMAP.get(slug, 'Community & Social')
            st['verified'][code] = {'name': name, 'category': cat, 'country': '', 'og_title': ogt, 'detail': url, 'slug': slug}
            print(f'  KEPT {code} [{cat}] {ogt[:60]}', flush=True)
    elif status == 'pending':
        st['pending'][code] = {'name': name, 'reason': reason, 'detail': url}
        print(f'  PENDING {code} {reason}', flush=True)
    else:
        st['dead'][code] = {'name': name, 'reason': reason, 'detail': url}
        print(f'  DEAD {code} {reason}', flush=True)
    save_state(st)
    return status == 'live' and code in st['verified']

# ---------- PAGE 4 ----------
if 4 not in st['pages_done'] and 4 not in st['pages_failed']:
    print('PAGE 4...', flush=True)
    h = fetch_page(PAGE4_LEAD, retries=3)
    if h:
        lst = parse_listings(h)
        print(f'PAGE 4 listings: {len(lst)}', flush=True)
        st['pages_done'].append(4)
        for it in lst:
            st['listings'][it['url']] = it
        save_state(st)
        for it in lst:
            process_detail(it['url'], it['name'], it['slug'])
            time.sleep(0.5)
    else:
        st['pages_failed'].append(4)
        save_state(st)
        print('PAGE 4 FAILED (all retries)', flush=True)

# ---------- 26 DETAIL PAGES ----------
print('26 DETAIL LEADS...', flush=True)
for u in DETAIL_LEADS:
    if u in st['detail'] and st['detail'][u].get('done'):
        continue
    process_detail(u)
    time.sleep(0.5)
print('detail leads done. kept so far:', len(st['verified']), flush=True)

# ---------- PAGES 11+ ----------
MAX_PAGE = 110
page = 11
prev_sig = None
while page <= MAX_PAGE:
    if page in st['pages_done']:
        page += 1
        continue
    url = f'https://tugrupo.online/whatsapp/?query-eb715b85={page}'
    print(f'PAGE {page}...', flush=True)
    h = fetch_page(url, retries=3)
    if not h:
        st['pages_failed'].append(page)
        save_state(st)
        print(f'PAGE {page} FAILED — banking rest as leads, stopping', flush=True)
        break
    lst = parse_listings(h)
    sig = tuple(x['url'] for x in lst)
    if not lst or sig == prev_sig:
        print(f'PAGE {page}: empty/repeat listings — STOP', flush=True)
        st['pages_done'].append(page)
        save_state(st)
        break
    prev_sig = sig
    print(f'PAGE {page} listings: {len(lst)}', flush=True)
    st['pages_done'].append(page)
    for it in lst:
        st['listings'][it['url']] = it
    save_state(st)
    for it in lst:
        process_detail(it['url'], it['name'], it['slug'])
        time.sleep(0.4)
    page += 1

print('DONE. pages:', sorted(st['pages_done']), 'failed:', st['pages_failed'],
      'verified:', len(st['verified']), 'pending:', len(st['pending']),
      'dead:', len(st['dead']), 'excluded:', len(st['excluded']), flush=True)
