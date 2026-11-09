#!/usr/bin/env python3
"""Team24 harvest: groupizo sitemap-12 (110 pages), igrupos gids>526564, ongrupos new slugs vs Nov8."""
import json, re, subprocess, html, os
from concurrent.futures import ThreadPoolExecutor

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
W8 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
union = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))

def curl(url, timeout=45):
    try:
        r = subprocess.run(['curl','-sS','-m',str(timeout),'-L','-A',UA,url],
                           capture_output=True, timeout=timeout+10)
        return r.stdout.decode('utf-8', errors='replace') if r.returncode == 0 else ''
    except Exception as e:
        print('FETCH ERR', url, e, flush=True)
        return ''

def clean(t):
    return html.unescape(re.sub(r'\s+',' ', re.sub(r'<[^>]+>',' ', t or ''))).strip()

# ---------- (a) groupizo ----------
xml = open(WAVE+'team24_raw/groupizo12.xml', errors='ignore').read()
urls = re.findall(r'<loc>(.*?)</loc>', xml)
dates = re.findall(r'<lastmod>(.*?)</lastmod>', xml)
print('groupizo urls:', len(urls), flush=True)
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{22})')
def fetch_gz(pair):
    u, d = pair
    t = curl(u)
    if not t:
        return (u, d, None)
    codes = CODE_RE.findall(t)
    title = re.search(r'<title>(.*?)</title>', t, re.S)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    return (u, d, {'codes': codes,
                   'title': clean(title.group(1)) if title else '',
                   'h1': clean(h1.group(1)) if h1 else '',
                   'desc': clean(desc.group(1)) if desc else '',
                   'len': len(t)})
gz = []
with ThreadPoolExecutor(max_workers=4) as ex:
    for res in ex.map(fetch_gz, list(zip(urls, dates))):
        gz.append(res)
fetched = sum(1 for _,_,v in gz if v)
withcode = sum(1 for _,_,v in gz if v and v['codes'])
print(f'groupizo fetched {fetched}/{len(urls)} with-code {withcode}', flush=True)
json.dump([{'url':u,'lastmod':d,'data':v} for u,d,v in gz],
          open(WAVE+'team24_raw/groupizo12_pages.json','w'), ensure_ascii=False, indent=1)
gz_codes = {}
for u,d,v in gz:
    if not v or not v['codes']:
        continue
    for c in v['codes']:
        gz_codes.setdefault(c, {'url':u,'lastmod':d,'title':v['title'],'h1':v['h1'],'desc':v['desc']})
print('groupizo unique codes:', len(gz_codes),
      'fresh vs existing:', len([c for c in gz_codes if c not in union]), flush=True)

# ---------- (c) igrupos newest ----------
ig_cards = {}
CARD_RE = re.compile(r"lnkgroup\('(\d+)'\)(.*?)(?=lnkgroup\('|\Z)", re.S)
def parse_ig(htext, label):
    n=0
    for m in CARD_RE.finditer(htext):
        gid, chunk = m.group(1), m.group(2)[:2000]
        title = re.search(r'<h3[^>]*>(.*?)</h3>', chunk, re.S)
        desc = re.search(r'<p[^>]*>(.*?)</p>', chunk, re.S)
        flag = re.search(r'banderas24/([A-Za-z0-9]+)\.png', chunk)
        rec = ig_cards.setdefault(gid, {'title':'','desc':'','flag':'','sources':[]})
        t = clean(title.group(1)) if title else ''
        ds = clean(desc.group(1)) if desc else ''
        if t and not rec['title']: rec['title']=t
        if ds and not rec['desc']: rec['desc']=ds
        if flag and not rec['flag']: rec['flag']=flag.group(1)
        rec['sources'].append(label)
        n+=1
    return n
