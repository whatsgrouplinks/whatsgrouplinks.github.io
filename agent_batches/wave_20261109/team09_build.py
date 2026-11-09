"""Team 09 build step: merge verify results, screen, categorize, write outputs.
Reads team09_verify_raw2.jsonl + reliable v1 entries in team09_verify_raw.jsonl.
Writes team09-candidates.json, team09-pending.json, team09-leads.json,
team09-summary.json in the wave dir.
"""
import json, re, os, html

WAVE = os.path.dirname(os.path.abspath(__file__))
CTX = json.load(open(os.path.join(WAVE, "../wave_20261108/team08-candidates.json")))
CODES = json.load(open(os.path.join(WAVE, "team08_codes.json")))
EXISTING = set(json.load(open(os.path.join(WAVE, "../../.existing_codes.json"))))

CATEGORIES = ["Gaming", "Education", "Online Earning", "Community & Social",
              "Business", "Friendship", "Finance", "Buy Sell", "Islamic",
              "Entertainment", "Jobs", "Technology", "Funny", "Sports",
              "Health", "News"]

# ---- screening ----
DROP_PATTERNS = [
    r"porn", r"\bxxx\b", r"sex\b", r"sexy", r"hookup", r"hook-up",
    r"escort", r"cam[\s\-]?girl", r"call[\s\-]?girl", r"adult\s*(video|chat|group)",
    r"b[\s\-]?love", r"forsage", r"sheyi", r"airdrop", r"free\s*money",
    r"double\s*(your\s*)?money", r"earn\s*\$\s*\d+\s*(per|/)\s*day",
    r"nude", r"hot\s*girl", r"desi\s*bhabhi", r"mms\b",
    r"pearlvine", r"dark\s*web", r"exit\s+group", r"personal\s+data.*dark",
    r"your\s+data.*(hack|leak|dark)", r"account.*hack",
    r"virus", r"data[\s_\-]*h[ae]ck",
    r"carding", r"carder", r"cc\s*seller", r"cc\s*shop", r"carded\s*uc",
    r"usdt\s*flash", r"btc\s*flash", r"flashing\s*software",
    r"meta[\s\-]?whale", r"holiverse", r"binary\s*option", r"unick",
]
DROP_RE = re.compile("|".join(DROP_PATTERNS), re.I)

# sentences that PROHIBIT adult content are not content: strip them before screening
PROHIBIT_RE = re.compile(
    r"[^.!\n]*(inappropriate|adult|porn|xxx|sex|nude|bad|wrong|gandi|ghalat)[^.!\\n]*"
    r"(na\s*karein|not\s*allowed|mana\s*hai|not\s*allow|prohibit|share\s*na)[^.!\\n]*[.!\n]?",
    re.I)

def screen_text(name, ctx):
    t = (name + " " + (ctx or "")).strip()
    t2 = PROHIBIT_RE.sub(" ", t)
    m = DROP_RE.search(t2)
    if m:
        return m.group(0)
    # sexual-emoji clusters in the group name itself (not the ctx)
    sex_emoji = ["💋", "🫦", "🍆", "🍑", "👙", "🔞", "🍌"]
    hits = sum(1 for e in sex_emoji if e in (name or ""))
    if "🔞" in (name or "") or hits >= 2:
        return "sexual emoji cluster"
    return None

