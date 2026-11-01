#!/usr/bin/env python3
"""TEAM 232: scrape two WhatsApp directories never deeply scraped before:
  - https://whtspgrouplink.com  (503 post URLs via Yoast sitemap)
  - https://freshgrouplinks.com  (23 post URLs + 10 category archives via Yoast sitemap)
Extract (name, invite-code) pairs, dedupe vs _seen_all_codes.pkl + within output,
filter adult content, assign category/country from slug.
Output: scraped/team232-newdirs2.json  [{name, invite, description, category, country, image}]
"""
import re, json, html, time, os, pickle, sys
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'scraped', 'team232-newdirs2.json')
SEEN_PKL = os.path.join(BASE, 'scraped', '_seen_all_codes.pkl')
PROGRESS = os.path.join(BASE, 'scraped', 'team232-progress.json')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{14,40})')

ADULT_RE = re.compile(
    r'\bporn\b|\bxxx\b|\bsexy\b|\bnude\b|\bnaked\b|\bescort\b|call\s*girl|callgirl|'
    r'\bsex\s*(chat|video|group|videos)\b', re.I)

CAT_RULES = [
    (r'job|recruit|vacan|career|rozgar|naukri|employment|hiring', 'Jobs'),
    (r'crypto|bitcoin|binance|web3', 'Crypto'),
    (r'forex|trading|stock|nifty|banknifty|share.?market|option', 'Trading'),
    (r'pubg|bgmi|free.?fire|gta|fortnite|ludo|chess|gaming|game|esport|cod|valorant|minecraft', 'Gaming'),
    (r'cricket|football|ipl|fifa|sport|tennis|hockey|kabaddi|wwe|psl', 'Sports'),
    (r'movie|film|drama|serial|series|anime|netflix|bollywood|hollywood|web.?series', 'Entertainment'),
    (r'news|newspaper|breaking|headlines|taza|khabar', 'News'),
    (r'islam|quran|muslim|madani|masjid|namaz|roza|hajj|naat|deen', 'Islamic'),
    (r'business|entrepreneur|startup|import|export', 'Business'),
    (r'earn|money|online.?earning|passive.?income|freelanc', 'Online Earning'),
    (r'stud(y|ies)|exam|education|school|college|univers|ielts|ssc|upsc|css|pcs|board|academy|scholarship|learn', 'Education'),
    (r'girl|friendship|friend|dating|couple|love', 'Friendship'),
    (r'tech|coding|program|python|java|ai|artificial|software|computer|cyber|hack', 'Technology'),
    (r'health|fitness|yoga|doctor|medical|hospital|diet|weight', 'Health'),
    (r'poetr|shayari|status|sticker|mehndi|fashion|shopping|buy|sell|deal|resell|bazar|market', 'Entertainment'),
    (r'youtube|tiktok|instagram|social.?media|influencer|vlog', 'Entertainment'),
    (r'real.?estate|propert', 'Business'),
]
COUNTRY_RULES = [
    (r'pakistan|pakistani|karachi|lahore|islamabad|peshawar|quetta|multan|faisalabad|rawalpindi|hyderabad.?pk|sindh|punjab.?pk|baloch|ghotki', 'Pakistan'),
    (r'\bindia\b|indian|delhi|mumbai|chennai|kolkata|bangalore|bengaluru|tamil|telugu|kerala|kannada|punjab(?!i)|hindi|upsc|ssc|rajasthan|gujarat|bihar|maharashtra', 'India'),
    (r'\busa\b|america|new.?york|texas|california|florida', 'USA'),
    (r'\buk\b|britain|london|england', 'UK'),
    (r'uae|dubai|abu.?dhabi|sharjah', 'UAE'),
    (r'saudi', 'Saudi Arabia'),
    (r'bangladesh|bangla|dhaka', 'Bangladesh'),
    (r'nigeria', 'Nigeria'),
    (r'kenya', 'Kenya'),
    (r'south.?africa', 'South Africa'),
    (r'canada', 'Canada'),
    (r'australia', 'Australia'),
    (r'germany', 'Germany'),
    (r'france', 'France'),
    (r'italy', 'Italy'),
    (r'spain', 'Spain'),
    (r'turkey|turkiye', 'Turkey'),
    (r'malaysia', 'Malaysia'),
    (r'indonesia', 'Indonesia'),
    (r'philippines', 'Philippines'),
    (r'nepal', 'Nepal'),
    (r'sri.?lanka', 'Sri Lanka'),
    (r'afghanistan', 'Afghanistan'),
    (r'egypt', 'Egypt'),
    (r'qatar', 'Qatar'),
    (r'kuwait', 'Kuwait'),
    (r'oman', 'Oman'),
    (r'bahrain', 'Bahrain'),
]


def fetch(url, timeout=30):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None


