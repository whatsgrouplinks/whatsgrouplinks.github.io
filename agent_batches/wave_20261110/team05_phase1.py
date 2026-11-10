import json, re, html, time, os, requests
from urllib.parse import urljoin, urlparse

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
INP = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_05.json"
CKPT = f"{WD}/team05_phase1_ckpt.jsonl"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

leads = json.load(open(INP))
done = {}
if os.path.exists(CKPT):
    for line in open(CKPT):
        try:
            r = json.loads(line)
            done[r['url']] = r
        except Exception:
            pass
print("input", len(leads), "already done", len(done), flush=True)

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})')
TAG_RE = re.compile(r'<[^>]+>')

def clean_text(s):
    s = html.unescape(TAG_RE.sub(' ', s))
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract(html_text, page_url):
    items = {}
    for pat in (r'<li\b[^>]*>(.*?)</li>', r'<tr\b[^>]*>(.*?)</tr>'):
        for m in re.finditer(pat, html_text, re.S | re.I):
            chunk = m.group(1)
            codes = CODE_RE.findall(chunk)
            if not codes:
                continue
            txt = clean_text(chunk)
            txt = re.sub(r'\b(Join|Join Now|Join Group|Click Here|WhatsApp Group Link)\b', '', txt, flags=re.I)
            txt = re.sub(r'\s+', ' ', txt).strip(' -–—|•·:').strip()
            name = txt[:100].strip()
            for c in codes:
                if c == 'invite':
                    continue
                if c not in items or (len(name) > len(items[c])):
                    items[c] = name
    for m in re.finditer(r'<a\b[^>]*href=["\']https?://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})["\'][^>]*>(.*?)</a>', html_text, re.S | re.I):
        code = m.group(1)
        if code in items and items[code]:
            continue
        start = max(0, m.start() - 400)
        before = clean_text(html_text[start:m.start()])
        cand = before.split('>')[-1].strip()
        cand = re.sub(r'\s+', ' ', cand).strip(' -–—|•·:')[:100]
        if code not in items:
            items[code] = cand
        elif not items[code] and cand:
            items[code] = cand
    base = urlparse(page_url)
    disc = set()
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html_text, re.I):
        href = html.unescape(m.group(1))
        if 'chat.whatsapp.com' in href or 'whatsapp.com/channel' in href:
            continue
        full = urljoin(page_url, href)
        p = urlparse(full)
        if p.netloc != base.netloc:
            continue
        if p.path.endswith(('.webp', '.jpg', '.png', '.css', '.js', '.xml')):
            continue
        low = p.path.lower()
        if any(k in low for k in ('whatsapp-group', 'whatsapp-group-link', '/category/', '/whatsapp/', '/group/country', '/group/')):
            disc.add(full.rstrip('/'))
    return items, sorted(disc)

from concurrent.futures import ThreadPoolExecutor
import threading
lock = threading.Lock()
last = [0.0]

def fetch(entry):
    url = entry['url']
    if url in done:
        return done[url]
    with lock:
        dt = time.time() - last[0]
        if dt < 0.25:
            time.sleep(0.25 - dt)
        last[0] = time.time()
    try:
        r = requests.get(url, headers=UA, timeout=25)
        status = r.status_code
        text = r.text if status == 200 else ''
    except Exception as e:
        res = {'url': url, 'source': entry.get('source'), 'status': 0, 'error': str(e)[:120], 'items': {}, 'discovered': []}
        with lock:
            with open(CKPT, 'a') as f:
                f.write(json.dumps(res) + '\n')
        return res
    if status != 200:
        res = {'url': url, 'source': entry.get('source'), 'status': status, 'error': f'HTTP {status}', 'items': {}, 'discovered': []}
    else:
        items, disc = extract(text, url)
        res = {'url': url, 'source': entry.get('source'), 'status': status, 'items': items, 'discovered': disc}
    with lock:
        with open(CKPT, 'a') as f:
            f.write(json.dumps(res) + '\n')
    return res

todo = [e for e in leads if e['url'] not in done]
print("todo", len(todo), flush=True)
results = list(done.values())
with ThreadPoolExecutor(max_workers=3) as ex:
    for i, res in enumerate(ex.map(fetch, todo)):
        results.append(res)
        if (i + 1) % 20 == 0:
            print(f"fetched {i+1}/{len(todo)}", flush=True)

ok = sum(1 for r in results if r['status'] == 200)
tot = sum(len(r['items']) for r in results)
print("pages 200:", ok, "of", len(results), "raw code occurrences:", tot, flush=True)
json.dump(results, open(f"{WD}/team05_phase1_raw.json", "w"), indent=1)
seen = {}
for r in results:
    for code, name in r['items'].items():
        if code not in seen:
            seen[code] = {'code': code, 'dir_name': name, 'page': r['url'], 'source': r.get('source')}
print("unique codes:", len(seen), flush=True)
json.dump(list(seen.values()), open(f"{WD}/team05_phase1_codes.json", "w"), indent=1)
input_urls = {e['url'].rstrip('/') for e in leads}
disc_all = set()
for r in results:
    disc_all.update(r['discovered'])
disc_all = sorted(u for u in disc_all if u not in input_urls)
print("discovered new listing urls:", len(disc_all), flush=True)
json.dump(disc_all, open(f"{WD}/team05_phase1_discovered.json", "w"), indent=1)
fails = [(r['url'], r['status'], r.get('error')) for r in results if r['status'] != 200]
print("failed pages:", len(fails), flush=True)
for f in fails:
    print(f, flush=True)
