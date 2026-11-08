"""Team 18 final assembly: verified_raw -> team18-appgrouplink.json (schema-exact),
pending_raw -> team18-unverified-pending.json, leads -> team18-leads.json.
Applies porn/scam/minors filters, category+country mapping, original descriptions."""
import json, os, re

WORK = os.path.dirname(os.path.abspath(__file__))

PORN_RE = re.compile(r'porn|pornhub|xxx|nude|sex\s*video|escort|call\s*girl|fuck|dick|pussy|boobs|anal|bokep|🥵|🍆|🍑|🔞|💦|👅|👄|💋|مزا\s*دینے|مزہ\s*دینے|سکسی|sexy\s*(video|girl)|adult\s*video', re.I)
SCAM_RE = re.compile(r'\bsatta\b|\bmatka\b|betway|1xbet|betting\s*odds|\baviator\b.*(pro|class|predict)|double\s*(your|the)\s*money|\bhyip\b|paypal.*(loader|receiver)|receiver.*loader|fix(ed)?\s*(match|game)|money\s*doubler|earn\s*\$\d+\s*per\s*day', re.I)
MINOR_RE = re.compile(r'\b(teen|teens|kids|school\s*(girl|boy)s?|under\s*1[0-7]|1[3-7]\s*(years|yrs|yo)|minor[s]?)\b.*(dating|friendship|love|romance)|dating.*\b(teen|school|minor)', re.I)
MINOR_EXC = re.compile(r'stray\s*kids', re.I)  # K-pop band, not minors-targeted

CATS = [
    ("job", "Jobs"), ("government-jobs", "Jobs"),
    ("cricket", "Sports"), ("football", "Sports"), ("sports", "Sports"), ("fan-club", "Sports"),
    ("gym", "Health"), ("fitness", "Health"), ("yoga", "Health"), ("meditation", "Health"),
    ("weight-loss", "Health"), ("medical", "Health"),
    ("gaming", "Gaming"), ("coin-master", "Gaming"),
    ("education", "Education"), ("study", "Education"), ("teachers", "Education"),
    ("college", "Education"), ("upsc", "Education"), ("iit", "Education"), ("jee", "Education"),
    ("gk", "Education"), ("ielts", "Education"), ("online-classes", "Education"),
    ("scholarship", "Education"), ("english-learning", "Education"), ("duolingo", "Education"),
    ("arabic", "Education"), ("iti", "Education"),
    ("binance", "Crypto"), ("crypto", "Crypto"),
    ("forex-trading", "Finance"), ("trading", "Finance"), ("share-market", "Finance"),
    ("business", "Business"), ("ecommerce", "Business"), ("dropshipping", "Business"),
    ("affiliate-marketing", "Business"), ("digital-marketing", "Business"), ("seo", "Business"),
    ("lead-generation", "Business"), ("sales-and-marketing", "Business"), ("startup", "Business"),
    ("entrepreneur", "Business"), ("freelancer", "Business"), ("reseller", "Business"),
    ("wholesale", "Business"), ("import-export", "Business"), ("real-estate", "Business"),
    ("event-management", "Business"), ("diamond-buyers", "Buy-Sell"),
    ("amazon-deals", "Buy-Sell"), ("shopping", "Buy-Sell"),
    ("news", "News"), ("newspaper", "News"), ("gujarati-newspaper", "News"),
    ("islamic", "Islamic"), ("christian", "Community"),
    ("movie", "Movies"), ("tv-shows", "Movies"), ("k-drama", "Movies"), ("bollywood", "Movies"),
    ("drama", "Entertainment"), ("anime", "Entertainment"), ("celebrity", "Entertainment"),
    ("audition", "Entertainment"), ("acting", "Entertainment"), ("modeling", "Entertainment"),
    ("photography", "Entertainment"), ("photoshop", "Entertainment"), ("photo-editing", "Entertainment"),
    ("tvk-family", "Entertainment"), ("creative", "Entertainment"), ("innovative", "Entertainment"),
    ("art", "Entertainment"),
    ("music", "Music"), ("k-pop", "Music"), ("bts-army", "Music"), ("seventeen-kpop", "Music"),
    ("exo-kpop", "Music"), ("blackpink", "Music"), ("dj", "Music"), ("edm", "Music"),
    ("girls", "Girls"), ("dating", "Friendship"), ("friendship", "Friendship"),
    ("boys", "Friendship"), ("romantic", "Friendship"), ("love", "Friendship"),
    ("funny", "Funny"), ("joker", "Funny"), ("status", "Funny"), ("wallpapers", "Funny"),
    ("travel", "Travel"), ("driver", "Travel"),
    ("cooking", "Food"), ("food", "Food"),
    ("coding", "Technology"), ("web-developer", "Technology"), ("technology", "Technology"),
    ("lifestyle", "Community"), ("motivational", "Other"), ("free", "Other"),
    ("makeup-artist", "Other"), ("beauty-parlour", "Other"), ("designers", "Other"),
    ("graphic-design", "Other"), ("agriculture", "Other"), ("urdu-poetry", "Entertainment"),
]
COUNTRIES = {
    "pakistani": "PK", "indian": "IN", "tamil": "IN", "hindi": "IN", "malayalam": "IN",
    "kerala": "IN", "bangalore": "IN", "uttar-pradesh": "IN", "assam": "IN",
    "gujarati": "IN", "kannada": "IN", "bangladesh": "BD", "dubai": "AE",
    "abu-dhabi": "AE", "qatar": "QA", "kuwait": "KW", "saudi-arabia": "SA", "oman": "OM",
    "bahamas": "BS", "uk": "GB", "usa": "US", "london": "GB", "new-york": "US",
    "california": "US", "las-vegas": "US", "canada": "CA", "paris": "FR", "france": "FR",
    "brazil": "BR", "mexico": "MX", "uganda": "UG", "tanzania": "TZ", "romania": "RO",
    "poland": "PL", "kenya": "KE", "zimbabwe": "ZW", "sri-lanka": "LK", "afghanistan": "AF",
    "spain": "ES", "italy": "IT", "germany": "DE", "china": "CN", "japanese": "JP",
    "thailand": "TH", "philippines": "PH", "nigeria": "NG", "hong-kong": "HK",
    "south-africa": "ZA", "russian": "RU", "gay": "International",
}
COUNTRY_WORD = {"PK": "Pakistan", "IN": "India", "BD": "Bangladesh", "AE": "the UAE",
    "QA": "Qatar", "KW": "Kuwait", "SA": "Saudi Arabia", "OM": "Oman", "BS": "the Bahamas",
    "GB": "the UK", "US": "the USA", "CA": "Canada", "FR": "France", "BR": "Brazil",
    "MX": "Mexico", "UG": "Uganda", "TZ": "Tanzania", "RO": "Romania", "PL": "Poland",
    "KE": "Kenya", "ZW": "Zimbabwe", "LK": "Sri Lanka", "AF": "Afghanistan", "ES": "Spain",
    "IT": "Italy", "DE": "Germany", "CN": "China", "JP": "Japan", "TH": "Thailand",
    "PH": "the Philippines", "NG": "Nigeria", "HK": "Hong Kong", "ZA": "South Africa",
    "RU": "Russia", "International": "members worldwide"}

