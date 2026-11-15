#!/usr/bin/env python3
"""team26 build: screen live titles, assign canonical category/country, emit candidates/pending."""
import json, re, html

CATS = ["Education","Entertainment","Sports","Funny","Community & Social","Finance","Buy Sell",
        "Islamic","Health","News","Jobs","Technology","Gaming","Business","Cooking","Crypto",
        "Poetry","Real Estate","Travel","Scholarship","Freelance","Earning"]

PORN_RE = re.compile(r'(?i)\b(porn|xxx|sex\s*video|hot\s*sexy|nude|desi\s*bhabhi|bhabhi\s*hot|call\s*girl|escort\s*service|onlyfans|leak(?:ed|s)?\s*(?:video|mms)?\s*(?:girl|xxx)?)\b')
# negated-prohibition restore: "no porn", "no xxx", "no sex", "anti porn" etc.
NEG_RE = re.compile(r'(?i)\b(no|not|anti|against|stop|zero|free\s+from)\s+(porn|xxx|sex|betting|gambling|casino|scam)\b')
SCAM_RE = re.compile(r'(?i)(airdrop|binary\s*option|double\s*(?:your|the)?\s*money|earn\s*(?:rs|₹|\$)?\s*\d+\s*(?:daily|per\s*day)|free\s*money|click\s*and\s*earn|investment\s*double|tigrinho|fortune\s*tiger|sinais|plataformas?\s*pagantes|wjbet|aviator\s*(?:signal|predictor|hack)|betting\s*signal|slot\s*(?:machine|game)|casino|betting\s*tips?\s*(?:100%|sure|fixed)|fixed\s*match)')
FOOD_FIT_RE = re.compile(r'(?i)\b(recipe|food|cook|fitness|gym|workout|yoga|diet)\b')

def screen(title):
    t = title.strip()
    low = t.lower()
    # restore: negated prohibition sentences
    if NEG_RE.search(t):
        return None
    if 'sexta-feira' in low or 'chuta' in low:
        pass  # not porn signals
    if PORN_RE.search(t):
        # 18+ age gate on non-porn group: allow if no porn term besides the gate
        if re.search(r'(?i)18\s*\+', t) and not re.search(r'(?i)\b(porn|xxx|sex\s*video|nude|onlyfans)\b', t):
            return None
        return 'porn/xxx content'
    if SCAM_RE.search(t):
        # food/fitness contexts restore (e.g. "casino" in a food name is not a thing; keep strict)
        return 'crypto-airdrop/betting/casino scam signal'
    return None

SECTION_CAT = [
    (r'premier league|arsenal|chelsea|liverpool|manchester united|manchester sports|football|soccer|cricket', 'Sports'),
    (r'fitness|gym|workout', 'Health'),
    (r'crypto', 'Crypto'),
    (r'forex|finance|business & finance|share market|stock', 'Finance'),
    (r'news', 'News'),
    (r'job|career|nhs|healthcare jobs|employment', 'Jobs'),
    (r'health', 'Health'),
    (r'education|student|universit|school|college|exam|study|societies & clubs|freshers', 'Education'),
    (r'scholarship|study abroad', 'Scholarship'),
    (r'freelanc|earning|online earning|make money', 'Freelance'),
    (r'gaming|bgmi|free fire|pubg', 'Gaming'),
    (r'movie|entertainment|youtube|funny|meme|comedy', 'Entertainment'),
    (r'funny', 'Funny'),
    (r'islamic|naat|quran', 'Islamic'),
    (r'shopping|buy|sell|marketplace', 'Buy Sell'),
    (r'shayari|poetry|poem', 'Poetry'),
    (r'cooking|recipe|food', 'Cooking'),
    (r'travel|tour', 'Travel'),
    (r'friendship|friends|community|social|international|foreign', 'Community & Social'),
    (r'hacking|tech|program|developer|coding', 'Technology'),
    (r'business|networking|startup', 'Business'),
    (r'real estate|property|rent', 'Real Estate'),
]

