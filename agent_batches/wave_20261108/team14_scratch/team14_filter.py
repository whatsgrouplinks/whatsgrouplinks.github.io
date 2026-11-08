#!/usr/bin/env python3
"""Team14: filter raw groupjoin harvest -> kept candidates (pre-verify)."""
import json, re, sys

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108"
union = set(json.load(open(f"{WAVE}/dedupe_union.json")))

CATMAP = {
 "education":"Education","jobs":"Jobs","entertainment":"Entertainment","islamic":"Islamic",
 "news":"News","sports":"Sports","technology":"Technology","health":"Health","business":"Business",
 "gaming":"Gaming","friendship":"Friendship","community-social":"Community & Social",
 "online-earning":"Online Earning","crypto":"Crypto","cooking":"Cooking","poetry":"Poetry",
 "travel":"Travel","scholarship":"Scholarship","freelance":"Freelance","real-estate":"Real Estate",
 "buy-sell":"Buy & Sell","finance":"Finance","funny":"Funny",
 "music":"Entertainment","movies":"Entertainment","comedy":"Funny","fan-club":"Entertainment",
 "love-and-relationship":"Friendship","flirting":"Friendship","quotes":"Poetry",
 "photography":"Entertainment","science-and-technology":"Technology",
 "beauty-and-fashion":"Buy & Sell","money":"Finance","earn-money-online":"Online Earning",
 "spiritual":"Islamic","travel-and-tourism":"Travel","sports-and-fitness":"Sports",
 "online-shopping":"Buy & Sell","autos-and-vehicles":"Buy & Sell",
 "pets-and-animals":"Community & Social","food-and-recipes":"Cooking",
 "art-and-design":"Entertainment","advertising":"Business","marketing":"Business",
 "news-and-politics":"News","comics":"Entertainment","deals-and-offers":"Buy & Sell",
 "investment":"Finance","howto-and-style":"Education","lifestyle":"Community & Social",
 "other":"Community & Social",
}
TAGCAT = {
 "music":"Entertainment","movies":"Entertainment","cricket":"Sports","football":"Sports",
 "pubg":"Gaming","quran":"Islamic","islamic":"Islamic","poetry":"Poetry","shayari":"Poetry",
 "recipes":"Cooking","cooking":"Cooking","food":"Cooking","travel":"Travel",
 "photography":"Entertainment","books":"Education","crypto":"Crypto","forex":"Crypto",
 "freelancing":"Freelance","love":"Friendship","romantic":"Friendship","status":"Friendship",
 "quotes":"Poetry","motivation":"Community & Social","fitness":"Health","beauty":"Community & Social",
 "makeup":"Community & Social","mobile":"Buy & Sell","cars":"Buy & Sell","property":"Real Estate",
 "students":"Education","university":"Education","study":"Education","ielts":"Education",
 "exams":"Education","scholarships":"Scholarship","wedding":"Community & Social",
 "rishta":"Community & Social","punjabi":"Community & Social","sindhi":"Community & Social",
 "pashto":"Community & Social","english":"Education","hindi":"Entertainment","tamil":"Entertainment",
 "gaming":"Gaming","sports":"Sports","business":"Business","pakistan":"Community & Social",
 "malaysia":"Community & Social","lahore":"Community & Social","karachi":"Community & Social",
 "islamabad":"Community & Social","dubai":"Community & Social","nepal":"Community & Social",
 "kenya":"Community & Social","school":"Education","career":"Jobs","fashion":"Buy & Sell",
 "trading":"Finance","clothing":"Buy & Sell","friendship":"Friendship","girls":"Friendship",
 "work-from-home":"Online Earning","online-shopping":"Buy & Sell","shopping":"Buy & Sell",
 "youtube":"Entertainment","urdu":"Poetry","sri-lanka":"Community & Social","earning":"Online Earning",
 "health":"Health","funny":"Funny","entertainment":"Entertainment","videos":"Entertainment",
 "bangladesh":"Community & Social","science":"Education","indonesia":"Community & Social",
 "nursing":"Health","css":"Education","ramadan":"Islamic","ludo":"Gaming",
}
ADULT_TAGS = {"adult","18+","xxx","porn","sex","porno","sexy","nude","nudes","bhabhi","desi-sex"}
PORN_RE = re.compile(r"porn|pornhub|xxx|nudes?|sex video|escort|call girl|randi|fuck|dick|pussy|boobs|anal|orgasm|cumshot|blowjob|sexy video|sex chat|video call girl|bhabhi sex|desi sex|mallu|hot girl|sexy girl|saxy|ndues|chodn|chuit|garam aunty|mom.*exchange|leaks? group|leaked video|viral mms|mms video", re.I)
SCAM_RE = re.compile(r"paypal loader|receiver and loader|money[- ]?mule|double (your|the) money|counterfeit currency|buy (drugs|cocaine|heroin)|bitfinex|guaranteed profit|double your investment|investment.*2x|earn \d+.*per day.*investment", re.I)
MINOR_RE = re.compile(r"\b(minor|under ?18|child|teen.*sex|school ?girl.*sex|11 ?yrs?|12 ?yrs?|13 ?yrs?)\b", re.I)
ADULT_EMOJI = set("🥵🍆🍑🔞💦👅👄💋")
PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{9,}\d")

