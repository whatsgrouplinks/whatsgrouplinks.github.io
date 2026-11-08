#!/usr/bin/env python3
"""TEAM 28R (replacement) — groups1.com non-cricket/sports slice, wave_20261103.
Scrapes category pages, extracts codes, dedupes vs union, verifies via og:title.
State checkpointed so reruns resume."""
import json, re, time, html, os, sys, requests

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261103/')
STATE_F = os.path.join(WAVE, '_team28R_state.json')
OUT_VERIFIED = os.path.join(WAVE, 'team28R-groups1.json')
OUT_PENDING = os.path.join(WAVE, 'team28R-unverified-pending.json')
OUT_LEADS = os.path.join(WAVE, 'team28R-leads.json')
URLS_F = '/tmp/g1_allurls.txt'

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
LI_RE = re.compile(r'<li>\s*(.*?)\s*[—-]\s*<a\s+href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"', re.S)
LI_RE2 = re.compile(r'<li>(.*?)<a\s+href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"', re.S)
TAG_RE = re.compile(r'<[^>]+>')

PORN_WORDS = ['porn','pornhub','xxx','nude','sex video','escort','call girl','callgirl','fuck','dick','pussy','boobs','anal','onlyfans','desi-mms','mms video','leak video']
PORN_EMOJI = ['\U0001F975','\U0001F346','\U0001F351','\U0001F51E','\U0001F4A6','\U0001F445','\U0001F444','\U0001F48B']
MULE_WORDS = ['old coin buyer','paypal loader','passcode','fake investment','counterfeit','forsage','loading','whatsapp unban trick']

# Sports/betting pages EXCLUDED (team18 wave-20261030 / team47 this wave)
EXCLUDE_SLUGS = {
 'cricket-whatsapp-group-link','cricket-betting-whatsapp-group-link','cricket-highlights-whatsapp-group-link',
 'icc-cricket-whatsapp-group-link','cpl-whatsapp-group-link','football-whatsapp-group-link',
 'football-predictions-whatsapp-group-link','premier-league-whatsapp-group-link','chelsea-whatsapp-group-link',
 'liverpool-whatsapp-group-link','horse-racing-whatsapp-group-link','chess-whatsapp-group-link',
 'esports-whatsapp-group-link','bet-prediction-whatsapp-group-link','bet365-whatsapp-group-link',
 'bet9ja-whatsapp-group-link','betting-whatsapp-group-link','betway-whatsapp-group-link',
 'bookie-whatsapp-group-link','fixed-matches-correct-score-whatsapp-group-link','fixed-matches-whatsapp-group-link',
 'vip-fixed-matches-whatsapp-group-link','correct-score-pay-after-win-whatsapp-group-link',
 'correct-score-whatsapp-group-link','online-betting-whatsapp-group-link','sportybet-whatsapp-group-link',
 'sure-bet-whatsapp-group-link','odds-whatsapp-group-link','fun88-whatsapp-group-link',
 'disawar-satta-whatsapp-group-link','aviator-game-whatsapp-group-link',
}

