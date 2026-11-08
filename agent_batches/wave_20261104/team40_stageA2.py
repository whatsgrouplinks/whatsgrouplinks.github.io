#!/usr/bin/env python3
"""Team40 stage A2: fast extraction with tight timeouts, no per-group API storm."""
import re, os, json, html, requests
from concurrent.futures import ThreadPoolExecutor

WD = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?!invite/)([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')
T = (8, 25)

union = set(json.load(open(WD + '/dedupe_union.json')))
s = requests.Session(); s.headers.update(UA)
seen = {}
def add(code, name, src):
    if code in union or code in seen:
        return
    seen[code] = {'name': name.strip(), 'src': src}

def name_near(t, pos):
    ctx = t[max(0, pos-700):pos]
    items = re.findall(r'<li[^>]*>(.*?)<\s*a[^>]*$', ctx, re.S)
    if items:
        name = html.unescape(re.sub(r'<[^>]+>', '', items[-1])).strip()
        return re.sub(r'\s*[–—-]\s*Join\s*$', '', name, flags=re.I).strip()
    t2 = re.findall(r'>([^<>]{2,100})$', ctx)
    return html.unescape(t2[-1]).strip() if t2 else ''

# 1) whtsagrouplinks.com gaming pages
for url in ['https://www.whtsagrouplinks.com/',
            'https://www.whtsagrouplinks.com/gaming-whatsapp-group-links/',
            'https://www.whtsagrouplinks.com/pubg-whatsapp-group-links/',
            'https://www.whtsagrouplinks.com/free-fire-whatsapp-groups-links/']:
    try:
        r = s.get(url, timeout=T)
        print('WHTSA', (url.split('whtsagrouplinks.com/')[1] or 'home'), r.status_code, len(r.content), flush=True)
        if r.status_code == 200:
            for m in CODE_RE.finditer(r.text):
                add(m.group(1), name_near(r.text, m.start()), url)
    except Exception as e:
        print('WHTSA FAIL', url, str(e)[:100], flush=True)

# 2) groupjoin.link: direct codes from listing HTML + API for group ids (bounded)
gjl_ids = {}
for tag in ['-gaming-', 'gaming', 'GAMING', 'gamer']:
    for page in range(1, 6):
        url = f'https://www.groupjoin.link/tag/{tag}/?page={page}&limit=20&safeSearch=blur'
        try:
            r = s.get(url, timeout=T, allow_redirects=True)
            if r.status_code != 200:
                print('GJL', tag, page, 'HTTP', r.status_code, flush=True); break
            ids = list(dict.fromkeys(re.findall(r'/group/([A-Za-z0-9]{20,24})', r.text)))
            ncode = len(CODE_RE.findall(r.text))
            print('GJL', tag, 'p', page, 'ids:', len(ids), 'direct codes:', ncode, flush=True)
            if not ids:
                break
            for m in CODE_RE.finditer(r.text):
                add(m.group(1), name_near(r.text, m.start()), url)
            for gid in ids:
                gjl_ids.setdefault(gid, url)
        except Exception as e:
            print('GJL FAIL', tag, page, str(e)[:90], flush=True); break

print('API resolve for', len(gjl_ids), 'group ids', flush=True)
def resolve(item):
    gid, src = item
    try:
        r = s.get(f'https://api.groupjoin.link/groups/{gid}', timeout=T,
                  headers={**UA, 'Accept': 'application/json', 'Referer': 'https://www.groupjoin.link/'})
        if r.status_code == 200:
            d = r.json()
            inv = d.get('invite') or d.get('inviteLink') or d.get('link') or ''
            nm = d.get('name') or d.get('title') or ''
            mc = CODE_RE.search(inv or '')
            return (mc.group(1), nm, f'gjl:{gid}') if mc else None
    except Exception:
        pass
    return None

with ThreadPoolExecutor(max_workers=8) as ex:
    for res in ex.map(resolve, list(gjl_ids.items())):
        if res:
            add(*res)

json.dump(seen, open(WD + '/team40_stageA.json', 'w'), ensure_ascii=False, indent=1)
print('CANDIDATES:', len(seen), flush=True)
for c, i in list(seen.items()):
    print(' -', c, '|', (i['name'] or '(noname)')[:55], '|', i['src'][:55], flush=True)
