#!/usr/bin/env python3
"""TEAM 208 (business): Scrape business/forex/online-earning WhatsApp directories.
Dedupes by invite code vs _seen_all_codes.pkl. Saves NEW groups to scraped/team208-business.json.
Each: {"name","invite","desc","cat"}.
"""
import re, json, time, html, os, pickle
import urllib.request, urllib.error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT_PATH = os.path.join(SCRAPED, 'team208-business.json')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

# (url, default_cat, filter_relevant_only)
PAGES = [
    ("https://77links.com/buy-and-sell-whatsapp-group-links/", "Business", False),
    ("https://77links.com/cryptocurrency-whatsapp-group-links/", "Online Earning", False),
    ("https://77links.com/digital-marketing-whatsapp-group-links/", "Business", False),
    ("https://77links.com/international-business-whatsapp-group-links/", "Business", False),
    ("https://77links.com/online-earning-whatsapp-groups/", "Online Earning", False),
    ("https://77links.com/real-estate-whatsapp-group-links/", "Business", False),
    ("https://77links.com/shopping-whatsapp-group-links/", "Business", False),
    ("https://77links.com/fashion-whatsapp-group-links/", "Business", False),
]

INVITE_RE = re.compile(r'https?://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{8,})')

PORN_RE = re.compile(r'(?i)\b(porn|pornhub|xxx\b|sexy|nudes?\b|escorts?|call\s*girls?|desi\s*bhabhi|adult\s*(video|dating|chat)|hentai|onlyfans|cam\s*girls?|bhabhi\s*sex|18\s*\+\s*(video|sex|group))\b')
SCAM_RE = re.compile(r'(?i)(flash(ing)?\s*(usdt|software|tether)|carding|nadra\s*(data|record)|redeem\s*code\s*giveaway|free\s*internet\s*vpn|aviator|pak92|betting|id\s*seller|trusted\s*id|uc\s*carding|hack(er|ing)\s*(tool|software)|forsage|\bebl\b|mlm\s*scam|double\s*your\s*money)')

EARN_KW = re.compile(r'(?i)(earn|money|income|invest|trad|forex|signal|crypto|binance|bitcoin|work\s*from\s*home|refer|loot|cash|paisa|kamai|reward|rich|profit|salary|job)')
BIZ_KW = re.compile(r'(?i)(business|entrepreneur|startup|marketing|resell|wholesale|e-?commerce|import|export|freelanc|dropship|affiliate|brand|store|shop|bazaar|deal|seller|buyer|network|investor|consult)')


def fetch(url, timeout=30):
    import http.client
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                try:
                    return r.read().decode('utf-8', errors='ignore')
                except http.client.IncompleteRead as e:
                    print('  partial read, using %d bytes' % len(e.partial))
                    return e.partial.decode('utf-8', errors='ignore')
        except http.client.IncompleteRead as e:
            print('  partial read (outer), using %d bytes' % len(e.partial))
            return e.partial.decode('utf-8', errors='ignore')
        except Exception as e:
            print('  fetch fail (%s): %s' % (attempt, str(e)[:80]))
            time.sleep(3)
    return None


