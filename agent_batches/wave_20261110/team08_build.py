"""Build team08 final outputs from verify results (wave 20261110, slice 8)."""
import json, re, os, html, unicodedata

WD = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110'
SRC = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_08.json'

verify = json.load(open(os.path.join(WD, 'team08_verify.json')))
ctx = json.load(open(os.path.join(WD, 'team08_to_verify_ctx.json')))
prescreen_excl = json.load(open(os.path.join(WD, 'team08_prescreen_exclusions.json')))
fetch_raw = json.load(open(os.path.join(WD, 'team08_fetch_raw.json')))
leads_in = json.load(open(SRC))

CATS = ["Entertainment", "Jobs", "Education", "Islamic", "Sports", "Community & Social",
        "Finance", "Funny", "Buy Sell", "Health", "News", "Gaming", "Technology", "Business"]

ADULT_TITLE_RE = re.compile(
    r'🔞|🥵|\bsexy\b|saxy|hookup|escort|\bporn\b|xxx|\bpussy\b|seksi|bideos|'
    r'18\+\s*(hot|adult|sex|video|girls?)|hot\s+(girls?|bhabhi|aunty|videos?)|'
    r'\bcall\s*girls?\b|nude|naked|sex\s*(video|chat|group|dating)|'
    r'\bcam\s*(girls?|models?|shows?|live)\b|onlyfans|webcam|adlut|hentai|ecchi', re.I)
SCAM_TITLE_RE = re.compile(
    r'forsage|\bb-?love\b|shey(i|y)\b|paypal loader|bitfinex|counterfeit|carding|'
    r'airdrop|double (your|the) (money|investment|usdt|trx|btc)|'
    r'(earn|earning).{0,20}(usdt|ustd|\$|daily profit|without investment)|'
    r'(forex|trading).{0,15}(earn|🤑|usdt|ustd)|'
    r'\b(bitcoin|btc|usdt).{0,15}(doubl|earn|profit|invest)|'
    r'matka|satta|\bkalyan\b.{0,10}game|fix\s*(game|jodi|number)|'
    r'loan.{0,20}(100%|guaranteed|instant approval|without documents|no documents)', re.I)
PHONE_RE = re.compile(r'\d{7,}')
URL_RE = re.compile(r'https?://\S+|www\.\S+')
EMOJI_RE = re.compile(r'[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200d]+')
SOURCE_WORD_RE = re.compile(r'\b(groupjoin|grouplink|groupsor|groupssor|grupbul|grupodewhatsapp|'
                            r'gruposwats|groupsinvite|linktogroups|whatsgroup|whatstele|freewagroup|'
                            r'wglfinder|tglinkhub|grouplinksforyou|groupslinks|groupsgyani|whgroups|'
                            r'newgrouplinks|whatsappkanali|igrupos|tugrupo|linkado|groupizo|groupwa|'
                            r'wagroup|dostizone|eduwealthhub|joingram|wahublink|hubrecipes|ccsupsc|'
                            r'englishan|opendoorpathways)\b', re.I)


GJ_TAG_ADULT_RE = re.compile(r'^(adult|adlut|18\+|sexy|saxy|porn|xxx|escort|cam|hot girls|call girls)$', re.I)
GJ_TAG_SCAM_RE = re.compile(r'forsage|b-?love|shey(i|y)|airdrop|paypal loader|bitfinex|counterfeit|carding', re.I)

def parse_gj(ctx_text):
    """Extract group_desc + tags from a groupjoin Next.js JSON blob inside listing context."""
    t = ctx_text.replace('\\"', '"').replace('\\u0026', '&').replace('\\/', '/').replace('\\n', ' ')
    t = re.sub(r'\\u[0-9a-fA-F]{4}', ' ', t)
    desc = ''
    m = re.search(r'"group_desc"\s*:\s*"((?:[^"\\]|\\.)*)"', t)
    if m:
        desc = m.group(1).replace('\\"', '"').strip()
    if not desc:
        m = re.search(r'Welcome to my whatsapp group\s+(.{15,300})', t, re.I)
        if m:
            desc = 'Welcome to my whatsapp group ' + m.group(1).split('\"')[0].strip()
    tags = []
    m2 = re.search(r'"tags"\s*:\s*\[(.*?)\]', t)
    if m2:
        tags = [x.strip().strip('"') for x in re.split(r'",\s*"', m2.group(1)) if x.strip()]
        tags = [x for x in tags if x]
    return desc, tags

