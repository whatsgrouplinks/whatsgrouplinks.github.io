#!/usr/bin/env python3
"""TEAM 208 fixup: re-scrape wtgrouplinks listicles with proper name extraction,
repair bad entries in team208-business.json."""
import re, json, time, html, os
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT_PATH = os.path.join(SCRAPED, 'team208-business.json')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

PAGES = [
    "https://wtgrouplinks.com/business-whatsapp-group-links/",
    "https://wtgrouplinks.com/refer-and-earn-whatsapp-group-link/",
]
INVITE_RE = re.compile(r'https?://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{8,})')
PORN_RE = re.compile(r'(?i)\b(porn|pornhub|xxx\b|sexy|nudes?\b|escorts?|call\s*girls?|desi\s*bhabhi|adult\s*(video|dating|chat)|hentai|onlyfans|cam\s*girls?|18\s*\+\s*(video|sex|group))\b')
SCAM_RE = re.compile(r'(?i)(flash(ing)?\s*(usdt|software|tether)|carding|redeem\s*code\s*giveaway|aviator|betting|forsage|\bebl\b|double\s*your\s*money|diamond\s*pay)')


def fetch(url, timeout=45):
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print('  fail:', str(e)[:80])
            time.sleep(4)
    return None


def extract_name(li_html, match_start_in_li):
    """li_html: the <li>...</li> (or up-to-match) chunk."""
    before = li_html[:match_start_in_li]
    # remove trailing incomplete tag fragment like <a href="
    before = re.sub(r'<[^>]*$', '', before)
    # prefer <em>name</em>
    ems = re.findall(r'<em[^>]*>(.*?)</em>', before, re.DOTALL)
    if ems:
        t = ems[-1]
    else:
        # drop the trailing <a ...>...</a> join link if present
        t = re.sub(r'<a\b[^>]*>.*$', '', before, flags=re.DOTALL)
        # take text after last block boundary
        t = re.split(r'</(?:h\d|p|div)>', t)[-1]
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(r'(?i)[\s\-–—|👉:]*\b(join(\s*now)?|click\s*here)\b[\s\-–—|👉:]*$', '', t).strip()
    t = t.strip(' -–—|:👉').strip()
    return t[:120]


def main():
    data = json.load(open(OUT_PATH, encoding='utf-8'))
    by_code = {}
    for e in data:
        m = INVITE_RE.search(e.get('invite', ''))
        if m:
            by_code[m.group(1)] = e
    fixed, removed = 0, 0
    done_codes = set()
    for url in PAGES:
        print('FETCH:', url)
        h = fetch(url)
        if not h:
            continue
        for m in INVITE_RE.finditer(h):
            code = m.group(1)
            if code in done_codes:
                continue
            done_codes.add(code)
            li_start = h.rfind('<li', 0, m.start())
            chunk = h[li_start:m.start()] if li_start != -1 else h[max(0, m.start() - 500):m.start()]
            name = extract_name(chunk, len(chunk))
            e = by_code.get(code)
            if not e:
                continue
            old = e['name']
            bad = ('<a href' in old) or (' at ' in old and re.search(r'\d{4} at \d', old)) or len(old) < 3
            if not bad:
                continue
            if not name or len(name) < 3 or PORN_RE.search(name) or SCAM_RE.search(name):
                # drop unfixable
                data.remove(e)
                removed += 1
                print('  DROP', code, repr(old[:50]))
                continue
            e['name'] = name
            if re.search(r'(?i)(earn|money|income|invest|trad|forex|signal|crypto|binance|bitcoin|refer|loot|cash|reward|profit)', name):
                e['cat'] = 'Online Earning'
                e['desc'] = "Join %s — an active WhatsApp group for online earning tips, money-making ideas and updates." % name
            else:
                e['cat'] = 'Business'
                e['desc'] = "Join %s — an active WhatsApp business group for networking, deals and business opportunities." % name
            fixed += 1
            print('  FIX', repr(old[:45]), '->', repr(name[:60]))
        time.sleep(2)
    json.dump(data, open(OUT_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('fixed %d, removed %d, total %d' % (fixed, removed, len(data)))


if __name__ == '__main__':
    main()
