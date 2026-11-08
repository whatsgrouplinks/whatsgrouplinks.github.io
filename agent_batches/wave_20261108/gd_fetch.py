#!/usr/bin/env python3
"""Team09 wave20261108: fetch groupda.com listing-post pages via Wayback
(live site is Cloudflare-403 to curl, browser and reader proxy) and extract
(name, invite-code) candidates. No live groupda.com fetch is attempted here.
"""
import json, os, re, subprocess, time, html as ihtml

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261108')
OUTDIR = os.path.join(WAVE, 'team09_gd_pages')
os.makedirs(OUTDIR, exist_ok=True)

# (post url, canonical category, country hint)
POSTS = [
    ('https://groupda.com/business/real-estate-whatsapp-group-link-pakistan-join-2022/', 'Real Estate', 'PK'),
    ('https://groupda.com/chat/mobile-legends-whatsapp-group-link-join-2022/', 'Gaming', 'International'),
    ('https://groupda.com/jobs/it-jobs-whatsapp-group-link-join-2022/', 'Jobs', 'IN'),
    ('https://groupda.com/entertainment/sindhi-tiktok-whatsapp-group-link-join-2022/', 'Entertainment', 'PK'),
    ('https://groupda.com/games/rummy-whatsapp-group-link-join-2022/', 'Gaming', 'IN'),
    ('https://groupda.com/sports/badminton-whatsapp-group-link-join-2022/', 'Sports', 'IN'),
    ('https://groupda.com/jobs/engineering-jobs-whatsapp-group-link-join-2022/', 'Jobs', 'IN'),
    ('https://groupda.com/education/python-whatsapp-group-link-join-2022/', 'Technology', 'IN'),
    ('https://groupda.com/news-2/sindhi-news-whatsapp-group-link-join-2022/', 'News', 'PK'),
    ('https://groupda.com/spiritual/quran-tafseer-whatsapp-group-links-2022/', 'Islamic', 'International'),
    ('https://groupda.com/buysell/meesho-reseller-whatsapp-group-link-join-2022/', 'Buy & Sell', 'IN'),
    ('https://groupda.com/spiritual/best-islamic-whatsapp-group-link-2022/', 'Islamic', 'International'),
    ('https://groupda.com/jobs/rajasthan-job-whatsapp-group-link-join-2022/', 'Jobs', 'IN'),
    ('https://groupda.com/education/diploma-civil-whatsapp-group-link-join-2022/', 'Education', 'IN'),
    ('https://groupda.com/chat/graphic-design-whatsapp-group-links-2022/', 'Freelance', 'International'),
    ('https://groupda.com/business/mumbai-investors-whatsapp-group-links-2022/', 'Finance', 'IN'),
]

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def curl(url, outpath, max_time=50):
    r = subprocess.run(['curl', '-sS', '-L', '-A', UA, '--max-time', str(max_time),
                        '-o', outpath, '-w', '%{http_code}', url],
                       capture_output=True, text=True)
    return r.stdout.strip()

def latest_snapshot(post_url):
    cdx = ('https://web.archive.org/cdx/search/cdx?url=' + post_url +
           '&output=json&filter=statuscode:200&limit=100')
    tmp = '/tmp/gd_cdx.json'
    code = curl(cdx, tmp, 40)
    try:
        rows = json.load(open(tmp))
    except Exception as e:
        print('  CDX parse fail', code, e); return None
    if len(rows) < 2:
        print('  CDX: no snapshots'); return None
    rows = rows[1:]
    rows.sort(key=lambda r: r[1])
    return rows[-1][1]  # latest timestamp

def fetch_post(post_url, category, country):
    slug = re.sub(r'[^a-z0-9]+', '_', post_url.rstrip('/').split('/')[-1])[:60]
    html_path = os.path.join(OUTDIR, slug + '.html')
    if os.path.exists(html_path) and os.path.getsize(html_path) > 5000:
        print(f'  cached {slug} ({os.path.getsize(html_path)}b)')
        return html_path
    ts = latest_snapshot(post_url)
    print(f'  latest snapshot: {ts}')
    if not ts:
        return None
    snap = f'https://web.archive.org/web/{ts}id_/{post_url}'
    code = curl(snap, html_path, 60)
    print(f'  fetch code={code} size={os.path.getsize(html_path) if os.path.exists(html_path) else 0}')
    return html_path if os.path.exists(html_path) and os.path.getsize(html_path) > 1000 else None

SKIP_TEXTS = {'join', 'join group', 'click here', 'join now', 'link', 'join link', 'join here',
              'join group link', 'view all group links', 'whatsapp group links', 'remaining group link'}

def strip_tags(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.I | re.S)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.I | re.S)
    s = re.sub(r'<[^>]+>', '\n', s)
    s = re.sub(r'<[^>]*$', '', s)
    s = ihtml.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    return s

def extract(html_text):
    results = []
    for m in re.finditer(r'https?://chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})', html_text):
        code = m.group(1)
        pre = html_text[max(0, m.start() - 1500):m.start()]
        text = strip_tags(pre)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        while lines and lines[-1].lower() in SKIP_TEXTS:
            lines.pop()
        if not lines:
            continue
        name = lines[-1]
        if '|' in name and len(name.split('|')[0].strip()) > 2:
            name = name.split('|')[0].strip()
        name = re.sub(r'\s+', ' ', name).strip()[:120]
        if not name or name.lower() in SKIP_TEXTS or len(name) < 3:
            continue
        results.append((name, code))
    return results

def main():
    union = set(json.load(open(os.path.join(WAVE, 'dedupe_union.json'))))
    print('union codes:', len(union))
    all_cands, seen = [], set()
    for url, cat, country in POSTS:
        print('POST', url)
        try:
            hp = fetch_post(url, cat, country)
        except Exception as e:
            print('  ERROR', e); continue
        if not hp:
            continue
        html_text = open(hp, encoding='utf-8', errors='ignore').read()
        pairs = extract(html_text)
        fresh = 0
        for name, code in pairs:
            if code in union or code in seen:
                continue
            seen.add(code)
            all_cands.append({'name': name, 'category': cat, 'country': country,
                              'invite': 'https://chat.whatsapp.com/' + code,
                              'post': url})
            fresh += 1
        print(f'  raw pairs: {len(pairs)}, fresh-not-in-union: {fresh}')
        time.sleep(4)
    out = os.path.join(WAVE, 'team09_gd_candidates.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(all_cands, f, indent=1, ensure_ascii=False)
    print('TOTAL fresh candidates:', len(all_cands), '->', out)

if __name__ == '__main__':
    main()