def clean_desc(raw, name, cat, country):
    d = (raw or "").strip()
    d = re.sub(r"^Welcome to my whatsapp group\s*", "", d, flags=re.I)
    d = re.sub(r"Please join my whatsapp group\.?\s*", "", d, flags=re.I)
    d = re.sub(r"\s+", " ", d).strip()
    if len(d) < 8 or set(d) <= set("$b78 ") or d.lower() in ("no rules",):
        d = ""
    if d:
        sents = re.split(r"(?<=[.!?])\s+", d)
        d = " ".join(sents[:2])[:220].strip()
        if d and d[-1] not in ".!?":
            d += "."
        return d
    ctry = "" if country in ("International", "") else f" from {country}"
    return f"Join {name}, a WhatsApp group listed under {cat}{ctry}. Chat and share with active members every day."

def main():
    recs = []
    for line in open(f"{WAVE}/team14_raw.jsonl"):
        line = line.strip()
        if line:
            recs.append(json.loads(line))
    print("raw:", len(recs))
    seen, kept = set(), []
    drop = {"union":0,"dup":0,"adult_cat":0,"adult_tag":0,"porn":0,"scam":0,"minor":0,
            "emoji":0,"phone":0,"badname":0,"badcode":0}
    for c in recs:
        code = c["code"]
        if not re.fullmatch(r"[A-Za-z0-9_-]{22}", code or ""):
            drop["badcode"] += 1; continue
        if code in union:
            drop["union"] += 1; continue
        if code in seen:
            drop["dup"] += 1; continue
        seen.add(code)
        if c.get("cat_slug") == "adult":
            drop["adult_cat"] += 1; continue
        tags_l = [t.strip().lower() for t in (c.get("tags") or [])]
        if ADULT_TAGS & set(tags_l):
            drop["adult_tag"] += 1; continue
        blob = f"{c['name']} {c['desc_raw']} {' '.join(c.get('tags') or [])}"
        if PORN_RE.search(blob):
            drop["porn"] += 1; continue
        if SCAM_RE.search(blob):
            drop["scam"] += 1; continue
        if MINOR_RE.search(blob):
            drop["minor"] += 1; continue
        if any(e in blob for e in ADULT_EMOJI):
            drop["emoji"] += 1; continue
        name = re.sub(r"\s+", " ", (c["name"] or "").strip())[:120]
        if not name or len(name) < 2 or set(name) <= set(".-_ "):
            drop["badname"] += 1; continue
        if PHONE_RE.search(name):
            drop["phone"] += 1; continue
        cat = CATMAP.get(c.get("cat_slug","")) or TAGCAT.get(c.get("tag","")) or "Community & Social"
        country = c.get("country") or "International"
        kept.append({"code": code, "name": name, "category": cat, "country": country,
                     "description": clean_desc(c.get("desc_raw",""), name, cat, country),
                     "invite": f"https://chat.whatsapp.com/{code}", "image": "",
                     "_tag": c.get("tag"), "_page": c.get("page")})
    print("dropped:", drop)
    print("kept:", len(kept))
    from collections import Counter
    print("kept by tag:", dict(Counter(k["_tag"] for k in kept)))
    print("kept by cat:", dict(Counter(k["category"] for k in kept)))
    with open(f"{WAVE}/team14_kept.json", "w") as f:
        json.dump(kept, f, ensure_ascii=False, indent=1)
    print("wrote team14_kept.json")

if __name__ == "__main__":
    main()
