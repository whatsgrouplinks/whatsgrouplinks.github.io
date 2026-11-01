#!/usr/bin/env python3
"""TEAM 207 wave 8: re-scrape via r.jina.ai text proxy (markdown with full URLs)."""
import re, json, html, time, os, pickle
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'scraped', 'team207-entertainment.json')
LOG = os.path.join(BASE, 'scraped', 'team207-wave8.log')
PKL = os.path.join(BASE, 'scraped', '_existing_invites.pkl')
GROUPS_JSON = os.path.join(BASE, 'groups.json')

PAGES = [
    "https://www.whtsagrouplinks.com/movies-whatsapp-group-link/",
    "https://whtsgrouplink.com/movies-whatsapp-group-links/",
    "https://pkwhatsgrouplinks.com/movies-whatsapp-group-links/",
    "https://whtspgrouplink.com/1000-members-whatsapp-group-links/",
    "https://whtspgrouplink.com/south-indian-whatsapp-group-links/",
    "https://77links.com/tamil-whatsapp-group-links/",
    "https://freewagroup.com/tamil-whatsapp-group-links/",
    "https://instantgrouplink.com/drama-whatsapp-group-links/",
    "https://activewagroup.com/drama-whatsapp-group-links/",
    "https://wagroupnest.com/drama-whatsapp-group-links/",
    "https://wagroupshub.com/drama-whatsapp-group-links/",
    "https://wahublink.com/entertainment-whatsapp-group-links/",
    "https://whatstele.com/whatsapp/group-links/best-stickers/",
    "https://whatstele.com/whatsapp/group-links/memes-stickers/",
    "https://wagrouplinks.online/memes-whatsapp-group-links/",
    "https://whatsagroupslinks.com/memes-whatsapp-group-links/",
    "https://whatgroups.com/tamil-whatsapp-group-links/",
    "https://whatsagroupslinks.com/tamil-whatsapp-group-links/",
    "https://wagroupnest.com/tamil-whatsapp-group-links/",
    "https://whatsagroupslinks.com/punjabi-whatsapp-group-links/",
    "https://hubrecipes.com/best-movies-whatsapp-group-links/",
    "https://whatslists.com/telugu-movies-whatsapp-group-links/",
    "https://hubrecipes.com/join-active-mallu-whatsapp-group-links/",
    "https://groupda.com/singer/arijit-singh-whatsapp-group-links-join-list/",
    "https://geeksgyaan.com/2020/11/whatsapp-group-links.html",
    "https://technoearning.in/06/join-interesting-whatsapp-group-whatsapp-group-joining-link/",
    "https://www.whtsagrouplinks.com",
    "https://whatsgroulink.com/",
    "http://grouplink.com.in/600-whatsapp-groups-for-indian-and-pakistani-dramas/",
    "http://whtspgroup.com/pakistani-drama-whatsapp-group/",
    "https://whatsgroulinks.com/active-tamil-whatsapp-group-links-new-updated/",
    "https://www.groupjoin.link/tag/Music?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Movies?safeSearch=moderate",
    "https://www.groupjoin.link/tag/Comedy?safeSearch=moderate",
]
URLS = ["https://r.jina.ai/" + u for u in PAGES]

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36'}
BLOCK = [r'\bporn\b', r'\bxxx\b', r'\bjav\b', r'\bsax\b', r'18\s*\+', r'\bsex\b', r'\bsexy\b',
         r'\badult\b', r'\bnude\b', r'\bnaked\b', r'\bescort\b', r'\bbhabhi\b',
         r'\bmms\b', r'\bleak\w*\b', r'viral\s*video', r'h\*t', r'p\*\*',
         r'hot\s*girl', r'night\s*\w*\s*girl', r'call\s*girl', r'\bdesi\s*(girl|mms)',
         r'\bitem\s*girl', r'aunty\s*hot', r'malaya', r'ngono', '🍆', '🍑', '💦']
BLOCK_RE = re.compile('|'.join(BLOCK), re.I)
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{16,30})')
OFFTOPIC = re.compile(r'\b(health|medicine|doctor|hospital|clinic|job|jobs|hiring|salary|career|news|newspaper|politic|election|study|exam|school|college|university|admission|scholarship|crypto|forex|trading|betting|loan|business|real[\s-]?estate|islamic|quran|namaz|dua|dars|bayan|matrimonial|rishta|shaadi|shopping|sale|offer|deal|discount|earn(ing)?\s*money|friendship|dosti|bhaichara|pubg|free\s*fire|bgmi)\b', re.I)
# markdown: * Name – [**Join**](url)  or  | Name | [Join](url) |
MD_PAT = re.compile(r'(?:^|\n)[*\-]\s+(.+?)\s*[–\-]\s*\[?\*{0,2}?(?:Join|Link|Click Here)\*{0,2}?\]?\((https://chat\.whatsapp\.com/[A-Za-z0-9]{16,30})[^)]*\)', re.I)
TD_PAT = re.compile(r'\|\s*([^|\n]+?)\s*\|\s*\[?\*{0,2}?(?:Join|Link|Click Here)\*{0,2}?\]?\((https://chat\.whatsapp\.com/[A-Za-z0-9]{16,30})[^)]*\)\s*\|', re.I)

def log(msg):
    open(LOG, 'a').write(msg + '\n'); print(msg, flush=True)

def clean(t):
    t = html.unescape(t)
    t = re.sub(r'[*_#`~]+', '', t)
    return re.sub(r'\s+', ' ', t).strip(' –-|:;•·').strip()

def fetch(url, timeout=60):
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception:
            time.sleep(4)
    return None

def extract(md):
    pairs, seen = [], set()
    for pat in (MD_PAT, TD_PAT):
        for m in pat.finditer(md):
            name, url = clean(m.group(1)), m.group(2)
            cm = CODE_RE.search(url)
            if not cm: continue
            code = cm.group(1)
            if code in seen or not name: continue
            if name.lower() in ('join', 'join now', 'click here', 'join group', 'link'): continue
            pairs.append((name, code)); seen.add(code)
    # fallback: any remaining code -> nearest preceding markdown line text
    for m in CODE_RE.finditer(md):
        code = m.group(1)
        if code in seen: continue
        before = md[max(0, m.start() - 300):m.start()]
        lines = [l for l in before.split('\n') if l.strip()]
        name = clean(lines[-1]) if lines else ''
        if name.lower() in ('join', 'join now', 'click here', 'join group', 'link', ''): name = ''
        pairs.append((name, code)); seen.add(code)
    return pairs

def good_name(name):
    name = clean(name)
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
        existing.add(g['invite'].split('/')[-1])
    log(f"existing: {len(existing)}, current: {len(out)}")
    results = {}
    def work(url):
        md = fetch(url); time.sleep(2)
        if not md: log(f"FAIL {url[19:60]}"); return
        pairs = extract(md)
        log(f"OK {url[19:60]} pairs={len(pairs)}")
        results[url] = pairs
    with ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(work, URLS))
    seen_new, added = set(), 0
    for url in URLS:
        for name, code in results.get(url, []):
            if code in existing or code in seen_new: continue
            name = good_name(name)
            if not name: continue
            out.append({"name": name, "invite": f"https://chat.whatsapp.com/{code}",
                        "desc": f"Join {name}, a WhatsApp group for entertainment, movies and fun.",
                        "cat": "Entertainment"})
            seen_new.add(code); added += 1
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log(f"ADDED {added}, TOTAL {len(out)}")

if __name__ == '__main__':
    main()
