#!/usr/bin/env python3
"""TEAM 207 wave 2: fresh domains not covered by earlier teams."""
import re, json, html, time, os, pickle, sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'scraped', 'team207-entertainment.json')
PKL = os.path.join(BASE, 'scraped', '_existing_invites.pkl')
GROUPS_JSON = os.path.join(BASE, 'groups.json')

URLS = [
    "https://www.groupjoin.link/tag/Netflixseries?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Movies?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Movie?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Music?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Songs?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Comedy?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Funny?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Jokes?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Drama?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Memes?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Bollywood?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Hollywood?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Anime?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Webseries?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Entertainment?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Tamil?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Kdrama?safeSearch=moderate",
    "https://www.pak24tv.net/group/netflix-whatsapp-group-link",
    "https://www.pak24tv.net/group/amazon-prime-whatsapp-group-link",
    "https://www.pak24tv.net/group/korean-dramas-whatsapp-group-link",
    "https://www.pak24tv.net/group/music-whatsapp-group-link",
    "https://www.pak24tv.net/group/anime-whatsapp-group-link",
    "https://www.pak24tv.net/group/funny-whatsapp-group-link",
    "https://www.pak24tv.net/group/movies-whatsapp-group-link",
    "https://www.pak24tv.net/group/web-series-whatsapp-group-link",
    "https://www.pak24tv.net/group/pakistani-dramas-whatsapp-group-link",
    "https://www.pak24tv.net/group/entertainment-whatsapp-group-link",
    "https://sites.google.com/view/whatsapp-group-link-join-and-s/home",
    "https://sites.google.com/view/12000-new-whatsapp-group-links/home",
    "https://77links.com",
    "https://digitalnamanji.com/whatsapp-group-link/",
]

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

BLOCK = [r'\bporn\b', r'\bxxx\b', r'\bjav\b', r'18\s*\+', r'\bsex\b', r'\bsexy\b',
         r'\badult\b', r'\bnude\b', r'\bnaked\b', r'\bescort\b', r'\bbhabhi\b',
         r'\bmms\b', r'\bleak\w*\b', r'viral\s*video', r'h\*t', r'p\*\*',
         r'hot\s*girl', r'night\s*\w*\s*girl', r'call\s*girl', r'\bdesi\s*(girl|mms)',
         r'\bitem\s*girl', r'aunty\s*hot', r'malaya', r'ngono']
BLOCK_RE = re.compile('|'.join(BLOCK), re.I)
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{16,30})')
# keep names entertainment-relevant; drop obvious off-topic
OFFTOPIC = re.compile(r'\b(health|medicine|doctor|hospital|job|jobs|hiring|salary|news|newspaper|politic|election|study|exam|school|college|university|admission|scholarship|crypto|forex|trading|betting|loan|business|real estate|islamic|quran|namaz|dua|dars|bayan|matrimonial|rishta|shaadi|marriage|dowry|shopping|sale|offer|deal|discount|earn money|earning)\b', re.I)

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
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def extract_pairs(page_html):
    pairs, seen = [], set()
    pat1 = re.compile(r'<td[^>]*>(.*?)</td>\s*<td[^>]*>\s*<a[^>]*href="[^"]*chat\.whatsapp\.com/([A-Za-z0-9]{16,30})[^"]*"', re.I | re.S)
    for m in pat1.finditer(page_html):
        if m.group(2) not in seen:
            pairs.append((clean_text(m.group(1)), m.group(2))); seen.add(m.group(2))
    pat2 = re.compile(r'<li[^>]*>(.*?)<a[^>]*href="[^"]*chat\.whatsapp\.com/([A-Za-z0-9]{16,30})[^"]*"', re.I | re.S)
    for m in pat2.finditer(page_html):
        if m.group(2) not in seen:
            pairs.append((clean_text(m.group(1)), m.group(2))); seen.add(m.group(2))
    # generic: any anchor with chat link -> anchor text or heading before
    pat3 = re.compile(r'(<h[1-4][^>]*>.*?</h[1-4]>|<a[^>]*>(.*?)</a>)\s*<a[^>]*href="[^"]*chat\.whatsapp\.com/([A-Za-z0-9]{16,30})[^"]*"[^>]*>(.*?)</a>', re.I | re.S)
    for m in pat3.finditer(page_html):
        code = m.group(3)
        if code in seen:
            continue
        name = clean_text(m.group(2) or '') or clean_text(m.group(4) or '')
        if name and name.lower() not in ('join', 'join now', 'click here', 'join group', 'link'):
            pairs.append((name, code)); seen.add(code)
    # fallback: nearest preceding text
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
    scraped = os.path.join(BASE, 'scraped')
    for fn in os.listdir(scraped):
        if not fn.endswith('.json'):
            continue
        try:
            d = json.load(open(os.path.join(scraped, fn)))
        except Exception:
            continue
        for g in (d if isinstance(d, list) else []):
            m = CODE_RE.search(g.get('invite') or '')
            if m: codes.add(m.group(1))
    return codes

def main():
    existing = load_existing()
    print(f"existing codes: {len(existing)}", flush=True)
    prev = []
    if os.path.exists(OUT):
        prev = json.load(open(OUT))
        for g in prev:
            m = CODE_RE.search(g.get('invite') or '')
            if m: existing.add(m.group(1))
    out, seen_new = list(prev), set()
    for url in URLS:
        print(f"fetch {url}", flush=True)
        page_html = fetch(url)
        time.sleep(1.2)
        if not page_html:
            print("  FAILED", flush=True); continue
        pairs = extract_pairs(page_html)
        added = 0
        for name, code in pairs:
            if code in existing or code in seen_new:
                continue
            name = clean_text(name).strip(' –-|:').strip()
            if not name or len(name) > 120 or len(name) < 2:
                continue
            if BLOCK_RE.search(name) or OFFTOPIC.search(name):
                continue
            out.append({"name": name,
                        "invite": f"https://chat.whatsapp.com/{code}",
                        "desc": f"Join {name}, a WhatsApp group for entertainment, movies and fun.",
                        "cat": "Entertainment"})
            seen_new.add(code); added += 1
        print(f"  pairs={len(pairs)} new={added}", flush=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"SAVED {len(out)} -> {OUT}", flush=True)

if __name__ == '__main__':
    main()
