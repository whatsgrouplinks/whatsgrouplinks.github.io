import json, re, os, html
W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
st = json.load(open(f"{W}/team05-extracted.json"))
ver = json.load(open(f"{W}/team05-verify.json"))
leads = json.load(open(f"{W}/leads_slice_05.json"))
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

# --- screening ---
BANNED = ["xxx","porn","sex","hookup","escort","cam girl","camgirl","sexy","b-love","blove","forsage","sheyi",
          "airdrop","free money","earn money free","double your money","investment double","nude","naked",
          "adult video","hot girl","hot girls","call girl","call girls","dating sex","sex chat","sex video",
          "sex group","adult group","18+","18 +","xvideo","xnxx","pornhub","onlyfans","desi sex","bhabhi sex"]
# 'sex' as substring is too broad (e.g. 'Sussex'); use word-boundary for short words
def strip_prohibitions(text):
    # remove sentences that PROHIBIT such content (rules), before screening
    sents = re.split(r"(?<=[.!?])\s+", text)
    keep = []
    for s in sents:
        sl = s.lower()
        if any(p in sl for p in ["na karein","na karen","not allowed","prohibited","mana hai","mana he","strictly prohibited","allow nahi","allowed nahi","share na","mat karein","mat karen","no adult","no porn","no sex","no xxx","galat","wrong"]):
            continue
        keep.append(s)
    return " ".join(keep)
def is_banned(text):
    t = strip_prohibitions(text).lower()
    for b in BANNED:
        if " " in b or len(b) > 4:
            if b in t: return b
        else:
            if re.search(r"\b"+re.escape(b)+r"\b", t): return b
    return None

CATS = ["Gaming","Education","Online Earning","Community & Social","Business","Friendship","Finance","Buy Sell","Islamic","Entertainment","Jobs","Technology","Funny","Sports","Health","News"]
def categorize(name, ctx):
    t = (name + " " + ctx).lower()
    if any(k in t for k in ["job","jobs","naukri","vacancy","rojgar","recruitment","hiring"]): return "Jobs"
    if any(k in t for k in ["news","samachar","khabar","newspaper","breaking"]): return "News"
    if any(k in t for k in ["study","education","exam","student","school","college","university","shiksha","padhai","teacher","coaching","notes","mcq"]): return "Education"
    if any(k in t for k in ["earn","earning","online earning","paise kamaye","income","paisa"]): return "Online Earning"
    if any(k in t for k in ["stock","share market","trading","investor","investment","crypto","bitcoin","finance","loan","real estate","property","buyer","seller"]): return "Finance"
    if any(k in t for k in ["buy","sell","shopping","bazar","market","sale","olx","deal"]): return "Buy Sell"
    if any(k in t for k in ["islam","islamic","quran","muslim","allah","namaz","dua","hadith","deen"]): return "Islamic"
    if any(k in t for k in ["game","gaming","pubg","free fire","cricket","football","sport","ipl","match"]): return "Sports" if any(k in t for k in ["cricket","football","sport","ipl","match"]) else "Gaming"
    if any(k in t for k in ["funny","joke","jokes","meme","comedy","hasna","fun"]): return "Funny"
    if any(k in t for k in ["movie","film","song","music","entertainment","video","drama","serial","status"]): return "Entertainment"
    if any(k in t for k in ["health","doctor","fitness","yoga","hospital","medical","diet"]): return "Health"
    if any(k in t for k in ["friend","friendship","dosti","girls","ladki","chat group","new friends"]): return "Friendship"
    if any(k in t for k in ["business","startup","company","shop","store","udyog","vyapar"]): return "Business"
    if any(k in t for k in ["tech","technology","computer","mobile","android","software","coding","app"]): return "Technology"
    return "Community & Social"
def country_guess(name, ctx):
    t = (name + " " + ctx).lower()
    if any(k in t for k in ["pakistan","pakistani","lahore","karachi","islamabad","urdu"]): return "PK"
    if any(k in t for k in ["bangladesh","bangla","dhaka"]): return "BD"
    if any(k in t for k in ["nepal","nepali","kathmandu"]): return "NP"
    if any(k in t for k in ["sri lanka","colombo"]): return "LK"
    if any(k in t for k in ["usa","america","united states","new york"]): return "US"
    if any(k in t for k in ["uk ","london","england"]): return "GB"
    if any(k in t for k in ["uae","dubai","abu dhabi"]): return "AE"
    if any(k in t for k in ["saudi"]): return "SA"
    if any(k in t for k in ["nigeria","+234"]): return "NG"
    if any(k in t for k in ["kenya"]): return "KE"
    if any(k in t for k in ["ghana"]): return "GH"
    if any(k in t for k in ["philippines","filipino"]): return "PH"
    if any(k in t for k in ["indonesia"]): return "ID"
    return "IN"