def strip_tags(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def extract_name(chunk_html):
    # drop trailing incomplete tag fragment like <a href=" or <a class="kb-button
    chunk = re.sub(r'<[^>]*$', '', chunk_html)
    # prefer <em>name</em>
    ems = re.findall(r'<em[^>]*>(.*?)</em>', chunk, re.DOTALL)
    if ems:
        t = ems[-1]
    else:
        # 77links-style: last <p>Name: description</p> before the join button
        ps = re.findall(r'<p[^>]*>(.*?)</p>', chunk, re.DOTALL)
        t = ''
        for p in reversed(ps):
            pt = re.sub(r'<[^>]+>', ' ', p)
            pt = html.unescape(re.sub(r'\s+', ' ', pt)).strip()
            # strip 77links artifacts: leading 'sf ', trailing 'Join' button label
            pt = re.sub(r'^sf\s+', '', pt)
            pt = re.sub(r'\s+Join(\s+(Now|Group|Here|Us))?\s*$', '', pt, flags=re.I).strip()
            if len(pt) < 3:
                continue
            if re.match(r'^(join|click)\b', pt, re.I) or 'join our' in pt.lower():
                continue
            if ':' in pt:
                cand = pt.split(':')[0].strip()
                if 3 <= len(cand) <= 60:
                    t = cand
                    break
            else:
                # no colon: try leading ALL-CAPS run as the name
                # e.g. "ALPHAS CRYPTO SIGNALS Get Free Binance..." -> "ALPHAS CRYPTO SIGNALS"
                cm = re.match(r'^((?:[^\sa-z]{2,}\s+){1,8})', pt)
                if cm and len(cm.group(1).strip()) >= 3:
                    t = cm.group(1).strip()
                    break
                elif len(pt) <= 80:
                    t = pt
                    break
        if not t:
            # remove trailing <a>...</a> join link
            tc = re.sub(r'<a\b[^>]*>.*$', '', chunk, flags=re.DOTALL)
            # prefer heading text if present
            hs = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', tc, re.DOTALL)
            if hs:
                t = hs[-1]
            else:
                parts = re.split(r'</(?:p|div|li)>', tc)
                t = parts[-1] if parts else tc
    t = strip_tags(t)
    # strip comment-date prefixes: "March 10, 2025 at 10:47 AM ..."
    t = re.sub(r'^(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\s+at\s+\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\s*', '', t).strip()
    # drop trailing join/link words
    t = re.sub(r'(?i)[\s\-–—|👉:;_]*\b(join(\s*(now|in|group|here))?|click\s*here|tap\s*here)\b[\s\-–—|👉:;_]*$', '', t).strip()
    t = re.sub(r'\s+', ' ', t).strip(' -–—|:👉_;')
    return t[:120]


def categorize(name, default):
    if BIZ_KW.search(name) and not EARN_KW.search(name):
        return "Business"
    if EARN_KW.search(name):
        return "Online Earning"
    return default


def make_desc(name, cat):
    if cat == "Online Earning":
        return "Join %s — an active WhatsApp group for online earning tips, money-making ideas and updates." % name
    return "Join %s — an active WhatsApp business group for networking, deals and business opportunities." % name


def main():
    seen = set(pickle.load(open(os.path.join(SCRAPED, '_seen_all_codes.pkl'), 'rb')))
    print('seen codes:', len(seen))
    # incremental: load existing results
    results, run_codes = [], set()
    if os.path.exists(OUT_PATH):
        try:
            results = json.load(open(OUT_PATH, encoding='utf-8'))
            for r in results:
                m = INVITE_RE.search(r.get('invite', ''))
                if m:
                    run_codes.add(m.group(1))
                    seen.add(m.group(1))
            print('loaded existing:', len(results))
        except Exception as e:
            print('load existing failed:', e)
    stats = {'raw': 0, 'new': 0, 'dup': 0, 'porn': 0, 'scam': 0, 'noname': 0, 'fail': 0}

    # direct link from search result (DeCliff VIP Forex Signals) - only if not present
    if "IKNhOcQXg2o91lD2puOnrS" not in run_codes and "IKNhOcQXg2o91lD2puOnrS" not in seen:
        results.append({
            "name": "DeCliff VIP Forex Signals",
            "invite": "https://chat.whatsapp.com/IKNhOcQXg2o91lD2puOnrS",
            "desc": "Join DeCliff VIP Forex Signals — daily forex trade signals with expert market analysis on WhatsApp.",
            "cat": "Online Earning",
        })
        run_codes.add("IKNhOcQXg2o91lD2puOnrS")
        stats['new'] += 1

    for url, default_cat, filter_rel in PAGES:
        print('FETCH:', url)
        content = fetch(url)
        if not content:
            stats['fail'] += 1
            continue
        matches = list(INVITE_RE.finditer(content))
        pnew = 0
        for m in matches:
            stats['raw'] += 1
            code = m.group(1)
            if code in run_codes or code in seen:
                stats['dup'] += 1
                continue
            # take a wide window: name may sit in a preceding sibling column
            # (e.g. 77links: <p>Name: desc</p> in previous wp-block-column)
            chunk = content[max(0, m.start() - 2000):m.start()]
            name = extract_name(chunk)
            if not name or len(name) < 3:
                stats['noname'] += 1
                continue
            if filter_rel and not (EARN_KW.search(name) or BIZ_KW.search(name)):
                continue
            if PORN_RE.search(name):
                stats['porn'] += 1
                continue
            if SCAM_RE.search(name):
                stats['scam'] += 1
                continue
            cat = categorize(name, default_cat)
            results.append({
                "name": name,
                "invite": "https://chat.whatsapp.com/" + code,
                "desc": make_desc(name, cat),
                "cat": cat,
            })
            run_codes.add(code)
            stats['new'] += 1
            pnew += 1
        print('  matches: %d, new: %d' % (len(matches), pnew))
        time.sleep(1.5)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print('stats:', stats)
    print('saved %d to %s' % (len(results), OUT_PATH))


if __name__ == '__main__':
    main()
