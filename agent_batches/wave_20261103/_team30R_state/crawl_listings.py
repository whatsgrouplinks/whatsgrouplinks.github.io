"""TEAM 30R: crawl category/country/language listing pages -> slug metadata map."""
import json, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
BASE = 'https://groupsinvite.link'

def fetch_meta(url, kind, label):
    try:
        r = requests.get(url, headers=UA, timeout=25)
        if r.status_code != 200:
            return url, None
        html = r.text
        cards = re.findall(r'href="https://groupsinvite\.link/group/link/([A-Za-z0-9]{20,24})/"', html)
        # titles: find card title near link
        pairs = re.findall(
            r'href="https://groupsinvite\.link/group/link/([A-Za-z0-9]{20,24})/"[^>]*>.*?<[^>]*class="[^"]*title[^"]*"[^>]*>([^<]{2,120})<',
            html, re.S | re.I)
        return url, {'slugs': sorted(set(cards)), 'titles': {s: t.strip() for s, t in pairs},
                     'kind': kind, 'label': label}
    except Exception as e:
        return url, None

def main():
    urls = json.load(open('/tmp/team30r/sitemap_urls.json'))
    jobs = []
    for u in sorted(set(urls)):
        m = re.match(r'^https://groupsinvite\.link/group/(category|country|language)/([^/]+)/$', u)
        if m:
            jobs.append((u, m.group(1), m.group(2)))
    print(f'listing pages: {len(jobs)}', flush=True)
    meta = {}
    done_pages = set()
    try:
        saved = json.load(open('/tmp/team30r/listing_meta.json'))
        meta = saved.get('meta', {})
        done_pages = set(saved.get('done', []))
        print(f'resuming: {len(done_pages)} done', flush=True)
    except Exception:
        pass
    todo = [j for j in jobs if j[0] not in done_pages]
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(fetch_meta, u, k, l): u for u, k, l in todo}
        n = 0
        for f in as_completed(futs):
            url, res = f.result()
            if res:
                meta[url] = res
            done_pages.add(url)
            n += 1
            if n % 20 == 0:
                json.dump({'meta': meta, 'done': sorted(done_pages)}, open('/tmp/team30r/listing_meta.json', 'w'))
                print(f'{n}/{len(todo)} listing pages', flush=True)
    json.dump({'meta': meta, 'done': sorted(done_pages)}, open('/tmp/team30r/listing_meta.json', 'w'))
    # build slug -> labels map
    slugmap = {}
    for url, res in meta.items():
        for s in res['slugs']:
            e = slugmap.setdefault(s, {'titles': [], 'cats': [], 'countries': [], 'langs': []})
            for t in res['titles'].get(s, '').strip(), :
                if t and t not in e['titles']:
                    e['titles'].append(t)
            if res['kind'] == 'category' and res['label'] not in e['cats']:
                e['cats'].append(res['label'])
            if res['kind'] == 'country' and res['label'] not in e['countries']:
                e['countries'].append(res['label'])
            if res['kind'] == 'language' and res['label'] not in e['langs']:
                e['langs'].append(res['label'])
    json.dump(slugmap, open('/tmp/team30r/slug_meta.json', 'w'))
    print(f'slugs with metadata: {len(slugmap)}', flush=True)

if __name__ == '__main__':
    main()
