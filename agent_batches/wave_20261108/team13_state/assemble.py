"""Team 13 assembler: live records -> final schema-exact output files.
- Filters (rule 3): hard porn/xxx, escort/call-girl, scam/money-mule, counterfeit
  currency, adult emoji set (exact: 🥵🍆🍑🔞💦👅👄💋) in name OR og_title OR
  description; minor-targeted dating. Girls/friendship KEPT.
- Names: use og_title as the group name (live truth from WhatsApp); fall back to
  listing name. Strip nothing else; drop records with empty/invalid names.
- Categories: canonical 23 only. appgrouplink: slug keyword map. groupsinvite:
  category_slug map.
- Country: appgrouplink slug map; groupsinvite country_slug map; else International.
- Descriptions: use listing description if decent, else og_desc if decent, else
  generated "Join <name>, a WhatsApp group listed under <category>. ..."
- Dedupes by code vs union + within batch. Writes the three output files.
"""
import json, os, re, html as ihtml

WORK = os.path.dirname(os.path.abspath(__file__))
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108"
OUTDIR = WAVE

CANON = ["Education", "Jobs", "Entertainment", "Islamic", "News", "Sports",
         "Technology", "Health", "Business", "Gaming", "Friendship",
         "Community & Social", "Online Earning", "Crypto", "Cooking", "Poetry",
         "Travel", "Scholarship", "Freelance", "Real Estate", "Buy & Sell",
         "Finance", "Funny"]
ADULT_EMOJI = set("🥵🍆🍑🔞💦👅👄💋")

PORN_RE = re.compile(r'porn|pornhub|xxx|nude|sex\s*video|sex\s*chat|escort|call\s*girl|call\s*boy|bokep|sexy\s*(video|girl|bhabhi)|adult\s*video|desi\s*sex|hot\s*sex', re.I)
SCAM_RE = re.compile(r'bitfinexinvests|paypal.*(loader|receiver)|receiver.*loader|money\s*doubler|double\s*(your|the)\s*money|\bhyip\b|counterfeit\s*(currency|money|notes?)|fake\s*(currency|money|notes?)|satta|matka|1xbet|betway|fix(ed)?\s*(match|game)', re.I)
MINOR_RE = re.compile(r'\b(teen|teens|kids|school\s*(girl|boy)s?|under\s*1[0-7]|1[3-7]\s*(years|yrs|yo)|minor[s]?)\b.*(dating|friendship|love|romance)|dating.*\b(teen|school|minor)', re.I)
MINOR_EXC = re.compile(r'stray\s*kids', re.I)

