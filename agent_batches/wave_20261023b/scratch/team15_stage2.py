#!/usr/bin/env python3
"""team15 stage 2: verify NEW candidates, build entries, append to output JSON."""
import json, re, subprocess, time, os
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
DIR = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261023b"
CAND = os.path.join(DIR, "team15_candidates.json")
OUT = os.path.join(DIR, "team15-whtspgl-latest3.json")

VALID_CATS = {"Education","Jobs","Entertainment","Islamic","News","Sports","Technology",
              "Health","Business","Gaming","Friendship","Community & Social","Online Earning",
              "Crypto","Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell"}
CAT_MAP = [
    ("jobs", "Jobs"), ("job", "Jobs"), ("naukri", "Jobs"), ("vacanc", "Jobs"), ("rozgar", "Jobs"),
    ("study", "Education"), ("education", "Education"), ("exam", "Education"), ("school", "Education"),
    ("college", "Education"), ("learning", "Education"), ("learn", "Education"), ("student", "Education"),
    ("css", "Education"), ("ppsc", "Education"),
    ("movie", "Entertainment"), ("movies", "Entertainment"), ("film", "Entertainment"),
    ("music", "Entertainment"), ("song", "Entertainment"), ("fun", "Entertainment"),
    ("comedy", "Entertainment"), ("meme", "Entertainment"), ("drama", "Entertainment"), ("series", "Entertainment"),
    ("islam", "Islamic"), ("muslim", "Islamic"), ("quran", "Islamic"), ("naat", "Islamic"),
    ("deeni", "Islamic"), ("dua", "Islamic"), ("namaz", "Islamic"), ("roza", "Islamic"), ("hajj", "Islamic"),
    ("news", "News"), ("headline", "News"),
    ("sport", "Sports"), ("cricket", "Sports"), ("football", "Sports"),
    ("gaming", "Gaming"), ("pubg", "Gaming"), ("free fire", "Gaming"), ("gamer", "Gaming"), ("esports", "Gaming"),
    ("tech", "Technology"), ("computer", "Technology"), ("mobile", "Technology"),
    ("software", "Technology"), ("health", "Health"), ("medical", "Health"), ("doctor", "Health"),
    ("pharma", "Health"), ("fitness", "Health"), ("hospital", "Health"),
    ("business", "Business"), ("marketing", "Business"), ("startup", "Business"),
    ("trade", "Business"), ("shop", "Buy & Sell"), ("sell", "Buy & Sell"), ("buy", "Buy & Sell"),
    ("market", "Buy & Sell"), ("resell", "Buy & Sell"), ("property", "Real Estate"), ("real estate", "Real Estate"),
    ("plot", "Real Estate"), ("friend", "Friendship"), ("friendship", "Friendship"), ("girls", "Friendship"),
    ("dating", "Friendship"), ("love", "Friendship"), ("earn", "Online Earning"), ("earning", "Online Earning"),
    ("money", "Online Earning"), ("income", "Online Earning"), ("crypto", "Crypto"), ("bitcoin", "Crypto"),
    ("forex", "Crypto"), ("trading", "Crypto"), ("binance", "Crypto"),
    ("cooking", "Cooking"), ("recipe", "Cooking"), ("food", "Cooking"),
    ("poetry", "Poetry"), ("shayari", "Poetry"),
    ("travel", "Travel"), ("tour", "Travel"), ("trip", "Travel"),
    ("scholarship", "Scholarship"), ("freelance", "Freelance"),
]
COUNTRY_HINTS = [
    ("pakistan", "Pakistan"), ("karachi", "Pakistan"), ("lahore", "Pakistan"), ("islamabad", "Pakistan"),
    ("punjab", "Pakistan"), ("sindh", "Pakistan"), ("peshawar", "Pakistan"), ("quetta", "Pakistan"),
    ("multan", "Pakistan"), ("rawalpindi", "Pakistan"), ("faisalabad", "Pakistan"),
    ("india", "India"), ("indian", "India"), ("mumbai", "India"), ("delhi", "India"),
    ("bangladesh", "Bangladesh"), ("dhaka", "Bangladesh"), ("nepal", "Nepal"), ("kathmandu", "Nepal"),
    ("sri lanka", "Sri Lanka"), ("usa", "USA"), ("america", "USA"), ("uk", "United Kingdom"),
    ("london", "United Kingdom"), ("uae", "UAE"), ("dubai", "UAE"), ("saudi", "Saudi Arabia"),
    ("qatar", "Qatar"), ("kuwait", "Kuwait"), ("oman", "Oman"), ("bahrain", "Bahrain"),
    ("china", "China"), ("hong kong", "Hong Kong"), ("vietnam", "Vietnam"), ("malaysia", "Malaysia"),
    ("indonesia", "Indonesia"), ("nigeria", "Nigeria"), ("kenya", "Kenya"), ("ghana", "Ghana"),
    ("turkey", "Turkey"), ("germany", "Germany"), ("france", "France"), ("spain", "Spain"),
    ("italy", "Italy"), ("canada", "Canada"), ("australia", "Australia"),
]

