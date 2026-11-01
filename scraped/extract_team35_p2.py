#!/usr/bin/env python3
"""TEAM 35 pass 2: re-scrape grouplink.com.in pages with table+li patterns, fix fallback names."""
import re, json, time, random, html as ihtml
import urllib.request, gzip
from concurrent.futures import ThreadPoolExecutor

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.9'}

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    return re.sub(r'\s+', ' ', ihtml.unescape(s)).strip()

ROW_RE = re.compile(
    r'<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>\s*<a[^>]*href="https?://(?:www\.)?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,26})',
    re.I | re.S)
# <li>Group Name – <a href="https://chat.whatsapp.com/invite/CODE"
LI_RE = re.compile(
    r'<li[^>]*>\s*(.*?)\s*(?:&ndash;|&#8211;|–|-|:)\s*<a[^>]*href="https?://(?:www\.)?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,26})',
    re.I | re.S)
LINK_RE = re.compile(r'https?://(?:www\.)?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,26})', re.I)
TITLE_RE = re.compile(r'<title>(.*?)</title>', re.I | re.S)

CAT_MAP = [
    ('study', 'Education'), ('education', 'Education'), ('css', 'Education'),
    ('mcqs', 'Education'), ('exam', 'Education'), ('student', 'Education'),
    ('ielts', 'Education'), ('job', 'Jobs'), ('career', 'Jobs'), ('employment', 'Jobs'),
    ('earning', 'Online Earning'), ('freelanc', 'Online Earning'), ('business', 'Business'),
    ('buy', 'Buy Sell'), ('sell', 'Buy Sell'), ('shop', 'Buy Sell'),
    ('news', 'News'), ('cricket', 'Sports'), ('football', 'Sports'), ('sport', 'Sports'),
    ('game', 'Gaming'), ('gaming', 'Gaming'), ('free fire', 'Gaming'), ('pubg', 'Gaming'),
    ('movie', 'Entertainment'), ('film', 'Entertainment'), ('drama', 'Entertainment'),
    ('funny', 'Entertainment'), ('joke', 'Entertainment'), ('meme', 'Entertainment'),
    ('music', 'Entertainment'), ('song', 'Entertainment'), ('poetry', 'Entertainment'),
    ('shayari', 'Entertainment'), ('islam', 'Islamic'), ('quran', 'Islamic'), ('naat', 'Islamic'),
    ('health', 'Health'), ('doctor', 'Health'), ('fitness', 'Health'),
    ('tech', 'Technology'), ('mobile', 'Technology'), ('computer', 'Technology'),
    ('girl', 'Friendship'), ('friend', 'Friendship'), ('boy', 'Friendship'),
    ('love', 'Friendship'), ('romantic', 'Friendship'), ('couple', 'Friendship'),
    ('finance', 'Finance'), ('forex', 'Finance'), ('crypto', 'Finance'), ('trade', 'Finance'),
]
def category_from_title(title):
    t = title.lower()
    for kw, cat in CAT_MAP:
        if kw in t:
            return cat
    return 'Community & Social'

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(0.6, 1.6))
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                if r.info().get('Content-Encoding') == 'gzip':
                    try: raw = gzip.decompress(raw)
                    except Exception: pass
                return raw.decode('utf-8', 'ignore')
        except Exception:
            time.sleep(3 * (attempt + 1))
    return None

def worker(url):
    h = fetch(url)
    if not h:
        return url, []
    title = clean(TITLE_RE.search(h).group(1)) if TITLE_RE.search(h) else ''
    cat = category_from_title(title)
    out = {}
    for name_html, code in ROW_RE.findall(h):
        name = clean(name_html)[:90]
        if len(name) >= 2:
            out[code] = (name, cat)
    for name_html, code in LI_RE.findall(h):
        if code in out:
            continue
        name = clean(name_html)[:90]
        if len(name) >= 2 and not re.fullmatch(r'(join|link|click)+', name, re.I):
            out[code] = (name, cat)
    return url, list(out.items())

def main():
    urls = [l.strip() for l in open('/tmp/gl_urls.txt') if l.strip()]
    print(f'pages: {len(urls)}', flush=True)
    found = {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        for i, (u, pairs) in enumerate(ex.map(worker, urls)):
            if i % 200 == 0:
                print(f'progress {i}/{len(urls)} unique={len(found)}', flush=True)
            for code, (name, cat) in pairs:
                if code not in found or found[code][0].startswith('WhatsApp Group '):
                    found[code] = (name, cat)
    print(f'done: unique={len(found)}', flush=True)
    json.dump({c: {'name': n, 'category': cat} for c, (n, cat) in found.items()},
              open('/tmp/gl35_raw2.json', 'w'), ensure_ascii=False)
    print('saved /tmp/gl35_raw2.json', flush=True)

if __name__ == '__main__':
    main()
