#!/usr/bin/env python3
"""TEAM 13: build pending items from harvested candidates.
og:title verification impossible this wave (transport failure) -> everything
goes to team13-unverified-pending.json with note. Verified file = [].
"""
import json, os, re, random

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"

CAT_MAP = {
    "education": "Education", "business": "Business", "entertainment": "Entertainment",
    "gaming": "Gaming", "money": "Finance", "finance": "Finance", "earning": "Finance",
    "online-shopping": "Buy-Sell", "health": "Health", "technology": "Technology",
    "crypto": "Crypto", "cryptocurrency": "Crypto", "travel": "Travel",
    "music": "Music", "movies": "Movies", "film": "Movies", "food": "Food",
    "pets": "Pets", "funny": "Funny", "comedy": "Funny", "islamic": "Islamic",
    "news": "News", "sports": "Sports", "sports-and-fitness": "Sports",
    "jobs": "Jobs", "career": "Jobs", "friendship": "Friendship", "friends": "Friendship",
    "family": "Friendship", "fashion": "Other", "clothing": "Buy-Sell",
    "art": "Entertainment", "design": "Technology", "photography": "Entertainment",
    "spiritual": "Islamic", "devotional": "Other", "youtube": "Entertainment",
    "fan-club": "Entertainment", "cricket": "Sports", "science": "Education",
    "school": "Education", "animation": "Entertainment", "trading": "Finance",
    "forex": "Finance", "marketing": "Business", "advertising": "Business",
    "community": "Community", "social": "Community", "chat": "Friendship",
    "love": "Friendship", "girls": "Girls", "dating": "Friendship",
    "autos-and-vehicles": "Other", "vehicle": "Other", "auto": "Other",
}
TAG_FALLBACK = {
    "sri lanka": "Regional", "urdu": "Community", "bangladesh": "Regional",
    "kerala": "Regional", "bangla": "Community", "telugu": "Community",
    "kannada": "Community", "arabic": "Community", "japanese": "Education",
    "japan": "Regional", "morocco": "Regional", "egypt": "Regional",
    "lahore": "Regional", "punjabi": "Community", "afrikaans": "Community",
    "marathi": "Community", "cricket": "Sports", "islamic": "Islamic",
    "school": "Education", "career": "Jobs", "fashion": "Other",
    "art": "Entertainment", "softwareengineer": "Technology",
    "photography": "Entertainment", "design": "Technology", "trading": "Finance",
    "technology": "Technology", "science": "Education", "spiritual": "Islamic",
    "amanah": "Islamic", "devotional": "Other", "web series": "Entertainment",
    "work from home": "Jobs", "youtube": "Entertainment",
    "friendship": "Friendship", "clothing": "Buy-Sell",
}
COUNTRY_NAME = {"PK": "Pakistan", "IN": "India", "BD": "Bangladesh",
                "LK": "Sri Lanka", "JP": "Japan", "MA": "Morocco",
                "EG": "Egypt", "ZA": "South Africa", "NG": "Nigeria",
                "ID": "Indonesia", "MY": "Malaysia", "AE": "UAE",
                "SA": "Saudi Arabia", "GB": "UK", "US": "USA",
                "AU": "Australia", "CA": "Canada", "DE": "Germany",
                "FR": "France", "BR": "Brazil", "MX": "Mexico",
                "TR": "Turkey", "PH": "Philippines", "TH": "Thailand",
                "VN": "Vietnam", "SG": "Singapore", "NZ": "New Zealand",
                "QA": "Qatar", "KW": "Kuwait", "OM": "Oman",
                "NP": "Nepal", "AF": "Afghanistan", "MM": "Myanmar",
                "KH": "Cambodia", "LA": "Laos", "TW": "Taiwan",
                "KR": "South Korea", "CN": "China", "HK": "Hong Kong",
                "CM": "Cameroon", "UG": "Uganda", "GH": "Ghana",
                "RW": "Rwanda", "UA": "Ukraine", "KE": "Kenya",
                "TZ": "Tanzania", "ET": "Ethiopia", "SD": "Sudan"}

