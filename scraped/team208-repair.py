#!/usr/bin/env python3
"""TEAM 208 repair v2: re-scrape all source pages with improved name extraction,
repair every bad name in team208-business.json by invite code. Drops unfixable.
Run AFTER batch jobs finish (it rewrites the file)."""
import re, json, time, html, os, pickle
import urllib.request
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT_PATH = os.path.join(SCRAPED, 'team208-business.json')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

# (url, default_cat) - all business/earning pages scraped by team208
PAGES = [
    ("https://www.whtsagrouplinks.com/forex-trading-whatsapp-group-links/", "Online Earning"),
    ("https://www.whtsagrouplinks.com/earn-money-whatsapp-group-link/", "Online Earning"),
    ("https://wahublink.com/online-earning-whatsapp-group-links/", "Online Earning"),
    ("https://www.whtsagrouplinks.com/work-from-home-whatsapp-group-links/", "Online Earning"),
    ("https://www.whtsagrouplinks.com/freelancer-whatsapp-group-links/", "Business"),
    ("https://appgrouplink.com/forex-trading-whatsapp-group-links/", "Online Earning"),
    ("https://whatgroups.com/forex-trading-whatsapp-group-links/", "Online Earning"),
    ("https://joingram.in/online-earning-whatsapp-group-links/", "Online Earning"),
    ("https://coinweb.com/crypto-trading-signals-on-whatsapp/", "Online Earning"),
    ("https://whatstele.com/whatsapp/group-links/stock-market/", "Online Earning"),
    ("https://whtsgrouplink.com/reseller-whatsapp-group-links/", "Business"),
    ("https://www.whtsagrouplinks.com/clothing-whatsapp-group-links/", "Business"),
    ("https://whtspgrouplink.com/usa-buy-and-sell-whatsapp-group-links/", "Business"),
    ("https://whtsgrouplink.com/fashion-whatsapp-group-links/", "Business"),
    ("https://thewhatspgrouplinks.com/usa-business-whatsapp-group-links/", "Business"),
    ("https://thewhatspgrouplinks.com/indian-business-whatsapp-group-links/", "Business"),
    ("https://whtspgrouplink.com/uae-business-whatsapp-group-links/", "Business"),
    ("https://hubrecipes.com/active-business-whatsapp-group-links/", "Business"),
    ("https://thinkingoutsidethesandbox.ca/135-best-business-whatsapp-group-links/", "Business"),
    ("https://www.whtsagrouplinks.com/buy-and-sell-whatsapp-group-links/", "Business"),
    ("https://wagroupzone.com/", "Online Earning"),
    ("https://freshgrouplinks.com/crypto-trading-whatsapp-group-links/", "Online Earning"),
    ("https://whtsgrouplink.com/forex-whatsapp-group-links/", "Online Earning"),
    ("https://sites.google.com/view/bucksaw-links/home", "Online Earning"),
    ("https://www.whtsagrouplinks.com/pakistani-whatsapp-group-link/", "Online Earning"),
    ("https://wtgrouplinks.com/business-whatsapp-group-links/", "Business"),
    ("https://wtgrouplinks.com/refer-and-earn-whatsapp-group-link/", "Online Earning"),
    ("https://freshgrouplinks.com/social-media-marketing-whatsapp-group-links/", "Business"),
    ("https://www.whtsagrouplinks.com/trading-whatsapp-group-links/", "Online Earning"),
    ("https://www.whtsagrouplinks.com/blogger-whatsapp-group-link/", "Business"),
    ("https://whatsgroulink.com/", "Business"),
    ("https://freewagroup.com/indian-whatsapp-group-links/", "Online Earning"),
    ("https://grouplink.com.in/mysore/", "Online Earning"),
    ("https://whtsgrouplink.com/digital-marketing-whatsapp-group-links/", "Business"),
    ("https://whtsgrouplink.com/earn-money-whatsapp-group-links/", "Online Earning"),
    ("https://whtsgrouplink.com/freelancer-whatsapp-group-links/", "Business"),
    ("https://whtsgrouplink.com/new-business-idea-whatsapp-group-links/", "Business"),
    ("https://whtsgrouplink.com/share-market-whatsapp-group-links/", "Online Earning"),
    ("https://hubrecipes.com/active-work-from-home-whatsapp-group-links/", "Online Earning"),
]

