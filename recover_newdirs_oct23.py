#!/usr/bin/env python3
"""Recover the lost newdirs batch: scrape 4 fresh directory sites, dedupe, verify, save.
Writes to the PERSISTENT agent_batches dir (NOT /tmp — /tmp gets wiped)."""
import re, json, html, time, os, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

SITE_DIR = '/home/hatch/workspace/whatsapp-groups-site'
OUT_DIR = os.path.join(SITE_DIR, 'agent_batches')
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, 'wgl_agent_newdirs_new.json')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

PAGES = [
    # (url, category, country)
    ('https://whatzgrouplink.com/latest-whatsapp-group-links/', 'Community & Social', ''),
    ('https://whatzgrouplink.com/earning-whatsapp-group-link/', 'Online Earning', ''),
    ('https://whatzgrouplink.com/dream11-whatsapp-group-links/', 'Sports', 'IN'),
    ('https://whatzgrouplink.com/fanfight-whatsapp-group-links/', 'Sports', 'IN'),
    ('https://whatzgrouplink.com/football-whatsapp-group-links/', 'Sports', ''),
    ('https://whatzgrouplink.com/free-fire-whatsapp-group-links/', 'Gaming', ''),
    ('https://whatzgrouplink.com/funny-whatsapp-group-links/', 'Entertainment', ''),
    ('https://whatzgrouplink.com/girls-whatsapp-group-links/', 'Friendship', ''),
    ('https://whatzgrouplink.com/ipl-whatsapp-group-links/', 'Sports', 'IN'),
    ('https://whatzgrouplink.com/ludo-whatsapp-group-links/', 'Gaming', 'IN'),
    ('https://whatzgrouplink.com/news-whatsapp-group-links/', 'News', ''),
    ('https://whatzgrouplink.com/youtube-whatsapp-group-links/', 'Entertainment', ''),
    ('https://whatsgroulink.com/category/earning/', 'Online Earning', ''),
    ('https://whatsgroulink.com/category/game/', 'Gaming', ''),
    ('https://whatsgroulink.com/category/jobs/', 'Jobs', ''),
    ('https://whatsgroulink.com/category/movies/', 'Entertainment', ''),
    ('https://whatsgroulink.com/category/shopping/', 'Buy & Sell', ''),
    ('https://whatsgroulink.com/category/study/', 'Education', ''),
    ('https://whatsgroulink.com/category/country/', 'Community & Social', ''),
    ('https://whatsgroulink.com/bangalore-whatsapp-group-links/', 'Community & Social', 'IN'),
    ('https://whatsgroulink.com/indian-whatsapp-group-links/', 'Community & Social', 'IN'),
    ('https://whatsgroulink.com/international-whatsapp-groups-links/', 'Community & Social', ''),
    ('https://whatsgroulink.com/italy-whatsapp-group-links/', 'Community & Social', 'IT'),
    ('https://whatsgroulink.com/karachi-whatsapp-group-links/', 'Community & Social', 'PK'),
    ('https://whatsgroulink.com/rajasthan-whatsapp-group-links/', 'Community & Social', 'IN'),
    ('https://whatsgroulink.com/south-africa-jobs-whatsapp-group-links/', 'Jobs', 'ZA'),
    ('https://whatsapp-group-link.com/1334-delhi-whatsapp-group-links-join-now-update-now/', 'Community & Social', 'IN'),
    ('https://whatsapp-group-link.com/category/earn-money/', 'Online Earning', ''),
    ('https://whatsapp-group-link.com/category/education/', 'Education', ''),
    ('https://whatsapp-group-link.com/category/entertainment/', 'Entertainment', ''),
    ('https://whatsapp-group-link.com/category/games/', 'Gaming', ''),
    ('https://whatsapp-group-link.com/category/girls-group/', 'Friendship', ''),
    ('https://whatsapp-group-link.com/category/indian-group/', 'Community & Social', 'IN'),
    ('https://whatsapp-group-link.com/education-whatsapp-group-links/', 'Education', ''),
    ('https://whatsapp-group-link.com/funny-whatsapp-group-links/', 'Entertainment', ''),
    ('https://whatsapp-group-link.com/games-whatsapp-group-link/', 'Gaming', ''),
    ('https://whatsapp-group-link.com/girls-whatsapp-group-links/', 'Friendship', ''),
    ('https://whatsapp-group-link.com/indian-whatsapp-group-links/', 'Community & Social', 'IN'),
    ('https://whatsapp-group-link.com/pakistani-whatsapp-group-links/', 'Community & Social', 'PK'),
    ('https://whatsapp-group-link.com/shayari-whatsapp-group-links/', 'Poetry', ''),
    ('https://whatsapp-group-link.com/tamil-whatsapp-group-links/', 'Community & Social', 'IN'),
    ('https://whatsapp-group-link.com/tik-tok-whatsapp-group-links/', 'Entertainment', ''),
    ('https://whatsapp-group-link.com/uk-whatsapp-group-links/', 'Community & Social', 'UK'),
    ('https://whatsapp-group-link.com/usa-whatsapp-group-links/', 'Community & Social', 'US'),
    ('https://www.whtsagrouplinks.com/international-whatsapp-groups-links/', 'Community & Social', ''),
    ('https://www.whtsagrouplinks.com/govt-jobs-whatsapp-group-links/', 'Jobs', 'IN'),
    ('https://www.whtsagrouplinks.com/work-from-home-whatsapp-group-links/', 'Jobs', ''),
    ('https://www.whtsagrouplinks.com/web-series-whatsapp-group-links/', 'Entertainment', 'IN'),
    ('https://www.whtsagrouplinks.com/urdu-poetry-whatsapp-group-links/', 'Poetry', 'PK'),
    ('https://www.whtsagrouplinks.com/travel-whatsapp-group-links/', 'Travel', ''),
    ('https://www.whtsagrouplinks.com/trading-whatsapp-group-links/', 'Business', ''),
    ('https://www.whtsagrouplinks.com/sub4sub-whatsapp-group-links/', 'Entertainment', ''),
    ('https://www.whtsagrouplinks.com/study/', 'Education', ''),
    ('https://www.whtsagrouplinks.com/students-whatsapp-group-links/', 'Education', ''),
    ('https://www.whtsagrouplinks.com/social-media-whatsapp-group-links/', 'Entertainment', ''),
    ('https://www.whtsagrouplinks.com/shopping/', 'Buy & Sell', ''),
    ('https://www.whtsagrouplinks.com/shayari-whatsapp-group-links/', 'Poetry', ''),
    ('https://www.whtsagrouplinks.com/share-market-whatsapp-group-links/', 'Business', 'IN'),
    ('https://www.whtsagrouplinks.com/reseller-whatsapp-group-link/', 'Buy & Sell', 'IN'),
    ('https://www.whtsagrouplinks.com/pubg-whatsapp-group-links/', 'Gaming', ''),
    ('https://www.whtsagrouplinks.com/pakistani-whatsapp-group-link/', 'Community & Social', 'PK'),
    ('https://www.whtsagrouplinks.com/other-whatsapp-group-links/', 'Community & Social', ''),
]