DESC2 = {
    "Sports": "Members follow live matches, share scores, team news and sports talk with fellow fans every day.",
    "Gaming": "Gamers connect here to discuss strategies, share game updates and team up for online play.",
    "Jobs": "Members receive job alerts, vacancy posts and career updates to help with the job search.",
    "Education": "Students and learners share study notes, exam tips and learning resources with each other.",
    "Entertainment": "Members share entertaining posts, videos and updates on trending topics in this fun community.",
    "Friendship": "A friendly community where members chat, make new friends and enjoy daily conversations.",
    "News": "Stay updated with the latest headlines, breaking news and daily updates shared by members.",
    "Islamic": "Members share Islamic reminders, duas, Quranic verses and religious knowledge in a respectful space.",
    "Business": "Entrepreneurs and professionals exchange business ideas, opportunities and market insights here.",
    "Finance": "Members discuss trading, markets and money matters, sharing tips and financial news.",
    "Buy-Sell": "Buyers and sellers connect here to share deals, product offers and shopping updates.",
    "Health": "Members share health tips, fitness routines and wellness advice to stay fit together.",
    "Community": "A welcoming community group where members chat, help each other and share useful updates.",
    "Technology": "Tech enthusiasts discuss gadgets, software, coding and the latest technology trends.",
    "Crypto": "Crypto followers share market updates, coin news and blockchain discussions in this group.",
    "Travel": "Travellers exchange trip ideas, travel tips and destination guides with fellow explorers.",
    "Music": "Music lovers share songs, playlists and updates about their favourite artists and bands.",
    "Movies": "Movie fans discuss films, shows, trailers and entertainment news with fellow watchers.",
    "Food": "Food lovers share recipes, cooking tips and tasty food ideas with fellow members.",
    "Funny": "Members share funny memes, jokes and comedy clips for a daily dose of laughter.",
    "Girls": "A girls-only social group for chatting, sharing lifestyle posts and making new friends.",
    "Regional": "Locals and interested members connect here to share regional news, culture and community updates.",
    "Other": "Members chat and share useful posts, updates and discussions on everyday topics.",
}

