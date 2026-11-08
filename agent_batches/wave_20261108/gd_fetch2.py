#!/usr/bin/env python3
"""Team09 wave20261108 round 2: more groupda listing posts via Wayback.
Snapshot pick: try newest-first, accept first snapshot whose raw HTML is
>20000 bytes (older/smaller captures are CF-block or stub pages).
"""
import json, os, re, subprocess, time, html as ihtml

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261108')
OUTDIR = os.path.join(WAVE, 'team09_gd_pages')
os.makedirs(OUTDIR, exist_ok=True)

POSTS = [
    ('https://groupda.com/business/real-estate-whatsapp-group-link-pakistan-join-2022/', 'Real Estate', 'PK'),
    ('https://groupda.com/games/rummy-whatsapp-group-link-join-2022/', 'Gaming', 'IN'),
    ('https://groupda.com/jobs/it-jobs-whatsapp-group-link-join-2022/', 'Jobs', 'IN'),
    ('https://groupda.com/news-2/sindhi-news-whatsapp-group-link-join-2022/', 'News', 'PK'),
    ('https://groupda.com/chat/graphic-design-whatsapp-group-links-2022/', 'Freelance', 'International'),
    ('https://groupda.com/spiritual/best-islamic-whatsapp-group-link-2022/', 'Islamic', 'International'),
    ('https://groupda.com/jobs/chennai-part-time-whatsapp-group-link-join-2022/', 'Jobs', 'IN'),
    ('https://groupda.com/jobs/hyderabad-jobs-whatsapp-group-link-join-2022/', 'Jobs', 'IN'),
    ('https://groupda.com/jobs/rajkot-job-whatsapp-group-link-join-2022/', 'Jobs', 'IN'),
    ('https://groupda.com/education/diploma-mechanical-whatsapp-group-link-join-2022/', 'Education', 'IN'),
    ('https://groupda.com/education/polytechnic-whatsapp-group-link-join-2022/', 'Education', 'IN'),
    ('https://groupda.com/sports/roanaldo-whatsapp-group-link-join-2022/', 'Sports', 'IN'),
    ('https://groupda.com/sports/somnath-whatsapp-group-links-2022/', 'Sports', 'IN'),
    ('https://groupda.com/games/clash-of-clans-whatsapp-group-link-join-2022/', 'Gaming', 'IN'),
    ('https://groupda.com/chat/karate-whatsapp-group-link-join-2022/', 'Sports', 'International'),
    ('https://groupda.com/chat/army-lover-whatsapp-group-link-join-2022/', 'Friendship', 'IN'),
    ('https://groupda.com/news-2/rajasthan-news-whatsapp-group-link-join-2022/', 'News', 'IN'),
    ('https://groupda.com/spiritual/islamic-books-whatsapp-group-links-2022/', 'Islamic', 'International'),
    ('https://groupda.com/spiritual/iskcon-whatsapp-group-links-2022/', 'Islamic', 'IN'),
    ('https://groupda.com/spiritual/brahma-kumaris-whatsapp-group-links-2022/', 'Islamic', 'IN'),
    ('https://groupda.com/business/grocery-wholesale-whatsapp-group-link-join-2022/', 'Business', 'IN'),
    ('https://groupda.com/buysell/vegetable-buyers-whatsapp-group-links-2022/', 'Buy & Sell', 'IN'),
    ('https://groupda.com/health/hiv-positive-whatsapp-group-link-join-2022/', 'Health', 'International'),
    ('https://groupda.com/beauty/spa-whatsapp-group-link-join-2022/', 'Health', 'IN'),
    ('https://groupda.com/movie/bgmi-account-selling-whatsapp-group-link/', 'Buy & Sell', 'IN'),
    ('https://groupda.com/matrimonial/nikah-whatsapp-group-links-2022/', 'Community & Social', 'IN'),
    ('https://groupda.com/chat/4000-hours-watchtime-whatsapp-group-link-join-2022/', 'Online Earning', 'International'),
    ('https://groupda.com/engineering/civil-contractors-whatsapp-group-link-join-2022/', 'Jobs', 'IN'),
    ('https://groupda.com/spiritual/krishna-consciousnes-whatsapp-group-links-2022/', 'Islamic', 'IN'),
    ('https://groupda.com/matrimonial/iskcon-marriage-whatsapp-group-links-2022/', 'Community & Social', 'IN'),
]

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def curl(url, outpath, max_time=50):
    r = subprocess.run(['curl', '-sS', '-L', '-A', UA, '--max-time', str(max_time),
                        '-o', outpath, '-w', '%{http_code}', url],
                       capture_output=True, text=True)
    return r.stdout.strip()

