#!/usr/bin/env python3
"""Team 18: assemble final output files from all verify rounds (mismatch-aware)."""
import json, os, re, html as ihtml
from harvest import infer_country, describe, PORN

WORK = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(WORK)

MATH_BLOCKS = [
    (0x1D400, 0x1D419, ord('A')), (0x1D41A, 0x1D433, ord('a')), (0x1D7CE, 0x1D7D7, ord('0')),
    (0x1D434, 0x1D44D, ord('A')), (0x1D44E, 0x1D467, ord('a')),
    (0x1D468, 0x1D481, ord('A')), (0x1D482, 0x1D49B, ord('a')),
    (0x1D5A0, 0x1D5B9, ord('A')), (0x1D5BA, 0x1D5D3, ord('a')), (0x1D7E2, 0x1D7EB, ord('0')),
    (0x1D5D4, 0x1D5ED, ord('A')), (0x1D5EE, 0x1D607, ord('a')),
    (0x1D608, 0x1D621, ord('A')), (0x1D622, 0x1D63B, ord('a')),
    (0x1D63C, 0x1D655, ord('A')), (0x1D656, 0x1D66F, ord('a')), (0x1D7F6, 0x1D7FF, ord('0')),
    (0x1D538, 0x1D551, ord('A')), (0x1D552, 0x1D56B, ord('a')),
    (0x1D4D0, 0x1D4E9, ord('A')), (0x1D4EA, 0x1D503, ord('a')),
    (0x1D504, 0x1D51D, ord('A')), (0x1D51E, 0x1D537, ord('a')),
    (0x24B6, 0x24CF, ord('A')), (0x24D0, 0x24E9, ord('a')),
    (0x1F170, 0x1F189, ord('A')),
]
MATH_SINGLES = {0x2102: 'C', 0x210D: 'H', 0x2115: 'N', 0x2119: 'P', 0x211A: 'Q',
                0x211D: 'R', 0x2124: 'Z', 0x2133: 'M'}

def fold_math(t):
    out = []
    for ch in t:
        o = ord(ch)
        done = False
        for lo, hi, base in MATH_BLOCKS:
            if lo <= o <= hi:
                out.append(chr(base + (o - lo)))
                done = True
                break
        if done:
            continue
        if o in MATH_SINGLES:
            out.append(MATH_SINGLES[o])
        elif 0x1F1E6 <= o <= 0x1F1FF or 0x0300 <= o <= 0x036F:
            continue  # flags / combining marks
        else:
            out.append(ch)
    return ''.join(out)