CAT_RULES = [
 (['job','employment','rojgar','psc','tnpsc','nqt','staff-nurse','medical-representative','driver-job','restaurant-job','retail-job','offshore','oil-and-gas','power-plant','packers','movers','tally','airport-job','police-job','railway','tcs','speed-job','ushering','internship','career','vacancy','qa-and-qc','human-resource','grab-driver','bolt-driver','taxi-driver','truck-driver','car-driver','acting-driver'],'Jobs'),
 (['class','study','exam','ielts','quiz','grammar','teacher','universit','school','college','coaching','cbse','neet','ias','bpsc','css','ppsc','apsc','pharmacy','bca','biology','chemistry','physics','engineering','nursing','medical-student','paramedical','open-university','polytechnic','doubtnut','drishti','rajaji','talent-academy','sbi-po','nda','jkssb','current-affairs','general-knowledge','knowledge','science','education','english-learning','english-speaking','online-quran','study-abroad','msw'],'Education'),
 (['business','affiliate','digital-marketing','entrepreneur','fiverr','e-commerce','online-business','amazon-seller','seller','company','networking','sales-and-marketing','marketing','investment-india','startup','csc','vle','aadhar'],'Business'),
 (['drama','web-series','cartoon','cid','kurulus','turkish-drama','entertainment','all-drama'],'Entertainment'),
 (['movie','cinema','netflix','bollywood','ullu','horror-movie','korean-movie','punjabi-movie','tamil-movie','telugu-movie'],'Movies'),
 (['islamic','azadari','quran','mufti','molana','ahle-hadees','nikah','bible','jesus','iskcon','krishna','hanuman','dwarkadhish','bhakti','buddhist','jesus'],'Islamic'),
 (['girls','aunty','bhabhi','ladies','house-wife','female-'],'Girls'),
 (['dating','matrimony','marriage','biodata','rishta','shadi','divorced','widow','couple','singles','flirting','chatting','friendship'],'Friendship'),
 (['news','al-jazeera','bbc','dawn','dainik','greater-kashmir','kawish','gulistan','otv','ary-news','hindi-news','92-news','karachi-news'],'News'),
 (['pubg','ludo','fortnite','gta','pokemon','roblox','coin-master','free-fire','call-of-duty','mobile-legends','rummy','poker','game-developer','pc-gaming','android-game','fiewin','ludo-king','ludo-star'],'Gaming'),
 (['doctor','medical','nursing','health','female-doctor','pharma','hospital'],'Health'),
 (['ai-whatsapp','computer-technology','video-editing','facebook','instagram','twitter','android','iphone','hosting'],'Technology'),
 (['binance','crypto','forex','bank-nifty','zerodha','dabba','tron','opay','palmpay','paypal','online-loan','earning','online-earning','investment'],'Finance'),
 (['shopping','amazon','flipkart','saree','kurti','jewellery','olx','mobile-sale','iphone-sell','buy-and-sell','buy/sell','buysell','wholesale','dress','dresses','jeans','shirt','shoes','sneaker','blouse','leggings','pants','sweater','innerwear','t-shit','shorts','fashion','beauty-parlour','tailoring','reseller','aarev-jewellery','aps-jewellery','gj-jewellery','car-sale','mobile-accessories','mart'],'Buy-Sell'),
 (['restaurant','food','hotel-job','fruit','spice'],'Food'),
 (['music','dj','blackpink','bts','kpop','cumbia','electronic-music','jungkook'],'Music'),
 (['funny','joke','motivation','sad','love-shayari','shayari','romantic','poetry','novel','astrology'],'Funny'),
 (['tamil','malayalam','telugu','kannada','gujarati','bengali','marathi','punjabi','urdu','pashto','sindhi','hindi','arabic','french','german','chinese','danish','dutch','estonian','finnish','greek','afrikaans','albanian','armenian','azerbaijani','basque','belarusian','czech','indonesian','peruvian','croatian','zambian','chennai','madurai','coimbatore','trichy','salem','erode','karur','dharmapuri','dindigul','thanjavur','theni','sivagangai','pudukkottai','ramanathapuram','ranipet','kallakurichi','kanchipuram','kanniyakumari','nagapattinam','namakkal','nilgiri','perambalur','pattukkottai','tenkasi','velai-vaippu','karachi','lagos','nairobi','abuja','balochistan','malaysia'],'Regional'),
 (['travel','island','wildlife','forest','agriculture','horticulture','livestock','tomato-farming','train','ticket'],'Travel'),
 (['pti','bjp','aap','admk','dmk','pmk','cpim','trs','rjd','congress','political','politics','maryam-nawaz','revanth-reddy','udhayanidhi','hanuman-beniwal','rashtriya-janata'],'Other'),
 (['community','deaf','spiritual','uncle','real-','search-'],'Community'),
]

COUNTRY_RULES = [
 ('pakistan','PK'),('karachi','PK'),('urdu','PK'),('pashto','PK'),('sindhi','PK'),('pti','PK'),('punjabi-poetry','PK'),
 ('india','IN'),('tamil','IN'),('telugu','IN'),('malayalam','IN'),('kannada','IN'),('gujarati','IN'),('marathi','IN'),('bengali','IN'),
 ('hindi','IN'),('mumbai','IN'),('delhi','IN'),('chennai','IN'),('assam','IN'),('bihar','IN'),('punjab','IN'),('kerala','IN'),('bangla','IN'),
 ('nigeria','NG'),('lagos','NG'),('abuja','NG'),('nigerian','NG'),('hausa','NG'),('opay','NG'),('palmpay','NG'),
 ('usa','US'),('america','US'),('new-york','US'),('california','US'),('kenya','KE'),('nairobi','KE'),('ghana','GH'),('uganda','UG'),
 ('ethiopia','ET'),('uk','GB'),('bangladesh','BD'),('indonesia','ID'),('malaysia','MY'),('nepal','NP'),('sri-lanka','LK'),
 ('philippines','PH'),('singapore','SG'),('zambia','ZM'),('zimbabwe','ZW'),('rwanda','RW'),('somalia','SO'),('canada','CA'),
 ('australia','AU'),('dubai','AE'),('saudi','SA'),('germany','DE'),('france','FR'),('spain','ES'),('italy','IT'),('russia','RU'),
 ('turkey','TR'),('egypt','EG'),('peru','PE'),('cumbia','CO'),('finnish','FI'),('croatian','HR'),('chinese','CN'),('japan','JP'),
 ('korea','KR'),('vietnam','VN'),('thailand','TH'),('brazil','BR'),('mexico','MX'),('argentina','AR'),('colombia','CO'),
 ('csc','IN'),('dharmapuri','IN'),('balija','IN'),('thanjavur','IN'),
]

