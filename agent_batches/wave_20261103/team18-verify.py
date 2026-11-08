#!/usr/bin/env python3
"""TEAM 18 — verify candidates against chat.whatsapp.com og:title."""
import re, json, time, html as h
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
HEAD = {"User-Agent": UA, "Accept": "text/html,*/*;q=0.9"}

PORN_RE = re.compile(
    r'porn|pornhub|\bxxx\b|nude|sex\s*video|escort|call\s*girl|\bfuck\b|dick|pussy|boobs|\banal\b|🥵|🍆|🍑|🔞|💦|👅|👄|💋',
    re.I)

CATEGORY_KEYWORDS = [
    (r'\bcricket\b|ipl|football|soccer|sport', "Sports"),
    (r'\bgaming\b|game\b|pubg|free fire|bgmi', "Gaming"),
    (r'\bjob\b|jobs\b|hiring|career|vacan|recruit|test prep|exam|ssc|upsc', "Jobs"),
    (r'study|educat|school|college|university|learn|tutorial|gk\b|notes|coaching', "Education"),
    (r'movie|film|netflix|cinema', "Movies"),
    (r'music|song|dj\b', "Music"),
    (r'news|newspaper|daily', "News"),
    (r'islam|quran|hadith|ramadan|allah|muhammad|masjid|dua\b|namaz|naat', "Islamic"),
    (r'business|trade|import|export|entrepreneur|startup', "Business"),
    (r'finance|forex|trading|crypto|bitcoin|binance|invest|money|earning|loan', "Finance"),
    (r'sell|buy|shop|market|store|deal\b|bazaar|olx', "Buy-Sell"),
    (r'health|doctor|medical|fitness|diet|hospital', "Health"),
    (r'tech|software|app\b|ai\b|computer|programming', "Technology"),
    (r'travel|tour|hotel|flight|visa', "Travel"),
    (r'food|recipe|cook|restaurant|biryani', "Food"),
    (r'pet\b|cat\b|dog\b|animal', "Pets"),
    (r'funny|joke|meme|comedy|humor', "Funny"),
    (r'girl|ladies|women|bhabhi', "Girls"),
    (r'friend|dosti|dost|masti|gupshup|chat\b', "Friendship"),
    (r'pakistan|india|kenya|uk\b|canada|german|arab|america|china|dubai|tamil|telugu|kannada|bangla|punjab|sindh|karachi|lahore|desi', "Regional"),
]

def guess_category(name, slug):
    t = (name + " " + slug).lower()
    for pat, cat in CATEGORY_KEYWORDS:
        if re.search(pat, t):
            return cat
    return "Regional"

def check(code):
    # fresh connection per request
    try:
        r = requests.get(f"https://chat.whatsapp.com/{code}",
                         headers=HEAD, timeout=25)
        m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', r.text)
        if not m:
            m = re.search(r"<meta[^>]+property='og:title'[^>]+content='([^']*)'", r.text)
        title = h.unescape(m.group(1)).strip() if m else ""
        return title
    except Exception as e:
        return None  # transport failure

cands = json.load(open(f"{WAVE}/team18-candidates-raw.json"))
# Manual content screening (verified non-English meaning):
PORN_CODES = {"JNdrEudxsM6AnTNukOcVU7", "BtUbERIwbjC6Qua99ZbSQh"}  # தேவடியா, ಸೂಳೇಗಳ ತುಲ್ಲು = hard adult
MULE_CODES = {"G4P5BoQfPNSBUlWMxUAHAi", "Dd2lFY3HinZIlcBh5E2aXX"}  # money-mule flavor: "daily earnings", "LinkedIn rentals"
porn = 0
mule = 0
filtered = []
for t in cands:
    code = t[1]
    if code in PORN_CODES:
        porn += 1
        continue
    if code in MULE_CODES:
        mule += 1
        continue
    filtered.append(t)
cands = filtered
print(f"pre-screen: porn_dropped={porn} mule_excluded={mule}", flush=True)

verified, pending = [], []
DEAD_KNOWN = {"EQyNHAwMnlmCROKZ4hOB0Q", "Dh2wOU6RvHs7PlS08rOekE", "EsxbIEKkjFtE2UmS8O8WOV",
              "KRGqyANpiz2232gixIGC1C", "H1GsvhshIa9EHUKi61kMDJ", "CGzpIyTqHMDJR1mzYGiK02",
              "DYQOqVZ2G6B2fwZTEmsEpj"}
for name, code, country, slug in cands:
    if code in DEAD_KNOWN:
        print("DEAD (known)", code, flush=True)
        continue
    if PORN_RE.search(name):
        porn += 1
        continue
    title = check(code)
    time.sleep(0.7)
    if title is None:
        pending.append({"name": name or f"Group {code[:6]}", "category": guess_category(name, slug),
                        "country": country,
                        "description": f"WhatsApp group for members in {country} listed on a group directory.",
                        "invite": f"https://chat.whatsapp.com/{code}", "image": "",
                        "note": "transport failure"})
        print("PENDING", code, name[:40], flush=True)
    elif title == "":
        print("DEAD", code, name[:40], flush=True)
    else:
        nm = name if name and len(name) >= 3 else title
        if PORN_RE.search(title):
            porn += 1
            continue
        cat = guess_category(nm, slug)
        desc = f"{cat} WhatsApp group for people in {country}: {title[:80]}. Join to chat, share updates and connect with members from {country}."
        verified.append({"name": nm, "category": cat, "country": country,
                         "description": desc,
                         "invite": f"https://chat.whatsapp.com/{code}", "image": ""})
        print("OK", code, nm[:45], flush=True)

json.dump(verified, open(f"{WAVE}/team18-wglfinder-countries.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{WAVE}/team18-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
print(f"verified={len(verified)} pending={len(pending)} porn_dropped={porn}", flush=True)
