#!/usr/bin/env python3
"""Team14: verify groups1.com candidate codes via og:title."""
import json, re, os, html, time, threading, sys
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104')
CAND = os.path.expanduser('~/workspace/team28_work/candidates.json')
T28V = os.path.expanduser('~/workspace/team28_work/verified.json')
UNION = os.path.join(WAVE, 'dedupe_union.json')
OUT_V = os.path.join(WAVE, 'team14-groups1.json')
OUT_P = os.path.join(WAVE, 'team14-unverified-pending.json')
CKPT = os.path.join(WAVE, 'team14_checkpoint.json')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
OG = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
OG2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)
CODE = re.compile(r'^[A-Za-z0-9]{20,24}$')

PORN = re.compile(r'porn|pornhub|xxx|nude|sex\s*video|escort|call\s*girl|fuck|dick|pussy|boob|anal|bokep|🥵|🍆|🍑|🔞|💦|👅|👄|💋|مزا دینے|مزہ دینے', re.I)
SCAM = re.compile(r'\bsatta\b|\bmatka\b|money\s*double|double\s*your\s*money|hyip|paypal\s*(receiver|loader)|free\s*money|investment\s*double|crypto\s*doubl|loan\s*without|work\s*from\s*home\s*earn\s*lakhs', re.I)
MINORS = re.compile(r'\b(teen|teens|school\s*(girl|boy|kid)|kid|minor|under\s*18|underage)\b.{0,40}\b(dating|love|romance|girlfriend|boyfriend)\b|\b(dating|love|romance)\b.{0,40}\b(teen|school\s*(girl|boy)|under\s*18)\b', re.I)

COUNTRY_KW = {
 'india':'IN','indian':'IN','hindi':'IN','tamil':'IN','telugu':'IN','kannada':'IN','malayalam':'IN','punjabi':'IN','bengali':'IN','marathi':'IN','gujarati':'IN','delhi':'IN','mumbai':'IN','kerala':'IN','kashmir':'IN','assam':'IN',
 'pakistan':'PK','pakistani':'PK','urdu':'PK','karachi':'PK','lahore':'PK','punjab':'PK','sindh':'PK','baloch':'PK','peshawar':'PK','multan':'PK',
 'bangladesh':'BD','bangla':'BD','dhaka':'BD','nigeria':'NG','nigerian':'NG','lagos':'NG','hausa':'NG','igbo':'NG','yoruba':'NG',
 'ghana':'GH','uganda':'UG','kenya':'KE','kenyan':'KE','south africa':'ZA','afrikaans':'ZA','zambia':'ZM','zimbabwe':'ZW','tanzania':'TZ','ethiopia':'ET','somalia':'SO','cameroon':'CM','congo':'CD','rwanda':'RW','senegal':'SN',
 'malaysia':'MY','malaysian':'MY','singapore':'SG','indonesia':'ID','indonesian':'ID','philippines':'PH','filipino':'PH','thailand':'TH','vietnam':'VN','myanmar':'MM','nepal':'NP','nepali':'NP','sri lanka':'LK','maldives':'MV','bhutan':'BT',
 'dubai':'AE','uae':'AE','emirates':'AE','saudi':'SA','qatar':'QA','kuwait':'KW','oman':'OM','bahrain':'BH','yemen':'YE','iraq':'IQ','jordan':'JO','lebanon':'LB','egypt':'EG','egyptian':'EG','morocco':'MA','algeria':'DZ','tunisia':'TN','libya':'LY',
 'turkey':'TR','turkish':'TR','iran':'IR','afghanistan':'AF','afghan':'AF',
 'china':'CN','chinese':'CN','hong kong':'HK','taiwan':'TW','japan':'JP','korea':'KR','germany':'DE','german':'DE','france':'FR','french':'FR','italy':'IT','italian':'IT','spain':'ES','spanish':'ES','portugal':'PT','netherlands':'NL','belgium':'BE','sweden':'SE','norway':'NO','denmark':'DK','finland':'FI','greece':'GR','greek':'GR','poland':'PL','ukraine':'UA','russia':'RU','russian':'RU','armenia':'AM','armenian':'AM','azerbaijan':'AZ','azerbaijani':'AZ','georgia':'GE',
 'uk':'GB','britain':'GB','london':'GB','usa':'US','america':'US','canada':'CA','australia':'AU','brazil':'BR','argentina':'AR','colombia':'CO','peru':'PE','mexico':'MX','arabic':'SA',
}