NAME_COUNTRY_HINTS = [
 ('lagos','NG'),('abuja','NG'),('nairobi','KE'),('karachi','PK'),('lahore','PK'),('islamabad','PK'),('rawalpindi','PK'),
 ('chennai','IN'),('mumbai','IN'),('delhi','IN'),('kolkata','IN'),('bangalore','IN'),('hyderabad','IN'),('madurai','IN'),
 ('coimbatore','IN'),('dhaka','BD'),('kathmandu','NP'),('colombo','LK'),('jakarta','ID'),('kuala lumpur','MY'),
 ('cairo','EG'),('riyadh','SA'),('jeddah','SA'),('dubai','AE'),('doha','QA'),('muscat','OM'),('manama','BH'),('kuwait','KW'),
 ('accra','GH'),('kampala','UG'),('addis','ET'),('kigali','RW'),('lusaka','ZM'),('harare','ZW'),('mogadishu','SO'),
 ('new york','US'),('los angeles','US'),('chicago','US'),('houston','US'),('london','GB'),('toronto','CA'),('sydney','AU'),
 ('india','IN'),('banglore','IN'),('mysore','IN'),('dharmapuri','IN'),('thanjavur','IN'),('tanjavur','IN'),('tanjore','IN'),('revanth','IN'),('jagan','IN'),('ysrcp','IN'),('telugu','IN'),('nalgonda','IN'),('bidar','IN'),('banaras','IN'),('malad','IN'),('haryana','IN'),('bangladesh','BD'),(' bd','BD'),
]

def clean_text(s):
    s = TAG_RE.sub(' ', s); s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_name(name):
    """Strip trailing list separators and site-phrase tails from page-extracted names."""
    n = name.strip()
    n = re.sub(r'\s*[–—-]\s*Group Link.*$', '', n, flags=re.I)
    n = re.sub(r'\s*[–—\-]+\s*$', '', n)
    return n.strip()

def normalize_item(item):
    """Re-clean name and re-classify by name keywords (fixes slug-level misses)."""
    name = clean_name(item.get('name', ''))
    nl = name.lower()
    cat = item.get('category', 'Other'); cc = item.get('country', 'International')
    # strong name-based overrides
    if 'csc' in nl or 'vle' in nl or 'aadhar' in nl or 'aadhaar' in nl:
        cat, cc = 'Business', 'IN'
    elif 'matrimony' in nl or 'marriage' in nl or 'rishta' in nl or 'shadi' in nl:
        cat = 'Friendship'
        if 'bd' in nl.split() or 'bangladesh' in nl: cc = 'BD'
        elif cc == 'International':
            for key, c2 in NAME_COUNTRY_HINTS:
                if key in nl: cc = c2; break
            else:
                # default South-Asian matrimony slugs are Indian
                cc = 'IN'
    elif 'buy/sell' in nl or 'buy & sell' in nl:
        cat = 'Buy-Sell'
    if cc == 'International':
        for key, c2 in NAME_COUNTRY_HINTS:
            if key in nl: cc = c2; break
    item['name'] = name
    item['category'] = cat
    item['country'] = cc
    item['description'] = make_desc(name, cat, cc)
    return item

def classify(slug, name):
    blob = (slug + ' ' + name).lower()
    cat = 'Other'
    for keys, c in CAT_RULES:
        if any(k in blob for k in keys):
            cat = c; break
    country = 'International'
    for key, cc in COUNTRY_RULES:
        if key in slug.lower():
            country = cc; break
    if country == 'International':
        nl = name.lower()
        for key, cc in NAME_COUNTRY_HINTS:
            if key in nl:
                country = cc; break
    return cat, country