TAG_CATEGORY = {
    'jobs': 'Jobs', 'new jobs': 'Jobs', 'pakistan jobs update': 'Jobs', 'vacancies': 'Jobs',
    'new vacancy': 'Jobs', 'gulf jobs': 'Jobs', 'bank jobs': 'Jobs', 'female job': 'Jobs',
    'education': 'Education', 'school': 'Education', 'study': 'Education', 'learning': 'Education',
    'business': 'Business', 'online business': 'Business', 'advertising': 'Business',
    'marketing': 'Business', 'online business opportunity': 'Business', 'freelancer': 'Business',
    'entertainment': 'Entertainment', 'movies': 'Entertainment', 'music': 'Entertainment',
    'songs': 'Entertainment', 'web series': 'Entertainment', 'videos': 'Entertainment',
    'sports': 'Sports', 'cricket': 'Sports', 'football': 'Sports',
    'funny': 'Funny', 'jokes': 'Funny', 'memes': 'Funny', 'comedy': 'Funny',
    'health': 'Health', 'fitness': 'Health',
    'news': 'News',
    'gaming': 'Gaming', 'games': 'Gaming', 'game': 'Gaming',
    'technology': 'Technology', 'apps': 'Technology', 'app': 'Technology',
    'islamic': 'Islamic', 'quran': 'Islamic', 'naat': 'Islamic', 'ramadan': 'Islamic',
    'shopping': 'Buy Sell', 'deals': 'Buy Sell', 'coupons': 'Buy Sell',
    'finance': 'Finance', 'earning': 'Finance', 'crypto': 'Finance', 'forex': 'Finance',
    'money': 'Finance', 'online earning': 'Finance', 'trading': 'Finance',
    'friendship': 'Community & Social', 'dating': 'Community & Social', 'chat': 'Community & Social',
    'community': 'Community & Social', 'social': 'Community & Social',
}

def category_from_tags(tags):
    for t in tags:
        c = TAG_CATEGORY.get(t.strip().lower())
        if c:
            return c
    return None

def country_from_tags(tags):
    for t in tags:
        for word, code in COUNTRY_WORDS:
            if t.strip().lower() == word.lower():
                return code
    return None

CAT_KEYWORDS = [
    ("Islamic", ["islamic", "quran", "naat", "ramadan", "dua", "muslim", "allah", "masjid", "islam", "hadith", "namaz", "roza"]),
    ("Education", ["education", "study", "exam", "ielts", "neet", "upsc", "scholarship", "python", "grammar", "learn english", "english learning", "student", "university", "kota", "test preparation", "sarkari result", "board exam", "class 12", "12th class", "jpsc", "bpsc", "notes", "study material"]),
    ("Jobs", ["job", "jobs", "vacancy", "vacancies", "employment", "career", "hiring", "naukri", "govt job", "placement", "recruitment", "gulf job", "europe job", "bank job", "private job", "female job", "data entry"]),
    ("Gaming", ["free fire", "bgmi", "pubg", "clash of clans", "gaming", "gamer", "game", "games", "ludo", "fortnite", "efootball", "dream11"]),
    ("Sports", ["sport", "cricket", "football", "soccer", "fantasy", "ipl", "psl", "match", "league", "kabaddi", "hockey", "wrestling"]),
    ("Funny", ["funny", "joke", "jokes", "meme", "memes", "comedy", "humor", "hilarious", "fun videos"]),
    ("Health", ["health", "fitness", "weight loss", "diet", "yoga", "medical", "healthy heart", "doctor", "hospital", "wellness"]),
    ("News", ["news", "breaking news", "headlines", "daily news", "latest news"]),
    ("Buy Sell", ["shop", "shopping", "buy", "sell", "sale", "deals", "coupon", "store", "market", "bazar", "online shopping", "price", "order now"]),
    ("Finance", ["forex", "trading", "invest", "investment", "stock market", "crypto", "bitcoin", "usdt", "token", "tokens", "coin", "banking", "finance", "earn money", "online earning", "income", "money making", "loan", "earning", "earn"]),
    ("Technology", ["technology", "tech ", " android", "software", "computer", "programming", "developer", "app", "apps", "artificial intelligence", " ai ", "gadget"]),
    ("Business", ["business", "entrepreneur", "marketing", "advertising", "startup", "ecommerce", "e-commerce", "import", "export", "freelancer", "freelancing", "fiverr"]),
    ("Entertainment", ["movie", "movies", "music", "song", "songs", "series", "web series", "drama", "film", "videos", "entertainment", "bollywood", "hollywood", "shayari", "poetry", "status video", "reels"]),
]

