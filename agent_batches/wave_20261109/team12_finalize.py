import json, re, html

ALLOWED_CATS = ["Gaming","Education","Online Earning","Community & Social","Business","Friendship",
                "Finance","Buy Sell","Islamic","Entertainment","Jobs","Technology","Funny","Sports",
                "Health","News"]

# hard-drop patterns (name / og:title / listing context) — adult + scam
DROP_PATTERNS = [
    r'\bxxx\b', r'\bporn\b', r'pornography', r'\bsex\b', r'sexy', r'hookup', r'hook-up',
    r'escort', r'cam[- ]?girl', r'camgirl', r'nude', r'nudes', r'\bhot girls?\b.*\bvideo\b',
    r'kambi', r'thund', r'vedi', r'mallu\s+(sex|hot|kambi|thund)', r'call girl',
    r'b-?love', r'forsage', r'sheyi', r'free money', r'earn money (fast|free|daily)',
    r'crypto (airdrop|free|giveaway)', r'airdrop', r'double (your )?(money|bitcoin|usdt)',
    r'free (usdt|bitcoin|btc|eth|trx|dollar)',
]
# words that flag adult content only when not part of a prohibition sentence
ADULT_WORDS = [r'xxx', r'porn', r'sex', r'sexy', r'nude', r'hookup', r'escort', r'camgirl',
               r'cam girl', r'kambi', r'thund', r'call girl', r'hot video']

def strip_prohibitions(text):
    # remove sentences that PROHIBIT adult content (rules), they are not content
    sents = re.split(r'(?<=[.!?])\s+', text)
    keep = [s for s in sents if not re.search(r'(na karein|not allowed|prohibit|no .*content|mana hai|not share|dont share|don\'t share)', s, re.I)]
    return ' '.join(keep)

def clean_name(t):
    t = html.unescape(t or "")
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def has_phone(t):
    return bool(re.search(r'\d{7,}', re.sub(r'[\s\-()]', '', t or "")))

def is_drop(name, og, section):
    blob = strip_prohibitions(f"{name} {og} {section}")
    low = blob.lower()
    for p in DROP_PATTERNS:
        if re.search(p, low):
            return True, p
    return False, ""

SECTION_COUNTRY = {
    "American Groups": "US", "London Groups": "GB", "Kenyan Groups": "KE",
    "BD Groups": "BD", "SL Groups": "LK", "Pakistani WhatsApp Groups": "PK",
    "Tanzania WhatsApp Groups": "TZ", "Malayalam Groups": "IN", "Kerala Groups": "IN",
    "Malayalam Girls Groups": "IN", "Malayalam Actress Groups": "IN",
    "Malayalam Aunty Groups": "IN", "Malayalam Bhabhi Groups": "IN",
    "Malayalam Moms Groups": "IN", "Education Groups": "IN",
    "International Friend Groups": "IN",
}
def guess_country(name, og, section):
    n = f"{name} {og}".lower()
    for kw, cc in [("pakistan", "PK"), ("pakistani", "PK"), ("kerala", "IN"), ("malayalam", "IN"),
                   ("tamil", "IN"), ("india", "IN"), ("indian", "IN"), ("kenya", "KE"),
                   ("kenyan", "KE"), ("tanzania", "TZ"), ("bangladesh", "BD"), ("sri lanka", "LK"),
                   ("london", "GB"), ("uk ", "GB"), ("america", "US"), ("usa", "US"),
                   ("dubai", "AE"), ("uae", "AE"), ("saudi", "SA"), ("nepal", "NP"),
                   ("nigeria", "NG"), ("ghana", "GH"), ("zimbabwe", "ZW"), ("uganda", "UG"),
                   ("south africa", "ZA"), ("brazil", "BR"), ("philippines", "PH"), ("canada", "CA")]:
        if kw in n:
            return cc
    return SECTION_COUNTRY.get(section, "IN")

def guess_category(name, og, section):
    n = f"{name} {og} {section}".lower()
    if re.search(r'free fire|pubg|gaming|game|gamer|efootball|esport', n): return "Gaming"
    if re.search(r'\bjob|vacanc|hiring|recruit|employment', n): return "Jobs"
    if re.search(r'movie|film|cinema|actress|actor|drama|serial|song|music|entertain', n): return "Entertainment"
    if re.search(r'news|breaking', n): return "News"
    if re.search(r'quran|islam|muslim|madrasa|namaz|dua', n): return "Islamic"
    if re.search(r'study|learn|exam|education|school|college|university|coaching|class|teacher|student|psc|upsc|ssc', n): return "Education"
    if re.search(r'football|cricket|sport|ipl|toss|betting|prediction', n):
        return "Sports" if re.search(r'football|cricket|sport|ipl', n) else "Finance"
    if re.search(r'forex|trading|crypto|bitcoin|invest|stock|money|earn|income|business', n):
        if re.search(r'earn|income|online earning|make money', n): return "Online Earning"
        if re.search(r'business|shop|store|buy|sell|sale|market', n) and not re.search(r'earn|money', n): return "Buy Sell"
        return "Finance"
    if re.search(r'buy|sell|sale|shopping|store|market|kurti|clothing|fashion', n): return "Buy Sell"
    if re.search(r'funny|comedy|joke|meme|humor|humour', n): return "Funny"
    if re.search(r'health|fitness|doctor|hospital|ayurveda|yoga', n): return "Health"
    if re.search(r'status|shayari|poetry', n): return "Entertainment"
    if re.search(r'work from home|home base work|online work', n): return "Online Earning"
    if re.search(r'\btech\b|computer|mobile|android|\bapp\b|software|\bai\b|programming|iphone|samsung', n): return "Technology"
    if re.search(r'girl|friend|chat|friendship|moms|mom|aunty|bhabhi|ladies|women|single', n): return "Friendship"
    if re.search(r'kerala|malayalam|community|group|friends|indian|tamil|pakistan', n): return "Community & Social"
    return "Community & Social"