TITLE_CAT = [
    (r'\b(football|soccer|premier league|arsenal|chelsea|liverpool|man ?utd|manchester united|cricket|f1|nfl|nba|sport)\b', 'Sports'),
    (r'\b(fitness|gym|workout|yoga|health|weight loss)\b', 'Health'),
    (r'\b(crypto|bitcoin|btc|eth)\b', 'Crypto'),
    (r'\b(forex|trading|stock|invest)\b', 'Finance'),
    (r'\b(news|breaking|headlines)\b', 'News'),
    (r'\b(job|jobs|hiring|vacanc|career|nhs|nurse|healthcare)\b', 'Jobs'),
    (r'\b(university|college|school|student|study|exam|learn english|ielts|society|freshers|law society|medsoc)\b', 'Education'),
    (r'\b(scholarship)\b', 'Scholarship'),
    (r'\b(freelanc|fiverr|upwork)\b', 'Freelance'),
    (r'\b(earn money|online earning|make money)\b', 'Earning'),
    (r'\b(gaming|gamer|bgmi|pubg|free fire|fortnite|ps5|xbox|fifa)\b', 'Gaming'),
    (r'\b(movie|movies|film|netflix|youtube|music|song|entertainment)\b', 'Entertainment'),
    (r'\b(funny|joke|meme|comedy|humor|humour)\b', 'Funny'),
    (r'\b(islam|islamic|quran|naat|muslim|ramadan)\b', 'Islamic'),
    (r'\b(buy|sell|shop|shopping|marketplace|deal)\b', 'Buy Sell'),
    (r'\b(shayari|poetry|poem|ghazal)\b', 'Poetry'),
    (r'\b(recipe|cooking|food)\b', 'Cooking'),
    (r'\b(travel|tour|trip|visa|abroad)\b', 'Travel'),
    (r'\b(business|startup|entrepreneur|networking)\b', 'Business'),
    (r'\b(property|real estate|rent|flat|house)\b', 'Real Estate'),
    (r'\b(tech|programmer|developer|coding|python|javascript|app)\b', 'Technology'),
]

def category_for(title, section):
    s = (section or '')
    for pat, cat in SECTION_CAT:
        if re.search(pat, s, re.I):
            return cat
    for pat, cat in TITLE_CAT:
        if re.search(pat, title, re.I):
            return cat
    return 'Community & Social'

def country_for(source, section):
    if 'groupjoin.link/country/75' in source:
        return 'FR'
    if 'grouplinks.co.uk' in source:
        return 'GB'
    if 'wahublink.com/uk-' in source:
        return 'GB'
    if 'wahublink.com/usa-' in source:
        return 'US'
    if 'whatsgroup.in' in source and 'dubai' in (section or '').lower():
        return 'AE'
    return ''

COUNTRY_WORD = {'GB': 'the UK', 'US': 'the USA', 'FR': 'France', 'AE': 'the UAE'}

def clean_name(title):
    n = html.unescape(title).strip()
    n = re.sub(r'\s+', ' ', n)
    n = re.sub(r'(?i)\s*[\|\-–—]\s*(whatsapp\s*group|join\s*whatsapp).*$', '', n).strip()
    return n

def description(name, cat, country):
    cl = cat.lower()
    base = f"Join {name}, an active WhatsApp group for {cl}."
    if country:
        base += f" Connect with members in {COUNTRY_WORD.get(country, country)}, share updates and chat about {cl}."
    else:
        base += f" Connect with members, share updates and chat about {cl}."
    return base

if __name__ == '__main__':
    fresh = {r['code']: r for r in json.load(open('team26_fresh_all.json'))}
    ver = json.load(open('team26_verify.json'))
    cands, excluded, pending, dead = [], [], [], []
    for v in ver:
        code = v['code']
        src = fresh.get(code, {})
        if v['status'] == 'pending':
            pending.append({'code': code, 'reason': v.get('reason', ''), 'source': src.get('source', '')})
        elif v['status'] == 'dead':
            dead.append(code)
        elif v['status'] == 'live':
            title = v['title']
            why = screen(title)
            if why:
                excluded.append({'code': code, 'title': title, 'reason': why,
                                 'source': src.get('source', ''), 'section': src.get('section', '')})
                continue
            name = clean_name(title)
            if not name:
                excluded.append({'code': code, 'title': title, 'reason': 'empty name after clean',
                                 'source': src.get('source', ''), 'section': src.get('section', '')})
                continue
            cat = category_for(title, src.get('section', ''))
            country = country_for(src.get('source', ''), src.get('section', ''))
            cands.append({'name': name, 'category': cat, 'country': country,
                          'description': description(name, cat, country),
                          'invite': f'https://chat.whatsapp.com/{code}'})
    json.dump(cands, open('team26-candidates.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open('team26-pending.json', 'w'), ensure_ascii=False, indent=1)
    json.dump({'excluded': excluded, 'dead': dead}, open('team26_screened.json', 'w'), ensure_ascii=False, indent=1)
    print(f"candidates={len(cands)} excluded={len(excluded)} pending={len(pending)} dead={len(dead)}")
    for e in excluded:
        print('EXCL', e['code'], e['reason'], '|', e['title'][:80])
    from collections import Counter
    print(Counter(c['category'] for c in cands))
    print(Counter(c['country'] for c in cands))
