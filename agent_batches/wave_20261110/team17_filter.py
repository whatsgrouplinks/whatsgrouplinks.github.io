import json, re, sys
from datetime import datetime

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/"
BASE = "/home/hatch/workspace/whatsapp-groups-site/"
CUTOFF = "2026-11-08T19:28:51Z"

raw = json.load(open(WD + "team17_api_raw.json"))
print("api entries:", len(raw))
print("newest:", raw[0].get("createdAt"), "oldest:", raw[-1].get("createdAt"))

# union dedupe set
existing = set(json.load(open(BASE + ".existing_codes.json")))
groups = json.load(open(BASE + "groups.json"))
g_codes = set()
for g in groups:
    inv = g.get("invite", "")
    m = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)", inv)
    if m:
        g_codes.add(m.group(1))
union = existing | g_codes
print("existing:", len(existing), "groups.json codes:", len(g_codes), "union:", len(union))

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)")

SCAM_PATTERNS = [
    "b-love", "b love", "forsage", "shey", "paypal loader", "bitfinex",
    "counterfeit currency", "crypto doubling", "double your crypto",
    "double your bitcoin", "carding", "money mule", "airdrop",
    "earn $", "earn money fast", "investment double", "double money",
    "free usdt", "usdt doubling", "mining app withdraw", "click and earn",
]
ADULT_PATTERNS = [
    "\U0001f51e", "\U0001f975", "sexy", "hookup", "escort", "porn", "xxx",
    "18+", "18 +", "adult sex", "sex video", "sex chat", "sex group",
    "call girl", "call girls", "nude", "bhabhi sex", "aunty sex",
    "desi sex", "hot girl", "hot girls", "hot bhabhi", "mms", "leak video",
    "leaked video", "viral mms", "honeymoon", "bedroom fun",
]
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{8,}\d")

CATMAP = {
    "entertainment": "Entertainment", "jobs": "Jobs", "education": "Education",
    "islamic": "Islamic", "sports": "Sports", "community": "Community & Social",
    "community & social": "Community & Social", "social": "Community & Social",
    "finance": "Finance", "funny": "Funny", "buy sell": "Buy Sell",
    "buy/sell": "Buy Sell", "health": "Health", "news": "News",
    "gaming": "Gaming", "technology": "Technology", "business": "Business",
    "crypto": "Finance", "music": "Entertainment", "movies": "Entertainment",
    "study": "Education", "job": "Jobs", "shopping": "Buy Sell",
    "food": "Community & Social", "travel": "Community & Social",
    "fashion": "Buy Sell", "love": "Community & Social",
    "friendship": "Community & Social", "dating": "Community & Social",
    "religion": "Islamic", "quran": "Islamic", "naat": "Islamic",
    "cricket": "Sports", "football": "Sports",
}

def screen_text(name, desc):
    t = (name + " " + desc).lower()
    for p in SCAM_PATTERNS:
        if p in t:
            return "scam: " + p
    for p in ADULT_PATTERNS:
        if p in t:
            return "adult: " + p
    if re.search(r"\bsex\b", t):
        return "adult: sex keyword"
    return None

candidates = []
exclusions = []
seen_codes = set()
stats = {"total": len(raw), "older_than_cutoff": 0, "non_whatsapp": 0,
         "channel": 0, "no_code": 0, "already_known": 0, "dup_in_api": 0,
         "screened": 0}

for item in raw:
    created = item.get("createdAt", "")
    if created <= CUTOFF:
        stats["older_than_cutoff"] += 1
        continue
    if item.get("platform", "").lower() != "whatsapp":
        stats["non_whatsapp"] += 1
        exclusions.append({"code": "", "reason": "non-whatsapp platform: " + str(item.get("platform")) + " name=" + str(item.get("name"))[:60]})
        continue
    link = item.get("inviteLink", "") or ""
    if "/channel/" in link or "whatsapp.com/channel" in link:
        stats["channel"] += 1
        exclusions.append({"code": "", "reason": "whatsapp channel, not group: " + link[:80]})
        continue
    m = CODE_RE.search(link)
    if not m:
        stats["no_code"] += 1
        exclusions.append({"code": "", "reason": "no chat.whatsapp.com invite code: " + link[:80]})
        continue
    code = m.group(1)
    if code in seen_codes:
        stats["dup_in_api"] += 1
        continue
    seen_codes.add(code)
    if code in union:
        stats["already_known"] += 1
        continue
    name = (item.get("name") or "").strip()
    desc_raw = (item.get("description") or "").strip()
    # name must not be a URL / phone
    if not name or name.startswith("http") or "t.me" in name or "chat.whatsapp.com" in name:
        stats["screened"] += 1
        exclusions.append({"code": code, "reason": "bad/URL name: " + name[:60]})
        continue
    reason = screen_text(name, desc_raw)
    if reason:
        stats["screened"] += 1
        exclusions.append({"code": code, "reason": reason + " | name=" + name[:60]})
        continue
    # personal info: phone in name -> drop; phone in desc -> will rewrite desc generically
    if PHONE_RE.search(name):
        stats["screened"] += 1
        exclusions.append({"code": code, "reason": "personal info (phone) in name"})
        continue
    cat_raw = (item.get("category") or "").strip().lower()
    cat = CATMAP.get(cat_raw)
    if not cat:
        # infer from name/desc keywords
        t = (name + " " + desc_raw).lower()
        if any(k in t for k in ["job", "hiring", "vacancy", "recruitment"]):
            cat = "Jobs"
        elif any(k in t for k in ["quran", "islam", "naat", "muslim", "allah"]):
            cat = "Islamic"
        elif any(k in t for k in ["cricket", "football", "sport"]):
            cat = "Sports"
        elif any(k in t for k in ["earn", "trading", "crypto", "forex", "money"]):
            cat = "Finance"
        elif any(k in t for k in ["study", "exam", "school", "learn", "course"]):
            cat = "Education"
        elif any(k in t for k in ["buy", "sell", "shop", "sale", "market"]):
            cat = "Buy Sell"
        elif any(k in t for k in ["funny", "joke", "meme", "comedy"]):
            cat = "Funny"
        elif any(k in t for k in ["health", "doctor", "ayurved", "fitness"]):
            cat = "Health"
        elif any(k in t for k in ["game", "gaming", "free fire", "pubg"]):
            cat = "Gaming"
        elif any(k in t for k in ["news", "breaking"]):
            cat = "News"
        else:
            cat = "Community & Social"
    country = (item.get("country") or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{2}", country):
        country = "International"
    candidates.append({
        "name": name[:100],
        "category": cat,
        "country": country,
        "description_raw": desc_raw,
        "invite": "https://chat.whatsapp.com/" + code,
        "code": code,
        "createdAt": created,
        "api_category": cat_raw,
        "language": item.get("language") or "",
    })

print(json.dumps(stats, indent=2))
print("candidates:", len(candidates))
json.dump(candidates, open(WD + "team17_candidates.json", "w"), ensure_ascii=False, indent=2)
json.dump(exclusions, open(WD + "team17_exclusions_stage1.json", "w"), ensure_ascii=False, indent=2)
for c in candidates:
    print(c["createdAt"], c["code"], c["category"], c["country"], "|", c["name"][:70])