CAT_TMPL = {
 'Jobs': ('Find active job vacancies, recruitment alerts and career openings shared daily in this {t} WhatsApp group.','Connect with employers and job seekers exchanging hiring leads and application tips for {t}.'),
 'Education': ('A study-focused WhatsApp group for {t} with notes, exam prep and learning resources.','Students and teachers share study material, exam tips and academic guidance on {t} in this group.'),
 'Business': ('Network with entrepreneurs and traders discussing {t} deals and business ideas.','A business WhatsApp community sharing {t} market insights, partnerships and growth strategies.'),
 'Buy-Sell': ('Buy and sell {t} directly with trusted buyers and sellers in this active WhatsApp group.','Daily deals, wholesale rates and new arrivals for {t} posted by verified sellers.'),
 'Friendship': ('Meet friendly people and make new friends chatting about {t} in this social WhatsApp group.','A warm friendship community where members chat daily about {t} and everyday life.'),
 'News': ('Get breaking {t} news updates and headlines delivered fast in this WhatsApp group.','Follow the latest {t} news, reports and updates shared by active members.'),
 'Islamic': ('Join fellow Muslims for {t} Islamic reminders, duas and religious discussions.','A faith-based WhatsApp group sharing {t} Islamic knowledge, Quranic reminders and naats.'),
 'Gaming': ('Team up with gamers for {t} matches, tournaments and gaming tips.','A gaming WhatsApp group for {t} players to find squads, share strategies and win together.'),
 'Regional': ('Connect with people from your region to chat about {t} news, culture and community life.','A regional WhatsApp community for {t} members sharing local updates and discussions.'),
 'Community': ('Join an active community WhatsApp group to discuss {t} and help each other.','Members support each other with daily {t} discussions, advice and local updates.'),
 'Entertainment': ('Daily {t} entertainment, fun posts and viral content in this lively WhatsApp group.','Enjoy {t} memes, videos and entertainment shared by fun-loving members.'),
 'Movies': ('Get {t} movie updates, reviews and recommendations in this film-lovers WhatsApp group.','Discuss {t} films, trailers and releases with fellow movie fans daily.'),
 'Girls': ('A friendly WhatsApp group for girls to chat about {t}, lifestyle and daily fun.','Ladies connect here to share {t} tips, fashion ideas and friendly conversations.'),
 'Technology': ('Stay updated on {t} tech news, gadgets and digital trends in this group.','Tech enthusiasts discuss {t} innovations, apps and how-to guides daily.'),
 'Travel': ('Plan trips and share {t} travel tips, photos and itineraries with fellow travellers.','A travel WhatsApp group for {t} lovers exchanging destination guides and experiences.'),
 'Food': ('Food lovers share {t} recipes, restaurant tips and cooking ideas in this group.','Discover {t} dishes, recipes and food deals posted by members daily.'),
 'Music': ('Music fans share {t} songs, playlists and artist news in this WhatsApp group.','Enjoy {t} music, new releases and recommendations from fellow listeners.'),
 'Pets': ('Pet lovers share {t} photos, care tips and adoption info in this friendly group.','A caring WhatsApp community for {t} pet owners and animal lovers.'),
 'Health': ('Get {t} health tips, wellness advice and fitness motivation in this group.','Members share {t} health guidance, remedies and healthy lifestyle ideas.'),
 'Other': ('An active WhatsApp group for {t} with daily discussions and updates.','Join members chatting about {t}, sharing news and helpful posts every day.'),
}

def clean_topic(post_title):
    t = re.sub(r'(?i)\s*whats?app\s*group\s*links?\s*$', '', post_title).strip()
    t = re.sub(r'(?i)\s*whats?app\s*$', '', t).strip()
    return t or 'community'

def country_of(text):
    tl = ' ' + text.lower() + ' '
    for kw, cc in COUNTRY_KW.items():
        if kw in tl:
            return cc
    return 'International'

def description_for(cat, topic):
    tmpls = CAT_TMPL.get(cat, CAT_TMPL['Other'])
    s = tmpls[hash(topic) % len(tmpls)].format(t=topic)
    return s[:280]

def og_title(html_text):
    m = OG.search(html_text) or OG2.search(html_text)
    if not m: return ''
    return html.unescape(m.group(1)).strip()

