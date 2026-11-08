#!/usr/bin/env python3
"""Team40 stage A: extract fresh gaming codes (fresh short-lived process)."""
import re, os, json, html, requests

WD = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?!invite/)([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')

union = set(json.load(open(WD + '/dedupe_union.json')))
s = requests.Session(); s.headers.update(UA)
seen = {}
def add(code, name, src):
    if code in union or code in seen:
        return
    seen[code] = {'name': name.strip(), 'src': src}

# 1) whtsagrouplinks.com gaming pages
whtsa_pages = [
    'https://www.whtsagrouplinks.com/',
    'https://www.whtsagrouplinks.com/gaming-whatsapp-group-links/',
    'https://www.whtsagrouplinks.com/pubg-whatsapp-group-links/',
    'https://www.whtsagrouplinks.com/free-fire-whatsapp-groups-links/',
]
for url in whtsa_pages:
    try:
        r = s.get(url, timeout=60)
        print('WHTSA', (url.split('whtsagrouplinks.com/')[1] or 'home'), r.status_code, len(r.content), flush=True)
        if r.status_code != 200:
            continue
        t = r.text
        for m in CODE_RE.finditer(t):
            code = m.group(1)
            ctx = t[max(0, m.start()-700):m.start()]
            name = ''
            items = re.findall(r'<li[^>]*>(.*?)<\s*a[^>]*$', ctx, re.S)
            if items:
                name = html.unescape(re.sub(r'<[^>]+>', '', items[-1])).strip()
                name = re.sub(r'\s*[–—-]\s*Join\s*$', '', name, flags=re.I).strip()
            if not name:
                t2 = re.findall(r'>([^<>]{2,100})$', ctx)
                name = html.unescape(t2[-1]).strip() if t2 else ''
            add(code, name, url)
    except Exception as e:
        print('WHTSA FAIL', url, str(e)[:110], flush=True)

# 2) groupjoin.link gaming tag pages
for tag in ['-gaming-', 'gaming', 'GAMING', 'gamer']:
    page = 1
    while page <= 60:
        url = f'https://www.groupjoin.link/tag/{tag}/?page={page}&limit=20&safeSearch=blur'
        try:
            r = s.get(url, timeout=60, allow_redirects=True)
            if r.status_code != 200:
                print('GJL', tag, page, 'HTTP', r.status_code, flush=True); break
            ids = list(dict.fromkeys(re.findall(r'/group/([A-Za-z0-9]{20,24})', r.text)))
            # also grab card titles next to each id
            cards = {}
            for cm in re.finditer(r'/group/([A-Za-z0-9]{20,24})', r.text):
                pass
            print('GJL', tag, 'p', page, 'ids:', len(ids), flush=True)
            if not ids:
                break
            for gid in ids:
                try:
                    ar = s.get(f'https://api.groupjoin.link/groups/{gid}', timeout=30,
                               headers={**UA, 'Accept': 'application/json', 'Referer': 'https://www.groupjoin.link/'})
                    if ar.status_code == 200:
                        d = ar.json()
                        inv = d.get('invite') or d.get('inviteLink') or d.get('link') or ''
                        nm = d.get('name') or d.get('title') or ''
                        cat = d.get('category') or d.get('tags') or ''
                        mc = CODE_RE.search(inv or '')
                        if mc:
                            seen.setdefault(mc.group(1), None)
                            add(mc.group(1), nm, f'gjl:{gid}')
                except Exception:
                    pass
            page += 1
        except Exception as e:
            print('GJL FAIL', tag, page, str(e)[:90], flush=True); break

# 3) groupjoin.link /category/gaming
try:
    r = s.get('https://www.groupjoin.link/category/gaming', timeout=60)
    print('GJL category/gaming', r.status_code, len(r.content), flush=True)
    if r.status_code == 200:
        for m in CODE_RE.finditer(r.text):
            ctx = r.text[max(0, m.start()-500):m.start()]
            nm = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', ctx, re.S)
            name = html.unescape(re.sub(r'<[^>]+>', '', nm[-1])).strip() if nm else ''
            add(m.group(1), name, 'gjl:category/gaming')
except Exception as e:
    print('GJL cat FAIL', str(e)[:90], flush=True)

json.dump(seen, open(WD + '/team40_stageA.json', 'w'), ensure_ascii=False, indent=1)
print('CANDIDATES:', len(seen), flush=True)
for c, i in list(seen.items())[:40]:
    print(' -', c, '|', (i['name'] or '(noname)')[:60], '|', i['src'][:60], flush=True)