DESC_T = {
    "Education": [
        "An education WhatsApp group in {cn} for {topic}: study notes, exam tips and learning resources shared daily by students and teachers.",
        "Join this study WhatsApp group in {cn} focused on {topic} — homework help, exam preparation and useful learning material for members.",
    ],
    "Islamic": [
        "An Islamic WhatsApp group in {cn} sharing {topic}: daily duas, reminders and faith-based discussion with fellow members.",
        "Connect with Muslims in this Islamic WhatsApp group in {cn} for {topic} — Quranic reminders, duas and peaceful community chat.",
    ],
    "Business": [
        "A business WhatsApp group in {cn} for {topic}: networking, deals and growth ideas shared among entrepreneurs and traders.",
        "Join business minds in this WhatsApp group in {cn} covering {topic} — opportunities, tips and marketplace updates.",
    ],
    "Finance": [
        "A finance WhatsApp group in {cn} about {topic}: market talk, earning ideas and money tips shared by active members.",
        "Discuss {topic} with this finance WhatsApp community in {cn} — investment ideas, trading talk and earning updates.",
    ],
    "Jobs": [
        "A jobs WhatsApp group in {cn} for {topic}: fresh vacancies, career advice and work opportunities posted regularly.",
        "Find work leads in this WhatsApp group in {cn} focused on {topic} — job alerts, career tips and hiring updates.",
    ],
    "Sports": [
        "A sports WhatsApp group in {cn} for {topic} fans: match updates, scores and lively fan discussion every day.",
        "Join fellow fans in this WhatsApp group in {cn} covering {topic} — live match talk, news and predictions.",
    ],
    "Entertainment": [
        "A fun entertainment WhatsApp group in {cn} about {topic}: videos, updates and daily fun for all members.",
        "Enjoy {topic} with this entertainment WhatsApp community in {cn} — fresh posts, clips and friendly chatter.",
    ],
    "Friendship": [
        "A friendly WhatsApp group in {cn} for {topic}: meet new people, chat daily and build real friendships.",
        "Make new friends in this WhatsApp group in {cn} centered on {topic} — warm daily conversation and community vibes.",
    ],
    "Community": [
        "A community WhatsApp group in {cn} for {topic}: local updates, discussions and helpful posts from members.",
        "Join this community WhatsApp group in {cn} about {topic} — stay connected with news, events and member updates.",
    ],
    "Regional": [
        "A regional WhatsApp group in {cn} for {topic}: local news, culture and daily chat with people from the region.",
        "Connect with the {cn} community in this WhatsApp group covering {topic} — regional updates and friendly discussion.",
    ],
    "Technology": [
        "A technology WhatsApp group in {cn} on {topic}: tech news, tips and discussions for enthusiasts and learners.",
        "Explore {topic} with this tech WhatsApp community in {cn} — gadgets, software talk and helpful how-tos.",
    ],
    "Buy-Sell": [
        "A buy-and-sell WhatsApp group in {cn} for {topic}: deals, products and marketplace posts from trusted sellers.",
        "Shop and sell in this WhatsApp group in {cn} focused on {topic} — fresh listings, offers and buyer-seller chat.",
    ],
    "Movies": [
        "A movies WhatsApp group in {cn} for {topic} lovers: film updates, recommendations and fan discussions.",
        "Discuss {topic} films in this WhatsApp group in {cn} — new releases, reviews and movie-lover chatter.",
    ],
    "Music": [
        "A music WhatsApp group in {cn} for {topic}: songs, artists and daily music sharing among fans.",
    ],
    "Health": [
        "A health WhatsApp group in {cn} about {topic}: wellness tips, fitness ideas and healthy-living discussion.",
    ],
    "News": [
        "A news WhatsApp group in {cn} covering {topic}: daily headlines and updates shared with members.",
    ],
    "Travel": [
        "A travel WhatsApp group in {cn} for {topic}: trip ideas, destination tips and traveler stories.",
    ],
    "Food": [
        "A food WhatsApp group in {cn} about {topic}: recipes, foodie talk and tasty recommendations.",
    ],
    "Girls": [
        "A girls WhatsApp group in {cn} for {topic}: friendly chat, lifestyle talk and a supportive community.",
    ],
    "Other": [
        "A WhatsApp group in {cn} for {topic} lovers: daily posts, updates and friendly member discussion.",
        "Join this WhatsApp community in {cn} about {topic} — active chat, shared interests and regular updates.",
    ],
}

def topic_words(title, src_tag):
    t = re.sub(r"[^\w\s]", " ", title.lower())
    t = re.sub(r"\s+", " ", t).strip()
    stop = {"whatsapp", "group", "groups", "join", "official", "new", "best",
            "the", "and", "for", "with", "all", "daily", "free", "2024",
            "2025", "2026", "link", "links", "only", "club"}
    words = [w for w in t.split() if w not in stop and len(w) > 1 and re.fullmatch(r"[a-z]+", w)][:4]
    topic = " ".join(words) if words else src_tag
    return topic[:60]

