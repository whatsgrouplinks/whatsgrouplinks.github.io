#!/usr/bin/env python3
"""Team 12 stage 1: harvest igrupos + ongrupos listing pages, extract invite codes from static HTML.
Writes team12-candidates.json in the wave dir. No verification here (stage 2)."""
import json, re, subprocess, os, html
from concurrent.futures import ThreadPoolExecutor

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
union = set(json.load(open(os.path.join(WAVE, 'dedupe_union.json'))))

def curl(url, timeout=45):
    try:
        r = subprocess.run(['curl', '-sS', '-m', str(timeout), '-L', '-A', UA, url],
                           capture_output=True, timeout=timeout + 10)
        return r.stdout.decode('utf-8', errors='replace') if r.returncode == 0 else ''
    except Exception as e:
        print('FETCH ERR', url, e)
        return ''

# ---------- igrupos listing pages ----------
listings = []  # (url, kind, label)
listings.append(('https://www.igrupos.com/whatsapp/2', 'main', 'whatsapp-p2'))
listings.append(('https://www.igrupos.com/whatsapp/3', 'main', 'whatsapp-p3'))
countries = {'AD':'AD','AR':'AR','BO':'BO','BR':'BR','CL':'CL','CO':'CO','CR':'CR','CU':'CU',
             'DO':'DO','EC':'EC','ES':'ES','GT':'GT','MX':'MX','PA':'PA','PE':'PE','PY':'PY',
             'SV':'SV','US':'US','UY':'UY','VE':'VE'}
for cc in countries:
    listings.append((f'https://www.igrupos.com/ciudades/{cc}/whatsapp', 'country', cc))
tags = ['amor','anime','bailar','gamers','gays','humor','instagram','k-pop','musica',
        'peliculas','politica','rock','rol','roleplay','senderismo','solteros','stickers','youtube']
for t in tags:
    listings.append((f'https://www.igrupos.com/tag/whatsapp/{t}', 'tag', t))

# reuse already-fetched pages
pages = {}
for f, key in [('/tmp/ig_home.html', 'HOME'), ('/tmp/ig_whatsapp.html', 'WHATSAPP'), ('/tmp/ig_mx.html', 'MX')]:
    try:
        pages[key] = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        pass

gid_meta = {}   # gid -> {title, desc, flag, sources[]}
CARD_RE = re.compile(r"lnkgroup\('(\d+)'\)(.*?)(?=lnkgroup\('|\Z)", re.S)
def parse_listing(html_text, src_label, country_hint=None):
    n = 0
    for m in CARD_RE.finditer(html_text):
        gid, chunk = m.group(1), m.group(2)[:2000]
        title = re.search(r'<h3[^>]*>(.*?)</h3>', chunk, re.S)
        desc = re.search(r'<p[^>]*>(.*?)</p>', chunk, re.S)
        flag = re.search(r'banderas24/([A-Za-z0-9]+)\.png', chunk)
        title = re.sub(r'<[^>]+>', '', title.group(1)).strip() if title else ''
        title = html.unescape(re.sub(r'\s+', ' ', title))
        desc = re.sub(r'<[^>]+>', '', desc.group(1)).strip() if desc else ''
        desc = html.unescape(re.sub(r'\s+', ' ', desc))
        flag = flag.group(1) if flag else ''
        rec = gid_meta.setdefault(gid, {'title': title, 'desc': desc, 'flag': flag, 'sources': []})
        if title and not rec['title']:
            rec['title'] = title
        if desc and not rec['desc']:
            rec['desc'] = desc
        if flag and not rec['flag']:
            rec['flag'] = flag
        rec['sources'].append(src_label)
        if country_hint:
            rec.setdefault('country_hint', country_hint)
        n += 1
    return n

total_cards = 0
total_cards += parse_listing(pages.get('HOME', ''), 'home')
total_cards += parse_listing(pages.get('WHATSAPP', ''), 'whatsapp-p1')
total_cards += parse_listing(pages.get('MX', ''), 'country-MX', 'MX')
print('reused pages cards:', total_cards, 'unique gids so far:', len(gid_meta), flush=True)

for url, kind, label in listings:
    if label == 'country-MX':
        continue  # already parsed
    htext = curl(url)
    if not htext:
        print('EMPTY FETCH', url, flush=True)
        continue
    ch = countries.get(label) if kind == 'country' else None
    c = parse_listing(htext, f'{kind}-{label}', ch)
    print(f'listing {label}: {c} cards, unique gids now {len(gid_meta)}', flush=True)

print('TOTAL unique gids:', len(gid_meta), flush=True)
gids_sorted = sorted(gid_meta.keys(), key=lambda g: int(g), reverse=True)
print('newest gid:', gids_sorted[0], 'oldest:', gids_sorted[-1], flush=True)

