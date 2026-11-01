#!/usr/bin/env python3
"""team15-whtspgl-latest3: scrape whtspgrouplink.com latest category pages 31-49."""
import json, re, subprocess, sys, time, os
from html import unescape

BASE = "https://whtspgrouplink.com/category/latest-whatsapp-group-links"
PAGES = range(31, 50)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OUT = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261023b/team15-whtspgl-latest3.json"

EXISTING = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))

EXCLUDE_PATHS = {
    "about", "contact-us", "privacy-policy", "disclaimer", "terms-and-conditions",
    "submit-your-whatsapp-group-link-here", "author",
}

PORN_RE = re.compile(r"\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b", re.I)
PHONE_RE = re.compile(r"^\+?\d[\d\s\-]{7,}\d$")

VALID_CATS = {"Education","Jobs","Entertainment","Islamic","News","Sports","Technology",
              "Health","Business","Gaming","Friendship","Community & Social","Online Earning",
              "Crypto","Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell"}

CAT_MAP = [
    ("jobs", "Jobs"), ("job", "Jobs"), ("naukri", "Jobs"),
    ("study", "Education"), ("education", "Education"), ("exam", "Education"), ("school", "Education"),
    ("college", "Education"), ("learning", "Education"), ("learn", "Education"),
    ("movie", "Entertainment"), ("movies", "Entertainment"), ("film", "Entertainment"),
    ("music", "Entertainment"), ("song", "Entertainment"), ("fun", "Entertainment"),
    ("comedy", "Entertainment"), ("meme", "Entertainment"), ("video", "Entertainment"),
    ("drama", "Entertainment"), ("series", "Entertainment"),
    ("islam", "Islamic"), ("muslim", "Islamic"), ("quran", "Islamic"), ("naat", "Islamic"),
    ("deeni", "Islamic"), ("dua", "Islamic"), ("namaz", "Islamic"),
    ("news", "News"), ("headline", "News"), ("update", "News"),
    ("sport", "Sports"), ("cricket", "Sports"), ("football", "Sports"), ("game", "Gaming"),
    ("gaming", "Gaming"), ("pubg", "Gaming"), ("free fire", "Gaming"), ("ff", "Gaming"),
    ("tech", "Technology"), ("computer", "Technology"), ("mobile", "Technology"),
    ("software", "Technology"), ("ai", "Technology"),
    ("health", "Health"), ("medical", "Health"), ("doctor", "Health"), ("pharma", "Health"),
    ("fitness", "Health"),
    ("business", "Business"), ("marketing", "Business"), ("startup", "Business"),
    ("trade", "Business"), ("shop", "Buy & Sell"), ("sell", "Buy & Sell"), ("buy", "Buy & Sell"),
    ("market", "Buy & Sell"),
    ("friend", "Friendship"), ("friendship", "Friendship"), ("girls", "Friendship"),
    ("dating", "Friendship"), ("love", "Friendship"), ("chat", "Friendship"),
    ("earn", "Online Earning"), ("earning", "Online Earning"), ("money", "Online Earning"),
    ("online earning", "Online Earning"), ("crypto", "Crypto"), ("bitcoin", "Crypto"),
    ("forex", "Crypto"), ("trading", "Crypto"), ("binance", "Crypto"),
    ("cooking", "Cooking"), ("recipe", "Cooking"), ("food", "Cooking"),
    ("poetry", "Poetry"), ("shayari", "Poetry"), ("urdu poetry", "Poetry"),
    ("travel", "Travel"), ("tour", "Travel"), ("trip", "Travel"),
    ("scholarship", "Scholarship"),
    ("freelance", "Freelance"),
    ("property", "Real Estate"), ("real estate", "Real Estate"), ("plot", "Real Estate"),
    ("social", "Community & Social"), ("community", "Community & Social"),
]

COUNTRY_HINTS = [
    ("pakistan", "Pakistan"), ("pak", "Pakistan"), ("karachi", "Pakistan"), ("lahore", "Pakistan"),
    ("islamabad", "Pakistan"), ("punjab", "Pakistan"), ("sindh", "Pakistan"),
    ("india", "India"), ("indian", "India"), ("mumbai", "India"), ("delhi", "India"),
    ("bangladesh", "Bangladesh"), ("dhaka", "Bangladesh"), ("nepal", "Nepal"),
    ("usa", "USA"), ("america", "USA"), ("uk", "United Kingdom"), ("london", "United Kingdom"),
    ("uae", "UAE"), ("dubai", "UAE"), ("saudi", "Saudi Arabia"), ("qatar", "Qatar"),
    ("china", "China"), ("hong kong", "Hong Kong"), ("vietnam", "Vietnam"),
    ("africa", "Africa"), ("nigeria", "Nigeria"), ("kenya", "Kenya"),
    ("turkey", "Turkey"), ("germany", "Germany"), ("france", "France"),
]

