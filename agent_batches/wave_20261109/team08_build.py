"""Build team08-candidates.json / pending / summary from verification results.
Run after verification + retries complete."""
import json, re, html, unicodedata

CATEGORIES = ["Gaming","Education","Online Earning","Community & Social","Business","Friendship","Finance","Buy Sell","Islamic","Entertainment","Jobs","Technology","Funny","Sports","Health","News"]

# --- screening ---
DROP_PATTERNS = [
    r'\bxxx\b', r'\bporn\b', r'pornhub', r'xvideos', r'\bsex\b', r'sexy', r'sex\s*(video|chat|group|call)',
    r's3x', r'\bseks\b', r'hookup', r'hook-up', r'escort', r'cam\s*girl', r'camgirl',
    r'call\s*girl', r'callgirl', r'nude', r'nudes', r'onlyfans', r'pussy', r'\bdick\b',
    r'\bcock\b', r'boobs', r'\bchut\b', r'\blund\b', r'\bmms\b', r'leak(ed)?\s*(video|mms|pics?)',
    r'\b18\+\b', r'🔞', r'🍆', r'🍑', r'hot\s*(girls?|bhabhi|aunty|videos?|pics?|desi)',
    r'bhabhi', r'randi', r'adult\s*(video|group|content|chat|18)', r'desi\s*(mms|video|sex|girls?)',
    r'gandi\s*(video|photo|cheez)', r'viral\s*mms', r'\baudult\b.*\bvideo\b',
    r'b-?love\b', r'forsage', r'\bsheyi\b', r'crypto\s*airdrop', r'airdrop.*(free|earn|claim)',
    r'free\s*money.*(join|earn)', r'earn\s*(rs\.?|₹|\$)\s*\d+.*(per day|daily|instant)',
    r'double\s*(your\s*)?money', r'invest\s*\d+.*(get|earn|return)', r'money\s*doubling',
    r'bitcoin\s*doubling', r'malware', r'keylogger', r'virus.*hack|hack.*virus',
    r'\bdesi\s*bhabhi\b', r'aunty\s*(hot|sex|video)', r'virus[_/\s]*data', r'heck.*virus|virus.*heck', r'\bhack\b.*\b(account|password|tool)',
]
DROP_RE = re.compile('|'.join(DROP_PATTERNS), re.I)

# sentences that PROHIBIT adult content - strip before screening
PROHIBIT_RE = re.compile(r'[^.!?\n]*(inappropriate|adult|porn|xxx|sex|nude|18\+)[^.!?\n]*(na\s*karein|not\s*allowed|mana\s*hai|prohibit|strictly\s*forbidden|no\s+.*(share|allow)|not\s+allow)[^.!?\n]*[.!?\n]?', re.I)
PROHIBIT_RE2 = re.compile(r'[^.!?\n]*(share\s*na\s*karein|galat\s*content|gandi\s*(video|photo|cheez)|fahash)[^.!?\n]*[.!?\n]?', re.I)

def strip_prohibitions(text):
    t = PROHIBIT_RE.sub(' ', text)
    t = PROHIBIT_RE2.sub(' ', t)
    return t

def screened_out(text):
    t = strip_prohibitions(text)
    m = DROP_RE.search(t)
    return m.group(0) if m else None

def clean_name(title):
    # decode html entities incl. &#x1d5xx; mathematical chars -> plain ascii
    t = html.unescape(title)
    # map mathematical bold/sans chars to ascii
    out = []
    for ch in t:
        try:
            name = unicodedata.name(ch, '')
        except Exception:
            name = ''
        if 'MATHEMATICAL' in name:
            base = name.rsplit(' ', 1)[-1]
            out.append(base if len(base) == 1 else ch)
        else:
            out.append(ch)
    t = ''.join(out)
    t = re.sub(r'\s+', ' ', t).strip()
    # strip leading/trailing emoji/punct junk, keep letters/digits/spaces & - & '
    t = t.strip(' -–—•·|/\\_=+*~#@!?.,:;()[]{}"\'')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# --- categorization ---
