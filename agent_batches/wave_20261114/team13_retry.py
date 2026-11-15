#!/usr/bin/env python3
"""team13 retry pass for no-code detail pages."""
import json, re, time, html, os
import requests

WAVE = os.path.dirname(os.path.abspath(__file__))
SITE = '/home/hatch/workspace/whatsapp-groups-site'
union = set(json.load(open(f'{SITE}/.existing_codes.json')))
t17 = json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team17-tugrupo-online-candidates.json'))
t17codes = set(c['invite'].rsplit('/', 1)[-1] for c in t17)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'}
ts = requests.Session(); ts.headers.update(UA)
vs = requests.Session(); vs.headers.update(UA)
st = json.load(open(f'{WAVE}/team13-state.json'))

def is_challenge(t):
    return ('One moment, please' in t or '__cf_chl_' in t or 'cf-challenge' in t)

def og_title(t):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', t, re.I | re.S)
    if not m:
        m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', t, re.I | re.S)
    return html.unescape(m.group(1)).strip() if m else ''

def verify_code(code, retries=3):
    url = f'https://chat.whatsapp.com/{code}'
    last = ''
    for a in range(retries):
        try:
            r = vs.get(url, timeout=75)
            if r.status_code == 429:
                return ('pending', '', f'HTTP 429 attempt {a+1}')
            t = og_title(r.text)
            if t:
                return ('live', t, f'HTTP {r.status_code}')
            last = f'empty og:title HTTP {r.status_code}'
        except Exception as e:
            last = f'{type(e).__name__}: {e}'
            if a == retries - 1:
                return ('pending', '', last)
        time.sleep(4 * (a + 1))
    return ('dead', '', last)

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
          'humor': 'Funny', 'ingles': 'Education', 'idiomas': 'Education'}
PORN = re.compile(r'\b(xxx|porn|porno|sexo\s*expl[ií]cito|videos\s*porno|putas|tetas|polla|verga|coño|follando?|nudes?|onlyfans|pack\s*de\s*(chicas|mujeres|nenas)|sex\s*chat|hot\s*girls?\s*(xxx|porn)?)\b', re.I)
SCAM = re.compile(r'(airdrop|binary\s*option|opciones\s*binarias|free\s*money|dinero\s*gratis|gana\s+\$?\d+\s*(al\s*d[ií]a|por\s*d[ií]a|diarios?)\s*(gratis|sin\s*inversi[oó]n)|plataformas?\s*pagantes|tigrinho|fortune\s*tiger|sinais\s*(de\s*)?(apostas?|cassino|tigre)|cassino|casino|slots?|apostas?\s*esportivas|wjbett?|bet365\s*signals?|aviator\s*signals?)', re.I)
NEG_PROHIB = re.compile(r'(prohibido|no\s+se\s+permite|sin\s+porno|no\s+porno|anti[-\s]?porno|prohibido\s+el\s+porno)', re.I)

def screen(name, ogt):
    text = f'{name} {ogt}'
    if NEG_PROHIB.search(text):
        return None
    if PORN.search(text):
        if re.search(r'\b(18\+|mayores?\s+de\s+18)\b', text) and not re.search(r'\b(porn|xxx|sexo|putas|nudes?|onlyfans)\b', text, re.I):
            return None
        return 'porn/xxx content'
    if SCAM.search(text):
        return 'crypto-airdrop/binary/casino/betting scam'
    return None

nocode = [u for u, v in st['detail'].items() if not v.get('code')]
print('retrying', len(nocode), 'no-code detail pages', flush=True)
for url in nocode:
    name_hint = st['listings'].get(url, {}).get('name', '')
    slug_hint = st['listings'].get(url, {}).get('slug', '')
    h = None
    for a in range(3):
        try:
            r = ts.get(url, timeout=60)
            if r.status_code == 200 and len(r.text) > 5000 and not is_challenge(r.text):
                h = r.text
                break
            print(f'  {url[:70]} -> {r.status_code} len {len(r.text)} challenge={is_challenge(r.text)}', flush=True)
        except Exception as e:
            print(f'  {url[:70]} ERR {type(e).__name__}', flush=True)
        time.sleep(8 * (a + 1))
    if not h:
        print(f'  STILL NO-CODE {url}', flush=True)
        continue
    codes = re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]{15,30})', h)
    if not codes:
        print(f'  LOADED BUT NO CODE {url}', flush=True)
        st['detail'][url] = {'done': True, 'code': None, 'err': 'loaded-no-code'}
        json.dump(st, open(f'{WAVE}/team13-state.json', 'w'), ensure_ascii=False, indent=1)
        continue
    code = codes[0]
    t = re.search(r'<title>(.*?)</title>', h, re.S | re.I)
    ptitle = html.unescape(t.group(1)).strip() if t else ''
    name = name_hint or ptitle.replace(' - TuGrupo.Online', '').replace(' | TuGrupo.Online', '').strip()
    m = re.match(r'https://tugrupo\.online/whatsapp/([a-z0-9\-]+)/', url)
    slug = slug_hint or (m.group(1) if m else '')
    st['detail'][url] = {'done': True, 'code': code, 'name': name, 'slug': slug, 'retried': True}
    json.dump(st, open(f'{WAVE}/team13-state.json', 'w'), ensure_ascii=False, indent=1)
    if code in union:
        print(f'  DUP-union {code} {name[:40]}', flush=True); continue
    if code in t17codes:
        print(f'  DUP-team17 {code} {name[:40]}', flush=True); continue
    if code in st['verified'] or code in st['pending'] or code in st['dead'] or code in st['excluded']:
        print(f'  DUP-team {code}', flush=True); continue
    status, ogt, reason = verify_code(code)
    if status == 'live':
        excl = screen(name, ogt)
        if excl:
            st['excluded'][code] = {'name': name, 'og_title': ogt, 'reason': excl, 'detail': url}
            print(f'  EXCLUDED {code} {excl} | {ogt[:60]}', flush=True)
        else:
            st['verified'][code] = {'name': name, 'category': CATMAP.get(slug, 'Community & Social'), 'country': '', 'og_title': ogt, 'detail': url, 'slug': slug}
            print(f'  KEPT {code} {ogt[:60]}', flush=True)
    elif status == 'pending':
        st['pending'][code] = {'name': name, 'reason': reason, 'detail': url}
        print(f'  PENDING {code} {reason}', flush=True)
    else:
        st['dead'][code] = {'name': name, 'reason': reason, 'detail': url}
        print(f'  DEAD {code} {reason}', flush=True)
    json.dump(st, open(f'{WAVE}/team13-state.json', 'w'), ensure_ascii=False, indent=1)
    time.sleep(0.5)
print('RETRY DONE verified', len(st['verified']), 'dead', len(st['dead']), 'pending', len(st['pending']), 'excluded', len(st['excluded']), flush=True)
