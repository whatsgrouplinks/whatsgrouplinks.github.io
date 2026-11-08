#!/usr/bin/env python3
"""team26: resolve a.elyex.com short slugs -> chat.whatsapp.com codes + og:title."""
import json, re, html, sys, time
import requests
import concurrent.futures

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"')

def resolve(slug):
    url = 'https://a.elyex.com/%s/' % slug
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=45, allow_redirects=True)
        final = r.url
        m = CODE_RE.search(final)
        code = m.group(1) if m else None
        t = TITLE_RE.search(r.text)
        title = html.unescape(t.group(1)).strip() if t else ''
        return {'slug': slug, 'status': r.status_code, 'final': final,
                'code': code, 'og_title': title, 'error': None}
    except Exception as e:
        return {'slug': slug, 'status': None, 'final': None, 'code': None,
                'og_title': '', 'error': type(e).__name__ + ': ' + str(e)[:100]}

def main():
    slugs = json.load(open(sys.argv[1]))
    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(resolve, s): s for s in slugs}
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            out.append(res)
            print(res['slug'], res['status'], res['code'], res['og_title'][:60], flush=True)
            time.sleep(0.3)
    json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
    print('saved', len(out), 'to', sys.argv[2])

if __name__ == '__main__':
    main()
