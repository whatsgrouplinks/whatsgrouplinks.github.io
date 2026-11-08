#!/usr/bin/env python3
"""Team02: build verified/pending JSON from groupda.pk candidates + og:title verification results."""
import json, re, html as htmlmod, unicodedata

def norm(s):
    """Fold stylized unicode (e.g. mathematical bold) to ASCII for matching."""
    return unicodedata.normalize('NFKD', s)

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/'
cands = json.load(open(WAVE + 'team02_candidates_raw.json'))

# ---------- porn / scam / minors filters ----------
PORN_PAT = re.compile(
    r'pornhub|porn|xxx|xvideos|xnxx|nude|nud3|sex\s*video|escort|call\s*girl|'
    r'fuck|dick|pussy|boobs|anal|blowjob|bokep|hentai|onlyfans|'
    r'سیکسی|ننگی|فحش|جنسی|مباشرت|ہمبستری|مز[ااہ]\s*دینے|'
    r'सेक्सी|नंगी|अश्लील|सेक्स\s*वीडियो|हॉट\s*गर्ल|सेक्स\s*चैट|'
    r'sexy\s*bhabhi|desi\s*bhabhi|hot\s*bhabhi|bhabhi\s*hot|adult\s*video|hot\s*video|'
    r'18\+\s*(sexy|hot|adult|nude)|sexy|erotic',
    re.I)
EMOJI_PAT = re.compile(r'[🥵🍆🍑🔞💦👅👄💋]')
MINOR_PAT = re.compile(r'\b(teen|teens|school\s*girl|schoolgirl|under\s*1[0-8]|minor|bachi|بچی|स्कूल\s*गर्ल)\b', re.I)
SCAM_PAT = re.compile(r'\b(satta|matka|fix\s*(game|number)|hyip|double\s*(your|money)|money\s*mule|paypal\s*(receiver|loader)|free\s*recharge\s*trick|bet\b|betting|casino|lottery\s*(trick|hack))\b', re.I)

# og:title boilerplate cleanup
def clean_name(t):
    t = htmlmod.unescape(t).strip()
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'(?i)^\s*(join|invite)\s+', '', t)                      # leading Join/Invite
    t = re.sub(r'(?i)\s*\|\s*whatsapp.*$', '', t)                        # trailing | WhatsApp...
    t = re.sub(r'(?i)\s*-\s*whatsapp\s*(group.*)?$', '', t)
    t = re.sub(r'(?i)\s*whatsapp\s*group\s*(invite|link|links)?\s*$', '', t)
    t = re.sub(r'(?i)\s*(group\s*)?(invite|invitation)\s*(link)?\s*$', '', t)
    return t.strip(' -|')

# category keyword inference from cleaned name
CAT_KW = [
    ('Sports', r'cricket|football|sport|ipl|psl|fifa|match|wrestl|hockey|tennis'),
    ('Gaming', r'game|gaming|pubg|freefire|free\s*fire|bgmi|gamer|ps5|xbox'),
    ('Jobs', r'\bjob|jobs|naukri|rozgar|hiring|vacanc|career|recruit|office\s*work|part\s*time|work\s*from\s*home|\brozgār\b'),
    ('Education', r'study|studies|exam|mcqs|test\s*prep|school|college|university|course|admission|scholarship|css|pms|9th|10th|matric|inter|notes|ilm|taleem|تعلیم'),
    ('News', r'\bnews|khabar|headlines|breaking|taza|تازہ|خبر'),
    ('Islamic', r'islam|quran|hadith|naat|ramadan|dua|deen|muslim|wazifa|قرآن|اسلام|دین|نعت'),
    ('Business', r'business|earn|earning|online\s*earning|shop|store|marketing|resell|dropship'),
    ('Finance', r'forex|trading|stock|invest|finance|loan|bank'),
    ('Buy-Sell', r'buy|sell|sale|olx|deal|bazar|bazaar|market|price'),
    ('Health', r'health|doctor|medical|hospital|fitness|diet|sehat|صحت'),
    ('Technology', r'tech|mobile|android|iphone|software|computer|laptop|ai\b'),
    ('Crypto', r'crypto|bitcoin|binance|usdt|airdrop'),
    ('Travel', r'travel|tour|trip|visa|ticket|flight|umrah|hajj'),
    ('Music', r'music|song|songs|gana|audio|dj\b'),
    ('Movies', r'movie|film|drama|serial|netflix|web\s*series|cinema|bollywood|lollywood'),
    ('Food', r'food|recipe|cooking|khana|restaurant'),
    ('Pets', r'pet|dog|cat|bird|animal'),
    ('Funny', r'funny|meme|joke|comedy|hasna|hansi|مزاح|لطیف'),
    ('Entertainment', r'fan\s*club|\bfans?\b|celebrity|actor|actress'),
    ('Girls', r'girl|dosti\s*(girl|girls)|bhabhi|aunty|ladki'),
    ('Friendship', r'friend|dosti|dost|chat|gup\s*shup|masti|دوست'),
]
def infer_category(name, fallback):
    name = norm(name)
    for cat, pat in CAT_KW:
        if re.search(pat, name, re.I):
            return cat
    return fallback

