"""team17: build candidate JSONL from TanStack flight-data records in category HTML.
Reads: team17_cat_*.html + dedupe_union.json
Writes: JSON lines to STDOUT (caller pipes to file — python file writes are sandbox-blocked).
Skips: adult (RETIRED), spiritual-devotional (Nov-3 slice).
"""
import json, re, sys, glob, html as htmlmod
sys.path.insert(0, ".")
from team17_flight import extract_records, records_to_candidates, CODE_RE, INVITE_RE
from team17_parse import country_to_iso

SKIP_CATS = {"adult", "spiritual-devotional"}

CAT_TO_SCHEMA = {
    "art-design-photography": "Other", "auto-vehicle": "Other",
    "business-advertising-marketing": "Business", "comedy-funny": "Funny",
    "dating-flirting-chatting": "Friendship", "education-school": "Education",
    "entertainment-masti": "Entertainment", "family-relationships": "Community",
    "fan-club-celebrities": "Entertainment", "fashion-style-clothing": "Other",
    "film-animation": "Movies", "food-drinks": "Food", "gaming-apps": "Gaming",
    "health-beauty-fitness": "Health", "jobs-career": "Jobs",
    "money-earning": "Finance", "music-audio-songs": "Music",
    "news-magazines-politics": "News", "pets-animals-nature": "Pets",
    "roleplay-comics": "Entertainment", "science-technology": "Technology",
    "shopping-buy-sell": "Buy-Sell", "social-friendship-community": "Friendship",
    "sports-games": "Sports", "thoughts-quotes-jokes": "Funny",
    "travel-local-place": "Travel",
}

PORN_RES = [
    r"pornhub", r"\bporn\b", r"xxx", r"\bnude", r"sex\s*video", r"escort",
    r"call\s*girl", r"fuck", r"\bdick\b", r"pussy", r"\bboobs?\b", r"\banal\b",
    r"bokep", r"مزا دینے", r"مزہ دینے",
    "🥵", "🍆", "🍑", "🔞", "💦", "👅", "👄", "💋",
]
SCAM_RES = [
    r"\bsatta\b", r"matka", r"double (your|the) money", r"hyip",
    r"paypal (receiver|loader)", r"money[\s-]*mule", r"free (bitcoin|crypto) doubler",
]
PORN_RE = re.compile("|".join(PORN_RES), re.I)
SCAM_RE = re.compile("|".join(SCAM_RES), re.I)
MINORS_RE = re.compile(r"(teen.{0,20}dating|dating.{0,20}teen|under ?18.{0,20}(dating|friend)|school.{0,15}(girl|boy).{0,15}(dating|friend))", re.I)

def clean_desc(d):
    d = re.sub(r'\\n', ' ', d)
    d = re.sub(r'https?://chat\.whatsapp\.com/\S+', '', d)
    d = re.sub(r'https?://whatsapp\.com/channel/\S+', '', d)
    d = re.sub(r'\s+', ' ', d).strip()
    return d

def emit(code, name, desc, cat, country_iso, image, extra, seen, union, stats):
    if not re.fullmatch(r"[A-Za-z0-9]{20,24}", code):
        stats["bad_code"] += 1
        return
    if code in union:
        stats["dup_union"] += 1
        return
    if code in seen:
        stats["dup_batch"] += 1
        return
    blob = (name + " " + desc)
    if PORN_RE.search(blob):
        stats["porn"] += 1
        return
    if SCAM_RE.search(blob.lower()):
        stats["scam"] += 1
        return
    if MINORS_RE.search(blob.lower()):
        stats["minors"] += 1
        return
    seen.add(code)
    out = {
        "category": cat, "name": name, "country": country_iso,
        "description": desc, "code": code, "image": image,
        "extra": extra,
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")

def main():
    union = set(json.load(open("dedupe_union.json")))
    seen = set()
    stats = {"records": 0, "skipped_cat": 0, "dup_union": 0, "dup_batch": 0,
             "porn": 0, "scam": 0, "minors": 0, "bad_code": 0, "emitted": 0}
    files = sorted(glob.glob("team17_cat_*.html"))
    for f in files:
        t = open(f, encoding="utf-8", errors="replace").read()
        if len(t) < 100000:
            continue
        recs = extract_records(t)
        cands = records_to_candidates(recs)
        for r in cands:
            stats["records"] += 1
            rcat = r["category_badge"]
            if rcat in SKIP_CATS:
                stats["skipped_cat"] += 1
                continue
            cat = CAT_TO_SCHEMA.get(rcat, "Other")
            name = r["name"] or "WhatsApp Group"
            desc = clean_desc(r["description"])
            if not desc:
                desc = name
            # original English 1-2 sentence description; trim to ~220 chars
            if len(desc) > 240:
                desc = desc[:237].rsplit(" ", 1)[0] + "..."
            country_iso = country_to_iso(r["country_badge"]) or "International"
            before = len(seen)
            emit(r["code"], name, desc, cat, country_iso, r["image"], False,
                 seen, union, stats)
            if len(seen) > before:
                stats["emitted"] += 1
            # extra codes embedded in raw description text
            invite_codes = set(INVITE_RE.findall(r["description"]))
            for cm in CODE_RE.finditer(r["description"]):
                xc = cm.group(1)
                if xc != r["code"] and xc not in invite_codes:
                    b2 = len(seen)
                    emit(xc, name, desc, cat, country_iso, r["image"], True,
                         seen, union, stats)
                    if len(seen) > b2:
                        stats["emitted"] += 1
    sys.stderr.write("STATS " + json.dumps(stats) + " files=" + str(len(files)) + "\n")

main()