def curl_fetch(url, timeout=25):
    try:
        p = subprocess.run(
            ["curl", "-sL", "--max-time", str(timeout), "-A", UA, url],
            capture_output=True, timeout=timeout + 10)
        return p.stdout.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def post_urls_from_archive(html):
    urls = []
    for m in re.finditer(r'href="(https://whtspgrouplink\.com/([^"#?/]+)/)"', html):
        full, slug = m.group(1), m.group(2)
        if slug in EXCLUDE_PATHS or slug == "category" or slug.startswith("page"):
            continue
        if full not in urls:
            urls.append(full)
    return urls

def groups_from_post(html, post_url, post_title):
    """Return list of (name, code) from table rows."""
    out = []
    # title fallback name
    for tr in re.finditer(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I):
        row = tr.group(1)
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)
        if len(tds) < 2:
            continue
        name_raw = re.sub(r"<[^>]+>", "", tds[0])
        name = unescape(name_raw).strip()
        name = re.sub(r"\s+", " ", name)
        m = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{15,})", row)
        if not m or not name:
            continue
        out.append((name, m.group(1)))
    return out

def categorize(name, title):
    text = (name + " " + title).lower()
    for kw, cat in CAT_MAP:
        if kw in text:
            return cat
    return "Community & Social"

def country(name, title):
    text = (name + " " + title).lower()
    for kw, c in COUNTRY_HINTS:
        if kw in text:
            return c
    return "International"

def make_desc(name, cat, ctry):
    base = f"{name} WhatsApp group for {cat.lower()}."
    extra = {"Education": "Join learners sharing notes, exam updates and study resources daily.",
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
             "Buy & Sell": "Join members sharing buy and sell deals, products and offers daily."}
    return base + " " + extra.get(cat, extra["Community & Social"])

def verify(code):
    """Verify invite with curl; return True if live WhatsApp group page."""
    try:
        p = subprocess.run(
            ["curl", "-sL", "--max-time", "20", "-A", UA,
             f"https://chat.whatsapp.com/invite/{code}"],
            capture_output=True, timeout=30)
        html = p.stdout.decode("utf-8", errors="ignore")
    except Exception:
        return False
    if "WhatsApp" not in html:
        return False
    if ("og:title" in html or "Join chat" in html or "Join group" in html
            or "WhatsApp Group" in html or "Group Invite" in html
            or "whatsapp.com" in html and "invite" in html):
        return True
    return False

def main():
    from concurrent.futures import ThreadPoolExecutor, as_completed
    t0 = time.time()
    entries = []
    seen = set()
    stats = {"pages": 0, "posts": 0, "candidates": 0, "new_candidates": 0,
             "verified": 0, "dupes": 0, "filtered": 0}
    DEADLINE = t0 + 26 * 60  # 26 min hard budget

    for pg in PAGES:
        if time.time() > DEADLINE:
            break
        html = curl_fetch(f"{BASE}/page/{pg}/")
        if not html or "whtspgrouplink" not in html:
            continue
        stats["pages"] += 1
        posts = post_urls_from_archive(html)
        for post_url in posts:
            if time.time() > DEADLINE:
                break
            if len(entries) >= 600:
                break
            ph = curl_fetch(post_url)
            if not ph:
                continue
            stats["posts"] += 1
            tm = re.search(r'<h1[^>]*>(.*?)</h1>', ph, re.S | re.I)
            title = unescape(re.sub(r"<[^>]+>", "", tm.group(1))).strip() if tm else ""
            rows = groups_from_post(ph, post_url, title)
            batch = []
            for name, code in rows:
                stats["candidates"] += 1
                if code in EXISTING or code in seen:
                    stats["dupes"] += 1
                    continue
                if len(name) < 3 or len(name) > 120:
                    stats["filtered"] += 1
                    continue
                if PHONE_RE.match(name) or PHONE_RE.match(name.replace(" ", "")):
                    stats["filtered"] += 1
                    continue
                if PORN_RE.search(name):
                    stats["filtered"] += 1
                    continue
                stats["new_candidates"] += 1
                seen.add(code)
                batch.append((name, code, title))
            # verify batch in parallel (8 workers)
            with ThreadPoolExecutor(max_workers=8) as ex:
                futs = {ex.submit(verify, code): (name, code, title)
                        for name, code, title in batch
                        if time.time() <= DEADLINE and len(entries) < 600}
                for fut in as_completed(futs):
                    name, code, title = futs[fut]
                    if len(entries) >= 600:
                        break
                    try:
                        ok = fut.result()
                    except Exception:
                        ok = False
                    if ok:
                        cat = categorize(name, title)
                        ctry = country(name, title)
                        entries.append({
                            "name": name[:80],
                            "category": cat,
                            "country": ctry,
                            "description": make_desc(name[:80], cat, ctry),
                            "image": "",
                            "invite": f"https://chat.whatsapp.com/invite/{code}",
                        })
                        stats["verified"] += 1
        # checkpoint
        with open(OUT, "w") as f:
            json.dump(entries, f, ensure_ascii=False, indent=1)
    with open(OUT, "w") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
    stats["entries"] = len(entries)
    stats["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(stats, indent=1))

if __name__ == "__main__":
    main()