DEVANAGARI = re.compile(r'[\u0900-\u097F]')
URDU_ARABIC = re.compile(r'[\u0600-\u06FF]')
def infer_country(name, post_title, post_cats):
    pt = post_title.lower()
    if 'pakistan' in pt: return 'PK'
    if 'usa' in pt: return 'US'
    if 'tamil' in pt or 'indian' in pt: return 'IN'
    if 'worldwide' in pt: return 'International'
    if DEVANAGARI.search(name): return 'IN'
    if URDU_ARABIC.search(name): return 'PK'
    if 'urdu' in name.lower(): return 'PK'
    if 'hindi' in name.lower(): return 'IN'
    if 'pakistan' in post_cats or 'pakistani' in ' '.join(post_cats).lower(): return 'PK'
    return 'International'

COUNTRY_WORD = {'PK': 'Pakistani', 'IN': 'Indian', 'US': 'American', 'International': 'international'}
DESC_TMPL = {
    'Sports': 'Active {cw} WhatsApp group for sports fans following {topic}. Get live scores, match discussions and sports news with fellow enthusiasts.',
    'Gaming': 'Active {cw} WhatsApp group for gamers into {topic}. Share gameplay tips, squad up and talk gaming with fellow players.',
    'Jobs': 'Active {cw} WhatsApp group sharing job openings around {topic}. Get daily job alerts and career updates with fellow job seekers.',
    'Education': 'Active {cw} WhatsApp group for students focused on {topic}. Share study notes, exam tips and learning resources with fellow learners.',
    'News': 'Active {cw} WhatsApp group delivering the latest news about {topic}. Stay updated with breaking headlines and daily news discussions.',
    'Islamic': 'Active {cw} WhatsApp group sharing Islamic reminders about {topic}. Join daily Quranic verses, duas and religious discussions.',
    'Business': 'Active {cw} WhatsApp group for entrepreneurs discussing {topic}. Network, share business ideas and growth tips with fellow members.',
    'Finance': 'Active {cw} WhatsApp group discussing {topic} and money matters. Share market insights and finance tips with fellow members.',
    'Buy-Sell': 'Active {cw} WhatsApp group for buying and selling around {topic}. Find great deals and trade safely with group members.',
    'Health': 'Active {cw} WhatsApp group focused on health and wellness around {topic}. Share health tips and fitness advice with fellow members.',
    'Technology': 'Active {cw} WhatsApp group for tech lovers into {topic}. Discuss gadgets, apps and the latest technology trends together.',
    'Crypto': 'Active {cw} WhatsApp group discussing {topic} and cryptocurrency. Share market updates and trading insights with fellow members.',
    'Travel': 'Active {cw} WhatsApp group for travellers interested in {topic}. Share travel plans, tips and destination ideas with fellow explorers.',
    'Music': 'Active {cw} WhatsApp group for music lovers into {topic}. Share songs, playlists and music updates with fellow fans.',
    'Movies': 'Active {cw} WhatsApp group for movie lovers following {topic}. Share the latest films, trailers and reviews with fellow cinema fans.',
    'Food': 'Active {cw} WhatsApp group for food lovers sharing {topic}. Exchange recipes and cooking tips with fellow foodies.',
    'Pets': 'Active {cw} WhatsApp group for pet lovers into {topic}. Share pet care tips and cute moments with fellow animal lovers.',
    'Funny': 'Active {cw} WhatsApp group sharing funny content around {topic}. Enjoy daily memes, jokes and comedy with fellow members.',
    'Girls': 'Active {cw} WhatsApp group for girls interested in {topic}. Chat, share and make new friends in a friendly community.',
    'Friendship': 'Active {cw} WhatsApp group for making friends around {topic}. Chat daily, share good vibes and build new friendships.',
    'Community': 'Active {cw} WhatsApp group bringing people together around {topic}. Join daily discussions and connect with like-minded members.',
    'Regional': 'Active {cw} WhatsApp community group about {topic}. Connect with people from the region for daily chat and local updates.',
    'Entertainment': 'Active {cw} WhatsApp group for entertainment around {topic}. Enjoy viral videos, fun posts and daily entertainment with members.',
    'Other': 'Active {cw} WhatsApp group about {topic}. Join the community for daily updates and friendly discussions.',
}
def topic_from_name(name):
    t = re.sub(r'(?i)\b(whatsapp|group|official|new|best|latest|active|2026|pakistan|india|indian|desi|usa|worldwide|tamil|nadu|nigeria)\b', '', name)
    t = re.sub(r'\s+', ' ', t).strip(' -|')
    return t if len(t) >= 3 else name

