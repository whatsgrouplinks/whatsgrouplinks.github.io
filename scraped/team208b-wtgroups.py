#!/usr/bin/env python3
"""TEAM 208b: Crawl wtgrouplinks.com /whatsapp-group/ pages (fresh, unscraped).
Seeds -> collect /whatsapp-group/ slugs -> fetch each -> title + most-frequent chat code.
Keeps business/earning relevant only. Dedupes vs _seen_all_codes.pkl + team208-business.json.
Appends to scraped/team208-business.json.
"""
import re, json, time, html, os, pickle
import urllib.request
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT_PATH = os.path.join(SCRAPED, 'team208-business.json')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

SEEDS = [
    "https://wtgrouplinks.com/whatsapp-group/sure-shot-traders/",
    "https://wtgrouplinks.com/whatsapp-group/globalbridge-imports/",
    "https://wtgrouplinks.com/whatsapp-group/olivier-digital-communaute/",
    "https://wtgrouplinks.com/whatsapp-group/cryptocurrency-and-airdrops/",
    "https://wtgrouplinks.com/whatsapp-group/gen-z-nation-earning-club/",
    "https://wtgrouplinks.com/whatsapp-group/millionaire-chat/",
    "https://wtgrouplinks.com/business-whatsapp-group-links/",
    "https://wtgrouplinks.com/refer-and-earn-whatsapp-group-link/",
    "https://wtgrouplinks.com/",
]

INVITE_RE = re.compile(r'https?://chat\.whatsapp\.com/([A-Za-z0-9]{8,})')
SLUG_RE = re.compile(r'href="(https://wtgrouplinks\.com/whatsapp-group/[^"#?]+?/?)"')
PORN_RE = re.compile(r'(?i)\b(porn|pornhub|xxx\b|sexy|nudes?\b|escorts?|call\s*girls?|desi\s*bhabhi|adult\s*(video|dating|chat)|hentai|onlyfans|cam\s*girls?|18\s*\+\s*(video|sex|group)|swiss-adulst)\b')
SCAM_RE = re.compile(r'(?i)(flash(ing)?\s*(usdt|software|tether)|carding|redeem\s*code\s*giveaway|aviator|betting|forsage|\bebl\b|double\s*your\s*money|diamond\s*pay)')
EARN_KW = re.compile(r'(?i)(earn|money|income|invest|trad|forex|signal|crypto|binance|bitcoin|work\s*from\s*home|refer|loot|cash|paisa|kamai|reward|rich|profit|millionaire|startup|business|entrepreneur|marketing|resell|wholesale|e-?commerce|import|export|freelanc|dropship|affiliate|brand|store|shop|bazaar|deal|seller|buyer|network|shopify|stock|mutual\s*fund|sip\b|bank|finance|gig|side\s*hustle)')


def fetch(url, timeout=45):
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print('  fail %s: %s' % (url[-40:], str(e)[:70]))
            time.sleep(4)
    return None


def clean_name(title):
    t = html.unescape(re.sub(r'\s+', ' ', title)).strip()
    t = re.sub(r'(?i)\s*(whatsapp group( links?)?|– wt group links|- wt group links|\[whatsapp group\]).*$', '', t).strip()
    t = t.strip(' -–—|:')
    return t[:120]


def main():
    seen = set(pickle.load(open(os.path.join(SCRAPED, '_seen_all_codes.pkl'), 'rb')))
    results = json.load(open(OUT_PATH, encoding='utf-8'))
    run_codes = set()
    for r in results:
        m = INVITE_RE.search(r.get('invite', ''))
        if m:
            run_codes.add(m.group(1))
            seen.add(m.group(1))
    print('existing results:', len(results))

    # direct snippet link: Reels banayo paisa kamao
    if 'CsGcMLRrHW6GhIncDIZxby' not in seen:
        results.append({
            "name": "Reels बनाओ पैसा कमाओ",
            "invite": "https://chat.whatsapp.com/CsGcMLRrHW6GhIncDIZxby",
            "desc": "Join Reels बनाओ पैसा कमाओ — an active WhatsApp group for online earning tips and money-making updates.",
            "cat": "Online Earning",
        })
        seen.add('CsGcMLRrHW6GhIncDIZxby')
        print('added snippet link')

    slugs = []
    for s in SEEDS:
        print('SEED:', s)
        h = fetch(s)
        if not h:
            continue
        for u in SLUG_RE.findall(h):
            u = u.rstrip('/') + '/'
            if u not in slugs and u not in SEEDS:
                slugs.append(u)
        time.sleep(2)
    print('slugs found:', len(slugs))
    slugs = slugs[:70]

    added = 0
    for i, u in enumerate(slugs):
        print('PAGE %d/%d: %s' % (i + 1, len(slugs), u))
        h = fetch(u)
        if not h:
            continue
        codes = Counter(INVITE_RE.findall(h))
        if not codes:
            time.sleep(2)
            continue
        code = codes.most_common(1)[0][0]
        if code in seen:
            time.sleep(2)
            continue
        m = re.search(r'<title>(.*?)</title>', h, re.DOTALL)
        name = clean_name(m.group(1)) if m else ''
        if not name or len(name) < 3 or not EARN_KW.search(name):
            time.sleep(2)
            continue
        if PORN_RE.search(name) or SCAM_RE.search(name):
            time.sleep(2)
            continue
        cat = "Online Earning" if re.search(r'(?i)(earn|money|income|invest|trad|forex|signal|crypto|binance|bitcoin|refer|loot|cash|reward|profit)', name) else "Business"
        desc = ("Join %s — an active WhatsApp group for online earning tips, money-making ideas and updates." % name
                if cat == "Online Earning" else
                "Join %s — an active WhatsApp business group for networking, deals and business opportunities." % name)
        results.append({"name": name, "invite": "https://chat.whatsapp.com/" + code, "desc": desc, "cat": cat})
        seen.add(code)
        added += 1
        print('  ADDED:', name)
        time.sleep(2)

    json.dump(results, open(OUT_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('added %d, total %d' % (added, len(results)))


if __name__ == '__main__':
    main()