def describe(name, og, section, cat):
    base = clean_name(og) or clean_name(name)
    s = section.replace(" Groups", "").replace(" WhatsApp", "")
    if cat == "Gaming":
        return f"A WhatsApp group for {base} fans to chat, share tips and play together. Join to connect with fellow gamers and stay updated."
    if cat == "Entertainment":
        return f"A WhatsApp group for fans of {base} to share updates, videos and discussions. Join to enjoy the latest entertainment with other members."
    if cat == "Friendship":
        return f"A friendly WhatsApp group to meet and chat with new people around {base}. Join to make friends and enjoy good conversations."
    if cat == "Jobs":
        return f"A WhatsApp group sharing job updates and vacancies related to {base}. Join to get the latest openings and career news."
    if cat == "Education":
        return f"A WhatsApp group for learning and study updates about {base}. Join to share notes, tips and educational resources."
    if cat == "News":
        return f"A WhatsApp group sharing the latest news and updates about {base}. Join to stay informed every day."
    if cat == "Sports":
        return f"A WhatsApp group for sports fans to follow {base}, scores and discussions. Join to chat with fellow fans."
    if cat == "Finance":
        return f"A WhatsApp group for discussions and updates about {base}. Join to share information and learn from other members."
    if cat == "Online Earning":
        return f"A WhatsApp group sharing online earning ideas and updates about {base}. Join to learn and discuss opportunities with members."
    if cat == "Buy Sell":
        return f"A WhatsApp group for buying and selling related to {base}. Join to find deals and connect with buyers and sellers."
    if cat == "Islamic":
        return f"A WhatsApp group sharing Islamic reminders and learning about {base}. Join to grow in knowledge with fellow members."
    if cat == "Funny":
        return f"A fun WhatsApp group sharing jokes, comedy and light moments about {base}. Join for a daily dose of laughter."
    if cat == "Health":
        return f"A WhatsApp group sharing health tips and wellness updates about {base}. Join to stay healthy and informed."
    if cat == "Technology":
        return f"A WhatsApp group for technology news, tips and discussions about {base}. Join to stay updated with the latest tech."
    return f"A WhatsApp community group for people interested in {base}. Join to chat, share updates and connect with members from {s}."

def main():
    results = json.load(open('team12_verify_partial.json'))
    live = [r for r in results if r["status"] == "live"]
    # per task rule: 200 + empty og:title after retries = dead; only transport failures stay pending
    pending = [r for r in results if r["status"] == "transport"]
    dead_n = sum(1 for r in results if r["status"] in ("dead", "ambiguous"))
    cands, dropped = [], []
    seen = set()
    for r in live:
        name = clean_name(r["og_title"])
        if not name or len(name) < 2 or len(name) > 120:
            dropped.append((r["code"], "bad og:title", name)); continue
        if has_phone(name) or has_phone(r["name"]):
            dropped.append((r["code"], "phone-like", name)); continue
        d, pat = is_drop(r["name"], name, r["section"])
        if d:
            dropped.append((r["code"], f"screen:{pat}", name)); continue
        if r["code"] in seen:
            continue
        seen.add(r["code"])
        cat = guess_category(r["name"], name, r["section"])
        cc = guess_country(r["name"], name, r["section"])
        cands.append({"name": name, "category": cat, "country": cc,
                      "description": describe(r["name"], name, r["section"], cat),
                      "invite": f"https://chat.whatsapp.com/{r['code']}"})
    pend_out = [{"code": r["code"], "name": r["name"], "section": r["section"],
                 "source": r["source"], "status": r["status"], "og_title": r["og_title"],
                 "note": "transport-failed (empty/short curl response); re-check later"}
                for r in pending]
    json.dump(cands, open('team12-candidates.json','w'), ensure_ascii=False, indent=1)
    json.dump(pend_out, open('team12-pending.json','w'), ensure_ascii=False, indent=1)
    print("live:", len(live), "candidates:", len(cands), "dropped:", len(dropped), "pending:", len(pend_out), "dead:", dead_n)
    for d in dropped: print("DROP", d)
    from collections import Counter
    print("cats:", Counter(c["category"] for c in cands))
    print("countries:", Counter(c["country"] for c in cands))

if __name__ == "__main__":
    main()