COUNTRY_WORDS = [
    ("Pakistan", "PK"), ("Pakistani", "PK"), ("Bangladesh", "BD"), ("Bangladeshi", "BD"),
    ("India", "IN"), ("Indian", "IN"), ("Indonesia", "ID"), ("Indonesian", "ID"),
    ("Nigeria", "NG"), ("Nigerian", "NG"), ("Kenya", "KE"), ("Kenyan", "KE"),
    ("Brazil", "BR"), ("Brasil", "BR"), ("Brazilian", "BR"), ("Sri Lanka", "LK"),
    ("Malaysia", "MY"), ("Malaysian", "MY"), ("Nepal", "NP"), ("Nepali", "NP"),
    ("Zimbabwe", "ZW"), ("Turkey", "TR"), ("Turkish", "TR"), ("Qatar", "QA"),
    ("UAE", "AE"), ("Saudi", "SA"), ("Dubai", "AE"), ("Ghana", "GH"),
    ("Tamil", "IN"), ("Hindi", "IN"), ("Urdu", "PK"), ("Sinhala", "LK"),
    ("Telugu", "IN"), ("Malayalam", "IN"), ("Bengali", "BD"), ("Punjabi", "IN"),
    ("Marathi", "IN"), ("Gujarati", "IN"), ("Kannada", "IN"), ("Odia", "IN"),
    ("Mexico", "MX"), ("Mexican", "MX"), ("Argentina", "AR"), ("Colombia", "CO"),
    ("Peru", "PE"), ("Chile", "CL"), ("Spain", "ES"), ("Spanish", "ES"),
    ("Portugal", "PT"), ("Portuguese", "BR"), ("France", "FR"), ("Germany", "DE"),
    ("Italy", "IT"), ("USA", "US"), ("America", "US"), ("Canada", "CA"),
    ("Australia", "AU"), ("UK", "GB"), ("England", "GB"), ("London", "GB"),
    ("Egypt", "EG"), ("Morocco", "MA"), ("Algeria", "DZ"), ("Tunisia", "TN"),
    ("Ethiopia", "ET"), ("Uganda", "UG"), ("Tanzania", "TZ"), ("South Africa", "ZA"),
    ("Philippines", "PH"), ("Filipino", "PH"), ("Vietnam", "VN"), ("Thailand", "TH"),
    ("Myanmar", "MM"), ("Afghanistan", "AF"),
]

GENERIC_DESC = {
    "Entertainment": "A WhatsApp group for entertainment lovers to share movies, music and fun updates. Join to chat with fellow fans and enjoy daily posts.",
    "Jobs": "A WhatsApp group sharing job openings and career updates for members. Join to find new opportunities and connect with other job seekers.",
    "Education": "A WhatsApp group for students and learners to share study material, notes and exam updates. Join to learn together and stay prepared.",
    "Islamic": "A WhatsApp group sharing Islamic reminders, prayers and religious guidance. Join for daily spiritual posts and respectful discussion.",
    "Sports": "A WhatsApp group for sports fans to follow matches, scores and updates. Join to discuss games and cheer with fellow supporters.",
    "Community & Social": "A friendly WhatsApp group for chatting, making friends and sharing daily updates. Join to meet new people and be part of the community.",
    "Finance": "A WhatsApp group sharing finance news, market updates and money tips. Join to learn and discuss with other members.",
    "Funny": "A WhatsApp group sharing funny videos, jokes and memes to brighten the day. Join for daily laughs with friendly members.",
    "Buy Sell": "A WhatsApp group for buying and selling items, deals and offers. Join to find good prices and connect with buyers and sellers.",
    "Health": "A WhatsApp group sharing health tips, fitness advice and wellness updates. Join to stay healthy and motivated together.",
    "News": "A WhatsApp group sharing the latest news and important updates. Join to stay informed with daily headlines.",
    "Gaming": "A WhatsApp group for gamers to share tips, updates and play together. Join to connect with fellow players and enjoy the game.",
    "Technology": "A WhatsApp group sharing technology news, apps and useful tips. Join to learn about the latest tech with other enthusiasts.",
    "Business": "A WhatsApp group for business owners and entrepreneurs to share ideas and opportunities. Join to network and grow together.",
}

def clean_name(t):
    t = html.unescape(t or '')
    t = strip_cf(''.join(c for c in t if unicodedata.category(c) not in ('Cf',)))
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:100]

def pick_category(title, ctx_text, url_text):
    blob = (' ' + title + ' ' + ctx_text + ' ' + url_text).lower()
    best, best_score = 'Community & Social', 0
    for cat, kws in CAT_KEYWORDS:
        score = 0
        for kw in kws:
            if kw in blob:
                score += 3 if kw in title.lower() else 1
        if score > best_score:
            best, best_score = cat, score
    return best

