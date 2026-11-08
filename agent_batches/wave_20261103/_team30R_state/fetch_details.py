"""TEAM 30R: fetch detail pages for verified slugs lacking metadata (pills + name)."""
import json, re, sys, html as htmllib
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
BASE = 'https://groupsinvite.link'

def fetch_detail(slug):
    try:
        r = requests.get(f'{BASE}/group/link/{slug}/', headers=UA, timeout=25)
        if r.status_code != 200:
            return slug, None
        html = r.text
        pills = re.findall(
            r'href="https://groupsinvite\.link/group/(category|country|language)/([^/]+)/"[^>]*>([^<]{1,60})<',
            html)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
        title = htmllib.unescape(m.group(1)).strip() if m else ''
        cats = sorted(set(p[1] for p in pills if p[0] == 'category'))
        cns = sorted(set(p[1] for p in pills if p[0] == 'country'))
        return slug, {'title': title, 'cats': cats, 'countries': cns}
    except Exception:
        return slug, None

def main():
    verify = json.load(open('/tmp/team30r/verify.json'))
    verified_slugs = set(v['slug'] for v in verify.values() if v['status'] == 'verified')
    try:
        sm = json.load(open('/tmp/team30r/slug_meta.json'))
    except Exception:
        sm = {}
    try:
        det = json.load(open('/tmp/team30r/detail_meta.json'))
    except Exception:
        det = {}
    todo = [s for s in verified_slugs if s not in sm and s not in det]
    print(f'detail fetch todo: {len(todo)}', flush=True)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_detail, s): s for s in todo}
        n = 0
        for f in as_completed(futs):
            slug, res = f.result()
            if res:
                det[slug] = res
            n += 1
            if n % 50 == 0:
                json.dump(det, open('/tmp/team30r/detail_meta.json', 'w'))
                print(f'{n}/{len(todo)}', flush=True)
    json.dump(det, open('/tmp/team30r/detail_meta.json', 'w'))
    print(f'FINAL detail pages: {len(det)}', flush=True)

if __name__ == '__main__':
    main()
