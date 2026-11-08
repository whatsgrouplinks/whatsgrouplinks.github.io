#!/usr/bin/env python3
"""TEAM 46R finalize: filter verified_raw -> team46-crypto-earning.json + pending.
Porn/scam exclusion per brief; category/country/description assignment."""
import json, os, re, html

BASE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(BASE)

PORN_PAT = re.compile(r'porn|pornhub|xxx|nude|sex video|escort|call girl|fuck|dick|pussy|boobs|anal(?!ysis)|🥵|🍆|🍑|🔞|💦|👅|👄|💋', re.I)
SCAM_PAT = re.compile(r'paypal.*(receiver|loader)|counterfeit|passcode|flash.*usdt|usdt.*flash|fake (currency|note|cash)|carding|money mule|dumps|clone card', re.I)
# "Xxxx left" / "XXXX" placeholder titles are junk, NOT porn — drop as junk instead
JUNK_PAT = re.compile(r'^[xX\s.,\-_]*$', re.I)

EARN_WORDS = re.compile(r'earn|income|money|work from home|freelanc|fiverr|business|refer|paisa|pesa|salary|job|online work|earning|income|dollar', re.I)
CRYPTO_WORDS = re.compile(r'crypto|bitcoin|btc|forex|fx|trading|trade|signal|airdrop|binance|mining|pips|gold|xau|deriv|binary|usdt|coin|ethereum|eth', re.I)

COUNTRY_HINTS = [
    (re.compile(r'pakistan|pkr|lahore|karachi|islamabad|urd[u]?', re.I), 'PK'),
    (re.compile(r'india|hindi|paytm|upi|₹|mumbai|delhi|chennai|kerala|tamil', re.I), 'IN'),
    (re.compile(r'nigeria|naira|₦', re.I), 'NG'),
    (re.compile(r'bangladesh|bdt|bengali', re.I), 'BD'),
    (re.compile(r'kenya|mpesa', re.I), 'KE'),
    (re.compile(r'ghana', re.I), 'GH'),
    (re.compile(r'nepal', re.I), 'NP'),
    (re.compile(r'uae|dubai|emirates', re.I), 'AE'),
    (re.compile(r'saudi', re.I), 'SA'),
    (re.compile(r'uk|britain|london', re.I), 'GB'),
    (re.compile(r'usa|america', re.I), 'US'),
]

def clean_title(t):
    t = html.unescape(t)
    t = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def pick_country(title):
    for pat, cc in COUNTRY_HINTS:
        if pat.search(title):
            return cc
    return 'PK'  # grouplinksforyou/newgrouplinks/whatgroups are PK-oriented sources

def pick_category(title):
    if CRYPTO_WORDS.search(title):
        return 'Crypto'
    if EARN_WORDS.search(title):
        return 'Finance'
    return 'Finance'

def clean_topic(t):
    t = clean_title(t)
    t = re.sub(r'(?i)\s*(whatsapp|group|links?|official|™|®|free|vip|community)\b', '', t)
    t = re.sub(r'\s+', ' ', t).strip(' -|·•')
    return t[:80] or t

COUNTRY_WORD = {'PK': 'Pakistan', 'IN': 'India', 'NG': 'Nigeria', 'BD': 'Bangladesh',
                'KE': 'Kenya', 'GH': 'Ghana', 'NP': 'Nepal', 'AE': 'UAE', 'SA': 'Saudi Arabia',
                'GB': 'the UK', 'US': 'the USA'}

def make_desc(title, cat, cc):
    topic = clean_topic(title)
    cw = COUNTRY_WORD.get(cc, 'Asia')
    if cat == 'Crypto':
        return (f"Active crypto community in {cw} sharing {topic.lower()} insights — daily trading signals, "
                f"market analysis and discussion for beginners and experienced crypto traders alike.")
    if cat == 'Business':
        return (f"Business networking WhatsApp group in {cw} focused on {topic.lower()} — freelancing tips, "
                f"work-from-home income ideas and community support.")
    return (f"Online earning community in {cw} sharing {topic.lower()} tips — passive income ideas, "
            f"money-making strategies and guidance for members.")

def main():
    raw = json.load(open(os.path.join(BASE, 'team46r_verified_raw.json')))
    state = json.load(open(os.path.join(BASE, 'team46r_verify_state.json')))
    union = set(json.load(open(os.path.join(WAVE, 'dedupe_union.json'))))

    items, porn, scam, junk, seen = [], 0, 0, 0, set()
    flagged_scam = []
    for r in raw:
        title = r['name']
        code = r['code']
        if JUNK_PAT.fullmatch(title.strip()) and title.strip():
            junk += 1
            continue
        if PORN_PAT.search(title):
            porn += 1
            continue
        if SCAM_PAT.search(title):
            scam += 1
            flagged_scam.append({'code': code, 'name': title, 'why': 'money-mule/phishing flavor'})
            continue
        if code in union or code in seen:
            continue
        seen.add(code)
        cat = pick_category(title)
        cc = pick_country(title)
        clean = clean_title(title) or r.get('srcname', '') or 'Crypto Earning Group'
        items.append({
            'name': clean,
            'category': cat,
            'country': cc,
            'description': make_desc(clean, cat, cc),
            'invite': f'https://chat.whatsapp.com/{code}',
            'image': '',
        })

    json.dump(items, open(os.path.join(WAVE, 'team46-crypto-earning.json'), 'w'), ensure_ascii=False, indent=1)

    pending = []
    for p in state.get('pending', []):
        if p['code'] not in union:
            pending.append({'name': p.get('name') or '', 'category': 'Crypto', 'country': 'PK',
                            'description': 'Pending verification — plausible crypto/earning group from listicle scrape.',
                            'invite': f"https://chat.whatsapp.com/{p['code']}", 'image': '', 'note': p.get('note', '')})
    json.dump(pending, open(os.path.join(WAVE, 'team46-unverified-pending.json'), 'w'), ensure_ascii=False, indent=1)

    json.dump(flagged_scam, open(os.path.join(BASE, 'team46r_flagged_scam.json'), 'w'), ensure_ascii=False, indent=1)

    print(f'verified_raw={len(raw)} banked={len(items)} porn_dropped={porn} junk_dropped={junk} scam_excluded={scam} pending={len(pending)}')
    cats = {}
    for i in items:
        cats[i['category']] = cats.get(i['category'], 0) + 1
    print('categories:', cats)

if __name__ == '__main__':
    main()
