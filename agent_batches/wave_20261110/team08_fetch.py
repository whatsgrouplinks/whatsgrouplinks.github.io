import json, re, subprocess, html, os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

WD = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110'
SRC = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_08.json'
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

leads = json.load(open(SRC))
union = set(json.load(open('/tmp/union_codes.json')))

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,32})')

def fetch(url):
    try:
        r = subprocess.run(['curl','-sL','--max-time','25','-A',UA,url],
                           capture_output=True, text=True, timeout=35)
        return r.stdout or ''
    except Exception:
        return ''

def clean(t):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S|re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def work(item):
    url, src = item['url'], item.get('source','')
    body = fetch(url)
    entries = []
    seen = set()
    for m in CODE_RE.finditer(body):
        code = m.group(1)
        if code in seen:
            continue
        seen.add(code)
        ctx_raw = body[max(0,m.start()-1200):m.start()]
        ctx = clean(ctx_raw)
        # groupjoin adult-category flag: look for 'Adult' as a category label near the code
        adult_flag = bool(re.search(r'\bAdult\b', ctx_raw, re.I)) and 'groupjoin' in url
        entries.append({'code': code, 'context': ctx[-400:], 'adult_flag': adult_flag})
    new_leads = []
    for href in set(re.findall(r'href="([^"]+)"', body)):
        if any(k in href for k in ('whatsapp-group','category','tag/','/group/','groups','page=')) and 'chat.whatsapp.com' not in href:
            if href.startswith('/'):
                href = urljoin(url, href)
            if href.startswith('http') and href != url:
                new_leads.append(href)
    return {'url': url, 'source': src, 'http_len': len(body),
            'entries': entries, 'new_leads': sorted(set(new_leads))[:20]}

with ThreadPoolExecutor(max_workers=6) as ex:
    results = list(ex.map(work, leads))

json.dump(results, open(os.path.join(WD,'team08_fetch_raw.json'),'w'), ensure_ascii=False, indent=1)
allcodes = set()
for r in results:
    for e in r['entries']:
        allcodes.add(e['code'])
fresh = allcodes - union
print('pages fetched:', len(results))
print('pages 0 bytes:', sum(1 for r in results if r['http_len']==0))
print('pages with codes:', sum(1 for r in results if r['entries']))
print('total distinct codes:', len(allcodes))
print('fresh vs union:', len(fresh))
print('adult-flagged entries:', sum(1 for r in results for e in r['entries'] if e['adult_flag']))
for r in results:
    if r['entries']:
        print(r['url'][:90], len(r['entries']), 'fresh:', sum(1 for e in r['entries'] if e['code'] in fresh))
