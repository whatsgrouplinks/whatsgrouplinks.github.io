import json, re, subprocess, html, time
from concurrent.futures import ThreadPoolExecutor

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{10,30})')

s = open(WAVE + 'team10_sitemap.xml', encoding='utf-8', errors='ignore').read()
entries = re.findall(r'<url>\s*<loc>([^<]+)</loc>\s*<lastmod>([^<]*)</lastmod>', s)
groups = [(u, m) for u, m in entries if '/grupo/' in u]
print('total group urls in sitemap:', len(groups))

START, END = 1500, 1900  # resume offset ~1500, walk older (sitemap order = lastmod desc)
batch = groups[START:END]
print('batch:', START, '->', END - 1, 'count', len(batch),
      'lastmod', batch[0][1], 'to', batch[-1][1])

def fetch(url):
    try:
        r = subprocess.run(['curl', '-sL', '--max-time', '30', '-A', UA, url],
                           capture_output=True, text=True, timeout=40)
        return r.stdout or ''
    except Exception:
        return ''

def clean(t):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()

def work(item):
    idx, (url, lastmod) = item
    body = fetch(url)
    if not body:
        return {'idx': idx, 'url': url, 'lastmod': lastmod, 'err': 'fetch-fail', 'codes': []}
    title = re.search(r'<title>([^<]*)</title>', body)
    title = html.unescape(title.group(1)).strip() if title else ''
    md = re.search(r'<meta name="description" content="([^"]*)"', body)
    desc = html.unescape(md.group(1)).strip() if md else ''
    codes = sorted(set(CODE_RE.findall(body)))
    return {'idx': idx, 'url': url, 'lastmod': lastmod, 'title': title,
            'desc': desc, 'codes': codes, 'http_len': len(body)}

with ThreadPoolExecutor(max_workers=6) as ex:
    results = list(ex.map(work, list(enumerate(batch, start=START))))

json.dump(results, open(WAVE + 'team10_raw.json', 'w'), ensure_ascii=False, indent=1)
ncode = sum(len(r['codes']) for r in results)
print('pages fetched:', len(results), '| fetch-fail:', sum(1 for r in results if r.get('err')),
      '| pages with codes:', sum(1 for r in results if r['codes']), '| total codes:', ncode)
print('first page:', results[0]['url'], results[0]['title'][:80], results[0]['codes'])
print('last page:', results[-1]['url'], results[-1]['title'][:80], results[-1]['codes'])
