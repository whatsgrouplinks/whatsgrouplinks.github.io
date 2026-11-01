#!/usr/bin/env python3
"""TEAM 207 wave 6b: sequential gentle retry of throttled groupjoin pages."""
import re, json, html, time, os, pickle
import urllib.request, http.client

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'scraped', 'team207-entertainment.json')
LOG = os.path.join(BASE, 'scraped', 'team207-wave6b.log')
PKL = os.path.join(BASE, 'scraped', '_existing_invites.pkl')
GROUPS_JSON = os.path.join(BASE, 'groups.json')

URLS = [
    "https://www.groupjoin.link/tag/Movies?page=2",
    "https://www.groupjoin.link/tag/Movies?page=3",
    "https://www.groupjoin.link/tag/Movies?page=4",
    "https://www.groupjoin.link/tag/Movies?page=5",
    "https://www.groupjoin.link/tag/Movies?page=6",
    "https://www.groupjoin.link/tag/Music?page=2",
    "https://www.groupjoin.link/tag/Music?page=3",
    "https://www.groupjoin.link/tag/Music?page=4",
    "https://www.groupjoin.link/tag/Music?page=5",
    "https://www.groupjoin.link/tag/Music?page=6",
    "https://www.groupjoin.link/tag/Songs?page=2",
    "https://www.groupjoin.link/tag/Songs?page=3",
    "https://www.groupjoin.link/tag/Songs?page=4",
    "https://www.groupjoin.link/tag/Songs?page=5",
    "https://www.groupjoin.link/tag/Songs?page=6",
    "https://www.groupjoin.link/tag/Comedy?page=2",
    "https://www.groupjoin.link/tag/Comedy?page=3",
    "https://www.groupjoin.link/tag/Comedy?page=4",
    "https://www.groupjoin.link/tag/Comedy?page=5",
    "https://www.groupjoin.link/tag/Comedy?page=6",
]

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
BLOCK = [r'\bporn\b', r'\bxxx\b', r'\bjav\b', r'\bsax\b', r'18\s*\+', r'\bsex\b', r'\bsexy\b',
         r'\badult\b', r'\bnude\b', r'\bnaked\b', r'\bescort\b', r'\bbhabhi\b',
         r'\bmms\b', r'\bleak\w*\b', r'viral\s*video', r'h\*t', r'p\*\*',
         r'hot\s*girl', r'night\s*\w*\s*girl', r'call\s*girl', r'\bdesi\s*(girl|mms)',
         r'\bitem\s*girl', r'aunty\s*hot', r'malaya', r'ngono']
BLOCK_RE = re.compile('|'.join(BLOCK), re.I)
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{16,30})')
GJ_RE = re.compile(r'\\"group_title\\":\\"((?:[^"\\]|\\.)*)\\".*?\\"link\\":\\"https://chat\.whatsapp\.com/([A-Za-z0-9]{16,30})', re.S)
OFFTOPIC = re.compile(r'\b(health|medicine|doctor|hospital|clinic|job|jobs|hiring|salary|career|news|newspaper|politic|election|study|exam|school|college|university|admission|scholarship|crypto|forex|trading|betting|loan|business|real[\s-]?estate|islamic|quran|namaz|dua|dars|bayan|matrimonial|rishta|shaadi|shopping|sale|offer|deal|discount|earn(ing)?\s*money|friendship|dosti|bhaichara)\b', re.I)

def log(msg):
    open(LOG, 'a').write(msg + '\n'); print(msg, flush=True)

def unesc(s):
    s = s.replace('\\\\', '\x00').replace('\\"', '"').replace("\\'", "'").replace('\\n', ' ').replace('\\u0026', '&')
    return html.unescape(s.replace('\x00', '\\')).strip()

def fetch(url, timeout=40):
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            try:
                return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='ignore')
            except http.client.IncompleteRead as e:
                return e.partial.decode('utf-8', errors='ignore')
        except Exception:
            time.sleep(5)
    return None

def good_name(name):
    name = re.sub(r'\s+', ' ', name).strip(' \u2013-|:;\u2022\u00b7').strip()
    if not name or len(name) > 120 or len(name) < 2: return None
    if BLOCK_RE.search(name) or OFFTOPIC.search(name): return None
    if re.fullmatch(r'[\W_]+', name): return None
    return name

def load_existing():
    codes = set()
    if os.path.exists(PKL):
        s = pickle.load(open(PKL, 'rb'))
        if isinstance(s, set): codes |= {c.strip() for c in s if c}
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
    out = json.load(open(OUT))
    for g in out:
        m = CODE_RE.search(g.get('invite') or '')
        if m: existing.add(m.group(1))
    log(f"existing codes: {len(existing)}, current out: {len(out)}")
    seen_new, added = set(), 0
    for url in URLS:
        pairs = []
        for attempt in range(3):
            page = fetch(url)
            if page:
                pairs = [(unesc(m.group(1)), m.group(2)) for m in GJ_RE.finditer(page)]
            if pairs:
                break
            log(f"  retry {url} (attempt {attempt+1} got {len(pairs)})")
            time.sleep(10)
        log(f"OK {url} pairs={len(pairs)}")
        for title, code in pairs:
            if code in existing or code in seen_new: continue
            name = good_name(title)
            if not name: continue
            out.append({"name": name, "invite": f"https://chat.whatsapp.com/{code}",
                        "desc": f"Join {name}, a WhatsApp group for entertainment, movies and fun.",
                        "cat": "Entertainment"})
            seen_new.add(code); added += 1
        time.sleep(8)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log(f"ADDED {added}, TOTAL {len(out)}")

if __name__ == '__main__':
    main()