# --- appgrouplink slug -> (category, country) ---
AG_CAT = [
    ("scholarship", "Scholarship"), ("government-jobs", "Jobs"), ("jobs", "Jobs"),
    ("cricket", "Sports"), ("football", "Sports"), ("sports", "Sports"), ("fan-club", "Sports"),
    ("gym", "Health"), ("fitness", "Health"), ("yoga", "Health"), ("meditation", "Health"),
    ("weight-loss", "Health"), ("medical", "Health"),
    ("gaming", "Gaming"), ("coin-master", "Gaming"),
    ("education", "Education"), ("study", "Education"), ("teachers", "Education"),
    ("college", "Education"), ("upsc", "Education"), ("iit", "Education"), ("jee", "Education"),
    ("gk", "Education"), ("ielts", "Education"), ("online-classes", "Education"),
    ("english-learning", "Education"), ("duolingo", "Education"),
    ("arabic", "Education"), ("iti", "Education"), ("hindi", "Education"),
    ("binance", "Crypto"), ("crypto", "Crypto"),
    ("forex-trading", "Finance"), ("trading", "Finance"), ("share-market", "Finance"),
    ("business", "Business"), ("ecommerce", "Business"), ("dropshipping", "Business"),
    ("affiliate-marketing", "Business"), ("digital-marketing", "Business"), ("seo", "Business"),
    ("lead-generation", "Business"), ("sales-and-marketing", "Business"), ("startup", "Business"),
    ("entrepreneur", "Business"), ("freelancer", "Freelance"), ("freelance", "Freelance"),
    ("reseller", "Business"), ("wholesale", "Business"), ("import-export", "Business"),
    ("real-estate", "Real Estate"), ("event-management", "Business"),
    ("diamond-buyers", "Buy & Sell"), ("amazon-deals", "Buy & Sell"), ("shopping", "Buy & Sell"),
    ("news", "News"), ("newspaper", "News"),
    ("islamic", "Islamic"),
    ("movie", "Entertainment"), ("tv-shows", "Entertainment"), ("k-drama", "Entertainment"),
    ("bollywood", "Entertainment"), ("drama", "Entertainment"), ("anime", "Entertainment"),
    ("celebrity", "Entertainment"), ("audition", "Entertainment"), ("acting", "Entertainment"),
    ("modeling", "Entertainment"), ("photography", "Entertainment"), ("photoshop", "Entertainment"),
    ("photo-editing", "Entertainment"), ("tvk-family", "Entertainment"), ("creative", "Entertainment"),
    ("innovative", "Entertainment"), ("art", "Entertainment"), ("music", "Entertainment"),
    ("k-pop", "Entertainment"), ("bts-army", "Entertainment"), ("seventeen-kpop", "Entertainment"),
    ("exo-kpop", "Entertainment"), ("blackpink", "Entertainment"), ("dj", "Entertainment"),
    ("edm", "Entertainment"),
    ("girls", "Friendship"), ("dating", "Friendship"), ("friendship", "Friendship"),
    ("boys", "Friendship"), ("romantic", "Friendship"), ("love", "Friendship"),
    ("funny", "Funny"), ("joker", "Funny"), ("status", "Funny"), ("wallpapers", "Funny"),
    ("travel", "Travel"), ("driver", "Travel"),
    ("cooking", "Cooking"), ("food", "Cooking"),
    ("coding", "Technology"), ("web-developer", "Technology"), ("technology", "Technology"),
    ("urdu-poetry", "Poetry"), ("poetry", "Poetry"),
    ("lifestyle", "Community & Social"), ("motivational", "Community & Social"),
    ("free", "Community & Social"), ("makeup-artist", "Community & Social"),
    ("beauty-parlour", "Community & Social"), ("designers", "Community & Social"),
    ("graphic-design", "Community & Social"), ("agriculture", "Community & Social"),
    ("christian", "Community & Social"),
]
AG_COUNTRY = {
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
    "south-africa": "ZA", "russian": "RU",
}
COUNTRY_WORD = {"PK": "Pakistan", "IN": "India", "BD": "Bangladesh", "AE": "the UAE",
    "QA": "Qatar", "KW": "Kuwait", "SA": "Saudi Arabia", "OM": "Oman", "BS": "the Bahamas",
    "GB": "the UK", "US": "the USA", "CA": "Canada", "FR": "France", "BR": "Brazil",
    "MX": "Mexico", "UG": "Uganda", "TZ": "Tanzania", "RO": "Romania", "PL": "Poland",
    "KE": "Kenya", "ZW": "Zimbabwe", "LK": "Sri Lanka", "AF": "Afghanistan", "ES": "Spain",
    "IT": "Italy", "DE": "Germany", "CN": "China", "JP": "Japan", "TH": "Thailand",
    "PH": "the Philippines", "NG": "Nigeria", "HK": "Hong Kong", "ZA": "South Africa",
    "RU": "Russia", "International": "members worldwide"}