def make_desc(name, category, country):
    topic = norm(topic_from_name(name))
    tmpl = DESC_TMPL.get(category, DESC_TMPL['Other'])
    return tmpl.format(cw=COUNTRY_WORD.get(country, 'international'), topic=topic)

# post-level defaults
def post_defaults(ptitle, pcats):
    pt = ptitle.lower()
    if 'movies' in pt: return ('Movies', None)
    if 'worldwide friends' in pt: return ('Friendship', 'International')
    if 'usa' in pt: return ('Community', 'US')
    if 'tamil' in pt: return ('Community', 'IN')
    if '1689' in pt: return ('Girls', None)
    if '2300' in pt or 'pakistan' in pt: return ('Girls', 'PK')
    if '18+' in pt or 'desi' in pt: return ('Girls', None)
    return ('Community', 'International')

verified, pending = [], []
porn_drops = scam_drops = minor_drops = 0
seen_codes = set()

for c in cands:
    code = c['code']
    if code in seen_codes: continue
    seen_codes.add(code)
    status = c.get('verify_status', 'unknown')
    if status != 'live':
        note = 'transport failure' if status == 'transport-failure' else status
        pending.append({'code': code, 'og_title': c.get('og_title',''),
                        'source_post': c.get('link',''), 'note': note})
        continue
    raw = c.get('og_title', '')
    name = clean_name(raw)
    check_txt = norm(raw + ' ' + c.get('title','') + ' ' + c.get('snippet',''))
    if PORN_PAT.search(check_txt) or EMOJI_PAT.search(check_txt):
        porn_drops += 1; continue
    if MINOR_PAT.search(check_txt):
        minor_drops += 1; continue
    if SCAM_PAT.search(check_txt):
        scam_drops += 1; continue
    if not name or len(name) < 3:
        pending.append({'code': code, 'og_title': raw, 'source_post': c.get('link',''),
                        'note': 'live but og:title unusable as name'}); continue
    fb_cat, fb_country = post_defaults(c.get('title',''), c.get('cats',[]))
    category = infer_category(name, fb_cat)
    country = fb_country or infer_country(name, c.get('title',''), c.get('cats',[]))
    verified.append({
        'name': name, 'category': category, 'country': country,
        'description': make_desc(name, category, country),
        'invite': 'https://chat.whatsapp.com/' + code, 'image': ''})

json.dump(verified, open(WAVE + 'team02-groupda-pk.json', 'w'), ensure_ascii=False, indent=1)
json.dump(pending, open(WAVE + 'team02-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
print(f"verified={len(verified)} pending={len(pending)} porn_drops={porn_drops} minor_drops={minor_drops} scam_drops={scam_drops}")
# sanity: name never a URL / no source domain
bad = [v for v in verified if 'http' in v['name'] or 'groupda' in (v['name']+v['description']).lower()]
print("schema violations:", len(bad))
for v in bad[:5]: print('  BAD:', v)
