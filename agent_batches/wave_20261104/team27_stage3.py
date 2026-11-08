import re, json, html, os, sys

sys.stdout.reconfigure(line_buffering=True)
WD = os.path.dirname(os.path.abspath(__file__))

cands = json.load(open(os.path.join(WD, "team27_candidates.json")))
bycode = {c["code"]: c for c in cands}
v = json.load(open(os.path.join(WD, "team27_verify_results.json")))
live = v["live"]
transport = v["transport"]

PORN_RES = [
    r"pornhub", r"\bporn\b", r"pornograph", r"\bxxx\b", r"\bnude\b", r"\bescort\b",
    r"call\s*girl", r"fuck", r"\bdick\b", r"pussy", r"\bboobs\b", r"\banal\b",
    r"bokep", r"مزا دینے", r"مزہ دینے", r"sex\s*video", r"\bsex\b", r"🥵", r"🍆", r"🍑", r"🔞", r"💦", r"👅", r"👄", r"💋",
    r"भाभी\s*चोदी", r"madarchod",
]
porn_re = re.compile("|".join(PORN_RES), re.I)

FRAUD_RES = [
    r"carding", r"\bcc\b\s*sellers?", r"carder", r"1xbet", r"betting",
    r"cashout", r"money\s*mule", r"hustler", r"ultimatebroker", r"julius\s*baer",
    r"gmail\s*market", r"paypal.{0,20}(receiver|loader)",
]
fraud_re = re.compile("|".join(FRAUD_RES), re.I)

PERSONAL_RES = [r"\+?\d{10,}", r"[\w.+-]+@[\w-]+\.\w+"]
personal_re = re.compile("|".join(PERSONAL_RES))

def clean_title(t):
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def clean_raw(raw):
    t = re.sub(r"<[^>]+>", " ", raw)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    parts = [p for p in re.split(r"Join (?:Here|Now)|Click Here|Join Link|Join$", t, flags=re.I) if p.strip()]
    t = parts[-1].strip() if parts else ""
    return t[-120:]

def guess_country(text):
    t = text
    if re.search(r"🇵🇰|Pakistan|PAKISTAN|\bPAK\b|\bPak\b", t): return "PK"
    if re.search(r"🇮🇳|India|INDIA|Kerala|Mumbai|Tamil|TAMIL", t): return "IN"
    if re.search(r"Nigeria|🇳🇬", t, re.I): return "NG"
    if re.search(r"Bangladesh|\bBD\b", t, re.I): return "BD"
    if re.search(r"Nepal", t, re.I): return "NP"
    if re.search(r"\bUSA\b", t): return "US"
    if re.search(r"\bUK\b", t): return "GB"
    if re.search(r"Brazil", t, re.I): return "BR"
    if re.search(r"Indonesia", t, re.I): return "ID"
    if re.search(r"Malaysia", t, re.I): return "MY"
    if re.search(r"Turkey|Turkish|Sohbet", t, re.I): return "TR"
    if re.search(r"Saudi|UAE|Dubai", t, re.I): return "AE"
    if re.search(r"Egypt", t, re.I): return "EG"
    if re.search(r"Philippines", t, re.I): return "PH"
    return "International"

def guess_category(name, page_cat):
    n = name
    nl = n.lower()
    if re.search(r"vehicle|gadget|reseller|unlock tool|tiktok.*account|account.*tiktok|store hub|marketplace", nl): return "Buy-Sell"
    if re.search(r"job|work from home", nl): return "Jobs"
    if re.search(r"\bnews\b|updates$", nl) and "gaming" not in nl and "ff" not in nl and "pubg" not in nl: return "News"
    if re.search(r"course|training|students|étudiants", nl): return "Education"
    if re.search(r"crypto|airdrop|mining|usdt|forex", nl): return "Crypto"
    if re.search(r"money", nl): return "Finance"
    if re.search(r"mumbai indians|cricket|ipl", nl): return "Sports"
    if re.search(r"الله|رسول|🕋|islam|quran", nl, re.I): return "Islamic"
    if re.search(r"women empowerment", nl): return "Community"
    if re.search(r"sohbet", nl): return "Friendship"
    if re.search(r"débat|débats|groupe fermé|humaines|soyons focus|solutions des vie", nl): return "Other"
    if re.search(r"movie|film|cinema|netflix", nl): return "Movies"
    if re.search(r"youtube|youtu| YT\b", n): return "Entertainment" if not re.search(r"free fire|ff\b|pubg|bgmi|gaming", nl) else "Gaming"
    if re.search(r"marketing", nl): return "Business"
    if re.search(r"hi-tech|socialmedia|tech other", nl): return "Technology"
    if re.search(r"palestine|فلسطين", nl): return "News"
    if re.search(r"goku|غوكو", nl): return "Entertainment"
    return page_cat

