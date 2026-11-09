#!/usr/bin/env python3
"""Team 11 assembler: live records -> final schema-exact output files.
Screening per task: DROP hard porn/xxx, sex/hookup, escort, cam-girl, 'sexy';
DROP B-Love / Forsage / SHEYI and similar crypto-airdrop / free-money scams.
KEEP betting groups and girls/friendship groups. Prohibition sentences
(rules saying such content is not allowed) are stripped BEFORE screening.
Categories: task's 16 only. Country: 2-letter ISO, default IN.
Writes team11-candidates.json, team11-pending.json, team11-leads.json,
team11-summary.json into the wave dir."""
import json, os, re, html as ihtml
from collections import Counter

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
WORK = WAVE

ALLOWED_CATS = ["Gaming", "Education", "Online Earning", "Community & Social",
                "Business", "Friendship", "Finance", "Buy Sell", "Islamic",
                "Entertainment", "Jobs", "Technology", "Funny", "Sports",
                "Health", "News"]

GI_CAT = {
    "education-study-learning": "Education",
    "career-jobs-freelancing": "Jobs",
    "business-startup-earn-money": "Online Earning",
    "marketing-advertising-affiliate": "Business",
    "crypto-blockchain-web3": "Finance",
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
    "travel-adventure-road-trips": "Community & Social",
    "real-estate-property-housing": "Business",
    "buy-sell-marketplace": "Buy Sell",
    "shopping-deals-coupons": "Buy Sell",
    "automotive-cars-bikes": "Community & Social",
    "cooking-food-recipes": "Community & Social",
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
    "argentina": "AR", "colombia": "CO", "peru": "PE", "chile": "CL",
}

ADULT_EMOJI = set("🥵🍆🍑🔞💦👅👄💋")
PORN_RE = re.compile(r'porn|pornhub|xxx|bokep|\bnude\b|nudes|sex\s*(video|chat|group|call)|'
                     r'\bsex\b.*\b(group|video|chat)\b|escort|call\s*girl|call\s*boy|'
                     r'cam\s*girl|camgirl|hookup|hook\s*up|sexy|desi\s*sex|hot\s*sex|'
                     r'adult\s*(video|content|chat|group)|18\+\s*(only|group|video|sex)', re.I)
SCAM_RE = re.compile(r'\bforsage\b|\bb-?love\b|\bsheyi\b|\bairdrop\b|free\s*(money|usdt|crypto|bitcoin)|'
                     r'money\s*doubler|double\s*(your|the)\s*money|get\s*rich\s*quick|'
                     r'earn\s*free\s*(money|usdt|crypto)|free\s*earning\s*app.*invest', re.I)
PHONE_RE = re.compile(r'\+?\d[\d\s\-]{9,}\d')
# sentences that PROHIBIT bad content (rules) - strip before screening
NEG_SENT_RE = re.compile(
    r'[^.!?\n]*\b(no|not|never|don\'t|dont|do not|prohibited|forbidden|avoid|against|'
    r'zero tolerance|not allowed|strictly prohibited)\b[^.!?\n]*'
    r'\b(adult|porn\w*|xxx|nude\w*|sex\w*|escort\w*|betting|gambling|satta|matka|spam|'
    r'links?|inappropriate|bad content|wrong)\b[^.!?\n]*[.!?\n]?', re.I)

DESC2 = {
    "Sports": "Members follow live matches, share scores, team news and sports talk with fellow fans every day.",
    "Gaming": "Gamers connect here to discuss strategies, share game updates and team up for online play.",
    "Jobs": "Members receive job alerts, vacancy posts and career updates to help with the job search.",
    "Education": "Students and learners share study notes, exam tips and learning resources with each other.",
    "Entertainment": "Members share entertaining posts, videos and updates on trending topics in this fun community.",
    "Friendship": "Members chat, make new friends and share everyday moments in a friendly community.",
    "Business": "Members discuss business ideas, deals and opportunities with like-minded people.",
    "Finance": "Members share finance news, market updates and money tips with each other.",
    "News": "Members share the latest news and updates from around the world.",
    "Technology": "Members discuss technology news, gadgets and software with fellow tech fans.",
    "Health": "Members share health tips, fitness routines and wellness advice with each other.",
    "Islamic": "Members share Islamic reminders, learning and community updates.",
    "Buy Sell": "Members buy and sell items, share deals and connect with buyers and sellers.",
    "Community & Social": "Members chat and share updates in a friendly community group.",
    "Online Earning": "Members share ways to earn money online, tips and opportunities.",
    "Funny": "Members share funny posts, jokes and memes to brighten the day.",
}

def clean_name(s):
    s = ihtml.unescape(str(s or "")).strip()
    s = re.sub(r'\s+', ' ', s)
    return s