def is_porn(name):
    n = name.lower()
    return any(w in n for w in PORN_WORDS) or any(e in name for e in PORN_EMOJI)

def is_mule(name):
    return any(w in name.lower() for w in MULE_WORDS)

def make_desc(name, cat, country):
    cc = 'Pakistani' if country=='PK' else 'Indian' if country=='IN' else 'Nigerian' if country=='NG' else 'Kenyan' if country=='KE' else ''
    topic = name.strip()
    d = {
     'Jobs': f"Find the latest job openings, vacancies and career updates in this active {cc} jobs WhatsApp group. Members share employment alerts, interview tips and hiring news daily.",
     'Education': f"Join this active {cc} education WhatsApp group for study notes, exam updates and learning resources. Students share preparation tips, past papers and academic guidance.",
     'Entertainment': f"Join this lively {cc} entertainment WhatsApp group for the latest shows, dramas and celebrity updates. Members share episode discussions, trailers and fun content daily.",
     'Movies': f"Join this {cc} movies WhatsApp group for film updates, reviews and recommendations. Members discuss new releases, share trailers and chat about their favourite movies.",
     'Islamic': f"Join this {cc} Islamic WhatsApp group for Quranic reminders, duas and religious knowledge. Members share Islamic quotes, lectures and spiritual guidance daily.",
     'Girls': f"Join this friendly {cc} girls WhatsApp group to chat, make friends and share daily updates. A social space for fun conversations, lifestyle topics and new friendships.",
     'Friendship': f"Join this friendly {cc} friendship WhatsApp group to meet new people and make friends. Members chat, share stories and connect in a warm social community.",
     'News': f"Stay updated with the latest headlines in this active {cc} news WhatsApp group. Members share breaking news, current affairs and daily updates as they happen.",
     'Gaming': f"Join this {cc} gaming WhatsApp group for game updates, tips and friendly matches. Gamers share strategies, event news and squad invites daily.",
     'Health': f"Join this {cc} health WhatsApp group for wellness tips, medical updates and healthy living advice. Members share health news and fitness guidance.",
     'Technology': f"Join this {cc} technology WhatsApp group for tech news, app updates and gadget discussions. Members share tips, tutorials and the latest digital trends.",
     'Crypto': f"Join this {cc} crypto WhatsApp group for market updates, trading discussions and coin news. Members share analysis, price alerts and blockchain insights.",
     'Finance': f"Join this {cc} finance WhatsApp group for money tips, investment ideas and market updates. Members discuss earnings, trading and smart saving strategies.",
     'Buy-Sell': f"Join this {cc} buy and sell WhatsApp group for great deals, product listings and shopping offers. Members post items for sale and discover daily bargains.",
     'Music': f"Join this {cc} music WhatsApp group for the latest songs, artists and playlists. Music lovers share tracks, videos and concert updates daily.",
     'Funny': f"Join this {cc} funny WhatsApp group for jokes, memes and daily laughter. Members share hilarious content, comedy clips and light-hearted fun.",
     'Regional': f"Join this {cc} regional WhatsApp group to connect with your community. Members share local news, culture, language content and friendly discussions.",
     'Travel': f"Join this {cc} travel WhatsApp group for trip ideas, destination tips and travel deals. Members share itineraries, photos and holiday planning advice.",
     'Food': f"Join this {cc} food WhatsApp group for recipes, restaurant tips and tasty recommendations. Food lovers share dishes, cooking ideas and dining deals.",
     'Community': f"Join this {cc} community WhatsApp group for local updates, discussions and friendly support. Members share announcements, events and helpful information.",
     'Other': f"Join this active {cc} WhatsApp group for daily updates, discussions and community news. Members share useful information and stay connected.",
    }
    t = d.get(cat, d['Other'])
    return t.replace('  ', ' ').strip()

def fetch(url, timeout=25):
    r = requests.get(url, headers=UA, timeout=timeout)
    return r

def verify(code):
    """Returns (og_title or None-if-dead, 'transport' if transport failure). Fresh connection."""
    try:
        r = requests.get(f'https://chat.whatsapp.com/{code}', headers=UA, timeout=25)
        html_txt = r.text
    except Exception:
        return (None, 'transport')
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html_txt)
    if not m:
        m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', html_txt)
    title = html.unescape(m.group(1)).strip() if m else ''
    return (title, 'ok')