CAT_RULES = [
    ("Gaming", [r'pubg', r'free\s*fire', r'bgmi', r'game', r'gaming', r'clash', r'ludo', r'cricket\s*bet', r'fortnite', r'codm', r'minecraft', r'psl', r'esport']),
    ("Education", [r'study', r'exam', r'upsc', r'neet', r'ielts', r'scholarship', r'education', r'student', r'learn', r'english', r'maths?', r'science', r'notes', r'python', r'coaching', r'class\s*\d', r'board\s*exam', r'academy', r'institute', r'school', r'college', r'tuition', r'teacher', r'knowledge', r'general\s*knowledge']),
    ("Online Earning", [r'earn', r'earning', r'online\s*earning', r'freelanc', r'fiverr', r'passive\s*income', r'make\s*money', r'work\s*from\s*home', r'data\s*entry', r'cash', r'prize', r'reward']),
    ("Jobs", [r'job', r'jobs', r'vacancy', r'recruit', r'career', r'placement', r'sarkari', r'govt', r'employment', r'work\s*visa', r'hiring']),
    ("Finance", [r'forex', r'crypto', r'bitcoin', r'binance', r'trading', r'stock', r'investment', r'finance', r'signal']),
    ("Islamic", [r'islam', r'quran', r'muslim', r'naat', r'wazifa', r'dua', r'allah', r'madrasa', r'hamd']),
    ("Sports", [r'sport', r'football', r'cricket', r'fantasy', r'odds', r'dream11', r'wwe', r'hockey']),
    ("Health", [r'health', r'fitness', r'yoga', r'diet', r'weight', r'heart', r'medical', r'doctor']),
    ("News", [r'news', r'headline', r'breaking', r'update(s)?\s*news', r'newspaper']),
    ("Technology", [r'tech', r'android', r'iphone', r'mobile', r'app', r'software', r'computer', r'ai\b', r'coding', r'developer']),
    ("Buy Sell", [r'buy\s*(and|&)?\s*sell', r'shopping', r'deal', r'offer', r'discount', r'sale', r'shop', r'store', r'market', r'buy', r'sell', r'olx', r'propert', r'real\s*estate', r'rent', r'clothing', r'clothes', r'fashion', r'shirt', r'dress', r'supplies', r'supplier', r'wholesale', r'kurti', r'saree', r'lehenga', r'salwar', r'kurta', r'market\s*place']),
    ("Business", [r'business', r'entrepreneur', r'startup', r'marketing', r'advertis', r'import', r'export', r'wholesale', r'reseller']),
    ("Entertainment", [r'movie', r'movies', r'film', r'song', r'music', r'reels?', r'shorts?', r'web\s*series', r'comedy', r'funny', r'joke', r'meme', r'entertainment', r'drama', r'video']),
    ("Friendship", [r'friend', r'friendship', r'girls?', r'boys?', r'chatting', r'chat\s*group', r'dating', r'masti', r'shayari', r'status']),
    ("Funny", [r'jokes?', r'funny', r'comedy', r'meme', r'humor', r'laugh']),
    ("Community & Social", [r'community', r'social', r'pakistan', r'punjab', r'sindh', r'urdu', r'hindi', r'tamil', r'group\s*links?']),
]
CAT_RES = [(c, [re.compile(p, re.I) for p in ps]) for c, ps in CAT_RULES]

def categorize(text):
    for cat, pats in CAT_RES:
        for p in pats:
            if p.search(text):
                return cat
    return "Community & Social"