def categorize(name, title):
    text = (name + " " + title).lower()
    for kw, cat in CAT_MAP:
        if kw in text:
            return cat
    return "Community & Social"

def country(name, title):
    text = (name + " " + title).lower()
    for kw, c in COUNTRY_HINTS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            return c
    return "International"

DESC_TPL = {
    "Education": "Join learners sharing notes, exam updates and study resources daily.",
    "Jobs": "Join members sharing job alerts, vacancies and career opportunities daily.",
    "Entertainment": "Join members sharing movies, music, memes and fun updates daily.",
    "Islamic": "Join members sharing Islamic reminders, duas and religious knowledge daily.",
    "News": "Join members sharing breaking news, headlines and daily updates.",
    "Sports": "Join fans sharing match updates, scores and sports discussion daily.",
    "Technology": "Join members sharing tech news, tips and digital updates daily.",
    "Health": "Join members sharing health tips, medical updates and wellness advice daily.",
    "Business": "Join entrepreneurs sharing business ideas, deals and marketing tips daily.",
    "Gaming": "Join gamers sharing gameplay tips, tournaments and gaming fun daily.",
    "Friendship": "Join friendly members for chatting, friendship and fun conversations daily.",
    "Community & Social": "Join an active community sharing updates, discussions and social posts daily.",
    "Online Earning": "Join members sharing online earning tips, tasks and income ideas daily.",
    "Crypto": "Join members sharing crypto signals, trading tips and market updates daily.",
    "Cooking": "Join members sharing recipes, cooking tips and food ideas daily.",
    "Poetry": "Join members sharing poetry, shayari and literary posts daily.",
    "Travel": "Join travelers sharing trip plans, tours and travel tips daily.",
    "Scholarship": "Join students sharing scholarship alerts, admissions and study abroad updates.",
    "Freelance": "Join freelancers sharing gigs, projects and freelancing tips daily.",
    "Real Estate": "Join members sharing property listings, plots and real estate deals daily.",
    "Buy & Sell": "Join members sharing buy and sell deals, products and offers daily.",
}

def verify(code):
    try:
        p = subprocess.run(["curl", "-sL", "--max-time", "20", "-A", UA,
                            f"https://chat.whatsapp.com/invite/{code}"],
                           capture_output=True, timeout=30)
        html = p.stdout.decode("utf-8", errors="ignore")
    except Exception:
        return False
    if "WhatsApp" not in html:
        return False
    return ("og:title" in html or "Join chat" in html or "Join group" in html
            or "WhatsApp Group" in html or "Group Invite" in html)

def main():
    t0 = time.time()
    cands = json.load(open(CAND))
    existing_out = json.load(open(OUT)) if os.path.exists(OUT) else []
    have = {re.search(r"invite/([A-Za-z0-9_-]+)", e["invite"]).group(1) for e in existing_out}
    todo = [c for c in cands if c["code"] not in have]
    print(f"{len(cands)} candidates, {len(todo)} to verify", flush=True)
    new_entries = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(verify, c["code"]): c for c in todo}
        for f in as_completed(futs):
            c = futs[f]
            try:
                ok = f.result()
            except Exception:
                ok = False
            print(("OK  " if ok else "DEAD") + " " + c["code"] + " | " + c["name"][:60], flush=True)
            if not ok:
                continue
            cat = categorize(c["name"], c["title"])
            ctry = country(c["name"], c["title"])
            nm = c["name"][:80]
            new_entries.append({
                "name": nm,
                "category": cat,
                "country": ctry,
                "description": f"{nm} WhatsApp group for {cat.lower()}. " + DESC_TPL.get(cat, DESC_TPL["Community & Social"]),
                "image": "",
                "invite": f"https://chat.whatsapp.com/invite/{c['code']}",
            })
    existing_out.extend(new_entries)
    json.dump(existing_out, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"verified-new added: {len(new_entries)}; total in file: {len(existing_out)} "
          f"(elapsed {time.time()-t0:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
