#!/usr/bin/env python3
"""team35 verification: 3,458 igrupos retry candidates -> team35-pending-retry.json (verified)
Writes checkpoint every 200 completions. Stop on HTTP 429."""
import json, re, html, time, threading, sys
from concurrent.futures import ThreadPoolExecutor

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
WORKERS = 16
TIMEOUT = 60

CATS = {"Sports","Gaming","Jobs","Education","Entertainment","Friendship","News","Islamic",
        "Business","Finance","Buy-Sell","Health","Community","Technology","Crypto","Travel",
        "Music","Movies","Food","Pets","Funny","Girls","Regional","Other"}

COUNTRY_NAMES = {'MX':'Mexico','CO':'Colombia','VE':'Venezuela','AR':'Argentina','CL':'Chile',
 'PE':'Peru','EC':'Ecuador','BO':'Bolivia','PY':'Paraguay','UY':'Uruguay','BR':'Brazil',
 'CR':'Costa Rica','PA':'Panama','GT':'Guatemala','HN':'Honduras','SV':'El Salvador',
 'NI':'Nicaragua','DO':'Dominican Republic','CU':'Cuba','PR':'Puerto Rico','ES':'Spain',
 'US':'United States','IN':'India','PK':'Pakistan'}

PORN_SUBS = ['porn','pornhub','xxx','nude','sex video','escort','call girl','fuck','dick',
             'pussy','boobs','anal','bokep','مzا','مزا دینے','مزہ دینے','sexo explicito',
             'videos porno','porno gratis','putas','puta ','putas ']
PORN_EMOJI = ['\U0001F975','\U0001F346','\U0001F351','\U0001F51E','\U0001F4A6',
              '\U0001F445','\U0001F444','\U0001F48B']
SCAM_SUBS = ['satta','matka','double your money','hyip','paypal receiver','and loader',
             'carding','fullz',' dumps','cvv','phishing','money mule','mula de dinero']
MINOR_SUBS = ['teen dating','dating teens','13-17','14-17','menores de edad solteros',
              'niñas solteras','niños solteros','chicos menores']

KEYWORD_CAT = [
    ('Gaming', ['free fire','gta','minecraft','pubg','call of duty','cod mobile','fortnite',
                'among us','gamer','gaming','juegos','videojuegos','roblox','brawl stars']),
    ('Sports', ['futbol','fútbol','football','deportes','sports','nfl','cricket','messi',
                'real madrid','barcelona','apuestas deportivas']),
    ('Music', ['musica','música','music','reggaeton','rock','kpop','k-pop','dj','trap latino']),
    ('Movies', ['peliculas','películas','movies','series','netflix','anime','cine']),
    ('Friendship', ['amistad','amigos','amor y amistad','conocer gente','nuevos amigos',
                    'friendship','friends','socializar','conocer personas']),
    ('Girls', ['solteras','solteros y solteras','citas','dating','noviazgo','pareja',
               'chicas','mujeres solteras','singles']),
    ('Jobs', ['empleo','trabajo','trabajos','ofertas laborales','empleos','jobs','vacantes',
              'bolsa de trabajo']),
    ('Business', ['negocios','emprendedores','emprendimiento','business','networking',
                  'inversionistas']),
    ('Finance', ['finanzas','dinero','inversiones','trading','forex','finanzas personales']),
    ('Buy-Sell', ['ventas','compra','vendo','marketplace','ofertas','descuentos','tienda',
                 'buy','sell','venta de']),
    ('Education', ['educacion','educación','estudiantes','universidad','tareas','clases',
                  'cursos','aprender','estudio','escuela']),
    ('News', ['noticias','news','ultima hora','última hora','informacion','información']),
    ('Health', ['salud','fitness','gym','dieta','bienestar','saludable','ejercicio']),
    ('Technology', ['tecnologia','tecnología','tech','programacion','programación',
                    'desarrollo','informatica','software']),
    ('Crypto', ['crypto','bitcoin','cripto','criptomonedas','ethereum']),
    ('Travel', ['viajes','travel','turismo','viajeros','vacaciones']),
    ('Food', ['comida','recetas','cocina','food','restaurantes']),
    ('Pets', ['mascotas','perros','gatos','pets','animales']),
    ('Funny', ['memes','humor','chistes','risas','funny','divertidos']),
    ('Entertainment', ['entretenimiento','diversión','diversion','farándula','farandula',
                       'entretenimiento']),
    ('Community', ['comunidad','cristianos','cristiano','dios','biblia','oracion','iglesia',
                   'catolicos','vecinos','colonia','barrio','apoyo']),
]

def map_category(title, cand_cat):
    if cand_cat in CATS and cand_cat != 'Other':
        return cand_cat
    t = (title or '').lower()
    for cat, kws in KEYWORD_CAT:
        if any(k in t for k in kws):
            return cat
    return 'Other'

def has_porn(t):
    tl = t.lower()
    return any(s in tl for s in PORN_SUBS) or any(e in t for e in PORN_EMOJI)

def has_scam(t):
    return any(s in t.lower() for s in SCAM_SUBS)

def has_minor(t):
    return any(s in t.lower() for s in MINOR_SUBS)