COUNTRY_HINTS = [
    ("PK", [r'pakistan', r'\bpk\b', r'punjab', r'sindh', r'karachi', r'lahore', r'urdu', r'\bpk\s', r'pkr']),
    ("IN", [r'india', r'indian', r'hindi', r'tamil', r'telugu', r'bengal', r'mumbai', r'delhi', r'upsc', r'neet', r'sarkari', r'inr', r'₹']),
    ("BD", [r'bangladesh', r'bangla', r'dhaka']),
    ("ID", [r'indonesia', r'jakarta']),
    ("NG", [r'nigeria', r'lagos']),
    ("KE", [r'kenya', r'nairobi']),
    ("BR", [r'brasil', r'brazil']),
    ("TR", [r'turkey', r'turkish', r'türk']),
    ("SA", [r'saudi']),
    ("AE", [r'dubai', r'uae', r'emirates']),
    ("US", [r'usa', r'america', r'united\s*states', r'new\s*york']),
    ("GB", [r'\buk\b', r'london', r'england']),
    ("LK", [r'sri\s*lanka', r'sinhala']),
    ("MY", [r'malaysia', r'malay']),
    ("NP", [r'nepal']),
    ("PH", [r'philippines', r'filipino']),
    ("TZ", [r'tanzania']),
    ("UG", [r'uganda']),
    ("GH", [r'ghana']),
    ("ZA", [r'south\s*africa']),
    ("ZW", [r'zimbabwe']),
    ("ZM", [r'zambia']),
    ("MZ", [r'mozambique']),
    ("RW", [r'rwanda']),
    ("SN", [r'senegal']),
    ("ET", [r'ethiopia']),
    ("EG", [r'egypt']),
    ("MA", [r'morocco']),
    ("MM", [r'myanmar']),
    ("KH", [r'cambodia']),
    ("VN", [r'vietnam']),
    ("TH", [r'thailand']),
    ("KR", [r'korea']),
    ("JP", [r'japan']),
    ("CN", [r'china', r'chinese']),
    ("SG", [r'singapore']),
    ("AU", [r'australia']),
    ("NZ", [r'new\s*zealand']),
    ("CA", [r'canada']),
    ("DE", [r'german', r'deutschland']),
    ("FR", [r'france', r'french']),
    ("ES", [r'spain', r'spanish']),
    ("MX", [r'mexico', r'mexican']),
]
COUNTRY_RES = [(c, [re.compile(p, re.I) for p in ps]) for c, ps in COUNTRY_HINTS]

def guess_country(text, source_url=''):
    for code, pats in COUNTRY_RES:
        for p in pats:
            if p.search(text):
                return code
    if 'pakistan' in source_url or '/pk' in source_url or 'groupslink.pk' in source_url or 'newgrouplinks.pk' in source_url or 'whatstele.com/whatsapp/group-links/pakistani' in source_url:
        return 'PK'
    return 'IN'


def sanitize_context(ctx_text):
    """Strip HTML/JSON/link-list junk from listing context; return readable sentences."""
    t = ctx_text or ''
    t = re.sub(r'\\u[0-9a-fA-F]{4}', ' ', t)
    t = re.sub(r'https?://\S+', ' ', t)
    t = re.sub(r'[A-Za-z0-9_\-./]*\.com/[A-Za-z0-9_\-./?=&%]*', ' ', t)
    t = re.sub(r'group_desc|groupRules|group_name|group_tags|\\"|&quot;|&amp;|&#x[0-9a-f]+;', ' ', t)
    # drop tokens that look like code/attributes
    toks = []
    for tok in re.split(r'\s+', t):
        if any(b in tok for b in ('<', '>', '=', '\\', '_blank', 'noopener', 'target', 'href', 'src=', 'data-')):
            continue
        toks.append(tok)
    t = ' '.join(toks)
    # split into sentences, keep readable ones
    sents = []
    for s in re.split(r'[.!?\n]+', t):
        s = re.sub(r'\s+', ' ', s).strip(' •-|–—')
        words = [w for w in s.split(' ') if w]
        alpha = sum(1 for w in words if re.search(r'[A-Za-z]{2,}', w))
        if len(s) >= 25 and alpha >= 3 and s.count('LINK') <= 1:
            sents.append(s)
    return sents