INVITE_RE = re.compile(r'https?://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{8,})')
PORN_RE = re.compile(r'(?i)\b(porn|pornhub|xxx\b|sexy|nudes?\b|escorts?|call\s*girls?|desi\s*bhabhi|adult\s*(video|dating|chat)|hentai|onlyfans|cam\s*girls?|18\s*\+\s*(video|sex|group)|indian xxx|xxx video)\b')
SCAM_RE = re.compile(r'(?i)(flash(ing)?\s*(usdt|software|tether)|carding|nadra\s*(data|record)|redeem\s*code\s*giveaway|free\s*internet\s*vpn|aviator|pak92|betting|id\s*seller|trusted\s*id|uc\s*carding|hack(er|ing)\s*(tool|software)|forsage|\bebl\b|double\s*your\s*money|diamond\s*pay|monthly profit 15)')


def fetch(url, timeout=40):
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print('  fail %s: %s' % (url[:60], str(e)[:70]))
            time.sleep(4)
    return None


def clean_name(raw):
    t = html.unescape(raw)
    t = re.sub(r'\s+', ' ', t).strip()
    # strip comment-date prefixes: "March 10, 2025 at 10:47 AM ..."
    t = re.sub(r'^(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\s+at\s+\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\s*', '', t).strip()
    # strip trailing join/link words
    t = re.sub(r'(?i)[\s\-–—|👉:;_]*\b(join(\s*(now|in|group|here))?|click\s*here|tap\s*here)\b[\s\-–—|👉:;_]*$', '', t).strip()
    t = t.strip(' -–—|:👉_;').strip()
    return t[:120]


def extract_name(chunk_html):
    # drop trailing incomplete tag fragment
    chunk = re.sub(r'<[^>]*$', '', chunk_html)
    # prefer <em>name</em>
    ems = re.findall(r'<em[^>]*>(.*?)</em>', chunk, re.DOTALL)
    if ems:
        t = ems[-1]
    else:
        # remove trailing <a>...</a> join link
        t = re.sub(r'<a\b[^>]*>.*$', '', chunk, flags=re.DOTALL)
        # prefer heading text if present
        hs = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', t, re.DOTALL)
        if hs:
            t = hs[-1]
        else:
            parts = re.split(r'</(?:p|div|li)>', t)
            t = parts[-1] if parts else t
    t = re.sub(r'<[^>]+>', ' ', t)
    return clean_name(t)


def main():
    data = json.load(open(OUT_PATH, encoding='utf-8'))
    print('loaded', len(data))
    # build code->name map by re-scraping
    name_map = {}
    for url, default_cat in PAGES:
        print('FETCH:', url)
        h = fetch(url)
        if not h:
            continue
        for m in INVITE_RE.finditer(h):
            code = m.group(1)
            if code in name_map:
                continue
            start = -1
            for tag in ('<li', '<tr', '<td', '<div', '<h1', '<h2', '<h3', '<h4', '<p'):
                i = h.rfind(tag, 0, m.start())
                if i > start:
                    start = i
            chunk = h[start:m.start()] if start != -1 else h[max(0, m.start() - 600):m.start()]
            name = extract_name(chunk)
            if name and len(name) >= 3:
                name_map[code] = name
        time.sleep(1.5)
    print('name map:', len(name_map))

    fixed, dropped, kept = 0, 0, 0
    out = []
    for e in data:
        m = INVITE_RE.search(e.get('invite', ''))
        code = m.group(1) if m else ''
        name = clean_name(e.get('name', ''))
        if (not name or len(name) < 3 or '<' in name) and code in name_map:
            name = name_map[code]
            fixed += 1
        if not name or len(name) < 3 or '<' in name:
            dropped += 1
            continue
        if PORN_RE.search(name) or SCAM_RE.search(name):
            dropped += 1
            continue
        e['name'] = name
        cat = "Online Earning" if re.search(r'(?i)(earn|money|income|invest|trad|forex|signal|crypto|binance|bitcoin|work\s*from\s*home|refer|loot|cash|paisa|kamai|reward|profit)', name) else ("Business" if re.search(r'(?i)(business|entrepreneur|startup|marketing|resell|wholesale|e-?commerce|import|export|freelanc|dropship|affiliate|brand|store|shop|bazaar|deal|seller|buyer|network)', name) else e.get('cat', 'Business'))
        e['cat'] = cat
        e['desc'] = ("Join %s — an active WhatsApp group for online earning tips, money-making ideas and updates." % name
                     if cat == "Online Earning" else
                     "Join %s — an active WhatsApp business group for networking, deals and business opportunities." % name)
        out.append(e)
        kept += 1
    json.dump(out, open(OUT_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('kept %d, fixed %d, dropped %d' % (kept, fixed, dropped))


if __name__ == '__main__':
    main()