DESCS = {
    "pubg_store": [
        "Pakistani PUBG Mobile account store community where gamers buy and sell accounts, UC and rare in-game items with trusted sellers.",
        "Active PUBG store WhatsApp group for buying and selling game accounts, UC top-ups and exclusive skins with fellow players.",
    ],
    "ff_store": [
        "Free Fire ID marketplace WhatsApp group where Indian players trade premium accounts, rare bundles and elite pass collections.",
        "Busy Free Fire store community for buying and selling game IDs, diamond top-ups and Evo gun skins with active dealers.",
    ],
    "tournament": [
        "Competitive gaming WhatsApp group posting daily scrims, custom room slots, match schedules and tournament prize updates.",
        "Esports tournament community sharing BGMI and PUBG custom rooms, TDM battles and paid competition announcements.",
    ],
    "ff_group": [
        "Free Fire WhatsApp gaming group where players find squads, share gameplay tips and stay updated on events and new seasons.",
        "Lively Free Fire community for ranked push teammates, custom room matches and daily gaming discussions.",
    ],
    "gaming": [
        "Active WhatsApp gaming community where members discuss their favourite games, share tips and connect with fellow gamers.",
        "Gaming WhatsApp group for players to chat about mobile and PC games, exchange tricks and find new teammates.",
    ],
    "movies": [
        "Movie lovers WhatsApp group sharing the latest film updates, trailers and recommendations for cinema fans.",
        "Entertainment WhatsApp community for discussing new movie releases, web series and classic films with fellow fans.",
    ],
    "jobs": ["Job alerts WhatsApp group posting fresh vacancy updates and work opportunities for job seekers."],
    "news": ["WhatsApp news community sharing the latest headlines and daily updates with its members."],
    "education": ["Learning-focused WhatsApp group sharing courses, study material and useful training resources."],
    "crypto": ["Crypto WhatsApp community discussing digital currencies, airdrops and market updates with enthusiasts."],
    "finance": ["Money and earning WhatsApp group where members discuss income ideas and financial updates."],
    "buysell": ["Buy and sell WhatsApp marketplace group where members trade products and deals with each other."],
    "sports": ["Sports fans WhatsApp group sharing match updates, scores and lively cricket discussions."],
    "islamic": ["Islamic WhatsApp community sharing religious reminders, quotes and faith-based discussions."],
    "community": ["Friendly WhatsApp community group for discussions, support and connecting with like-minded members."],
    "other": ["Active WhatsApp community group for discussions and connecting with members who share common interests."],
    "entertainment": ["Entertainment WhatsApp group for fun content, creator updates and lively fan discussions."],
    "technology": ["Tech WhatsApp group sharing digital tips, tools and the latest technology discussions."],
    "business": ["Business WhatsApp community for marketing ideas, networking and growth discussions."],
    "friendship": ["Friendly WhatsApp chat group for making new friends and enjoying everyday conversations."],
}