# ---- categorization ----
def _cat(s):
    if any(k in s for k in ["pubg", "free fire", "gaming", "gamer", "cricket game"]) \
            or re.search(r"\bpsl\b", s):
        return "Gaming"
    if any(k in s for k in ["job", "jobs", "naukri", "rozgar", "vacancy", "hiring",
                            "freelanc", "فرصه عمل", "فرصة عمل", "وظائف", "وظيفة",
                            "வேலை"]):
        return "Jobs"
    if any(k in s for k in ["study", "education", "student", "exam", "admission",
                            "scholarship", "university", "ielts", "css", "ppsc", "fpsc",
                            "study abroad", "learn english", "academy", "school", "college",
                            "جامعة", "جامعات", "طلاب", "طالبات", "دراسة", "تعليم"]):
        return "Education"
    if any(k in s for k in ["quran", "islam", "islamic", "naat", "madrasa", "deen", "allah"]):
        return "Islamic"
    if any(k in s for k in ["crypto", "bitcoin", "trading", "forex", "binance",
                            "investment", "profit", "stock"]):
        return "Finance"
    if any(k in s for k in ["earn", "earning", "online earning", "make money",
                            "making money", "income",
                            "الربح", "دخل", "احقق دخلي", "عمل من البيت", "من البيت", "من بيتك",
                            "التسويق بالعمولة", "مشروعك"]):
        return "Online Earning"
    if any(k in s for k in ["buy", "sell", "sale", "shopping", "market", "olx", "bazaar",
                            "ازياء", "ملابس", "تسوق"]):
        return "Buy Sell"
    if any(k in s for k in ["funny", "meme", "joke", "comedy", "hansi", "mazahiya"]):
        return "Funny"
    if any(k in s for k in ["cricket", "football", "sports", "hockey", "wwe",
                            "كرة القدم", "كرة", "رياضة"]):
        return "Sports"
    if any(k in s for k in ["health", "fitness", "doctor", "medical", "gym", "weight",
                            "الصحه", "الصحة", "الرشاقه", "الرشاقة"]):
        return "Health"
    if any(k in s for k in ["news", "breaking", "headlines", "journalist", "اخبار", "الأخبار",
                            "செய்தி"]):
        return "News"
    if any(k in s for k in ["movie", "drama", "song", "music", "entertainment",
                            "film", "status video", "tiktok", "shayari", "poetry"]):
        return "Entertainment"
    if any(k in s for k in ["technology", "tech", "mobile", "computer", "software",
                            "programming", "digital"]) or re.search(r"\bai\b", s):
        return "Technology"
    if any(k in s for k in ["business", "entrepreneur", "startup", "shop", "store",
                            "متابعين", "لايكات", "مشاهدات"]):
        return "Business"
    if any(k in s for k in ["friend", "friendship", "social", "dosti", "girls", "boys",
                            "chat", "chatting", "new friends", "community"]):
        return "Friendship"
    return "Community & Social"

def categorize(name, src_url, ctx):
    # Name first; fallback uses the listing-page URL only, NOT the ctx snippet:
    # ctx is an 800-char window that bleeds neighbouring listings' keywords.
    c = _cat((name or "").lower())
    if c != "Community & Social":
        return c
    return _cat((name + " " + (src_url or "")).lower())

FLAG_COUNTRY = {"🇧🇭": "BH", "🇰🇼": "KW", "🇸🇦": "SA", "🇵🇰": "PK", "🇮🇳": "IN",
                "🇮🇩": "ID", "🇿🇦": "ZA", "🇬🇭": "GH", "🇿🇼": "ZW", "🇦🇪": "AE",
                "🇧🇩": "BD", "🇳🇵": "NP", "🇱🇰": "LK"}

def guess_country(name, src_url, ctx):
    for flag, cc in FLAG_COUNTRY.items():
        if flag in (name or ""):
            return cc
    s = (name + " " + (src_url or "") + " " + (ctx or "")).lower()
    if "south-africa" in s or "south africa" in s:
        return "ZA"
    if "ghana" in s:
        return "GH"
    if "zimbabwe" in s:
        return "ZW"
    if "indonesia" in s:
        return "ID"
    if "saudi" in s:
        return "SA"
    if "kuwait" in s or "alkwet" in s:
        return "KW"
    if "bahrain" in s or "albhren" in s:
        return "BH"
    if "tamil" in s:
        return "IN"
    if any(k in s for k in ["pakistan", "pakistani", "punjabi", "lahore", "karachi",
                            "whatsgroupslinkspk", "sindh", "urdu"]):
        return "PK"
    return "IN"

def clean_name(name):
    n = html.unescape(name or "").strip()
    n = re.sub(r"\s+", " ", n)
    n = re.sub(r"https?://\S+", "", n)
    n = re.sub(r"\+?\d[\d\s\-]{9,}\d", "", n)  # phone numbers
    return n.strip(" -|")

def describe(name, category):
    topic = name.strip()
    return (f"Join this {category.lower()} WhatsApp group to connect with members "
            f"interested in {topic}. Share updates, ideas and chat with the community.")