def clean_text(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = t.replace('\xa0', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    # strip trailing join artifacts
    t = re.sub(r'\s*[–—\-:;|]+\s*(join|join now|join group|click here)?\s*$', '', t, flags=re.I)
    t = re.sub(r'^(join|join now)\s*[–—\-:;|]?\s*', '', t, flags=re.I)
    return t.strip()[:140]


def extract_pairs(page_html):
    pairs, seen_here = [], set()

    def add(name, code):
        if code not in seen_here:
            seen_here.add(code)
            pairs.append((name, code))

    # 1) <li>NAME ... <a href="...chat.whatsapp.com/CODE">
    pat1 = re.compile(
        r'<li[^>]*>(.*?)<a[^>]*href="[^"]*chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{14,40})[^"]*"',
        re.I | re.S)
    for m in pat1.finditer(page_html):
        name = clean_text(m.group(1))
        if name and not re.match(r'^(join|join now)$', name, re.I):
            add(name, m.group(2))
    # 2) <td>NAME</td> ... <a href="...CODE">
    pat2 = re.compile(
        r'<td[^>]*>(.*?)</td>\s*<td[^>]*>\s*<a[^>]*href="[^"]*chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{14,40})[^"]*"',
        re.I | re.S)
    for m in pat2.finditer(page_html):
        name = clean_text(m.group(1))
        if name:
            add(name, m.group(2))
    # 3) fallback: nearest preceding <strong>...</strong>
    for m in CODE_RE.finditer(page_html):
        code = m.group(1)
        if code in seen_here:
            continue
        before = page_html[max(0, m.start() - 1800):m.start()]
        strongs = re.findall(r'<strong>([^<>]{2,140})</strong>', before)
        name = clean_text(strongs[-1]) if strongs else ''
        if not name or re.match(r'^(join|join now)$', name, re.I):
            texts = re.findall(r'>([^<>]{4,140})<', before[-700:])
            name = clean_text(texts[-1]) if texts else ''
        if name and not re.match(r'^(join|join now)$', name, re.I):
            add(name, code)
    return pairs


def get_urls():
    urls = []
    sitemaps = [
        'https://whtspgrouplink.com/post-sitemap.xml',
        'https://freshgrouplinks.com/post-sitemap.xml',
        'https://freshgrouplinks.com/category-sitemap.xml',
    ]
    for sm in sitemaps:
        h = fetch(sm)
        if not h:
            print(f'  !! sitemap failed: {sm}', flush=True)
            continue
        for loc in re.findall(r'<loc>([^<]+)</loc>', h):
            loc = loc.strip()
            if loc.endswith('.xml'):
                continue
            urls.append(loc)
    # dedupe, keep order
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def classify(slug, title):
    text = f'{slug} {title}'.lower()
    cat = 'General'
    for pat, c in CAT_RULES:
        if re.search(pat, text):
            cat = c
            break
    country = ''
    for pat, co in COUNTRY_RULES:
        if re.search(pat, text):
            country = co
            break
    return cat, country


def norm_code(url_or_code):
    s = str(url_or_code).strip()
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{14,40})', s)
    if m:
        return m.group(1)
    m = re.match(r'^[A-Za-z0-9]{14,40}$', s)
    return s if m else None


def load_seen():
    codes = set()
    if os.path.exists(SEEN_PKL):
        try:
            s = pickle.load(open(SEEN_PKL, 'rb'))
            for c in s:
                n = norm_code(c)
                if n:
                    codes.add(n)
        except Exception as e:
            print(f'  !! seen pkl load failed: {e}', flush=True)
    return codes


def process_page(url, seen):
    page = fetch(url)
    if not page:
        return [], 'fetch-fail'
    m = re.search(r'<title>(.*?)</title>', page, re.I | re.S)
    title = clean_text(m.group(1)) if m else ''
    slug = url.rstrip('/').split('/')[-1]
    cat, country = classify(slug, title)
    pairs = extract_pairs(page)
    recs = []
    for name, code in pairs:
        n = norm_code(code)
        if not n or n in seen:
            continue
        blob = f'{name} {slug}'
        if ADULT_RE.search(blob):
            continue
        desc = f"Join {name} on WhatsApp — an active {cat.lower()} group."
        recs.append({
            'name': name,
            'invite': f'https://chat.whatsapp.com/{n}',
            'description': desc,
            'category': cat,
            'country': country,
            'image': '',
        })
        seen.add(n)
    return recs, 'ok'


def main():
    seen = load_seen()
    print(f'loaded {len(seen)} seen codes', flush=True)
    urls = get_urls()
    print(f'{len(urls)} page URLs to scrape', flush=True)
    done_urls = set()
    if os.path.exists(PROGRESS):
        try:
            done_urls = set(json.load(open(PROGRESS)))
        except Exception:
            pass
    urls = [u for u in urls if u not in done_urls]
    print(f'{len(urls)} remaining after progress', flush=True)
    max_pages = int(os.environ.get('TEAM232_MAX_PAGES', '0'))
    if os.environ.get('TEAM232_FIRST'):
        key = os.environ['TEAM232_FIRST']
        urls = [u for u in urls if key in u] + [u for u in urls if key not in u]
    if max_pages > 0:
        urls = urls[:max_pages]
        print(f'chunk limited to {len(urls)} pages', flush=True)

    all_recs, fails = [], 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as ex:
        fut2u = {ex.submit(process_page, u, seen): u for u in urls}
        for i, fut in enumerate(as_completed(fut2u), 1):
            u = fut2u[fut]
            try:
                recs, status = fut.result()
            except Exception as e:
                recs, status = [], f'error {e}'
            if status == 'ok':
                all_recs.extend(recs)
            else:
                fails += 1
            done_urls.add(u)
            if i % 40 == 0 or i == len(urls):
                el = time.time() - t0
                print(f'  {i}/{len(urls)} pages, {len(all_recs)} new groups, fails={fails}, {el:.0f}s', flush=True)
                json.dump(sorted(done_urls), open(PROGRESS, 'w'))

    # final dedupe by code (safety), merged with any records saved by earlier chunks
    dedup, seen_out = [], set()
    if os.path.exists(OUT):
        try:
            for r in json.load(open(OUT)):
                c = norm_code(r.get('invite', ''))
                if c and c not in seen_out:
                    seen_out.add(c)
                    dedup.append(r)
        except Exception:
            pass
    for r in all_recs:
        c = norm_code(r['invite'])
        if c and c not in seen_out:
            seen_out.add(c)
            dedup.append(r)

    with open(OUT, 'w') as f:
        json.dump(dedup, f, ensure_ascii=False, indent=2)
    print(f'DONE: {len(dedup)} unique NEW groups -> {OUT}', flush=True)


if __name__ == '__main__':
    main()
