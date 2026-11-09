import json, re, html

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
ALLOWED = ["Gaming","Education","Online Earning","Community & Social","Business",
           "Friendship","Finance","Buy Sell","Islamic","Entertainment","Jobs",
           "Technology","Funny","Sports","Health","News"]

CATMAP = {"Gaming":"Gaming","Business":"Business","Money":"Online Earning",
    "Earn Money Online":"Online Earning","Sports & Fitness":"Sports",
    "Online Shopping":"Buy Sell","Entertainment":"Entertainment",
    "Friendship":"Friendship","Education":"Education","Comedy":"Funny",
    "Jobs":"Jobs","Beauty & Fashion":"Community & Social",
    "Science & Technology":"Technology","Pets & Animals":"Community & Social",
    "Autos & Vehicles":"Community & Social","Quotes":"Entertainment",
    "Comics":"Entertainment","Spiritual":"Community & Social","Music":"Entertainment",
    "Photography":"Community & Social","Advertising":"Business","Fan Club":"Entertainment",
    "Flirting":"Friendship","Love & Relationship":"Friendship"}

COUNTRY_KW = {"pakistan":"PK","pakistani":"PK","india":"IN","indian":"IN","bangladesh":"BD",
    "nepal":"NP","sri lanka":"LK","usa":"US","america":"US","uk":"GB","england":"GB",
    "london":"GB","canada":"CA","australia":"AU","mexico":"MX","brazil":"BR","brasil":"BR",
    "spain":"ES","barcelona":"ES","france":"FR","germany":"DE","italy":"IT","turkey":"TR",
    "uae":"AE","abu dhabi":"AE","dubai":"AE","saudi":"SA","qatar":"QA","kuwait":"KW",
    "oman":"OM","bahrain":"BH","nigeria":"NG","kenya":"KE","ghana":"GH","philippines":"PH",
    "indonesia":"ID","malaysia":"MY","thailand":"TH","vietnam":"VN","japan":"JP",
    "korea":"KR","china":"CN","russia":"RU","ukraine":"UA","egypt":"EG","morocco":"MA",
    "tamil":"IN","telugu":"IN","punjabi":"PK","urdu":"PK","hindi":"IN","sinhala":"LK",
    "gulf":"AE","africa":"NG","europe":"GB"}

PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
PROHIBIT_RE = re.compile(
    r"[^.\n!?]*(?:not allowed|na karein|nahi kare|not allow|prohibit|no porn|no xxx|no sex|"
    r"links and pron not allowed|inappropriate content)[^.\n!?]*[.!\n]?", re.I)
ADULT_KW = ["xxx","porn","sex video","sex chat","sex group","sexy","escort","cam girl",
    "camgirl","call girl","call boy","video call service","paid service","incest",
    "mom son","real incest","family lovers","desi bhabhi","bhabhi video","hot girl",
    "hot aunty","aunty video","viral video link","desi viral video","mms","maal",
    "unseen","role play","nude","naked","boobs","bobs","vagina","penis","dick","pussy",
    "lesbian video","gay sex","hand job","blowjob","hookup","hook up","one night stand",
    "adult video","adult group","18+ video","🔞","💦","🍌","🍆","🍑"]
SCAM_KW = ["b-love","blove","forsage","sheyi","s-heyi","free money","double your money",
           "money doubling","airdrop","crypto airdrop"]
BOILER = re.compile(
    r"welcome to my whatsapp group[^.!\n]*[.!\n]?\s*please join my whatsapp group[^.!\n]*[.!\n]?",
    re.I)

def clean_desc(raw, fallback_topic):
    t = (raw or "")
    t = BOILER.sub(" ", t)
    t = PROHIBIT_RE.sub(" ", t)
    t = URL_RE.sub(" ", t)
    t = PHONE_RE.sub(" ", t)
    t = re.sub(r"chat\.whatsapp\.com\S*", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" .,-–—")
    # keep first 2 sentences
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]
    sents = [s for s in sents if len(s) > 3]
    if not sents:
        return f"A WhatsApp group for {fallback_topic} fans and members to chat, share updates and connect with each other."
    desc = " ".join(sents[:2])
    if not desc.endswith((".", "!", "?")):
        desc += "."
    if len(desc) > 300:
        desc = desc[:297].rsplit(" ", 1)[0] + "."
    return desc

def screen_ok(name, desc):
    t = PROHIBIT_RE.sub(" ", (name or "") + " " + (desc or "")).lower()
    for kw in ADULT_KW + SCAM_KW:
        if kw in t:
            return False, kw
    return True, None