def snapshots(post_url):
    cdx = ('https://web.archive.org/cdx/search/cdx?url=' + post_url +
           '&output=json&filter=statuscode:200&limit=100')
    tmp = '/tmp/gd_cdx2.json'
    curl(cdx, tmp, 40)
    try:
        rows = json.load(open(tmp))
    except Exception:
        return []
    if len(rows) < 2:
        return []
    rows = rows[1:]
    rows.sort(key=lambda r: r[1], reverse=True)
    return [(r[1], int(r[6]) if len(r) > 6 and r[6].isdigit() else 0) for r in rows]

def fetch_post(post_url):
    slug = re.sub(r'[^a-z0-9]+', '_', post_url.rstrip('/').split('/')[-1])[:60]
    html_path = os.path.join(OUTDIR, slug + '.html')
    if os.path.exists(html_path) and os.path.getsize(html_path) > 20000:
        print(f'  cached {slug}')
        return html_path
    snaps = snapshots(post_url)
    print(f'  snapshots: {len(snaps)} latest={snaps[0] if snaps else None}')
    for ts, length in snaps[:3]:
        snap = f'https://web.archive.org/web/{ts}id_/{post_url}'
        code = curl(snap, html_path, 60)
        size = os.path.getsize(html_path) if os.path.exists(html_path) else 0
        print(f'  try {ts} code={code} size={size}')
        if size > 20000:
            return html_path
        time.sleep(6)
    return None

SKIP_TEXTS = {'join', 'join group', 'click here', 'join now', 'link', 'join link', 'join here',
              'join group link', 'view all group links', 'whatsapp group links', 'remaining group link'}

def clean_name(name):
    name = re.sub(r'\s+', ' ', name).strip()
    name = re.sub(r'[\-\u2013\u2014\u2015\s]+$', '', name).strip()
    name = re.sub(r'^[\-\u2013\u2014\*\s]+', '', name).strip()
    if '|' in name and len(name.split('|')[0].strip()) > 2:
        name = name.split('|')[0].strip()
    return name[:120]

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
        name = clean_name(lines[-1])
        if not name or name.lower() in SKIP_TEXTS or len(name) < 3:
            continue
        if 'thoughts on' in name.lower() or 'http' in name.lower():
            continue
        if not re.search(r'[A-Za-z0-9\u0600-\u06FF\u0900-\u097F\u0E00-\u0E7F\u4E00-\u9FFF]', name):
            continue
        results.append((name, code))
    return results

def main():
    union = set(json.load(open(os.path.join(WAVE, 'dedupe_union.json'))))
    prev = []
    p1 = os.path.join(WAVE, 'team09_gd_candidates.json')
    if os.path.exists(p1):
        prev = json.load(open(p1))
    seen = set(x['invite'].split('/')[-1] for x in prev)
    all_cands = list(prev)
    print('union:', len(union), 'prev candidates:', len(prev))
    for url, cat, country in POSTS:
        print('POST', url)
        try:
            hp = fetch_post(url)
        except Exception as e:
            print('  ERROR', e); continue
        if not hp:
            print('  no usable snapshot'); continue
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
        time.sleep(6)
    out = os.path.join(WAVE, 'team09_gd_candidates.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(all_cands, f, indent=1, ensure_ascii=False)
    print('TOTAL fresh candidates:', len(all_cands), '->', out)

if __name__ == '__main__':
    main()