# ---------- igrupos detail pages (newest first, cap 300) ----------
CAP = 300
todo = gids_sorted[:CAP]
print(f'fetching {len(todo)} detail pages...', flush=True)
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{22})')
def fetch_detail(gid):
    htext = curl(f'https://www.igrupos.com/grupo/{gid}', timeout=40)
    if not htext:
        return gid, None
    codes = CODE_RE.findall(htext)
    # detail-page text for category/scope
    t = re.sub(r'<script.*?</script>', '', htext, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(re.sub(r'\s+', ' ', t))
    m = re.search(r'El grupo tiene \d+ visitas (.*?) Te recomendamos', t)
    detail_desc = m.group(1).strip() if m else ''
    cat = re.search(r'Grupos de Whatsapp\s+([A-Za-záéíóúñ ]+?)\s+Grupo para gente', t)
    scope = re.search(r'(Grupo para gente de [^\.]{0,80}|Grupo solo para gente de [^\.]{0,80})', t)
    city = re.search(r'Grupos de Whatsapp\s+[A-Za-záéíóúñ ]+?\s+Grupo para gente[^\n]{0,120}?([A-Z][A-Za-záéíóúñ ]{1,30})\s+Comparte', t)
    return gid, {'codes': codes, 'detail_desc': detail_desc,
                 'category_raw': cat.group(1).strip() if cat else '',
                 'scope': scope.group(1).strip() if scope else '',
                 'text_head': t[:600]}

details = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for gid, res in ex.map(fetch_detail, todo):
        details[gid] = res
done = sum(1 for v in details.values() if v)
withcode = sum(1 for v in details.values() if v and v['codes'])
print(f'detail pages fetched: {done}/{len(todo)}; with invite code: {withcode}', flush=True)
mangled = sum(1 for v in details.values() if v and not v['codes'] and 'chat.whatsapp' in (v.get('text_head') or ''))
print('pages mentioning chat.whatsapp but no 22-char code (mangled/broken): check manually if needed', flush=True)

# ---------- ongrupos: homepage + 41 category p1 ----------
on_slugs = {}  # slug -> {name, desc, category}
on_home = curl('https://ongrupos.com/')
catxml = curl('https://ongrupos.com/category.xml')
cat_urls = re.findall(r'<loc>(https://ongrupos\.com/categoria/[^<]+)</loc>', catxml)
print('ongrupos categories from sitemap:', len(cat_urls), flush=True)
SLUG_RE = re.compile(r'ongrupos\.com/grupo/([A-Za-z0-9_-]{22})')
def parse_on_page(htext, cat_label):
    n = 0
    for m in SLUG_RE.finditer(htext):
        slug = m.group(1)
        # name/desc: look backwards/forwards in a window for the card text
        seg = htext[max(0, m.start()-1500):m.start()+1500]
        seg_t = re.sub(r'<[^>]+>', ' ', seg)
        seg_t = html.unescape(re.sub(r'\s+', ' ', seg_t)).strip()
        rec = on_slugs.setdefault(slug, {'name': '', 'desc': '', 'categories': []})
        rec['categories'].append(cat_label)
        n += 1
    return n
parse_on_page(on_home, 'home')
for cu in cat_urls:
    htext = curl(cu)
    if not htext:
        print('EMPTY FETCH', cu, flush=True)
        continue
    c = parse_on_page(htext, cu.rsplit('/', 1)[-1])
    print(f'ongrupos {cu.rsplit("/",1)[-1]}: {c} slugs, unique now {len(on_slugs)}', flush=True)

fresh_on = [s for s in on_slugs if s not in union]
print(f'ongrupos unique slugs: {len(on_slugs)}; fresh vs union: {len(fresh_on)}; already in union: {len(on_slugs)-len(fresh_on)}', flush=True)

# ---------- assemble candidates ----------
cands = []
for gid, res in details.items():
    if not res or not res['codes']:
        continue
    code = res['codes'][0]
    meta = gid_meta.get(gid, {})
    cands.append({'source': 'igrupos', 'gid': gid, 'code': code,
                  'in_union': code in union,
                  'title': meta.get('title', ''), 'desc': meta.get('desc', ''),
                  'flag': meta.get('flag', ''), 'country_hint': meta.get('country_hint', ''),
                  'sources': meta.get('sources', []),
                  'detail_desc': res.get('detail_desc', ''),
                  'category_raw': res.get('category_raw', ''), 'scope': res.get('scope', '')})
for slug in fresh_on:
    cands.append({'source': 'ongrupos', 'gid': slug, 'code': slug, 'in_union': False,
                  'title': '', 'desc': '', 'flag': '', 'country_hint': 'BR',
                  'sources': on_slugs[slug]['categories'],
                  'detail_desc': '', 'category_raw': '', 'scope': ''})
# pilot codes already checked live earlier (keep for stage 2; note status)
fresh_ig = [c for c in cands if c['source'] == 'igrupos' and not c['in_union']]
dup_ig = [c for c in cands if c['source'] == 'igrupos' and c['in_union']]
print(f'igrupos codes extracted: {len([c for c in cands if c["source"]=="igrupos"])} '
      f'(fresh {len(fresh_ig)}, already in union {len(dup_ig)})', flush=True)
print(f'ongrupos fresh slugs: {len(fresh_on)}', flush=True)

json.dump({'listings_fetched': len(listings) + 3, 'unique_gids': len(gid_meta),
           'detail_pages': len(todo), 'ongrupos_slugs': len(on_slugs),
           'candidates': cands},
          open(os.path.join(WAVE, 'team12-candidates.json'), 'w'), ensure_ascii=False, indent=1)
print('WROTE team12-candidates.json with', len(cands), 'candidates', flush=True)