# --- groupsinvite category_slug -> canonical ---
GI_CAT = {
    "education-study-learning": "Education",
    "career-jobs-freelancing": "Jobs",
    "business-startup-earn-money": "Online Earning",
    "marketing-advertising-affiliate": "Business",
    "crypto-blockchain-web3": "Crypto",
    "finance-stocks-investing": "Finance",
    "news-politics-information": "News",
    "entertainment-comedy-fun": "Entertainment",
    "movies-tv-celebrities": "Entertainment",
    "music-songs-bands": "Entertainment",
    "photography-video-editing": "Entertainment",
    "books-ebooks-literature": "Entertainment",
    "sports-games-fantasy": "Sports",
    "community-friendship-social": "Friendship",
    "dating-matrimony-relationships": "Friendship",
    "local-city-country": "Community & Social",
    "beauty-fashion-lifestyle": "Community & Social",
    "religion-devotional-faith": "Islamic",
    "astrology-horoscope-spirituality": "Community & Social",
    "animals-pets-wildlife": "Community & Social",
    "art-drawing-crafts": "Entertainment",
    "hobbies-diy-home-projects": "Community & Social",
    "health-diet-nutrition": "Health",
    "fitness-gym-bodybuilding": "Health",
    "science-engineering-technology": "Technology",
    "ai-machine-learning-data-science": "Technology",
    "programming-coding-software": "Technology",
    "travel-adventure-road-trips": "Travel",
    "real-estate-property-housing": "Real Estate",
    "buy-sell-marketplace": "Buy & Sell",
    "shopping-deals-coupons": "Buy & Sell",
    "automotive-cars-bikes": "Community & Social",
    "cooking-food-recipes": "Cooking",
    "gardening-farming-agriculture": "Community & Social",
}
GI_COUNTRY = {
    "pakistan": "PK", "india": "IN", "bangladesh": "BD", "nigeria": "NG", "ghana": "GH",
    "kenya": "KE", "usa": "US", "united-states": "US", "uk": "GB", "united-kingdom": "GB",
    "canada": "CA", "uae": "AE", "dubai": "AE", "saudi-arabia": "SA", "qatar": "QA",
    "kuwait": "KW", "oman": "OM", "turkey": "TR", "turkiye": "TR", "indonesia": "ID",
    "malaysia": "MY", "philippines": "PH", "sri-lanka": "LK", "nepal": "NP",
    "south-africa": "ZA", "egypt": "EG", "morocco": "MA", "brazil": "BR", "mexico": "MX",
    "australia": "AU", "germany": "DE", "france": "FR", "italy": "IT", "spain": "ES",
    "netherlands": "NL", "russia": "RU", "ukraine": "UA", "china": "CN", "japan": "JP",
    "south-korea": "KR", "thailand": "TH", "vietnam": "VN", "singapore": "SG",
    "new-zealand": "NZ", "ireland": "IE", "portugal": "PT", "poland": "PL", "romania": "RO",
    "tanzania": "TZ", "uganda": "UG", "zimbabwe": "ZW", "ethiopia": "ET", "iran": "IR",
    "iraq": "IQ", "afghanistan": "AF", "myanmar": "MM", "cambodia": "KH", "laos": "LA",
}

DESC2 = {
    "Sports": "Members follow live matches, share scores, team news and sports talk with fellow fans every day.",
    "Gaming": "Gamers connect here to discuss strategies, share game updates and team up for online play.",
    "Jobs": "Members receive job alerts, vacancy posts and career updates to help with the job search.",
    "Education": "Students and learners share study notes, exam tips and learning resources with each other.",
    "Entertainment": "Members share entertaining posts, videos and updates on trending topics in this fun community.",
    "Friendship": "Members chat, make new friends and share everyday moments in a friendly community.",
    "Business": "Members discuss business ideas, deals and opportunities with like-minded people.",
    "Crypto": "Members discuss cryptocurrency news, market trends and trading ideas.",
    "Finance": "Members share finance news, market updates and money tips with each other.",
    "News": "Members share the latest news and updates from around the world.",
    "Technology": "Members discuss technology news, gadgets and software with fellow tech fans.",
    "Health": "Members share health tips, fitness routines and wellness advice with each other.",
    "Islamic": "Members share Islamic reminders, learning and community updates.",
    "Cooking": "Members share recipes, cooking tips and food ideas with each other.",
    "Poetry": "Members share poetry and verses with fellow poetry lovers.",
    "Travel": "Members share travel stories, tips and destination ideas.",
    "Scholarship": "Members share scholarship opportunities, deadlines and application tips.",
    "Freelance": "Freelancers share work opportunities, tips and client leads.",
    "Real Estate": "Members share property listings, housing news and real estate updates.",
    "Buy & Sell": "Members buy and sell items, share deals and connect with buyers and sellers.",
    "Community & Social": "Members chat and share updates in a friendly community group.",
    "Online Earning": "Members share ways to earn money online, tips and opportunities.",
    "Funny": "Members share funny posts, jokes and memes to brighten the day.",
}

