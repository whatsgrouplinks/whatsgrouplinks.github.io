#!/usr/bin/env python3
"""Team24 groupizo verify-step: fetch /verify/<slug> for all 110 sitemap-12 slugs, extract invite codes."""
import json, re, subprocess, html
from concurrent.futures import ThreadPoolExecutor

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{22})')

def curl(url, timeout=45):
    try:
        r = subprocess.run(['curl','-sS','-m',str(timeout),'-L','-A',UA,url],
                           capture_output=True, timeout=timeout+10)
        return r.stdout.decode('utf-8', errors='replace') if r.returncode == 0 else ''
    except Exception as e:
        print('FETCH ERR', url, e, flush=True)
        return ''

xml = open(WAVE+'team24_raw/groupizo12.xml', errors='ignore').read()
urls = re.findall(r'<loc>(.*?)</loc>', xml)
pages = json.load(open(WAVE+'team24_raw/groupizo12_pages.json'))
meta = {p['url']: p['data'] for p in pages}

def fetch_verify(u):
    slug = u.rstrip('/').rsplit('/',1)[-1]
    t = curl(f'https://groupizo.com/verify/{slug}')
    if not t:
        return (u, None)
    codes = CODE_RE.findall(t)
    return (u, {'codes': codes, 'len': len(t)})

out = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for u, res in ex.map(fetch_verify, urls):
        out[u] = res
fetched = sum(1 for v in out.values() if v)
withcode = sum(1 for v in out.values() if v and v['codes'])
print(f'verify fetched {fetched}/{len(urls)} with-code {withcode}', flush=True)
json.dump(out, open(WAVE+'team24_raw/groupizo12_verify.json','w'), ensure_ascii=False, indent=1)
codes = {}
for u, v in out.items():
    if not v or not v['codes']:
        continue
    m = meta.get(u) or {}
    for c in v['codes']:
        codes.setdefault(c, {'url': u, 'title': m.get('title',''), 'h1': m.get('h1',''),
                            'desc': m.get('desc',''), 'lastmod': ''})
print('unique codes:', len(codes), flush=True)
for c, v in codes.items():
    print(c, '|', v['title'][:70], flush=True)
json.dump(codes, open(WAVE+'team24_raw/groupizo12_codes.json','w'), ensure_ascii=False, indent=1)
print('GROUPZO VERIFY DONE', flush=True)
