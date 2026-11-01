#!/usr/bin/env python3
"""TEAM 207 wave 4: groupjoin.link tag pages - proper group_title extraction."""
import re, json, html, time, os, pickle
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'scraped', 'team207-entertainment.json')
LOG = os.path.join(BASE, 'scraped', 'team207-wave4.log')
PKL = os.path.join(BASE, 'scraped', '_existing_invites.pkl')
GROUPS_JSON = os.path.join(BASE, 'groups.json')

TAGS = ["Netflixseries", "Movies", "Movie", "Music", "Songs", "Comedy", "Funny",
        "Jokes", "Drama", "Memes", "Bollywood", "Hollywood", "Anime", "Webseries",
        "Entertainment", "Tamil", "Kdrama", "KoreanDrama", "Tollywood", "Punjabi",
        "Status", "Masti", "Cinema", "WebSeries", "Netflix", "Prime", "Hotstar",
        "Malayalam", "Telugu", "Kannada", "Bhojpuri", "Gujarati"]
URLS = [f"https://www.groupjoin.link/tag/{t}?safeSearch=moderate" for t in TAGS]

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
BLOCK = [r'\bporn\b', r'\bxxx\b', r'\bjav\b', r'18\s*\+', r'\bsex\b', r'\bsexy\b',
         r'\badult\b', r'\bnude\b', r'\bnaked\b', r'\bescort\b', r'\bbhabhi\b',
         r'\bmms\b', r'\bleak\w*\b', r'viral\s*video', r'h\*t', r'p\*\*',
         r'hot\s*girl', r'night\s*\w*\s*girl', r'call\s*girl', r'\bdesi\s*(girl|mms)',
         r'\bitem\s*girl', r'aunty\s*hot', r'malaya', r'ngono']
BLOCK_RE = re.compile('|'.join(BLOCK), re.I)
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{16,30})')
GJ_RE = re.compile(r'\\"group_title\\":\\"((?:[^"\\]|\\.)*)\\".*?\\"link\\":\\"https://chat\.whatsapp\.com/([A-Za-z0-9]{16,30})', re.S)
OFFTOPIC = re.compile(r'\b(health|medicine|doctor|hospital|clinic|job|jobs|hiring|salary|career|news|newspaper|politic|election|study|exam|school|college|university|admission|scholarship|crypto|forex|trading|betting|loan|business|real[\s-]?estate|islamic|quran|namaz|dua|dars|bayan|matrimonial|rishta|shaadi|shopping|sale|offer|deal|discount|earn(ing)?\s*money|friendship|dosti|bhaichara)\b', re.I)

def log(msg):
    open(LOG, 'a').write(msg + '\n')
    print(msg, flush=True)

def unesc(s):
    s = s.replace('\\\\', '\x00').replace('\\"', '"').replace("\\'", "'").replace('\\n', ' ').replace('\\u0026', '&')
    s = s.replace('\x00', '\\')
    return html.unescape(s).strip()

def fetch(url, timeout=20):
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception:
            time.sleep(2)
    return None

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
    if os.path.exists(OUT):
        for g in json.load(open(OUT)):
            m = CODE_RE.search(g.get('invite') or '')
            if m: codes.add(m.group(1))
    return codes

def main():
    open(LOG, 'w').write('')
    existing = load_existing()
    log(f"existing codes: {len(existing)}")
    results = {}
    def work(url):
        page = fetch(url)
        time.sleep(0.6)
        if not page:
            log(f"FAIL {url}"); return
        pairs = []
        for m in GJ_RE.finditer(page):
            title, code = unesc(m.group(1)), m.group(2)
            pairs.append((title, code))
        log(f"OK {url} pairs={len(pairs)}")
        results[url] = pairs
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(work, URLS))
    out = json.load(open(OUT))
    seen_new = set()
    added = 0
    for url in URLS:
        for title, code in results.get(url, []):
            if code in existing or code in seen_new:
                continue
            title = re.sub(r'\s+', ' ', title).strip()
            if not title or len(title) > 120 or len(title) < 2:
                continue
            if BLOCK_RE.search(title) or OFFTOPIC.search(title):
                continue
            out.append({"name": title, "invite": f"https://chat.whatsapp.com/{code}",
                        "desc": f"Join {title}, a WhatsApp group for entertainment, movies and fun.",
                        "cat": "Entertainment"})
            seen_new.add(code); added += 1
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log(f"ADDED {added}, TOTAL {len(out)}")

if __name__ == '__main__':
    main()