META_RX = re.compile(r'<meta[^>]*>', re.I | re.S)
def extract_og_title(page):
    for m in META_RX.finditer(page):
        tag = m.group(0)
        if re.search(r'property=["\']og:title["\']', tag, re.I):
            cm = re.search(r'content=["\'](.*?)["\']', tag, re.I | re.S)
            if cm:
                return html.unescape(cm.group(1)).strip()
    return ''

DESC_TMPLS = [
    "A {cat} WhatsApp group for {country} members to connect, share updates, and chat about {topic}.",
    "Join this active {cat} WhatsApp group from {country} for daily conversation and {topic} discussions.",
    "A community WhatsApp group in {country} focused on {cat} topics and {topic} with friendly members.",
    "Connect with people across {country} in this {cat} WhatsApp group sharing {topic} content and chat.",
    "This {country} WhatsApp group brings together {cat} fans to talk {topic} and make new friends.",
]

def clean_topic(name):
    # strip emojis/symbols, keep words, cap length
    t = re.sub(r'[^\w\s\-\.\&]', ' ', name, flags=re.U)
    t = re.sub(r'\s+', ' ', t).strip()
    words = t.split()[:6]
    return ' '.join(words) if words else 'general topics'

def make_description(name, cat, country):
    cn = COUNTRY_NAMES.get(country, country if len(country) == 2 else 'Latin America')
    catw = cat.lower().replace('-', ' ')
    topic = clean_topic(name)
    tmpl = DESC_TMPLS[hash(name) % len(DESC_TMPLS)]
    return tmpl.format(cat=catw, country=cn, topic=topic)

def main():
    cands = json.load(open(WAVE + '_team35_candidates.json'))
    print(f'candidates: {len(cands)}', flush=True)
    lock = threading.Lock()
    stop_429 = {'hit': False}
    results = {'verified': [], 'pending': [], 'dead': 0, 'porn': 0, 'scam': 0,
               'minors': 0, 'transport': 0, 'done': 0}
    per_source = {}

    def worker(chunk):
        import requests
        s = requests.Session()
        s.headers.update({'User-Agent': UA})
        for c in chunk:
            if stop_429['hit']:
                with lock:
                    results['pending'].append({'code': c['code'], 'note': 'rate-limited (not attempted)'})
                continue
            code = c['code']
            url = 'https://chat.whatsapp.com/' + code
            title = None
            status = None
            try:
                r = s.get(url, timeout=TIMEOUT)
                status = r.status_code
                if status == 429:
                    with lock:
                        stop_429['hit'] = True
                    raise RuntimeError('429')
                title = extract_og_title(r.text) if status == 200 else ''
            except RuntimeError:
                with lock:
                    results['transport'] += 1
                    results['pending'].append({'code': code, 'note': 'rate-limited'})
                continue
            except Exception:
                with lock:
                    results['transport'] += 1
                    results['pending'].append({'code': code, 'note': 'transport failure'})
                try:
                    s.close()
                except Exception:
                    pass
                s = requests.Session()
                s.headers.update({'User-Agent': UA})
                continue
            with lock:
                results['done'] += 1
                src = c['source']
                per_source[src] = per_source.get(src, 0) + 1
                if not title:
                    results['dead'] += 1
                    continue
                if has_porn(title):
                    results['porn'] += 1
                    continue
                if has_scam(title):
                    results['scam'] += 1
                    continue
                if has_minor(title):
                    results['minors'] += 1
                    continue
                country = c['country'] if re.fullmatch(r'[A-Z]{2}', c['country'] or '') else 'International'
                cat = map_category(title, c['category'])
                name = title if len(title) <= 120 else title[:120]
                results['verified'].append({
                    'name': name,
                    'category': cat,
                    'country': country,
                    'description': make_description(name, cat, country),
                    'invite': 'https://chat.whatsapp.com/' + code,
                    'image': '',
                })
                if results['done'] % 200 == 0:
                    ck = {'verified': results['verified'], 'pending': results['pending'],
                          'stats': {k: v for k, v in results.items() if k not in ('verified', 'pending')}}
                    json.dump(ck, open(WAVE + '_team35_checkpoint.json', 'w'), ensure_ascii=False)
                    print(f"progress: done={results['done']} verified={len(results['verified'])} "
                          f"dead={results['dead']} transport={results['transport']} pending={len(results['pending'])}",
                          flush=True)

    chunks = [cands[i::WORKERS] for i in range(WORKERS)]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(worker, chunks))

    json.dump(results['verified'], open(WAVE + 'team35-pending-retry.json', 'w'), ensure_ascii=False)
    pend = []
    for p in results['pending']:
        rec = next((c for c in cands if c['code'] == p['code']), None)
        pend.append({'name': (rec or {}).get('name', ''), 'category': (rec or {}).get('category', '') or 'Other',
                     'country': (rec or {}).get('country', '') or 'International',
                     'description': (rec or {}).get('description', ''),
                     'invite': 'https://chat.whatsapp.com/' + p['code'], 'image': '',
                     'note': p['note']})
    json.dump(pend, open(WAVE + 'team35-unverified-pending.json', 'w'), ensure_ascii=False)
    print(json.dumps({'verified': len(results['verified']), 'pending': len(pend),
                      'dead': results['dead'], 'porn_drops': results['porn'],
                      'scam_drops': results['scam'], 'minors_drops': results['minors'],
                      'transport': results['transport'], 'per_source': per_source,
                      'hit_429': stop_429['hit']}, indent=1))

if __name__ == '__main__':
    main()