def guess_category(g, title, desc):
    c = (g.get("category") or "")
    if c in CATMAP:
        return CATMAP[c]
    text = ((g.get("page_title") or "") + " " + title + " " + desc).lower()
    if any(k in text for k in ("job","hiring","vacancy","naukri","rojgar")): return "Jobs"
    if any(k in text for k in ("earn","earning","online paisa","make money","trading","forex","crypto","bitcoin","investment","finance","loan")): return "Online Earning"
    if any(k in text for k in ("game","gaming","pubg","free fire","ff ","ludo","cricket")): return "Gaming"
    if any(k in text for k in ("study","exam","education","school","college","university","ielts","gk ","general knowledge","notes")): return "Education"
    if any(k in text for k in ("islam","islamic","quran","naat","ramadan","muslim","allah","namaz")): return "Islamic"
    if any(k in text for k in ("buy","sell","shopping","sale","market","shop","olx","business","entrepreneur","startup")): return "Business"
    if any(k in text for k in ("friend","friendship","dosti","chat","girls","shayari","funny","meme","comedy","joke")): return "Friendship"
    if any(k in text for k in ("movie","movies","music","song","video","entertainment","drama","status","reel")): return "Entertainment"
    if any(k in text for k in ("news","breaking","headline")): return "News"
    if any(k in text for k in ("sport","football","cricket match","hockey")): return "Sports"
    if any(k in text for k in ("health","fitness","gym","yoga","doctor","medical")): return "Health"
    if any(k in text for k in ("tech","technology","mobile","android","software","coding","computer")): return "Technology"
    return "Community & Social"

def guess_country(g, title, desc):
    iso = (g.get("country") or "").strip().upper()
    if len(iso) == 2 and iso.isalpha():
        return iso
    text = ((g.get("page_title") or "") + " " + title + " " + desc).lower()
    for kw, cc in COUNTRY_KW.items():
        if kw in text:
            return cc
    return "IN"

def clean_name(n):
    n = html.unescape(n or "").strip()
    n = re.sub(r"\s+", " ", n)
    return n[:120]

def main():
    fresh = json.load(open(f"{W}/team04_fresh_raw.json"))
    verify = {}
    with open(f"{W}/team04_verify_ckpt.jsonl") as f:
        for line in f:
            r = json.loads(line); verify[r["code"]] = r
    to_verify = json.load(open(f"{W}/team04_to_verify.json"))
    dropped_pre = json.load(open(f"{W}/team04_prescreen_dropped.json"))

    candidates, pending, dead, screened_out = [], [], [], []
    for code, v in verify.items():
        g = to_verify.get(code, {})
        if v["status"] == "transport-fail":
            pending.append({"code": code, "invite": f"https://chat.whatsapp.com/{code}",
                            "from_url": v.get("from_url"), "note": "transport failed during verification"})
            continue
        if v["status"] != "live":
            dead.append({"code": code, "status": v["status"], "from_url": v.get("from_url")})
            continue
        og = clean_name(v.get("og_title") or "")
        listing_title = (g.get("title") or "").strip()
        name = og or listing_title
        if not name or len(re.sub(r"[^\w]", "", name)) < 2:
            screened_out.append({"code": code, "reason": "no usable name"})
            continue
        desc_src = g.get("desc") or g.get("context") or ""
        ok, kw = screen_ok(name, desc_src)
        if not ok:
            screened_out.append({"code": code, "reason": f"og-title/desc screen: {kw}", "og_title": og})
            continue
        topic = re.sub(r"whatsapp group.*$", "", name, flags=re.I).strip() or "community"
        desc = clean_desc(desc_src, topic)
        # final phone/url sweep on name+desc
        if PHONE_RE.search(name) or URL_RE.search(name):
            screened_out.append({"code": code, "reason": "phone/url in name"})
            continue
        candidates.append({
            "name": name,
            "category": guess_category(g, name, desc),
            "country": guess_country(g, name, desc),
            "description": desc,
            "invite": f"https://chat.whatsapp.com/{code}",
        })

    candidates.sort(key=lambda c: c["name"].lower())
    json.dump(candidates, open(f"{W}/team04-candidates.json","w"), indent=1, ensure_ascii=False)
    json.dump(pending, open(f"{W}/team04-pending.json","w"), indent=1, ensure_ascii=False)
    print(f"verified: {len(verify)} live: {sum(1 for v in verify.values() if v['status']=='live')} "
          f"dead: {len(dead)} pending: {len(pending)} screened_out(post-verify): {len(screened_out)} "
          f"candidates: {len(candidates)}")
    from collections import Counter
    print("candidate categories:", Counter(c["category"] for c in candidates))
    print("candidate countries:", Counter(c["country"] for c in candidates).most_common(10))
    json.dump({"dead": dead, "screened_out": screened_out, "prescreen_dropped": len(dropped_pre)},
              open(f"{W}/team04_rejects.json","w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
