#!/usr/bin/env python3
"""TEAM 1 (parallel): Scrape REMAINING groupizo.com groups, dedupe vs groups.json.
Saves NEW groups to scraped/team1-groupizo.json. Format: name, category, description, image, invite, country."""
import re, json, html, time, os, threading
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUPS_JSON = os.path.join(BASE, 'groups.json')
URLS_FILE = os.path.join(BASE, 'scraped', 'team1-all-urls.txt')
OUT_PATH = os.path.join(BASE, 'scraped', 'team1-groupizo.json')
PROGRESS = os.path.join(BASE, 'scraped', 'team1-progress.json')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
WORKERS = 3
DELAY = 1.0  # per-worker politeness delay (gentler after rate-limiting)
MAX_RETRIES = 3

def safe_url(url):
    from urllib.parse import quote, urlsplit, urlunsplit
    parts = urlsplit(url)
    path = quote(parts.path, safe='/%')
    return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))

def fetch(url, timeout=25):
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(safe_url(url), headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 * (attempt + 1))  # backoff
    return None

def parse_group_page(content):
    d = {'name': '', 'category': '', 'description': '', 'image': '', 'invite': '', 'country': ''}
    m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
    if m:
        d['name'] = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)).strip())
    m = re.search(r'<meta name="description" content="([^"]+)"', content)
    if m:
        desc = html.unescape(m.group(1))
        d['description'] = re.sub(r'\s*on Groupizo\.?', '', desc).strip()
        cm = re.search(r'listed under ([\w &]+)', desc)
        if cm:
            d['category'] = cm.group(1).strip()
    imgs = re.findall(r'<img[^>]+src="(https://pps\.whatsapp\.net/[^"]+)"[^>]*alt="([^"]*)"', content)
    if not imgs:
        imgs = re.findall(r'<img[^>]+alt="([^"]*)"[^>]+src="(https://pps\.whatsapp\.net/[^"]+)"', content)
        imgs = [(s, a) for a, s in imgs]
    for src, alt in imgs:
        if 'logo' not in alt.lower() and len(alt) > 3:
            d['image'] = src
            break
    m = re.search(r"window\.location\.href='(/verify/[^']+)'", content)
    verify = 'https://groupizo.com' + m.group(1) if m else ''
    m = re.search(r'flagcdn\.com/w40/([a-z]{2})\.png', content)
    if m:
        d['country'] = m.group(1).upper()
    return d, verify

def get_invite(verify_url):
    content = fetch(verify_url)
    if not content:
        return ''
    m = re.search(r'https://chat\.whatsapp\.com/[A-Za-z0-9]+', content)
    return m.group(0) if m else ''

def code_of(invite):
    return invite.strip().split('/')[-1].split('?')[0] if invite else ''

lock = threading.Lock()
results = []
done_urls = set()
existing_codes = set()
stats = {'new': 0, 'dup': 0, 'fail': 0, 'done': 0}

def checkpoint():
    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, ensure_ascii=False)
    with open(PROGRESS, 'w') as f:
        json.dump({'done_urls': sorted(done_urls)}, f)

def process_url(url):
    page = fetch(url)
    time.sleep(DELAY)
    if not page:
        # fetch failed (rate-limit/timeout) — do NOT mark done, will retry next run
        with lock:
            stats['fail'] += 1
            stats['done'] += 1
            n = stats['done']
        if n % 100 == 0:
            checkpoint()
            print(f"  [{n}] new={stats['new']} dup={stats['dup']} fail={stats['fail']}", flush=True)
        return
    with lock:
        done_urls.add(url)
        stats['done'] += 1
        n = stats['done']
    if n % 100 == 0:
        checkpoint()
        print(f"  [{n}] new={stats['new']} dup={stats['dup']} fail={stats['fail']}", flush=True)
    if not page:
        with lock:
            stats['fail'] += 1
        return
    g, verify = parse_group_page(page)
    if not g['name'] or not verify:
        with lock:
            stats['fail'] += 1
        return
    g['invite'] = get_invite(verify)
    time.sleep(DELAY)
    if not g['invite']:
        with lock:
            stats['fail'] += 1
        return
    c = code_of(g['invite'])
    with lock:
        if c in existing_codes:
            stats['dup'] += 1
            return
        existing_codes.add(c)
        results.append(g)
        stats['new'] += 1

def main():
    global results, done_urls, existing_codes
    with open(GROUPS_JSON) as f:
        existing = json.load(f)
    existing_codes = {code_of(g.get('invite', '')) for g in existing}
    existing_codes.discard('')
    with open(URLS_FILE) as f:
        urls = [l.strip() for l in f if l.strip()]
    try:
        with open(OUT_PATH) as f:
            results = json.load(f)
        with open(PROGRESS) as f:
            done_urls = set(json.load(f).get('done_urls', []))
        for g in results:
            existing_codes.add(code_of(g.get('invite', '')))
        print(f"Resuming: {len(results)} saved, {len(done_urls)} urls processed", flush=True)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    pending = [u for u in urls if u not in done_urls]
    print(f"Existing: {len(existing)}, pending URLs: {len(pending)}, workers: {WORKERS}", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(process_url, pending))

    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, ensure_ascii=False)
    with open(PROGRESS, 'w') as f:
        json.dump({'done_urls': sorted(done_urls)}, f)
    el = round(time.time() - t0, 1)
    print(f"DONE in {el}s: new={stats['new']} dup={stats['dup']} fail={stats['fail']} total_saved={len(results)}", flush=True)

if __name__ == '__main__':
    main()