def main():
    union = set(json.load(open(os.path.join(WAVE, 'dedupe_union.json'))))
    print('union size', len(union), flush=True)
    state = {'processed': [], 'seen': [], 'verified': [], 'pending': [], 'porn_drops': 0, 'mule_flags': 0}
    if os.path.exists(STATE_F):
        state = json.load(open(STATE_F))
        print('resuming: processed', len(state['processed']), 'verified', len(state['verified']), 'pending', len(state['pending']), flush=True)
    seen = set(state['seen']); processed = set(state['processed'])
    verified = [normalize_item(v) for v in state['verified']]; pending = [normalize_item(p) for p in state['pending']]
    print('normalized', len(verified), 'existing verified items', flush=True)

    urls = [u.strip() for u in open(URLS_F) if u.strip()]
    slugs = []
    for u in urls:
        slug = u.replace('https://groups1.com/', '').strip('/')
        if 'telegram' in slug or 'whatsapp' not in slug: continue
        if slug in EXCLUDE_SLUGS: continue
        if slug in processed: continue
        if slug not in slugs: slugs.append(slug)
    print('pages to process:', len(slugs), flush=True)
    # Process from the END of the slug list: the original team28 worker is also
    # on this slice (likely from the start); meet in the middle. Merge dedupes.
    slugs = list(reversed(slugs))

    max_pages = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    pages_done = 0
    for slug in slugs:
        if pages_done >= max_pages: break
        url = f'https://groups1.com/{slug}/'
        try:
            r = fetch(url)
        except Exception as e:
            print('FETCH FAIL', slug, e, flush=True); continue
        if r.status_code != 200 or 'chat.whatsapp.com' not in r.text:
            processed.add(slug); continue
        pairs = []
        for rx in (LI_RE, LI_RE2):
            for m in rx.finditer(r.text):
                raw_name, code = m.group(1), m.group(2)
                name = clean_text(raw_name)
                if code not in seen and code not in union:
                    pairs.append((name, code))
                    seen.add(code)
        # dedupe pairs by code keeping first name
        uniq = {}
        for n, c in pairs: uniq.setdefault(c, n)
        print(f'{slug}: {len(uniq)} fresh codes', flush=True)
        for code, name in uniq.items():
            if is_porn(name):
                state['porn_drops'] = state.get('porn_drops', 0) + 1; continue
            if is_mule(name):
                state['mule_flags'] = state.get('mule_flags', 0) + 1; continue
            title, status = verify(code)
            if status == 'transport':
                pending.append({'name': name or 'WhatsApp Group', 'category': classify(slug, name)[0],
                                'country': classify(slug, name)[1], 'description': make_desc(name, classify(slug, name)[0], classify(slug, name)[1]),
                                'invite': f'https://chat.whatsapp.com/{code}', 'image': '', 'note': 'transport failure'})
                time.sleep(0.6); continue
            if not title:
                time.sleep(0.6); continue  # dead
            cat, cc = classify(slug, name)
            gname = clean_name(name) if (len(clean_name(name)) >= 3 and 'http' not in name.lower()) else clean_name(title)
            item = {'name': gname, 'category': cat, 'country': cc,
                    'description': make_desc(gname, cat, cc),
                    'invite': f'https://chat.whatsapp.com/{code}', 'image': ''}
            verified.append(normalize_item(item))
            time.sleep(0.7)
        processed.add(slug); pages_done += 1
        state.update({'processed': list(processed), 'seen': list(seen), 'verified': verified, 'pending': pending})
        json.dump(state, open(STATE_F, 'w'))
        print(f'  -> verified total {len(verified)}, pending {len(pending)}, porn drops {state.get("porn_drops",0)}', flush=True)
    # final write
    json.dump(verified, open(OUT_VERIFIED, 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(OUT_PENDING, 'w'), ensure_ascii=False, indent=1)
    leads = [{'domain': 'groups1.com', 'url': 'https://groups1.com/sitemap_index.xml',
              'why': f"Resume point: {len(processed)} of ~{len(processed)+len(slugs)} eligible non-sports pages processed. Sitemap has full page list; rerun with same script."}]
    json.dump(leads, open(OUT_LEADS, 'w'), ensure_ascii=False, indent=1)
    print('DONE', len(verified), len(pending), flush=True)

if __name__ == '__main__':
    main()
