import json, re, html

CANON = ["Education","Entertainment","Sports","Funny","Community & Social","Finance","Buy Sell","Islamic","Health","News","Jobs","Technology","Gaming","Business","Cooking","Crypto","Poetry","Real Estate","Travel","Scholarship","Freelance","Earning"]

def clean_name(t):
    t = html.unescape(t or '')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def categorize(name, section, dirname=''):
    s = (' ' + name + ' ' + (section or '') + ' ' + (dirname or '') + ' ').lower()
    def has(*ks): return any(k in s for k in ks)
    if has('scholarship', 'fully funded'): return 'Scholarship'
    if has('job', 'vacanc', 'hiring', 'career', 'employment', 'recruit', 'nurses life', 'nurses in kenya'): return 'Jobs'
    if has('learn arabic', 'speak arabic', 'arabic language'): return 'Education'
    if has('islam', 'quran', 'naat', 'nasheed', 'mufti', 'allah', 'deen', 'hadith', 'sharia', 'madina', 'masjid', 'muslim', 'قرآن', 'اسلام', 'نعت', 'مدینہ', 'تلاوت', 'درود', 'احادیث', 'شریعت', 'اللہ', 'محمد', 'عربی', 'نشید', 'اسلامی', 'اہلبیت', 'صحابہ', 'حمد', 'قرآنی', 'قرآنی', 'اسلامک', 'مفتی', 'طارق مسعود'): return 'Islamic'
    if has('crypto', 'bitcoin', 'btc ', 'binance', 'airdrop'): return 'Crypto'
    if has('forex', 'trading', 'invest', 'stock market', 'share market'): return 'Finance'
    if has('football', 'soccer', 'cricket', 'sport', 'fifa', 'wrestling', 'tournament', 'starlink'): pass
    if has('football', 'soccer', 'cricket', 'sport', 'fifa', 'wrestling', 'tournament'): return 'Sports'
    if has('breaking news', 'daily updates', 'newsday', 'news 1', 'foreign news', 'news '): return 'News'
    if has('starlink', 'techzim', 'tech ', 'technology', 'software', ' ai ', 'artificial intelligence', 'airtime and internet', 'smartphone', 'computer'): return 'Technology'
    if has('game', 'gamer', 'pubg', 'free fire'): return 'Gaming'
    if has('real estate', 'property', 'houses for rent', 'house for rent', 'accommodation'): return 'Real Estate'
    if has('buy and sell', 'buy & sell', 'buy sell', 'shop', 'store', 'wholesale', 'marketplace', 'market place', 'cars for sale', 'car sales', 'perfume', 'cosmetic', 'boutique', 'closet'): return 'Buy Sell'
    if has('business', 'entrepreneur', 'zbin', 'company linkages'): return 'Business'
    if has('education', 'study', 'student', 'school', 'university', 'exam', 'learn', 'teacher', 'college', 'academy', 'diploma', 'teachers'): return 'Education'
    if has('health', 'medic', 'doctor', 'hospital', 'fitness', 'clinic', 'keto', 'herbal', 'dietary'): return 'Health'
    if has('travel', 'tour', 'safari', 'tourism'): return 'Travel'
    if has('food', 'cook', 'recipe', 'kitchen', 'spice'): return 'Cooking'
    if has('funny', 'meme', 'comedy', 'joke'): return 'Funny'
    if has('movie', 'music', 'entertainment', 'dance', 'video', 'drama', 'reggae', 'gospel'): return 'Entertainment'
    if has('poetry', 'shayari', 'poem'): return 'Poetry'
    if has('freelance', 'freelancer'): return 'Freelance'
    if has('earn', 'earning', 'make money'): return 'Earning'
    return 'Community & Social'

EXCLUDE_PATTERNS = [
    (r'\bporn\b|\bxxx\b|pornhub|xvideos|sex video|nude|escort|call girl|wasmo|kama sutra', 'hard porn/sexual content'),
    (r'airdrop|crypto airdrop|free money|free cash|binary option|double your money|earn \$\d|make money fast|get rich quick', 'crypto-airdrop/free-money scam'),
    (r'casino|slot|aviator|fixed match|fixed tip|betting|tigrinho|fortune tiger|\bsinais\b|plataformas pagantes|wjbet|matka|sure odd|sure win|fixed odd', 'casino/betting-signal group'),
    (r'message me for private chat|private chat me|dm me for', '1:1 chat solicitation, not a group'),
    (r'hack|crack|card dump|cc dump|pos hacking', 'hacking/fraud content'),
    (r'vermögenssteigerung|wealth increase|investment scheme|guaranteed returns|guaranteed profit', 'investment-scheme content'),
    (r'\bforsage\b|ponzi|pyramid scheme|crypto mlm', 'Forsage/crypto-MLM scam'),
]
# false-positive restores: negated prohibition, weekday, 18+ gate on non-porn, food/fitness
RESTORE_PATTERNS = [
    r'no porn|no sex|no xxx|anti-porn|say no to porn',
    r'sexta-feira',
    r'\bchuta\b',
]

def screen(title):
    t = title.lower()
    for pat in RESTORE_PATTERNS:
        if re.search(pat, t):
            return None  # restored: keep
    for pat, reason in EXCLUDE_PATTERNS:
        if re.search(pat, t):
            return reason
    return None

def build(results_path, pool_path, out_candidates, out_excluded):
    results = json.load(open(results_path))
    pool = json.load(open(pool_path))
    cands, excluded, pending = [], [], []
    for code, r in results.items():
        if r['status'] == 'PENDING':
            pending.append({"code": code, "reason": r['why']})
            continue
        if r['status'] != 'LIVE':
            continue
        title = clean_name(r['og_title'])
        reason = screen(title)
        if reason:
            excluded.append({"code": code, "reason": f"live og:title {title!r} — {reason}"})
            continue
        name = title if title else clean_name(pool[code]['name'])
        # strip trailing junk like ' | WhatsApp' if present
        name = re.sub(r'\s*\|\s*whatsapp.*$', '', name, flags=re.I).strip()
        cat = categorize(name, pool[code].get('section',''), pool[code].get('name',''))
        cc = pool[code]['country']
        desc = f"Join {name}, an active WhatsApp group for {cat}. Connect with members, share updates and chat with people who enjoy {cat.lower()}."
        cands.append({"name": name, "category": cat, "country": cc, "description": desc,
                      "invite": f"https://chat.whatsapp.com/{code}"})
    json.dump(cands, open(out_candidates,'w'), indent=1, ensure_ascii=False)
    json.dump(excluded, open(out_excluded,'w'), indent=1, ensure_ascii=False)
    json.dump(pending, open('team25-pending.json','w'), indent=1, ensure_ascii=False)
    print(f"candidates: {len(cands)} | excluded-live: {len(excluded)} | pending: {len(pending)}")
    return cands, excluded, pending

if __name__ == '__main__':
    build('team25_raw/verify_all.json', 'team25_raw/pool.json', 'team25-candidates.json', 'team25_raw/excluded.json')