INVITE_RE = re.compile(r'href="(https://chat\.whatsapp\.com(?:/invite)?/[A-Za-z0-9]+)"')
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)')
LI_RE = re.compile(r'<li[^>]*>(.*?)</li>', re.DOTALL | re.IGNORECASE)
PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi)\b', re.I)

def fetch(url):
    try:
        p = subprocess.run(['curl', '-s', '-L', '--max-time', '25', '-A', UA, url],
                           capture_output=True, timeout=35)
        return p.stdout.decode('utf-8', errors='ignore')
    except Exception:
        return ''

def clean_name(raw):
    t = re.sub(r'<[^>]+>', ' ', raw)
    t = html.unescape(t)
    t = re.sub(r'[➠➔→►▶»›←↑↓↔↕▪•●◦·|]', ' ', t)
    t = re.sub(r'\(New\)|\(new\)|\bNew\b\s*$', ' ', t, flags=re.I)
    t = re.sub(r'\b(join link|join group|join|click here|join now)\b\s*$', ' ', t, flags=re.I)
    t = re.sub(r'\s+', ' ', t).strip(' -–—:;,.')
    return t[:120]

def extract(page_html):
    """Return list of (name, invite_url)."""
    out = []
    # primary: <li>NAME ... <a href="invite"> pattern
    for li in LI_RE.findall(page_html):
        m = INVITE_RE.search(li)
        if not m:
            continue
        invite = m.group(1)
        before = li[:m.start()]
        name = clean_name(before)
        if len(name) < 2 or PORN_RE.search(name):
            if PORN_RE.search(name):
                continue
            name = ''
        out.append((name, invite))
    return out

def check_link(url):
    for _ in range(2):
        try:
            p = subprocess.run(['curl', '-s', '-L', '--max-time', '20', '-A', UA,
                                '-w', '\n%{http_code}', url],
                               capture_output=True, timeout=30)
            body = p.stdout.decode('utf-8', errors='ignore')
            code = body.rsplit('\n', 1)[1].strip() if '\n' in body else '000'
            if code != '200':
                time.sleep(0.5)
                continue
            m = re.search(r'og:title[^>]*?content="([^"]*)"', body)
            title = html.unescape(m.group(1)).strip() if m else ''
            return bool(title)
        except Exception:
            time.sleep(0.5)
    return False

def main():
    codes = set(json.load(open(os.path.join(SITE_DIR, '.existing_codes.json'))))
    print(f"existing codes: {len(codes)}", flush=True)
    cands = {}  # code -> dict
    for i, (url, cat, country) in enumerate(PAGES):
        h = fetch(url)
        if not h:
            print(f"  [{i+1}/{len(PAGES)}] FETCH FAIL {url}", flush=True)
            continue
        found = extract(h)
        new = 0
        for name, invite in found:
            m = CODE_RE.search(invite)
            if not m:
                continue
            code = m.group(1)
            if code in codes or code in cands:
                continue
            if not name:
                name = f"{cat} WhatsApp Group"
            cands[code] = {'name': name, 'category': cat,
                           'description': f"Join {name}, a WhatsApp group listed under {cat}.",
                           'image': '', 'invite': f'https://chat.whatsapp.com/{code}',
                           'country': country}
            new += 1
        print(f"  [{i+1}/{len(PAGES)}] {url[:60]}: {len(found)} links, {new} new codes", flush=True)
        time.sleep(0.3)
    print(f"candidates to verify: {len(cands)}", flush=True)
    verified = []
    done = 0
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(check_link, v['invite']): k for k, v in cands.items()}
        for fut in as_completed(futs):
            code = futs[fut]
            done += 1
            try:
                ok = fut.result()
            except Exception:
                ok = False
            if ok:
                verified.append(cands[code])
            if done % 200 == 0:
                print(f"  verified {done}/{len(cands)} -> {len(verified)} live", flush=True)
    with open(OUT, 'w') as f:
        json.dump(verified, f, ensure_ascii=False)
    print(f"DONE: {len(verified)} verified new groups -> {OUT}", flush=True)

if __name__ == '__main__':
    main()
