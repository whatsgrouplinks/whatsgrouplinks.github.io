import requests, re, json, time, html, os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
WAVE_DIR = os.path.dirname(SCRATCH)
CACHE = os.path.join(SCRATCH, "cache.json")

union = set(json.load(open(os.path.join(WAVE_DIR, "dedupe_union.json"))))
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

t = open(os.path.join(SCRATCH, "glfy_sa.html"), encoding="utf-8").read()
pairs = re.findall(
    r'<div style="text-align: center;">([^<]{1,120})</div>\s*<div[^>]*>\s*(?:<div[^>]*>\s*)*<a href=["\']https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})["\']',
    t)
hdr = re.findall(r"<a href='https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})' target='_blank'>", t)
paired = {c for _, c in pairs}
for c in hdr:
    if c not in paired:
        pairs.append((None, c))
print("pairs:", len(pairs), flush=True)

PORN = ["porn", "pornhub", "xxx", "nude", "sex video", "escort", "call girl", "fuck", "dick", "pussy", "boobs", "anal",
        "\U0001f975", "\U0001f346", "\U0001f351", "\U0001f51e", "\U0001f4a6", "\U0001f445", "\U0001f444", "\U0001f48b"]
HYIP_NAME = ["fundmine", "nnu income", "elint investment", "instant money", "meta web 3", "making legit money",
             "earning opportunity", "online earning platform", "social trust funds", "high income skills",
             "fortk nocks", "mallam zaachi"]
INVEST_SCAM = ["bitcoin investment", "bitcoin options trade", "forex investment", "crypto investment", "altran",
               "double your bitcoin", "binary options investment"]
INVEST_EXACT = {"investment", "investments", "forex investment group"}

def liveness(code):
    try:
        r = requests.get("https://chat.whatsapp.com/" + code,
                          headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}, timeout=25)
        m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', r.text) or \
            re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:title"', r.text)
        return html.unescape(m.group(1)).strip() if m else ""
    except Exception as e:
        return "TRANSPORT:" + type(e).__name__

def category_for(name):
    n = (name or "").lower()
    if any(k in n for k in ["job", "career"]): return "Jobs"
    if any(k in n for k in ["forex", "binary", "signal", "fx", "trading", "trade"]): return "Finance"
    if any(k in n for k in ["crypto", "bitcoin", "web 3", "web3"]): return "Crypto"
    if "invest" in n: return "Finance"
    if any(k in n for k in ["fifa", "world cup", "sport", "cricket", "rugby", "football", "soccer"]): return "Sports"
    if any(k in n for k in ["game", "gamer", "gaming"]): return "Gaming"
    if any(k in n for k in ["tiktok", "talk show", "entertain", "video"]): return "Entertainment"
    if any(k in n for k in ["funny", "joke", "meme"]): return "Funny"
    if any(k in n for k in ["bilal", "islam", "quran", "muslim"]): return "Islamic"
    if any(k in n for k in ["travel", "immigrat", "visa"]): return "Travel"
    if any(k in n for k in ["shop", "store", "fashion", "buy", "sell"]): return "Buy-Sell"
    if any(k in n for k in ["ad", "marketing", "business", "neolife", "solar", "company"]): return "Business"
    if any(k in n for k in ["girl", "boy", "friend", "dating", "chat"]): return "Friendship"
    if "news" in n: return "News"
    return "Regional"

def description_for(name, cat):
    return ("Join the %s WhatsApp group in South Africa for %s updates, discussions and networking with people across the country."
            % (name, cat.lower()))

verified, pending = [], []
seen = set()
porn_drops = hyip_drops = dup_drops = 0
for name, code in pairs:
    name = (name or "").strip() or None
    if code in union or code in seen:
        dup_drops += 1
        continue
    seen.add(code)
    if code in cache:
        outcome = cache[code]
    else:
        low = (name or "").lower()
        if any(p in low for p in PORN):
            outcome = {"st": "porn"}
        elif any(h in low for h in HYIP_NAME):
            outcome = {"st": "hyip"}
        else:
            title = liveness(code)
            time.sleep(0.7)
            if title.startswith("TRANSPORT:"):
                outcome = {"st": "pending"}
            elif not title:
                outcome = {"st": "dead"}
            elif any(p in title.lower() for p in PORN):
                outcome = {"st": "porn"}
            elif any(k in title.lower() for k in INVEST_SCAM) or title.lower().strip() in INVEST_EXACT:
                outcome = {"st": "hyip", "title": title}
            else:
                outcome = {"st": "ok", "title": title}
        cache[code] = outcome
        json.dump(cache, open(CACHE, "w"))
    st = outcome["st"]
    if st == "ok":
        title = outcome["title"]
        final_name = name or title
        cat = category_for(final_name)
        verified.append({"name": final_name, "category": cat, "country": "ZA",
                         "description": description_for(final_name, cat),
                         "invite": "https://chat.whatsapp.com/" + code, "image": ""})
        print("OK", cat, final_name, "->", title, flush=True)
    elif st == "pending":
        final_name = name or code
        cat = category_for(final_name)
        pending.append({"name": final_name, "category": cat, "country": "ZA",
                        "description": description_for(final_name, cat),
                        "invite": "https://chat.whatsapp.com/" + code, "image": "",
                        "note": "transport failure"})
        print("PENDING", code, flush=True)
    else:
        if st == "porn":
            porn_drops += 1
        if st == "hyip":
            hyip_drops += 1
        print(st.upper(), code, name or "", flush=True)

json.dump(verified, open(os.path.join(WAVE_DIR, "team34-southafrica.json"), "w"), ensure_ascii=False, indent=1)
if pending:
    json.dump(pending, open(os.path.join(WAVE_DIR, "team34-unverified-pending.json"), "w"), ensure_ascii=False, indent=1)
print("VERIFIED:", len(verified), "PENDING:", len(pending), "PORN:", porn_drops,
      "HYIP:", hyip_drops, "DUP:", dup_drops, flush=True)