def clean_name(title):
    n = html.unescape(title).strip()
    n = re.sub(r"\s+", " ", n)
    n = re.sub(r"^(whatsapp group invite|join|group)\s*[-:|]*\s*", "", n, flags=re.I)
    n = n.strip(" -–—:|")
    # strip trailing emoji-only runs? keep single emojis in middle; trim to 120 chars
    return n[:120].strip() or "WhatsApp Group"
def clean_desc(ctx, name, title):
    # build 1-2 sentence description from listing context, strip urls/phones/source names
    t = re.sub(r"https?://\S+", " ", ctx)
    t = re.sub(r"\+?\d[\d\s\-]{8,}\d", " ", t)  # phone-ish
    t = re.sub(r"\s+", " ", t).strip()
    # take sentences mentioning the group name words, else first sentences
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if len(s.strip()) > 15]
    picked = [s for s in sents if any(w.lower() in s.lower() for w in name.split()[:3] if len(w) > 3)][:2]
    if not picked: picked = sents[:2]
    d = " ".join(picked)
    d = re.sub(r"(whtspgrouplink|imagesplatform|wagroupnest|wagroupshub|whtsagrouplinks|groupsnest)[^ .]*", "", d, flags=re.I)
    d = re.sub(r"\s+", " ", d).strip(" .")
    if not d:
        d = f"Join this {name} WhatsApp group to connect with members, share updates and chat with the community."
    if len(d) > 280: d = d[:277].rsplit(" ", 1)[0] + "."
    if not d.endswith("."): d += "."
    return d

candidates, pending, dropped = [], [], []
live = [(c, v) for c, v in ver.items() if v.get("status") == 200 and v.get("title")]
amb = [(c, v) for c, v in ver.items() if v.get("status") == 200 and not v.get("title")]
dead = [(c, v) for c, v in ver.items() if v.get("status") != 200]
for c, v in live:
    rec = st["codes"].get(c, {})
    ctx = " ".join(rec.get("contexts", []))
    title = v["title"]
    name = clean_name(title)
    screen_text = name + " " + (v.get("desc") or "") + " " + ctx
    ban = is_banned(screen_text)
    if ban:
        dropped.append({"code": c, "name": name, "reason": f"screen banned: {ban}"})
        continue
    if re.search(r"\d{7,}", name) or re.search(r"\+\d{7,}", name):
        dropped.append({"code": c, "name": name, "reason": "phone number in name"})
        continue
    cat = categorize(name, ctx)
    candidates.append({
        "name": name,
        "category": cat,
        "country": country_guess(name, ctx),
        "description": clean_desc(ctx, name, title),
        "invite": f"https://chat.whatsapp.com/{c}",
    })
# pending: transport-failed only (status 0 / no body) — ambiguous empties are DEAD per rules after retries
for c, v in dead:
    if v.get("status") == 0:
        pending.append({"code": c, "invite": f"https://chat.whatsapp.com/{c}", "reason": "transport failed (no response)", "og_title": ""})
# also any fresh code not in verify results at all = pending
verified_codes = set(ver.keys())
for c in st["codes"]:
    if c not in existing and c not in verified_codes:
        pending.append({"code": c, "invite": f"https://chat.whatsapp.com/{c}", "reason": "not verified (verify run incomplete)", "og_title": ""})

json.dump(candidates, open(f"{W}/team05-candidates.json", "w"), indent=1, ensure_ascii=False)
json.dump(pending, open(f"{W}/team05-pending.json", "w"), indent=1, ensure_ascii=False)
print("candidates:", len(candidates), "pending:", len(pending), "dropped-screen:", len(dropped), "live:", len(live), "ambig-dead:", len(amb), "transport-dead:", len(dead))
for d in dropped: print("DROP", d)
for cand in candidates: print("KEEP", cand["category"], cand["country"], "|", cand["name"][:70])