def map_cat_country(slug):
    cat = "Other"
    for key, c in CATS:
        if key in slug:
            cat = c
            break
    if cat == "Other":
        regional_keys = ["pakistan", "india", "tamil", "hindi", "malayalam", "kerala",
                         "bangalore", "uttar", "assam", "gujarati", "kannada", "bangladesh",
                         "dubai", "qatar", "kuwait", "saudi", "oman", "bahamas", "london",
                         "york", "california", "vegas", "canada", "paris", "france", "brazil",
                         "mexico", "uganda", "tanzania", "romania", "poland", "kenya",
                         "zimbabwe", "sri-lanka", "afghanistan", "spain", "italy", "germany",
                         "europe", "china", "thailand", "philippines", "nigeria", "hong-kong",
                         "south-africa", "russian", "international", "abu-dhabi"]
        if any(k in slug for k in regional_keys):
            cat = "Regional"
    country = "International"
    for key, cc in COUNTRIES.items():
        if key in slug:
            country = cc
            break
    return cat, country

def clean_name(s):
    s = re.sub(r'\s+', ' ', (s or "").strip())
    return s[:140]

def describe(name, cat, country):
    cw = COUNTRY_WORD.get(country, "members worldwide")
    base = f"{name} is an active WhatsApp {cat.lower()} group connecting {cw}."
    return base + " " + DESC2.get(cat, DESC2["Other"])

def process(raw_items, with_note=False):
    out, porn, scam, minors, badname = [], 0, 0, 0, 0
    seen = set()
    for it in raw_items:
        name = clean_name(it.get("og_title") or it.get("name") or "")
        code = it["code"]
        slug = it.get("slug", "")
        if not name or len(name) < 2 or code in seen:
            badname += 1
            continue
        if PORN_RE.search(name):
            porn += 1
            continue
        if SCAM_RE.search(name):
            scam += 1
            continue
        if MINOR_RE.search(name) and not MINOR_EXC.search(name):
            minors += 1
            continue
        seen.add(code)
        cat, country = map_cat_country(slug)
        item = {
            "name": name,
            "category": cat,
            "country": country,
            "description": describe(name, cat, country),
            "invite": "https://chat.whatsapp.com/" + code,
            "image": "",
        }
        if with_note:
            item["note"] = it.get("note", "")
        out.append(item)
    return out, {"porn": porn, "scam": scam, "minors": minors, "badname": badname}

if __name__ == "__main__":
    verified = json.load(open(os.path.join(WORK, "team18_verified_raw.json")))
    pending = json.load(open(os.path.join(WORK, "team18_pending_raw.json")))
    v, vs = process(verified)
    p, ps = process(pending, with_note=True)
    json.dump(v, open(os.path.join(WORK, "team18-appgrouplink.json"), "w"), ensure_ascii=False)
    json.dump(p, open(os.path.join(WORK, "team18-unverified-pending.json"), "w"), ensure_ascii=False)
    leads = [
        {"domain": "appgrouplink.com",
         "url": "https://appgrouplink.com/abu-dhabi-whatsapp-group-links/",
         "why": "bulk fetch failed 4/4 retries (slow server); fetch via browser.open text or retry next wave"},
    ]
    raw = json.load(open(os.path.join(WORK, "team18_raw.json")))["pages"]
    failed = [k for k, x in raw.items() if x.get("fetch_failed")]
    for f in failed:
        if "abu-dhabi" not in f:
            leads.append({"domain": "appgrouplink.com",
                          "url": "https://appgrouplink.com/" + f + "/",
                          "why": "bulk fetch failed; retry next wave"})
    json.dump(leads, open(os.path.join(WORK, "team18-leads.json"), "w"), ensure_ascii=False)
    print("VERIFIED:", len(v), "PENDING:", len(p), "LEADS:", len(leads))
    print("verified drops:", vs, "pending drops:", ps)
    cats = {}
    for it in v:
        cats[it["category"]] = cats.get(it["category"], 0) + 1
    print("categories:", dict(sorted(cats.items(), key=lambda x: -x[1])))
    ctys = {}
    for it in v:
        ctys[it["country"]] = ctys.get(it["country"], 0) + 1
    print("top countries:", dict(sorted(ctys.items(), key=lambda x: -x[1])[:10]))
    print("sample:", json.dumps(v[0], ensure_ascii=False)[:220])
