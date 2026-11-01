#!/usr/bin/env python3
"""team13 verify-only phase: load /tmp/team13_cand.json, og:title-verify each, write outputs."""
import json, re, time, html as htmlmod, urllib.request, os

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261031")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

BLOCK_WORDS = ["porn", "pornhub", "xxx", "nude", "sex video", "escort", "call girl",
               "fuck", "dick", "pussy", "boobs", "anal", "sexy", "mms",
               "hot night", "desi hot", "18+", "18 +",
               # Urdu/Hindi sexual-service ad markers common on this site
               "ویڈیو کال", "کال گرل", "کال گرلز", "سیکس", "ننگی", "فحش",
               "ویڈیو سروس", "نائٹ گرل", "گرل سروس", "hot girl service"]
BLOCK_EMOJI = ["🥵", "🍆", "🍑", "🔞", "💦", "👅", "👄", "💋"]
JUNK_MARKERS = ["<a ", "href=", "join telegram", "group link", "active ", '"/>',
                "whatsapp group links", "– <", "| <", "c-.3", ".005"]

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = htmlmod.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

def is_blocked(name):
    nl = name.lower()
    for w in BLOCK_WORDS:
        if w in nl:
            return True
    for e in BLOCK_EMOJI:
        if e in name:
            return True
    return False

def looks_junk(name):
    nl = name.lower()
    if len(name) > 100:
        return True
    for j in JUNK_MARKERS:
        if j in nl:
            return True
    return False

def og_title(code):
    try:
        page = fetch("https://chat.whatsapp.com/" + code)
    except Exception as e:
        return None, "transport: %s" % type(e).__name__
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', page, re.I | re.S)
    if not m:
        m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', page, re.I | re.S)
    if not m:
        return "", None
    return clean(m.group(1)), None

CAT_KEYS = [("study", "Study Groups"), ("education", "Education"), ("job", "Jobs"),
            ("sport", "Sports"), ("cricket", "Sports"), ("movie", "Movies"),
            ("music", "Music"), ("health", "Health"), ("business", "Business"),
            ("shop", "Shopping"), ("travel", "Travel & Tourism"),
            ("food", "Food & Drinks"), ("poetry", "Poetry"),
            ("scholarship", "Scholarships"), ("dating", "Dating & Social"),
            ("rishta", "Family"), ("marriage", "Family"),
            ("friend", "Friendship"), ("girl", "Friendship"),
            ("earn", "Online Earning"), ("money", "Online Earning"),
            ("tech", "Technology"), ("crypto", "Crypto"),
            ("game", "Gaming"), ("news", "News"),
            ("comedy", "Comedy & Funny"), ("joke", "Quotes & Jokes"),
            ("funny", "Comedy & Funny"), ("islam", "Islamic"), ("quran", "Islamic"),
            ("naat", "Islamic"), ("muslim", "Islamic"), ("madrasa", "Islamic"),
            ("bible", "Religion"), ("hindu", "Religion"), ("christian", "Religion"),
            ("temple", "Religion"), ("shayari", "Poetry"), ("status", "Social Media"),
            ("tiktok", "Social Media"), ("youtube", "Social Media"),
            ("pubg", "Gaming"), ("teen patti", "Gaming"), ("3 patti", "Gaming"),
            ("ludo", "Gaming"), ("betting", "Sports"), ("college", "Education"),
            ("school", "Education"), ("university", "Education"),
            ("book", "Education"), ("exam", "Education")]

def category_for(slug, name):
    nl = (slug + " " + name).lower()
    if any(k in nl for k in ["islam", "quran", "muslim", "naat", "madrasa"]):
        return "Islamic"
    for key, cat in CAT_KEYS:
        if key in nl:
            return cat
    return "General Chat"

def country_for(name, slug):
    nl = (name + " " + slug).lower()
    if "pakistan" in nl or "karachi" in nl or "lahore" in nl or "quetta" in nl or "balochistan" in nl:
        return "PK"
    if "bangladesh" in nl or "dhaka" in nl:
        return "BD"
    if "nepal" in nl:
        return "NP"
    if "sri lanka" in nl:
        return "LK"
    if "myanmar" in nl:
        return "MM"
    if "uganda" in nl:
        return "UG"
    if "china" in nl:
        return "CN"
    if "poland" in nl or "austria" in nl or "bahamas" in nl or "honduras" in nl:
        return "XX"
    return "IN"

def main():
    import sys
    shard, nshards = int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else (0, 1)
    cand = json.load(open("/tmp/team13_cand.json"))
    items = list(cand.items())
    items = [it for i, it in enumerate(items) if i % nshards == shard]
    print("shard %d/%d: %d items" % (shard, nshards, len(items)), flush=True)
    # resume: skip codes already banked in output file
    done_codes = set()
    out_path = BASE + "/team13-whatspgroupslink-variant.shard%d.json" % shard
    if os.path.exists(out_path):
        try:
            for it in json.load(open(out_path)):
                done_codes.add(it["invite"].rsplit("/", 1)[-1])
        except Exception:
            pass
    pending_path = BASE + "/team13-unverified-pending.shard%d.json" % shard
    pending = []
    if os.path.exists(pending_path):
        try:
            pending = json.load(open(pending_path))
            done_codes.update(p["invite"].rsplit("/", 1)[-1] for p in pending)
        except Exception:
            pass

    verified = []
    if os.path.exists(out_path):
        try:
            verified = json.load(open(out_path))
        except Exception:
            verified = []

    n = 0
    for code, info in items:
        if code in done_codes:
            continue
        n += 1
        title, err = og_title(code)
        if err and err.startswith("transport"):
            pending.append({"name": info["name"], "category": category_for(info["slug"], info["name"]),
                            "description": "", "image": "",
                            "invite": "https://chat.whatsapp.com/" + code,
                            "country": country_for(info["name"], info["slug"]),
                            "note": "transport failure during og:title check (%s)" % err})
        elif title:
            if is_blocked(title):
                time.sleep(0.6)
                continue
            name = info["name"] if (info["name"] and not looks_junk(info["name"]) and not is_blocked(info["name"])) else title
            if is_blocked(name):
                time.sleep(0.6)
                continue
            cat = category_for(info["slug"], title)
            country = country_for(title, info["slug"])
            cname = {"IN": "India", "PK": "Pakistan", "BD": "Bangladesh",
                     "NP": "Nepal", "LK": "Sri Lanka", "MM": "Myanmar",
                     "UG": "Uganda", "CN": "China"}.get(country, "worldwide")
            verified.append({
                "name": name,
                "category": cat,
                "description": "%s is an active WhatsApp group for %s lovers. Join %s to chat, share updates and connect with the %s community in %s." % (name, cat.lower(), name, cat.lower(), cname),
                "image": "",
                "invite": "https://chat.whatsapp.com/" + code,
                "country": country,
            })
        time.sleep(0.6)
        if n % 40 == 0:
            print("shard %d verified %d new: %d ok, %d pending" % (shard, n, len(verified), len(pending)), flush=True)
            json.dump(verified, open(out_path, "w"), ensure_ascii=False, indent=1)
            if pending:
                json.dump(pending, open(pending_path, "w"), ensure_ascii=False, indent=1)
    json.dump(verified, open(out_path, "w"), ensure_ascii=False, indent=1)
    if pending:
        json.dump(pending, open(pending_path, "w"), ensure_ascii=False, indent=1)
    print("shard %d DONE verified=%d pending=%d" % (shard, len(verified), len(pending)), flush=True)

if __name__ == "__main__":
    main()