home = open(WAVE+'team24_raw/igrupos_home.html', errors='ignore').read()
parse_ig(home, 'home')
for url, label in [('https://www.igrupos.com/whatsapp','whatsapp-p1'),
                   ('https://www.igrupos.com/whatsapp/2','whatsapp-p2')]:
    t = curl(url)
    print('igrupos', label, 'len', len(t), flush=True)
    parse_ig(t, label)
new_gids = sorted([g for g in ig_cards if int(g) > 526564], key=int)
print('igrupos cards total:', len(ig_cards), 'new gids >526564:', len(new_gids), new_gids, flush=True)
json.dump({'cards': ig_cards, 'new_gids': new_gids},
          open(WAVE+'team24_raw/igrupos_new.json','w'), ensure_ascii=False, indent=1)

def fetch_ig_detail(gid):
    t = curl(f'https://www.igrupos.com/grupo/{gid}', timeout=40)
    if not t:
        return gid, None
    codes = CODE_RE.findall(t)
    tt = re.sub(r'<script.*?</script>','', t, flags=re.S)
    tt = re.sub(r'<style.*?</style>','', tt, flags=re.S)
    tt = clean(tt)
    m = re.search(r'El grupo tiene \d+ visitas (.*?) Te recomendamos', tt)
    cat = re.search(r'Grupos de Whatsapp\s+([A-Za-z\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\xc3\xb1 ]+?)\s+Grupo para gente', tt)
    return gid, {'codes': codes, 'detail_desc': m.group(1).strip() if m else '',
                 'category_raw': cat.group(1).strip() if cat else '', 'text_head': tt[:500]}
ig_details = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for gid, res in ex.map(fetch_ig_detail, new_gids):
        ig_details[gid] = res
done = sum(1 for v in ig_details.values() if v)
wc = sum(1 for v in ig_details.values() if v and v['codes'])
print(f'igrupos details fetched {done}/{len(new_gids)} with-code {wc}', flush=True)
json.dump(ig_details, open(WAVE+'team24_raw/igrupos_details.json','w'), ensure_ascii=False, indent=1)

# ---------- (b) ongrupos new slugs ----------
t12 = json.load(open(W8+'team12-candidates.json'))
old_on = set(x['code'] for x in t12['candidates'] if x['source']=='ongrupos')
old_on |= set(x['invite'].split('/')[-1] for x in json.load(open(W8+'team12-igrupos-ongrupos.json')))
print('ongrupos slugs known from Nov8:', len(old_on), flush=True)
catxml = curl('https://ongrupos.com/category.xml')
cat_urls = re.findall(r'<loc>(https://ongrupos\.com/categoria/[^<]+)</loc>', catxml)
print('ongrupos categories:', len(cat_urls), flush=True)
SLUG_RE = re.compile(r'ongrupos\.com/grupo/([A-Za-z0-9_-]{22})')
on_slugs = {}
def parse_on(htext, label):
    n=0
    for m in SLUG_RE.finditer(htext):
        on_slugs.setdefault(m.group(1), []).append(label)
        n+=1
    return n
parse_on(open(WAVE+'team24_raw/ongrupos_home.html', errors='ignore').read(), 'home')
for cu in cat_urls:
    t = curl(cu)
    c = parse_on(t, cu.rsplit('/',1)[-1])
    print(f'ongrupos {cu.rsplit("/",1)[-1]}: {c} slugs, unique now {len(on_slugs)}', flush=True)
new_on = [s for s in on_slugs if s not in old_on]
fresh_on = [s for s in new_on if s not in union]
print(f'ongrupos unique slugs: {len(on_slugs)}; new vs Nov8: {len(new_on)}; fresh vs existing: {len(fresh_on)}', flush=True)
print('new on slugs:', new_on, flush=True)
json.dump({'slugs': on_slugs, 'new': new_on, 'fresh': fresh_on, 'cat_urls': cat_urls},
          open(WAVE+'team24_raw/ongrupos_new.json','w'), ensure_ascii=False, indent=1)
print('HARVEST DONE', flush=True)