def pick_country(ctx_text, url_text, title):
    blob = (' ' + ctx_text + ' ' + url_text + ' ' + title)
    for word, code in COUNTRY_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', blob, re.I):
            return code
    if 'gruposwats.com' in url_text and ('/mx' in url_text or 'mx.gruposwats' in url_text):
        return 'MX'
    if 'whatsappkanali.com' in url_text:
        return 'TR'
    return 'International'

def clean_desc_text(t):
    t = html.unescape(t or '')
    t = t.replace('\\"', '"').replace('\\u0026', '&')
    t = re.sub(r'\\u[0-9a-fA-F]{4}', ' ', t)
    t = re.sub(r'\S*=\S+', ' ', t)
    t = re.sub(r'\b\w{30,}\b', ' ', t)
    t = re.sub(r'[\\"]+', ' ', t)
    t = URL_RE.sub(' ', t)
    t = SOURCE_WORD_RE.sub(' ', t)
    t = re.sub(r'Welcome to my whatsapp group\s*', ' ', t, flags=re.I)
    t = re.sub(r'Please join my whatsapp group\.?\s*', ' ', t, flags=re.I)
    t = EMOJI_RE.sub(' ', t)
    t = re.sub(r'\s+', ' ', t).strip(' .,-')
    return t

JUNK_DESC_RE = re.compile(r'click here|reply|comment|<a|whatsapp group|join (my|this) (whatsapp )?group|welcome to|please join|subscribe|subscriber|sub4sub|\bto\s+(my|the)\b.*group', re.I)

def strip_cf(t):
    t = ''.join(c for c in t if unicodedata.category(c) not in ('Cf',))
    return re.sub(r'[\uFE00-\uFE0F\u200D\u2060]', '', t)

def build_desc(title, og_desc, ctx_text, category, gj_desc=''):
    # prefer the listing's own group_desc
    if gj_desc:
        d = clean_desc_text(gj_desc)
        d = re.sub(r'Welcome to my whatsapp group\s*', ' ', d, flags=re.I)
        d = re.sub(r'Please join my whatsapp group\.?\s*', ' ', d, flags=re.I)
        d = strip_cf(re.sub(r'\s+', ' ', d).strip(' .,-'))
        if d and d.lower() not in (title.lower(),) and len(d) >= 25 and not JUNK_DESC_RE.search(d):
            s = d if d.endswith('.') else d + '.'
            return s[:280]
    # then a real og description
    d = strip_cf(clean_desc_text(og_desc))
    if len(d) >= 25 and 'whatsapp group invite' not in d.lower() and 'join group' not in d.lower() and not JUNK_DESC_RE.search(d):
        s = d if d.endswith('.') else d + '.'
        return s[:280]
    # else use listing text (first meaningful sentence)
    c = strip_cf(clean_desc_text(ctx_text))
    sentences = [s.strip() for s in re.split(r'(?<=[.!])\s+', c) if len(s.strip()) > 25]
    good = [s for s in sentences if not JUNK_DESC_RE.search(s) and 'http' not in s.lower()]
    if good:
        s = good[0]
        if not s.endswith('.'):
            s += '.'
        if len(s) < 300:
            return s
    return GENERIC_DESC[category]