def clean_name(s):
    s = ihtml.unescape(str(s or "")).strip()
    s = re.sub(r'\s+', ' ', s)
    return s

def has_adult_emoji(s):
    return any(ch in ADULT_EMOJI for ch in (s or ""))

NEG_RE = re.compile(
    r"(?i)\b(no|not|never|don't|dont|do not|prohibited|forbidden|avoid|against|zero tolerance\w*)\s+"
    r"(adult\s*videos?|porn\w*|xxx|nude\w*|sex\w*|escort\w*|betting|gambling|satta|matka|spam|links?|"
    r"adult\s*discussion|adult\s*content)\b"
    r"|\b(porn\w*|xxx|adult\s*videos?|sex\w*|betting)\s+(not allowed|prohibited|forbidden|not tolerate\w*)\b",
    re.I)

def blocked(name, title, desc):
    blob = " ".join([name or "", title or "", desc or ""])
    if has_adult_emoji(blob):
        return "adult-emoji"
    clean = NEG_RE.sub(" ", blob)
    if PORN_RE.search(clean):
        return "porn"
    if SCAM_RE.search(clean):
        return "scam"
    if MINOR_RE.search(clean) and not MINOR_EXC.search(clean):
        return "minor-dating"
    return None

def ag_cat_country(slug):
    cat = "Community & Social"
    for key, c in AG_CAT:
        if key in slug:
            cat = c
            break
    country = "International"
    for key, cc in AG_COUNTRY.items():
        if key in slug:
            country = cc
            break
    return cat, country

def gi_cat_country(rec):
    cat = GI_CAT.get(rec.get("category_slug", ""), "Community & Social")
    country = GI_COUNTRY.get(rec.get("country_slug", ""), "International")
    return cat, country

def describe(name, cat, country, listing_desc):
    d = clean_name(listing_desc)
    # listing descriptions from GI often contain the invite link / junk; only reuse if clean
    if d and len(d) > 20 and "chat.whatsapp.com" not in d and "http" not in d:
        if len(d) > 300:
            d = d[:297].rstrip() + "..."
        return d
    where = COUNTRY_WORD.get(country, "members worldwide")
    return "Join %s, a WhatsApp group listed under %s. %s" % (name, cat, DESC2.get(cat, "Members chat and share updates in this friendly community."))

def process(live_records):
    union = set(json.load(open(os.path.join(WAVE, "dedupe_union.json"))))
    out, seen, stats = [], set(), {"kept": 0, "dup_union": 0, "dup_batch": 0, "blocked": {}}
    for rec in live_records:
        code = rec["code"]
        if code in union:
            stats["dup_union"] += 1
            continue
        if code in seen:
            stats["dup_batch"] += 1
            continue
        name = clean_name(rec.get("og_title") or rec.get("name"))
        if len(name) < 3:
            # og:title too short to be a real group name (rendering artifact) — use listing name
            name = clean_name(rec.get("name"))
        title = clean_name(rec.get("og_title"))
        desc_src = rec.get("description", "") or ""
        if not name or len(name) < 2:
            stats["blocked"].setdefault("bad-name", 0)
            stats["blocked"]["bad-name"] += 1
            continue
        why = blocked(name, title, desc_src)
        if why:
            stats["blocked"][why] = stats["blocked"].get(why, 0) + 1
            continue
        if rec.get("source") == "groupsinvite":
            cat, country = gi_cat_country(rec)
        else:
            cat, country = ag_cat_country(rec.get("slug", ""))
        if cat not in CANON:
            cat = "Community & Social"
        seen.add(code)
        out.append({
            "name": name,
            "category": cat,
            "country": country,
            "description": describe(name, cat, country, desc_src),
            "invite": "https://chat.whatsapp.com/" + code,
            "image": "",
        })
        stats["kept"] += 1
    return out, stats