def strip_prohibitions(text):
    return NEG_SENT_RE.sub(" ", text or "")

def blocked(name, title, desc):
    blob = " ".join([name or "", title or "", desc or ""])
    if any(ch in ADULT_EMOJI for ch in blob):
        return "adult-emoji"
    clean = strip_prohibitions(blob)
    if PORN_RE.search(clean):
        return "porn-sex-escort"
    if SCAM_RE.search(clean):
        return "scam-airdrop"
    return None

def gi_cat_country(rec):
    cat = GI_CAT.get(rec.get("category_slug", ""), "Community & Social")
    country = GI_COUNTRY.get((rec.get("country_slug") or "").lower(), "IN")
    return cat, country

def describe(name, cat, country, listing_desc):
    d = clean_name(listing_desc)
    d = PHONE_RE.sub("", d)
    d = re.sub(r'\s+', ' ', d).strip()
    if d and len(d) > 20 and "chat.whatsapp.com" not in d and "http" not in d and "groupsinvite" not in d.lower():
        if len(d) > 300:
            d = d[:297].rstrip() + "..."
        # ensure 1-2 sentences: truncate at second sentence end
        parts = re.split(r'(?<=[.!?])\s+', d)
        if len(parts) > 2:
            d = " ".join(parts[:2])
        return d
    return "Join %s, a WhatsApp group listed under %s. %s" % (name, cat, DESC2.get(cat, "Members chat and share updates in this friendly community."))

def process(live_records):
    existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))
    out, seen, stats = [], set(), {"kept": 0, "dup_existing": 0, "dup_batch": 0, "blocked": {}}
    for rec in live_records:
        code = rec["code"]
        if code in existing:
            stats["dup_existing"] += 1
            continue
        if code in seen:
            stats["dup_batch"] += 1
            continue
        name = clean_name(rec.get("og_title") or rec.get("name"))
        if len(name) < 3:
            name = clean_name(rec.get("name"))
        title = clean_name(rec.get("og_title"))
        desc_src = rec.get("description", "") or ""
        if not name or len(name) < 2:
            stats["blocked"].setdefault("bad-name", 0)
            stats["blocked"]["bad-name"] += 1
            continue
        if PHONE_RE.search(name) and len(re.sub(r'\D', '', name)) >= 10:
            stats["blocked"].setdefault("phone-in-name", 0)
            stats["blocked"]["phone-in-name"] += 1
            continue
        why = blocked(name, title, desc_src)
        if why:
            stats["blocked"][why] = stats["blocked"].get(why, 0) + 1
            continue
        cat, country = gi_cat_country(rec)
        if cat not in ALLOWED_CATS:
            cat = "Community & Social"
        seen.add(code)
        out.append({
            "name": name,
            "category": cat,
            "country": country,
            "description": describe(name, cat, country, desc_src),
            "invite": "https://chat.whatsapp.com/" + code,
        })
        stats["kept"] += 1
    return out, stats

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    live_path = os.path.join(WORK, "team11_live.json")
    pend_path = os.path.join(WORK, "team11_pending_raw.json")
    live = json.load(open(live_path)) if os.path.exists(live_path) else []
    print("live records to assemble:", len(live))
    out, stats = process(live)
    print("stats:", stats)
    print("by category:", Counter(r["category"] for r in out).most_common())
    print("by country:", Counter(r["country"] for r in out).most_common(10))
    write_json(os.path.join(WAVE, "team11-candidates.json"), out)

    # pending: transport-pending only, same schema + reason
    pend_raw = json.load(open(pend_path)) if os.path.exists(pend_path) else []
    existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))
    pend_out, seen_p = [], set()
    for rec in pend_raw:
        code = rec["code"]
        if code in existing or code in seen_p:
            continue
        seen_p.add(code)
        cat, country = gi_cat_country(rec)
        pend_out.append({
            "name": clean_name(rec.get("name")),
            "category": cat,
            "country": country,
            "description": describe(clean_name(rec.get("name")), cat, country, ""),
            "invite": "https://chat.whatsapp.com/" + code,
            "reason": "transport",
        })
    write_json(os.path.join(WAVE, "team11-pending.json"), pend_out)
    print("pending written:", len(pend_out))

    # leads: category pages + find page (mined separately; see team11_cat_slugs.json)
    leads = [{"url": "https://groupsinvite.link/group/find/", "source": "groupsinvite", "note": "browse-all page"}]
    for cat in sorted(GI_CAT.keys()):
        leads.append({"url": "https://groupsinvite.link/group/category/%s/" % cat,
                      "source": "groupsinvite", "note": "category page"})
    write_json(os.path.join(WAVE, "team11-leads.json"), leads)
    print("leads written:", len(leads))
    print("verified candidates:", len(out))