def build():
    cands = json.load(open(os.path.join(WAVE, "team13_candidates.json")))
    stats = json.load(open(os.path.join(WAVE, "team13_harvest_stats.json")))
    rng = random.Random(20261104)
    items = []
    for c in cands:
        cat = CAT_MAP.get(c["cat_slug"]) or TAG_FALLBACK.get(c["src_tag"], "Other")
        iso = c["country"] if re.fullmatch(r"[A-Z]{2}", c["country"]) else "International"
        cn = COUNTRY_NAME.get(iso, "International")
        topic = topic_words(c["title"], c["src_tag"])
        tmpl = rng.choice(DESC_T.get(cat, DESC_T["Other"]))
        desc = tmpl.format(cn=cn, topic=topic)
        name = c["title"]
        if len(name) > 90:
            name = name[:87] + "..."
        img = c.get("img", "")
        if not img.startswith("https://pps.whatsapp.net/"):
            img = ""
        items.append({
            "name": name,
            "category": cat,
            "country": iso,
            "description": desc,
            "invite": f"https://chat.whatsapp.com/{c['code']}",
            "image": img,
            "note": "transport failure",
            "_src_tag": c["src_tag"],
        })
    json.dump([], open(os.path.join(WAVE, "team13-gjl-newtags.json"), "w"),
              ensure_ascii=False, indent=1)
    json.dump(items, open(os.path.join(WAVE, "team13-unverified-pending.json"), "w"),
              ensure_ascii=False, indent=1)
    leads = [
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/groups?tag=sri%20lanka&page=11&limit=20&safeSearch=blur",
         "why": "tag 'sri lanka' has ~1045 results (~53 pages); team13 scraped pp.1-10 only. Resume at page 11. NOTE: tag name (space) works, slug 'sri-lanka' returns 0 records. Heavy adult skew - keep adult-slug drops."},
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/groups?tag=urdu&page=9&limit=20&safeSearch=blur",
         "why": "tag 'urdu' (718 groups, ~36 pages); team13 scraped pp.1-8 only. Resume at page 9."},
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/groups?tag=school&page=7&limit=20&safeSearch=blur",
         "why": "tag 'school' (395 groups, ~20 pages); team13 scraped pp.1-6. Resume at page 7. Watch for minors-targeted entries (excluded)."},
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/groups?tag=career&page=6&limit=20&safeSearch=blur",
         "why": "tag 'career' (320 groups, ~16 pages); team13 scraped pp.1-5. Resume at page 6."},
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/groups?tag=friendship&page=5&limit=20&safeSearch=blur",
         "why": "tag 'friendship' (287 groups, ~15 pages); team13 scraped pp.1-4. Resume at page 5."},
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/groups?tag=fashion&page=5&limit=20&safeSearch=blur",
         "why": "tag 'fashion' (244 groups, ~13 pages); team13 scraped pp.1-4. Resume at page 5."},
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/groups?tag=clothing&page=5&limit=20&safeSearch=blur",
         "why": "tag 'clothing' (195 groups, ~10 pages); team13 scraped pp.1-4. Resume at page 5."},
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/groups?tag=work%20from%20home&page=5&limit=20&safeSearch=blur",
         "why": "tag 'work from home' (154 groups, ~8 pages); team13 scraped pp.1-4. Resume at page 5."},
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/groups?tag=youtube&page=5&limit=20&safeSearch=blur",
         "why": "tag 'youtube' (155 groups, ~8 pages); team13 scraped pp.1-4. Resume at page 5."},
        {"domain": "api.groupjoin.link",
         "url": "https://api.groupjoin.link/tags?limit=100&offset=300",
         "why": "tag universe enumeration (36,980 tags total, sorted by count). Team13 reviewed offsets 0-200. Fresh tag candidates NOT yet scraped (from tag counts): hindi (1931, likely adult-saturated - probe), tamil (1888, probe), malayalam (1369, probe), sinhala (770, overlaps sri lanka), film (151), love (140, dating-risk), girls (277, probe adult ratio), indianmovies (303), hollywoodmovies (302), netflixseries (253), amazonseries (253), webseries (52), hindi-movies (53), dubbed-movies (49), english-movies (49), movie (49), quotes (76), magazines (75), status (84), politics (84), quotes, tiktok (80), instagram (62), celebrities (62), anime (62), poetry (62), thoughts (61), fan-club (59), beauty (70), vehicle (93), auto (88), online-work (94), earn-money (89), forex (54), binance (65, crypto-adjacent), apps (946, spam-risk), songs (201), audio (189), online (191), free (216), viral (280), family (158), love (140), relationships (108, dating-risk), loving (100, dating-risk). AVOID: adult/18+/xxx/porn/sex/bokep-seeded tags (policy: drop on sight), PH/VN/TH/EU/Balkan/Gulf/Indonesia tags (retired), covered tags: pakistan funny jobs music movies crypto news health travel food pets football study nigeria brazil mexico money education business online-shopping entertainment gaming indonesia pubg freefire bgmi gamer kenya uk usa uganda ghana german malaysia sports-and-fitness."},
    ]
    json.dump(leads, open(os.path.join(WAVE, "team13-leads.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"pending items: {len(items)}; verified: 0 (transport failure); "
          f"harvest stats: {stats}", flush=True)

if __name__ == "__main__":
    build()