def write_json(path, data):
    for attempt in range(5):
        try:
            with open(path, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            return True
        except OSError:
            time.sleep(2)
    raise OSError("write failed after retries: " + path)

if __name__ == "__main__":
    import time
    live = []
    for p in ("live_ag.json", "live_gi.json"):
        fp = os.path.join(WORK, p)
        if os.path.exists(fp):
            live.extend(json.load(open(fp)))
    print("live records to assemble:", len(live))
    out, stats = process(live)
    print("stats:", stats)
    from collections import Counter
    print("by source+category:", Counter((r["category"]) for r in out).most_common())
    write_json(os.path.join(WAVE, "team13-appgrouplink-groupsinvite.json"), out)
    # pending: transport-pending only, schema + reason
    pend = []
    for p in ("pending_ag.json", "pending_gi.json"):
        fp = os.path.join(WORK, p)
        if os.path.exists(fp):
            pend.extend(json.load(open(fp)))
    pend_out = []
    seen_p = set()
    union = set(json.load(open(os.path.join(WAVE, "dedupe_union.json"))))
    for rec in pend:
        code = rec["code"]
        if code in union or code in seen_p:
            continue
        seen_p.add(code)
        cat, country = (gi_cat_country(rec) if rec.get("source") == "groupsinvite"
                        else ag_cat_country(rec.get("slug", "")))
        pend_out.append({
            "name": clean_name(rec.get("name")),
            "category": cat,
            "country": country,
            "description": describe(clean_name(rec.get("name")), cat, country, ""),
            "invite": "https://chat.whatsapp.com/" + code,
            "image": "",
            "reason": "transport",
        })
    write_json(os.path.join(WAVE, "team13-appgrouplink-groupsinvite-pending.json"), pend_out)
    print("pending written:", len(pend_out))
    # leads: listing pages NOT harvested per-category this run (GI was walked via
    # scope=all AJAX, first 1000 only; per-category pages let a future run page
    # each category fully) + appgrouplink sitemap for new-page detection.
    leads = [
        {"url": "https://appgrouplink.com/post-sitemap.xml", "source": "appgrouplink"},
        {"url": "https://groupsinvite.link/group/find/", "source": "groupsinvite"},
    ]
    for cat in [
        "ai-machine-learning-data-science", "astrology-horoscope-spirituality",
        "beauty-fashion-lifestyle", "business-startup-earn-money",
        "buy-sell-marketplace", "career-jobs-freelancing",
        "community-friendship-social", "crypto-blockchain-web3",
        "dating-matrimony-relationships", "education-study-learning",
        "entertainment-comedy-fun", "finance-stocks-investing",
        "fitness-gym-bodybuilding", "local-city-country",
        "marketing-advertising-affiliate", "music-songs-bands",
        "news-politics-information", "photography-video-editing",
        "programming-coding-software", "religion-devotional-faith",
        "science-engineering-technology", "shopping-deals-coupons",
        "sports-games-fantasy",
    ]:
        leads.append({"url": "https://groupsinvite.link/group/category/%s/" % cat,
                      "source": "groupsinvite"})
    write_json(os.path.join(WAVE, "team13-appgrouplink-groupsinvite-leads.json"), leads)
    print("verified written:", len(out), "leads:", len(leads))