def build_description(name, cat, ctx_text):
    sents = sanitize_context(ctx_text)
    good = []
    for s in sents:
        if screened_out(s):
            continue
        if re.search(r'\d{7,}', s) or 'chat.whatsapp.com' in s:
            continue
        low = s.lower()
        if any(b in low for b in ('tags', 'link :', 'http', 'www.', '.com', 'target', 'href', 'advertising')):
            continue
        nonalpha = sum(1 for ch in s if not (ch.isalnum() or ch.isspace() or ch in '.,!?'))
        if len(s) > 0 and nonalpha / len(s) > 0.30:
            continue
        good.append(s[:160])
        if len(good) >= 2:
            break
    if good:
        desc = '. '.join(good)
        if not desc.endswith('.'):
            desc += '.'
        return desc[:280]
    generics = {
        'Gaming': f'Join {name} to connect with fellow gamers, share tips and play together.',
        'Education': f'{name} is a study group for learners to share notes, resources and exam preparation help.',
        'Online Earning': f'{name} shares online earning ideas, tips and opportunities for members.',
        'Jobs': f'{name} shares job openings, career updates and employment opportunities.',
        'Finance': f'{name} is a group for discussing trading, crypto and finance updates.',
        'Islamic': f'{name} is an Islamic group for sharing religious content, duas and learning.',
        'Sports': f'{name} is a sports group for fans to discuss matches, scores and updates.',
        'Health': f'{name} is a health community sharing wellness tips and healthy living ideas.',
        'News': f'{name} shares the latest news and updates with its members.',
        'Technology': f'{name} is a tech group for sharing apps, tools and technology updates.',
        'Buy Sell': f'{name} is a buy and sell group for deals, shopping offers and product updates.',
        'Business': f'{name} is a business group for networking, marketing and business opportunities.',
        'Entertainment': f'{name} is an entertainment group sharing movies, music, videos and fun content.',
        'Friendship': f'{name} is a friendly group to chat, make new friends and have fun together.',
        'Funny': f'{name} is a fun group sharing jokes, memes and comedy content.',
        'Community & Social': f'{name} is a community group for members to chat, share and stay connected.',
    }
    return generics.get(cat, generics['Community & Social'])

def main():
    verify = json.load(open('team08_verify_slice.json'))
    ctx = json.load(open('team08_context.json'))
    existing = set(json.load(open('../../.existing_codes.json')))
    candidates, pending, screened, dead = [], [], [], 0
    seen_names = set()
    for v in verify:
        code = v['code']
        if code in existing:
            continue
        if v.get('http') == 0:
            pending.append({'code': code, 'invite': 'https://chat.whatsapp.com/' + code,
                            'reason': 'transport failed (curl error/timeout)', 'attempts': 1})
            continue
        title = (v.get('title') or '').strip()
        if v.get('http') == 200 and title:
            c = ctx.get(code, {})
            context = c.get('context', '')
            source = c.get('source', '')
            url = c.get('url', '')
            name = clean_name(title)
            if not name or len(name) < 2:
                screened.append({'code': code, 'reason': 'empty/unreadable group name', 'title': title})
                continue
            if re.search(r'\d{7,}', name) or re.search(r'\+\d[\d\s]{7,}', name):
                screened.append({'code': code, 'reason': 'name looks like a phone number', 'title': title})
                continue
            hay = name + ' ' + context
            bad = screened_out(hay)
            if bad:
                screened.append({'code': code, 'reason': 'screened: matched %r' % bad, 'title': title, 'name': name})
                continue
            cat = categorize(name)
            country = guess_country(name, url)
            desc = build_description(name, cat, context)
            # final screen on generated description
            bad2 = screened_out(name + ' ' + desc)
            if bad2:
                screened.append({'code': code, 'reason': 'screened desc: %r' % bad2, 'title': title, 'name': name})
                continue
            key = name.lower()
            if key in seen_names:
                screened.append({'code': code, 'reason': 'duplicate group name in this batch', 'title': title, 'name': name})
                continue
            seen_names.add(key)
            candidates.append({'name': name, 'category': cat, 'country': country,
                               'description': desc, 'invite': 'https://chat.whatsapp.com/' + code})
        elif v.get('http') == 200 and not title:
            dead += 1  # ambiguous, retries handled separately; counted dead only after retries
        else:
            dead += 1
    json.dump(candidates, open('team08-candidates.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open('team08-pending.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(screened, open('team08_screened.json', 'w'), ensure_ascii=False, indent=1)
    print('candidates:', len(candidates), 'pending:', len(pending), 'screened:', len(screened), 'dead/ambig:', dead)
    from collections import Counter
    print(Counter(c['category'] for c in candidates))
    print(Counter(c['country'] for c in candidates))

if __name__ == '__main__':
    main()
