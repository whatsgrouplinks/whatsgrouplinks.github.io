#!/usr/bin/env python3
"""TEAM 207 (entertainment): scrape entertainment/movies/music/drama/memes/funny
WhatsApp directories, dedupe vs existing invites, save NEW groups.
Output: scraped/team207-entertainment.json  [{name, invite, desc, cat}]"""
import re, json, html, time, os, pickle, sys
import urllib.request, urllib.error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'scraped', 'team207-entertainment.json')
PKL = os.path.join(BASE, 'scraped', '_existing_invites.pkl')
GROUPS_JSON = os.path.join(BASE, 'groups.json')

URLS = [
    ("https://wahublink.com/entertainment-whatsapp-group-links/", "Entertainment"),
    ("https://www.whtsagrouplinks.com/movies-whatsapp-group-link/", "Entertainment"),
    ("https://pkwhatsgrouplinks.com/movies-whatsapp-group-links/", "Entertainment"),
    ("https://whtsgrouplink.com/movies-whatsapp-group-links/", "Entertainment"),
    ("https://www.whatsapplink.cazajobz.com/uae-funny-whatsapp-group-link/", "Entertainment"),
    ("https://instantgrouplink.com/drama-whatsapp-group-links/", "Entertainment"),
    ("https://activewagroup.com/drama-whatsapp-group-links/", "Entertainment"),
    ("https://wagroupnest.com/drama-whatsapp-group-links/", "Entertainment"),
    ("https://zoneofwagroup.com/drama-whatsapp-group-links/", "Entertainment"),
    ("https://wagroupshub.com/drama-whatsapp-group-links/", "Entertainment"),
    ("http://grouplink.com.in/600-whatsapp-groups-for-indian-and-pakistani-dramas/", "Entertainment"),
    ("https://77links.com/tamil-whatsapp-group-links/", "Entertainment"),
    ("https://freewagroup.com/tamil-whatsapp-group-links/", "Entertainment"),
    ("https://whtspgrouplink.com/south-indian-whatsapp-group-links/", "Entertainment"),
    ("https://whtspgrouplink.com/1000-members-whatsapp-group-links/", "Entertainment"),
    ("https://whatstele.com/whatsapp/group-links/best-stickers/", "Entertainment"),
    ("https://grupbul.com/group/173398", "Entertainment"),
    ("https://grupbul.com/group/726258", "Entertainment"),
    ("https://grupbul.com/group/964840", "Entertainment"),
]

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

BLOCK = [r'\bporn\b', r'\bxxx\b', r'\bjav\b', r'18\s*\+', r'\bsex\b', r'\bsexy\b',
         r'\badult\b', r'\bnude\b', r'\bnaked\b', r'\bescort\b', r'\bbhabhi\b',
         r'\bmms\b', r'\bleak\w*\b', r'viral\s*video', r'h\*t', r'p\*\*',
         r'hot\s*girl', r'night\s*\w*\s*girl', r'call\s*girl', r'\bdesi\s*(girl|mms)',
         r'\bitem\s*girl', r'aunty\s*hot', r'malaya', r'ngono', r'\bxx\b']
BLOCK_RE = re.compile('|'.join(BLOCK), re.I)

CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{16,30})')

def fetch(url, timeout=30):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return None

def clean_text(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def extract_pairs(page_html):
    """Return list of (name, code). Tries table-cell pairing then fallbacks."""
    pairs = []
    seen_here = set()
    # 1) table style: <td>NAME</td> ... <td><a href="...chat.whatsapp.com/CODE">
    pat1 = re.compile(
        r'<td[^>]*>(.*?)</td>\s*<td[^>]*>\s*<a[^>]*href="[^"]*chat\.whatsapp\.com/([A-Za-z0-9]{16,30})[^"]*"',
        re.I | re.S)
    for m in pat1.finditer(page_html):
        name, code = clean_text(m.group(1)), m.group(2)
        if code not in seen_here:
            pairs.append((name, code)); seen_here.add(code)
    # 2) list style: <li>... NAME ... <a href="...CODE">...</a></li>
    pat2 = re.compile(
        r'<li[^>]*>(.*?)<a[^>]*href="[^"]*chat\.whatsapp\.com/([A-Za-z0-9]{16,30})[^"]*"',
        re.I | re.S)
    for m in pat2.finditer(page_html):
        name, code = clean_text(m.group(1)), m.group(2)
        if code not in seen_here:
            pairs.append((name, code)); seen_here.add(code)
    # 3) fallback: any remaining code -> nearest preceding visible text
    for m in CODE_RE.finditer(page_html):
        code = m.group(1)
        if code in seen_here:
            continue
        before = page_html[max(0, m.start() - 600):m.start()]
        texts = re.findall(r'>([^<>]{3,120})<', before)
        name = clean_text(texts[-1]) if texts else ''
        pairs.append((name, code)); seen_here.add(code)
    return pairs

def load_existing():
    codes = set()
    if os.path.exists(PKL):
        try:
            s = pickle.load(open(PKL, 'rb'))
            if isinstance(s, set):
                codes |= {c.strip() for c in s if c}
        except Exception as e:
            print("pkl load err:", e, file=sys.stderr)
    if os.path.exists(GROUPS_JSON):
        try:
            gj = json.load(open(GROUPS_JSON))
            items = gj if isinstance(gj, list) else gj.get('groups', [])
            for g in items:
                inv = (g.get('invite') or '')
                m = CODE_RE.search(inv)
                if m:
                    codes.add(m.group(1))
        except Exception as e:
            print("groups.json load err:", e, file=sys.stderr)
    # also dedupe vs other scraped team files
    scraped = os.path.join(BASE, 'scraped')
    for fn in os.listdir(scraped):
        if not fn.endswith('.json') or fn.startswith('team207'):
            continue
        try:
            d = json.load(open(os.path.join(scraped, fn)))
            items = d if isinstance(d, list) else []
            for g in items:
                inv = (g.get('invite') or '')
                m = CODE_RE.search(inv)
                if m:
                    codes.add(m.group(1))
        except Exception:
            pass
    return codes

def main():
    existing = load_existing()
    print(f"existing codes: {len(existing)}", flush=True)
    out, seen_new = [], set()
    for url, cat in URLS:
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
            name = name.strip()
            if not name or len(name) > 120:
                continue
            if BLOCK_RE.search(name):
                continue
            invite = f"https://chat.whatsapp.com/{code}"
            out.append({
                "name": name,
                "invite": invite,
                "desc": f"Join {name}, a WhatsApp group for entertainment, movies and fun.",
                "cat": cat,
            })
            seen_new.add(code); added += 1
        print(f"  pairs={len(pairs)} new={added}", flush=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"SAVED {len(out)} -> {OUT}", flush=True)

if __name__ == '__main__':
    main()
