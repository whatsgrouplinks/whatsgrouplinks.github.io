#!/usr/bin/env python3
"""TEAM 207 final wave: groupjoin.link tag pages + fresh domains, threaded."""
import re, json, html, time, os, pickle, sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'scraped', 'team207-entertainment.json')
LOG = os.path.join(BASE, 'scraped', 'team207-wave3.log')
PKL = os.path.join(BASE, 'scraped', '_existing_invites.pkl')
GROUPS_JSON = os.path.join(BASE, 'groups.json')

TAGS = ["Netflixseries", "Movies", "Movie", "Music", "Songs", "Comedy", "Funny",
        "Jokes", "Drama", "Memes", "Bollywood", "Hollywood", "Anime", "Webseries",
        "Entertainment", "Tamil", "Kdrama", "KoreanDrama", "Tollywood", "Punjabi",
        "Status", "Masti", "MovieBuff", "Cinema"]
URLS = [f"https://www.groupjoin.link/tag/{t}?safeSearch=moderate" for t in TAGS] + [
    "https://technoearning.in/06/join-interesting-whatsapp-group-whatsapp-group-joining-link/",
    "https://groupda.com/singer/arijit-singh-whatsapp-group-links-join-list/",
    "https://geeksgyaan.com/2020/11/whatsapp-group-links.html",
    "https://whatsagroupslinks.com/punjabi-whatsapp-group-links/",
    "https://hubrecipes.com/best-movies-whatsapp-group-links/",
    "https://whatslists.com/telugu-movies-whatsapp-group-links/",
    "https://hubrecipes.com/join-active-mallu-whatsapp-group-links/",
]

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
BLOCK = [r'\bporn\b', r'\bxxx\b', r'\bjav\b', r'18\s*\+', r'\bsex\b', r'\bsexy\b',
         r'\badult\b', r'\bnude\b', r'\bnaked\b', r'\bescort\b', r'\bbhabhi\b',
         r'\bmms\b', r'\bleak\w*\b', r'viral\s*video', r'h\*t', r'p\*\*',
         r'hot\s*girl', r'night\s*\w*\s*girl', r'call\s*girl', r'\bdesi\s*(girl|mms)',
         r'\bitem\s*girl', r'aunty\s*hot', r'malaya', r'ngono']
BLOCK_RE = re.compile('|'.join(BLOCK), re.I)
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{16,30})')
OFFTOPIC = re.compile(r'\b(health|medicine|doctor|hospital|clinic|job|jobs|hiring|salary|career|news|newspaper|politic|election|study|exam|school|college|university|admission|scholarship|crypto|forex|trading|betting|loan|business|real[\s-]?estate|islamic|quran|namaz|dua|dars|bayan|matrimonial|rishta|shaadi|shopping|sale|offer|deal|discount|earn(ing)?\s*money|friendship|dosti|bhaichara)\b', re.I)

def log(msg):
    with open(LOG, 'a') as f:
        f.write(msg + '\n')
    print(msg, flush=True)

def fetch(url, timeout=18):
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception:
            time.sleep(2)
    return None

def clean_text(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def extract_pairs(page_html):
    pairs, seen = [], set()
    pats = [
        re.compile(r'<td[^>]*>(.*?)</td>\s*<td[^>]*>\s*<a[^>]*href="[^"]*chat\.whatsapp\.com/([A-Za-z0-9]{16,30})[^"]*"', re.I | re.S),
        re.compile(r'<li[^>]*>(.*?)<a[^>]*href="[^"]*chat\.whatsapp\.com/([A-Za-z0-9]{16,30})[^"]*"', re.I | re.S),
        re.compile(r'(?:<h[1-4][^>]*>(.*?)</h[1-4]>|<a[^>]*>(.*?)</a>)\s*(?:<[^>]+>\s*){0,3}<a[^>]*href="[^"]*chat\.whatsapp\.com/([A-Za-z0-9]{16,30})[^"]*"', re.I | re.S),
    ]
    for pat in pats:
        for m in pat.finditer(page_html):
            groups = [g for g in m.groups() if g]
            code = groups[-1]
            name = clean_text(' '.join(groups[:-1]))
            if code in seen or not name:
                continue
            if name.lower() in ('join', 'join now', 'click here', 'join group', 'link'):
                continue
            pairs.append((name, code)); seen.add(code)
    for m in CODE_RE.finditer(page_html):
        code = m.group(1)
        if code in seen:
            continue
        before = page_html[max(0, m.start() - 800):m.start()]
        texts = re.findall(r'>([^<>]{3,140})<', before)
        name = clean_text(texts[-1]) if texts else ''
        if name.lower() in ('join', 'join now', 'click here', 'join group', 'link', ''):
            name = ''
        pairs.append((name, code)); seen.add(code)
    return pairs

def good_name(name):
    name = clean_text(name).strip(' –-|:;•·').strip()
    if not name or len(name) > 120 or len(name) < 2:
        return None
    if BLOCK_RE.search(name) or OFFTOPIC.search(name):
        return None
    if re.fullmatch(r'[\W_]+', name):
        return None
    return name

def load_existing():
    codes = set()
    if os.path.exists(PKL):
        s = pickle.load(open(PKL, 'rb'))
        if isinstance(s, set):
            codes |= {c.strip() for c in s if c}
    if os.path.exists(GROUPS_JSON):
        gj = json.load(open(GROUPS_JSON))
        items = gj if isinstance(gj, list) else gj.get('groups', [])
        for g in items:
            m = CODE_RE.search(g.get('invite') or '')
            if m: codes.add(m.group(1))
    return codes

def main():
    open(LOG, 'w').write('')
    existing = load_existing()
    log(f"existing codes: {len(existing)}")
    prev = []
    if os.path.exists(OUT):
        prev = json.load(open(OUT))
    kept, prev_codes = [], set()
    for g in prev:
        m = CODE_RE.search(g.get('invite') or '')
        code = m.group(1) if m else None
        name = good_name(g.get('name') or '')
        if code and name and code not in prev_codes:
            kept.append({"name": name, "invite": f"https://chat.whatsapp.com/{code}",
                         "desc": f"Join {name}, a WhatsApp group for entertainment, movies and fun.",
                         "cat": "Entertainment"})
            prev_codes.add(code); existing.add(code)
    log(f"kept from prev: {len(kept)}")
    results = {}
    def work(url):
        page_html = fetch(url)
        time.sleep(0.8)
        if not page_html:
            log(f"FAIL {url}")
            return
        pairs = extract_pairs(page_html)
        log(f"OK {url} pairs={len(pairs)}")
        results[url] = pairs
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(work, URLS))
    out, seen_new = list(kept), set()
    for url in URLS:
        for name, code in results.get(url, []):
            if code in existing or code in seen_new:
                continue
            name = good_name(name)
            if not name:
                continue
            out.append({"name": name, "invite": f"https://chat.whatsapp.com/{code}",
                        "desc": f"Join {name}, a WhatsApp group for entertainment, movies and fun.",
                        "cat": "Entertainment"})
            seen_new.add(code)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log(f"SAVED {len(out)} -> {OUT}")

if __name__ == '__main__':
    main()