exclusions = list(prescreen_excl)
verified, pending = [], []
dead = 0
for v in verify:
    code, http, title, desc = v['code'], v.get('http'), v.get('title', ''), v.get('desc', '')
    if http == 0:
        pending.append({'code': code, 'invite': 'https://chat.whatsapp.com/' + code,
                        'reason': 'transport failed (connection error/timeout) after retries; attempts=%s; never returned a group title' % v.get('attempts', 1)})
        continue
    if http != 200 or not title:
        dead += 1
        continue
    name = clean_name(title)
    if not name or len(name) < 2 or name.lower() in ('whatsapp group invite', 'join group', 'whatsapp group', 'group invite'):
        exclusions.append({'code': code, 'reason': 'no usable group name in og:title (%r)' % title[:60]})
        continue
    if ADULT_TITLE_RE.search(title) or ADULT_TITLE_RE.search(name):
        exclusions.append({'code': code, 'reason': 'adult-sexual signal in og:title: %r' % title[:80]})
        continue
    if SCAM_TITLE_RE.search(title):
        exclusions.append({'code': code, 'reason': 'scam pattern in og:title: %r' % title[:80]})
        continue
    if PHONE_RE.search(name):
        exclusions.append({'code': code, 'reason': 'phone number in group name (personal info): %r' % title[:80]})
        continue
    occ = ctx.get(code, [])
    ctx_text = ' '.join(o.get('context', '') for o in occ)
    url_text = ' '.join(o.get('url', '') + ' ' + o.get('source', '') for o in occ)
    gj_desc, gj_tags = '', []
    for o in occ:
        d0, t0 = parse_gj(o.get('context', ''))
        if d0:
            gj_desc = d0
        if t0:
            gj_tags = t0
    if any(GJ_TAG_ADULT_RE.match(t.strip()) for t in gj_tags):
        exclusions.append({'code': code, 'reason': 'adult tag on listing (groupjoin tags: %s)' % (', '.join(gj_tags[:12]))})
        continue
    if any(GJ_TAG_SCAM_RE.search(t) for t in gj_tags):
        exclusions.append({'code': code, 'reason': 'scam tag on listing (groupjoin tags: %s)' % (', '.join(gj_tags[:12]))})
        continue
    category = category_from_tags(gj_tags) or pick_category(name, gj_desc + ' ' + ' '.join(gj_tags), url_text)
    country = country_from_tags(gj_tags) or pick_country(gj_desc + ' ' + ' '.join(gj_tags), url_text, name)
    description = build_desc(name, desc, ctx_text, category, gj_desc)
    if PHONE_RE.search(description):
        description = GENERIC_DESC[category]
    verified.append({'name': name, 'category': category, 'country': country,
                     'description': description, 'invite': 'https://chat.whatsapp.com/' + code})

# leads: discovered listing URLs, deduped, minus input URLs
input_urls = {x['url'] for x in leads_in}
seen_lead = set()
leads = []
for r in fetch_raw:
    for u in r.get('new_leads', []):
        if u in seen_lead or u in input_urls or 'chat.whatsapp.com' in u:
            continue
        seen_lead.add(u)
        kind = 'single-group page (contains one invite); not yet fetched' if re.search(r'/group/|/listing/|/en/group/', u) else 'listing/category page discovered from slice page; not yet fetched'
        leads.append({'url': u, 'source': r.get('source', ''), 'note': kind})

json.dump(verified, open(os.path.join(WD, 'team08-leads-slice8.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(pending, open(os.path.join(WD, 'team08-leads-slice8-pending.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(leads, open(os.path.join(WD, 'team08-leads-slice8-leads.json'), 'w'), ensure_ascii=False, indent=1)

sources = sorted({x.get('source', '') for x in leads_in if x.get('source')})
empty_pages = [r['url'] for r in fetch_raw if r['http_len'] == 0]
summary = {
    'team': 8,
    'slice': 'leads slice 8',
    'sources': sources,
    'verified': len(verified),
    'pending': len(pending),
    'leads': len(leads),
    'dead': dead,
    'exclusions': exclusions,
    'resume': 'Slice 8 of the wave_20261109 leads bank, re-run in wave_20261110 (same 184 listing URLs as wave_20261109 team08). All 745 fresh codes verified with keep-alive requests (3 parallel, >=0.6s spacing, 15s timeout, 2 spaced retries on empty og:title). Progress checkpointed in team08_verify_progress.json; final verify results in team08_verify.json. %d listing pages returned 0 bytes and yielded no codes (mostly JS/blocked: groupssor, gruposwats, whatsappkanali); their URLs are in team08_fetch_raw.json with http_len 0.' % len(empty_pages),
    'notes': 'Union dedupe = .existing_codes.json (108,364) + groups.json codes (72,742, all already inside .existing) = 108,364 codes (task brief said 108,365; off by one). 3,004 distinct codes extracted from listings; 900 fresh vs union; 155 prescreen exclusions (120 groupjoin Adult-tagged never verified, 13 airdrop/scam-pattern, 22 adult-signal in listing context); 745 verified. Live rate lower than wave_20261109 (176/715) because 361 codes were brand-new listings and 379 were re-checks of codes dead on Nov 9. og:title screening dropped the 5 prior-live carryovers (Israel Pussy, Kidumangani Ultra 18+, Forsage Kenya, USTD Earning/Forex, phone-number subscriber-selling title). Descriptions are generic where the listing gave no clean group description; no source names/links or personal info in any banked field.',
}
json.dump(summary, open(os.path.join(WD, 'team08-leads-slice8-summary.json'), 'w'), ensure_ascii=False, indent=1)
print('verified:', len(verified), 'pending:', len(pending), 'leads:', len(leads), 'dead:', dead, 'exclusions:', len(exclusions))
from collections import Counter
print('categories:', Counter(x['category'] for x in verified))
print('countries:', Counter(x['country'] for x in verified).most_common(10))
