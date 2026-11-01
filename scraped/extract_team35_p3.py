#!/usr/bin/env python3
"""TEAM 35 pass 3: generic li/p container pattern to fix fallback names."""
import re, json, time, random, html as ihtml
import urllib.request, gzip
from concurrent.futures import ThreadPoolExecutor

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.9'}

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    return re.sub(r'\s+', ' ', ihtml.unescape(s)).strip()

# generic: <li ...> ...text... <a href="chat.whatsapp.com/invite/CODE"  OR  <p ...> ...text... <a href=...
GEN_RE = re.compile(
    r'<(li|p)[^>]*>(.*?)<a[^>]*href="https?://(?:www\.)?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,26})',
    re.I | re.S)

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
    out = {}
    for tag, inner, code in GEN_RE.findall(h):
        # name = text before the <a>, after last nested tag close; strip trailing separators
        # remove any <a>...</a> already captured? inner ends right before our <a
        name = clean(inner)
        # take text before common separators at end
        name = re.sub(r'\s*[–—\-:|]\s*$', '', name).strip()
        # if name contains the link text like "Join", strip it
        name = re.sub(r'\s*(join|click here|join now)\s*$', '', name, flags=re.I).strip()
        if len(name) >= 2 and len(name) <= 90 and code not in out:
            if not re.fullmatch(r'(link|join|click|here)+', name, re.I):
                out[code] = name
    return url, list(out.items())

def main():
    urls = [l.strip() for l in open('/tmp/gl_urls.txt') if l.strip()]
    print(f'pages: {len(urls)}', flush=True)
    found = {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        for i, (u, pairs) in enumerate(ex.map(worker, urls)):
            if i % 200 == 0:
                print(f'progress {i}/{len(urls)} unique={len(found)}', flush=True)
            for code, name in pairs:
                if code not in found:
                    found[code] = name
    print(f'done: unique={len(found)}', flush=True)
    json.dump(found, open('/tmp/gl35_raw3.json', 'w'), ensure_ascii=False)
    print('saved /tmp/gl35_raw3.json', flush=True)

if __name__ == '__main__':
    main()