def main():
    results = {}
    # v1 reliable entries
    if os.path.exists(os.path.join(WAVE, "team09_verify_raw.jsonl")):
        for line in open(os.path.join(WAVE, "team09_verify_raw.jsonl")):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("title"):
                results[r["code"]] = {"code": r["code"], "title": r["title"], "verdict": "live"}
            elif all(s > 100000 for s in r.get("sizes", [])) and r.get("http") == "200":
                results[r["code"]] = {"code": r["code"], "title": "", "verdict": "dead"}
    # v2 authoritative
    if os.path.exists(os.path.join(WAVE, "team09_verify_raw2.jsonl")):
        for line in open(os.path.join(WAVE, "team09_verify_raw2.jsonl")):
            line = line.strip()
            if line:
                r = json.loads(line)
                results[r["code"]] = {"code": r["code"], "title": r.get("title", ""),
                                      "verdict": r.get("verdict", "pending")}
    union_dup = [c for c in dict.fromkeys(CODES) if c in EXISTING]
    live = [r for r in results.values() if r["verdict"] == "live"]
    dead = [r for r in results.values() if r["verdict"] == "dead"]
    pending = [r for r in results.values() if r["verdict"] == "pending"]
    checked_codes = set(results)
    unchecked = [c for c in dict.fromkeys(CODES)
                 if c not in EXISTING and c not in checked_codes]

    candidates, screened_out, generic_name = [], [], []
    for r in live:
        code = r["code"]
        name = clean_name(r["title"])
        ctx_rec = CTX.get(code, {})
        ctx = ctx_rec.get("ctx", "")
        src = ctx_rec.get("src_url", "")
        if not name or name.lower() in ("whatsapp group invite", "whatsapp", "join group",
                                         "xxxx left") \
                or sum(1 for ch in name if ch.isalnum()) < 2:
            generic_name.append({"code": code, "title": r["title"], "ctx": ctx[:300],
                                 "note": "og:title generic/degenerate; needs manual name"})
            continue
        reason = screen_text(name, ctx)
        if reason:
            screened_out.append({"code": code, "name": name, "reason": reason})
            continue
        cat = categorize(name, src, ctx)
        candidates.append({
            "name": name,
            "category": cat,
            "country": guess_country(name, src, ctx),
            "description": describe(name, cat),
            "invite": "https://chat.whatsapp.com/" + code,
        })
    # de-dup candidates by invite (should be unique already)
    seen = set()
    uniq = []
    for c in candidates:
        if c["invite"] not in seen:
            seen.add(c["invite"])
            uniq.append(c)
    candidates = uniq

    pending_out = []
    for r in pending:
        ctx_rec = CTX.get(r["code"], {})
        pending_out.append({"code": r["code"],
                            "invite": "https://chat.whatsapp.com/" + r["code"],
                            "ctx": ctx_rec.get("ctx", "")[:500],
                            "src_url": ctx_rec.get("src_url", ""),
                            "note": "transport-failed after 3 attempts; recheck later"})
    for g in generic_name:
        pending_out.append({"code": g["code"],
                            "invite": "https://chat.whatsapp.com/" + g["code"],
                            "ctx": g["ctx"],
                            "src_url": CTX.get(g["code"], {}).get("src_url", ""),
                            "note": g["note"]})

    json.dump(candidates, open(os.path.join(WAVE, "team09-candidates.json"), "w"),
              ensure_ascii=False, indent=1)
    json.dump(pending_out, open(os.path.join(WAVE, "team09-pending.json"), "w"),
              ensure_ascii=False, indent=1)
    json.dump([], open(os.path.join(WAVE, "team09-leads.json"), "w"), ensure_ascii=False, indent=1)
    summary = {
        "team": "team09",
        "slice": "team08_codes.json (704 codes banked Nov 8, PUBG / whatsgroupslinkspk / crypto batches)",
        "sources": sorted(set(CTX.get(c, {}).get("src_url", "") for c in CODES if c in CTX)),
        "total_codes": len(dict.fromkeys(CODES)),
        "union_dup": len(union_dup),
        "checked": len(results),
        "unchecked": len(unchecked),
        "verified": len(candidates),
        "pending": len(pending_out),
        "leads": 0,
        "dead": len(dead),
        "screened_out": len(screened_out),
        "screened_out_reasons": {s["code"]: s["reason"] for s in screened_out},
        "notes": (
            "Slow checker: curl --http2 with browser UA, max 3 parallel, >=0.5s between checks; "
            "partial-head fetch (og:title sits at byte ~2518 on invite pages); "
            "og:title empty after up to 3 attempts = dead; fetch failures after 3 attempts = pending. "
            "HTTP/2 measured ~2x faster TTFB than HTTP/1.1 (~3.5s vs ~7s). "
            "Pending = live invites whose og:title is degenerate ('...', '.') or a leave-artifact "
            "('Xxxx left' x5), not a real group name. "
            "Verification-only slice: no new listing fetches, so leads = []. "
            "Descriptions are generic 1-2 sentence texts derived from group name/category only; "
            "no source names/links, no phone numbers (one Tamil matrimony name had its phone stripped). "
            "Screened out 18 live groups: Pearlvine MLM x3, carding/CC-seller fraud x6, "
            "dark-web/data-hack scare x3, sexual-emoji group x1, crypto-airdrop x1, "
            "USDT/BTC-flash software x1, Holiverse/Meta-Whale x1, binary options x1, Unick Forex x1."
        ),
    }
    json.dump(summary, open(os.path.join(WAVE, "team09-summary.json"), "w"),
              ensure_ascii=False, indent=2)
    print("candidates", len(candidates), "pending", len(pending_out),
          "dead", len(dead), "screened_out", len(screened_out),
          "unchecked", len(unchecked), "union_dup", len(union_dup))

if __name__ == "__main__":
    main()