def pick_desc(name, cat):
    nl = name.lower()
    n = name
    pool = None
    if re.search(r"pubg|bgmi", nl) and re.search(r"store|shop|seller|sale|buy|uc\b|account", nl): pool = DESCS["pubg_store"]
    elif re.search(r"free fire|\bff\b|ƒƒ", nl) and re.search(r"store|shop|seller|sale|buy|exchange|dealer|id\b", nl): pool = DESCS["ff_store"]
    elif re.search(r"tourn|scrim|esport|tdm|custom room", nl): pool = DESCS["tournament"]
    elif re.search(r"free fire|\bff\b", nl): pool = DESCS["ff_group"]
    elif cat == "Movies": pool = DESCS["movies"]
    elif cat == "Jobs": pool = DESCS["jobs"]
    elif cat == "News": pool = DESCS["news"]
    elif cat == "Education": pool = DESCS["education"]
    elif cat == "Crypto": pool = DESCS["crypto"]
    elif cat == "Finance": pool = DESCS["finance"]
    elif cat == "Buy-Sell": pool = DESCS["buysell"]
    elif cat == "Sports": pool = DESCS["sports"]
    elif cat == "Islamic": pool = DESCS["islamic"]
    elif cat == "Community": pool = DESCS["community"]
    elif cat == "Entertainment": pool = DESCS["entertainment"]
    elif cat == "Technology": pool = DESCS["technology"]
    elif cat == "Business": pool = DESCS["business"]
    elif cat == "Friendship": pool = DESCS["friendship"]
    elif cat == "Other": pool = DESCS["other"]
    else: pool = DESCS["gaming"]
    h = abs(hash(n)) % len(pool)
    return pool[h]

items = []
porn_drops = 0
fraud_drops = 0
personal_drops = 0
urlname_drops = 0
seen_codes = set()

for code, r in live.items():
    title = clean_title(r["title"] or "")
    cand = bycode[code]
    raw = clean_raw(cand["raw_name"])
    # Content-rule checks run on the group's OWN title only (og:title).
    # Neighbor raw_name context is not the group's content — never used for drops.
    if not title or re.match(r"^https?://", title) or "<" in title:
        # group is named with a URL/HTML — not a real group name; drop
        urlname_drops += 1
        continue
    if porn_re.search(title):
        porn_drops += 1
        continue
    if fraud_re.search(title):
        fraud_drops += 1
        continue
    if personal_re.search(title):
        personal_drops += 1
        continue
    if code in seen_codes:
        continue
    seen_codes.add(code)
    cat = guess_category(title, cand["category"])
    country = guess_country(title)
    items.append({
        "name": title,
        "category": cat,
        "country": country,
        "description": pick_desc(title, cat),
        "invite": "https://chat.whatsapp.com/" + code,
        "image": "",
    })

json.dump(items, open(os.path.join(WD, "team27-listicle-gaming.json"), "w"), ensure_ascii=False, indent=1)

# pending: transport failures as schema items + note
pend = []
for code, r in transport.items():
    cand = bycode[code]
    title = clean_title(r["title"] or "") or clean_raw(cand["raw_name"])
    pend.append({
        "name": title, "category": cand["category"], "country": "International",
        "description": "Pending verification.", "invite": "https://chat.whatsapp.com/" + code,
        "image": "", "note": "transport failure",
    })
json.dump(pend, open(os.path.join(WD, "team27-unverified-pending.json"), "w"), ensure_ascii=False, indent=1)

leads = [
    {"domain": "blog.waziper.com", "url": "http://blog.waziper.com/active-free-fire-whatsapp-group-links",
     "why": "Fresh Free Fire listicle discovered via search; page timed out on direct fetch during this wave — needs a browser-leg or retry next wave."},
    {"domain": "whtsgrouplink.com", "url": "https://whtsgrouplink.com/movies-whatsapp-group-links/",
     "why": "Movies listicle scraped (only 1 direct-format code; rest use /invite/ or JS-gated buttons) — rest of the directory unexamined, banked as lead."},
    {"domain": "asiamediajournal.com", "url": "https://www.asiamediajournal.com/gaming-whatsapp-group-links/",
     "why": "Gaming listicle; site rewrites join buttons to chat.whatsapp.com/invite/<code> (channel format per brief) — 359 invite-format codes skipped, excluded per rule 2."},
]
json.dump(leads, open(os.path.join(WD, "team27-leads.json"), "w"), ensure_ascii=False, indent=1)

print("verified:", len(items), "pending:", len(pend), "leads:", len(leads))
print("drops: porn", porn_drops, "fraud", fraud_drops, "personal", personal_drops, "urlname", urlname_drops)
from collections import Counter
print(Counter(i["category"] for i in items))
print(Counter(i["country"] for i in items))
