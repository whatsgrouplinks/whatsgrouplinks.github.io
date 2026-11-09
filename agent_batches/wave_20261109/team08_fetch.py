import json, re, subprocess, os, html, time
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
leads = json.load(open('leads_slice_08.json'))
existing = set(json.load(open('../../.existing_codes.json')))
pre = json.load(open('team08_codes.json'))

CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{10,30})')

def fetch(url):
    try:
        r = subprocess.run(['curl','-sL','--max-time','25','-A',UA,url],
                           capture_output=True, text=True, timeout=35)
        return r.stdout or ''
    except Exception as e:
        return ''

def clean(t):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S|re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

results = []
def work(item):
    url, src = item['url'], item.get('source','')
    body = fetch(url)
    codes = CODE_RE.findall(body)
    # also try anchor text context: find name near code in raw html
    entries = []
    for m in CODE_RE.finditer(body):
        code = m.group(1)
        # context window 600 chars before
        ctx = clean(body[max(0,m.start()-800):m.start()])
        entries.append({'code': code, 'context': ctx[-300:]})
    new_leads = []
    # discover other directory/listing urls on same domain
    for href in set(re.findall(r'href="([^"]+)"', body)):
        if any(k in href for k in ('whatsapp-group','category','tag/','/group/','groups','page=')) and 'chat.whatsapp.com' not in href:
            if href.startswith('/'):
                from urllib.parse import urljoin
                href = urljoin(url, href)
            if href.startswith('http') and href != url:
                new_leads.append(href)
    return {'url': url, 'source': src, 'http_len': len(body),
            'codes': sorted(set(codes)), 'entries': entries,
            'new_leads': sorted(set(new_leads))[:20]}

with ThreadPoolExecutor(max_workers=6) as ex:
    results = list(ex.map(work, leads))

json.dump(results, open('team08_fetch_raw.json','w'), ensure_ascii=False, indent=1)
allcodes = set()
for r in results:
    allcodes.update(r['codes'])
print('pages fetched:', len(results))
print('pages with 0 bytes:', sum(1 for r in results if r['http_len']==0))
print('pages with codes:', sum(1 for r in results if r['codes']))
print('total codes from listings:', len(allcodes))
print('fresh vs existing:', len(allcodes - existing))
print('pre-assigned codes not in listings:', len(set(pre) - allcodes))
print('listing codes not in pre-assigned:', len(allcodes - set(pre)))
print('union fresh:', len((allcodes | set(pre)) - existing))
# per-page counts
for r in results:
    if r['codes']:
        print(r['url'][:80], len(r['codes']))