def make_session():
    s = requests.Session()
    s.headers.update(UA)
    return s

STOP = threading.Event()
sess_local = threading.local()

def get_session():
    if getattr(sess_local, 's', None) is None:
        sess_local.s = make_session()
    return sess_local.s

def verify(rec):
    code = rec['code']
    if not CODE.match(code):
        return ('drop', 'bad-code')
    url = f'https://chat.whatsapp.com/{code}'
    try:
        s = get_session()
        r = s.get(url, timeout=55, allow_redirects=True)
        if r.status_code == 429:
            STOP.set(); sess_local.s = None
            return ('rate_limited', None)
        title = og_title(r.text)
    except Exception:
        sess_local.s = None
        return ('pending', 'transport failure')
    if not title:
        return ('pending', 'no og:title (dead or unreachable)')
    if PORN.search(title) or PORN.search(rec.get('post_title','')):
        return ('drop', 'porn')
    if SCAM.search(title):
        return ('drop', 'scam')
    if MINORS.search(title):
        return ('drop', 'minors')
    cat = rec.get('cat') or 'Other'
    topic = clean_topic(rec.get('post_title',''))
    cc = country_of(title + ' ' + rec.get('post_title',''))
    desc = description_for(cat, topic)
    item = {'name': title[:160], 'category': cat, 'country': cc,
            'description': desc, 'invite': url, 'image': ''}
    return ('ok', item)

def main():
    union = set(json.load(open(UNION)))
    cands = json.load(open(CAND))
    t28v = json.load(open(T28V))
    done28 = set()
    for x in t28v:
        m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', x.get('invite',''))
        if m: done28.add(m.group(1))
    pool = []
    seen = set()
    for r in reversed(cands):  # newest-first heuristic
        c = r['code']
        if c in union or c in done28 or c in seen: continue
        seen.add(c); pool.append(r)
    print('pool:', len(pool), flush=True)
    start = 0
    if os.path.exists(CKPT):
        start = json.load(open(CKPT)).get('idx', 0)
        print('resuming from', start, flush=True)
    verified, pending = [], []
    if os.path.exists(OUT_V):
        try: verified = json.load(open(OUT_V))
        except Exception: verified = []
    if os.path.exists(OUT_P):
        try: pending = json.load(open(OUT_P))
        except Exception: pending = []
    counts = {'ok':0,'pending':0,'porn':0,'scam':0,'minors':0,'bad':0,'rl':0}
    lock = threading.Lock()
    def task(i, rec):
        global done
        if STOP.is_set(): return
        kind, payload = verify(rec)
        with lock:
            if kind == 'ok':
                verified.append(payload); counts['ok'] += 1
            elif kind == 'pending':
                pending.append({'code': rec['code'], 'post_title': rec.get('post_title',''), 'cat': rec.get('cat',''), 'note': payload}); counts['pending'] += 1
            elif kind == 'rate_limited':
                counts['rl'] += 1
            else:
                counts[payload if payload in counts else 'bad'] += 1
        return kind
    N = len(pool)
    BATCH = 2000
    for bs in range(start, N, BATCH):
        if STOP.is_set(): break
        batch = pool[bs:bs+BATCH]
        with ThreadPoolExecutor(max_workers=30) as ex:
            list(ex.map(lambda t: task(*t), enumerate(batch, bs)))
        with lock:
            json.dump(verified, open(OUT_V,'w'))
            json.dump(pending, open(OUT_P,'w'))
            json.dump({'idx': min(bs+BATCH, N), 'ts': time.time()}, open(CKPT,'w'))
        print('done', min(bs+BATCH,N), counts, flush=True)
    if STOP.is_set() or counts['rl']:
        # bank remainder as rate-limited pending
        done_idx = json.load(open(CKPT)).get('idx', 0) if os.path.exists(CKPT) else N
        for r in pool[done_idx:]:
            pending.append({'code': r['code'], 'post_title': r.get('post_title',''), 'cat': r.get('cat',''), 'note': 'rate-limited'})
            counts['pending'] += 1
        json.dump(pending, open(OUT_P,'w'))
        json.dump({'idx': N, 'ts': time.time(), 'stopped_429': True}, open(CKPT,'w'))
    print('FINAL', counts, 'verified_file:', len(verified), 'pending_file:', len(pending), flush=True)

if __name__ == '__main__':
    main()