def clean_og(title):
    t = fold_math(ihtml.unescape(title or ''))
    t = re.sub(r'[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u20E3\u00a9\u00ae]', ' ', t)
    # drop any remaining non-ASCII (decorative symbols, CJK, phonetic junk)
    t = re.sub(r'[^A-Za-z0-9\s\-&\'().!+]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip(' -|&;')
    return t[:90]

DOMAIN_NAME = re.compile(r'^[\w.-]*\.(com|net|org|in|pk|xyz|top|site|online)$', re.I)

def alnum(s):
    return len(re.sub(r'[^A-Za-z0-9]', '', s))

def norm(name):
    return re.sub(r'\s+', ' ', name).strip(' -:|')[:90]

EXCLUDE = re.compile(r'hack(ed)?|dead group|leve (this|the) group|revoked|not (working|active)', re.I)

def categorize(name):
    low = name.lower()
    if re.search(r'casino|world777|1xbet|betway', low):
        return 'Gaming'
    if re.search(r'mutual fund|investment|trading|forex|crypto', low):
        return 'Business'
    if re.search(r'\bstatus\b', low):
        return 'Entertainment'
    if re.search(r'e[\s-]?football|\bdls\b|dream league|pes\b|pubg|free fire', low):
        return 'Gaming'
    if re.search(r'sell(ing)?|\bbuy\b|store|shop|bazar|market', low):
        return 'Buy & Sell'
    return 'Sports'

def make_desc(name, cat):
    low = name.lower()
    if cat == 'Buy & Sell':
        return 'A buy-and-sell community group for deals, listings and local trade.'
    if cat == 'Business':
        return 'A business and investment discussion group for market talk and tips.'
    if cat == 'Entertainment':
        return 'A WhatsApp status-sharing group for videos, quotes and daily updates.'
    if cat == 'Gaming':
        if re.search(r'e[\s-]?football|\bdls\b|dream league|pes\b', low):
            return 'A mobile football gaming group for eFootball/Dream League Soccer players, tournaments and squad talk.'
        return 'A gaming community group for players, tournaments and game talk.'
    # Sports
    if re.search(r'football|soccer|messi|ronaldo|argentina|premier league|la liga', low):
        return 'A football fans group for match talk, live updates, transfer news and highlights.'
    if 'tennis' in low:
        return 'A tennis fans group for match updates, tournament talk and fan discussions.'
    if re.search(r'sport', low) and 'cricket' not in low:
        return 'A sports fans group for match updates, discussions and club news.'
    return describe(name)

fresh, pending, leads = [], [], []
seen_codes = set()
stats = {'excluded_hacked': 0, 'excluded_porn': 0, 'excluded_dup': 0}

def handle(code, listing_name, og_title, country_hint, source_page):
    global stats
    real = clean_og(og_title)
    name = real if (real and alnum(real) >= 3) else norm(listing_name)
    if code in seen_codes:
        stats['excluded_dup'] += 1
        return
    if PORN.search(name) or PORN.search(og_title or ''):
        stats['excluded_porn'] += 1
        return
    if EXCLUDE.search(name):
        stats['excluded_hacked'] += 1
        return
    if DOMAIN_NAME.match(name.replace(' ', '')):
        stats['excluded_domain'] = stats.get('excluded_domain', 0) + 1
        return
    if not name or alnum(name) < 3:
        leads.append({"name": listing_name or code, "code_or_invite": code,
                      "source_page": source_page,
                      "note": "Live but group name unclear; needs manual review"})
        return
    if re.search(r'[Ꭰ-Ᏼ]', name):
        leads.append({"name": name, "code_or_invite": code,
                      "source_page": source_page,
                      "note": "Live but name uses decorative Cherokee letters; manual review"})
        return
    cat = categorize(name)
    country = infer_country(name, country_hint)
    low = name.lower()
    if 'kerala' in low:
        country = 'IN'
    if 'isian' in low:
        country = 'ID'
    if 'rathnapura' in low:
        country = 'LK'
    fresh.append({"name": name, "category": cat, "country": country,
                  "description": make_desc(name, cat), "image": "",
                  "invite": f"https://chat.whatsapp.com/{code}",
                  "_source": source_page})
    seen_codes.add(code)

def load_results(path):
    try:
        return json.load(open(path))
    except FileNotFoundError:
        return []

def main():
    for r in load_results(os.path.join(WORK, 'verify_results.json')):
        if r['alive']:
            handle(r['code'], r['name'], r['og_title'], r.get('country_hint', 'XX'), r['source_page'])
    for r in load_results(os.path.join(WORK, 'verify_results2.json')):
        if r['alive']:
            handle(r['code'], r['name'], r['og_title'], r.get('country_hint', 'XX'), r['source_page'])
    for r in load_results(os.path.join(WORK, 'verify_results3.json')):
        if r['alive']:
            handle(r['code'], r['name'], r['og_title'], r.get('country_hint', 'XX'), r['source_page'])
    for r in load_results(os.path.join(WORK, 'verify_results4.json')):
        if r['alive']:
            handle(r['code'], r['name'], r['og_title'], r.get('country_hint', 'XX'), r['source_page'])

    for r in json.load(open('/tmp/team18_wild_verify.json')):
        if r['alive']:
            handle(r['code'], r.get('name', ''), r['og_title'], r['country'], 'search:mailchi.mp/medium.com/meetup.com')
    for r in json.load(open('/tmp/team18_tennis_verify.json')):
        if r['alive']:
            nm = 'Qasr Al Riyada Sports' if r['code'] == 'HiFDLcc15bxDAwR5p9vOt1' else ''
            handle(r['code'], nm, r['og_title'], r['country'], 'search:t.me')

    # ---- Truncated/garbled codes -> leads / pending ----
    leads.extend([
        {"name": "AH Sports Moon Knight Super League", "code_or_invite": "https://chat.whatsapp.com/BaMTwmJwNKa...",
         "source_page": "https://www.youtube.com/watch?v=FnuzwDanJ7E",
         "note": "Truncated invite code in video description; full 22-char code not published"},
        {"name": "Karauli Sports", "code_or_invite": "https://chat.whatsapp.com/DFjpoDRKFFF...",
         "source_page": "https://www.youtube.com/watch?v=ECNHmIU5uK8",
         "note": "Truncated invite code in video description; full 22-char code not published"},
        {"name": "Shine Sports FRIENDS MANI 2026", "code_or_invite": "https://chat.whatsapp.com/L8s7xbVjJS4...",
         "source_page": "https://www.youtube.com/watch?v=BK4bwou3XXg",
         "note": "Truncated invite code in video description; full 22-char code not published"},
    ])
    # minidea 'KKR Fan Club' had a bare chat.whatsapp.com/ with no code -> pending
    pending.append({"code": "", "source_page": "https://minidea.co.in/cricket-whatsapp-group-link/"})

    # source-aware description fixup: football-page items must not get cricket text
    for it in fresh:
        src = it.pop('_source', '')
        if it['category'] == 'Sports' and ('football' in src or 'messi' in src):
            if it['description'].startswith('A cricket'):
                it['description'] = ('A football fans group for match talk, live updates, '
                                     'transfer news and highlights.')

    json.dump(fresh, open(os.path.join(WAVE, 'team18-fresh-cricket-sports.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WAVE, 'team18-unverified-pending.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(leads, open(os.path.join(WAVE, 'team18-leads.json'), 'w'), ensure_ascii=False, indent=1)
    print('fresh:', len(fresh), 'pending:', len(pending), 'leads:', len(leads), 'stats:', stats)
    from collections import Counter
    print('categories:', Counter(x['category'] for x in fresh))
    print('countries:', Counter(x['country'] for x in fresh))

if __name__ == '__main__':
    main()
