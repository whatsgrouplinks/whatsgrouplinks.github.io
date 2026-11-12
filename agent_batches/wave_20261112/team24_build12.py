"""Team24 wave 20261112: build output files from verification checkpoints.
- candidates: live fresh codes -> schema items (name from og:title if empty,
  category/country mapped from page slug + name; 'Online Earning' -> Finance)
- pending: transport codes (fresh + none from yesterday: all 7 old pending died)
- leads: [] (all 357 listing pages mined; nagercoil retried OK)
- summary: counts, exclusions, dead list, resume point.
"""
import json, re, html, os

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
INV = "https://chat.whatsapp.com/"

CATEGORIES = ["Education", "Entertainment", "Jobs", "Community & Social", "Sports",
              "Funny", "Islamic", "Health", "Finance", "News", "Buy & Sell",
              "Friendship", "Gaming", "Technology", "Business", "Cooking",
              "Crypto", "Real Estate", "Poetry"]

# slug keyword -> (category, country) hints; checked in order
SLUG_RULES = [
    (r'jobs?', "Jobs", ""),
    (r'news|newspaper', "News", ""),
    (r'islamic|quran|qadri|shyam|khatu|peer-', "Islamic", ""),
    (r'stock|forex|trading|invest|mutual|fund|bank-nifty|finance|loan|earning', "Finance", ""),
    (r'real-estate|property|jewellery|diamond|wholesale|marketplace|reseller', "Buy & Sell", ""),
    (r'cricket|football|fifa|ipl|pubg|free-fire|fortnite|gaming|chess|fans', "Sports", ""),
    (r'study|exam|ielts|upsc|tnpsc|ssc|cbse|ignou|school|college|university|learning|english', "Education", ""),
    (r'friends?|friendship', "Friendship", ""),
    (r'crypto|nft|bitcoin', "Crypto", ""),
    (r'health|doctor|dental|medical|yoga|meditation|fitness', "Health", ""),
    (r'technology|ai-|artificial-intelligence|blogg|ui-ux|video-editing|photography', "Technology", ""),
    (r'business|freelanc|blogger', "Business", ""),
    (r'cooking|food', "Cooking", ""),
    (r'poetry|shayari|status', "Poetry", ""),
    (r'funny|stickers|memes|jokes|time-pass|good-night', "Funny", ""),
    (r'study-govt-job', "Jobs", ""),
]
COUNTRY_SLUGS = {
    "brunei": "BN", "vdm": "", "spoken-english": "", "welding-jobs": "",
    "gabon": "GA", "mali": "ML", "colombia": "CO", "aruba": "AW",
    "philippines": "PH", "barbados": "BB", "martinique": "MQ", "uganda": "UG",
    "belarus": "BY", "libya": "LY", "luxembourg": "LU", "hungary": "HU",
    "mongolia": "MN", "comoros": "KM", "italy": "IT", "cameroon": "CM",
    "malawi": "MW", "japan": "JP", "uk-muslim": "GB", "monaco": "MC",
    "nauru": "NR", "latvia": "LV", "lithuania": "LT", "romania": "RO",
    "fiji": "FJ", "eritrea": "ER", "argentina": "AR", "portugal": "PT",
    "tonga": "TO", "cuba": "CU", "morocco": "MA", "puerto-rico": "PR",
    "california": "US", "texas": "US", "somalia": "SO", "malta": "MT",
    "finland": "FI", "burkina-faso": "BF", "liechtenstein": "LI", "chad": "TD",
    "poland": "PL", "kuwait": "KW", "nicaragua": "NI", "haitian": "HT",
    "anguilla": "AI", "paraguay": "PY", "kyrgyzstan": "KG", "lebanon": "LB",
    "uruguay": "UY", "andorra": "AD", "zambia": "ZM", "mayotte": "YT",
    "benin": "BJ", "tanzania": "TZ", "germany": "DE", "georgia": "GE",
    "czech-republic": "CZ", "serbia": "RS", "singapore": "SG", "nepal": "NP",
    "kiribati": "KI", "liberia": "LR", "angola": "AO", "taiwan": "TW",
    "jamaica": "JM", "brazil": "BR", "qatar": "QA", "sri-lanka": "",
    "thailand": "TH", "toronto": "CA", "canada": "CA", "usa": "US",
    "ukraine": "UA", "ireland": "IE", "europe": "", "african": "",
    "kenyans-in-usa": "US", "saudi-arabia": "SA", "uae": "AE", "dubai": "AE",
    "sharjah": "AE", "ajman": "AE", "abu-dhabi": "AE", "doha": "QA",
    "riyadh": "SA", "karachi": "PK", "ary-news": "PK", "aaj-tak": "IN",
    "bihar": "IN", "assam": "IN", "kerala": "IN", "tamil": "IN",
    "karnataka": "IN", "maharashtra": "IN", "rajasthan": "IN", "gujarat": "IN",
    "delhi": "IN", "mumbai": "IN", "chennai": "IN", "kolkata": "IN",
    "hyderabad": "IN", "pune": "IN", "lucknow": "IN", "bhopal": "IN",
    "indore": "IN", "patna": "IN", "agra": "IN", "dehradun": "IN",
    "chandigarh": "IN", "coimbatore": "IN", "madurai": "IN", "salem": "IN",
    "erode": "IN", "nagercoil": "IN", "kanyakumari": "IN", "palakkad": "IN",
    "malappuram": "IN", "ernakulam": "IN", "than javur": "IN", "thanjavur": "IN",
    "sangli": "IN", "vadodara": "IN", "ahmedabad": "IN", "rajkot": "",
    "raipur": "IN", "bhubaneswar": "IN", "tripura": "IN", "mizoram": "IN",
    "sydney": "AU", "adelaide": "AU", "new-york": "US", "birmingham": "GB",
    "liverpool": "GB", "london": "GB", "barcelona": "ES", "gibraltar": "GI",
    "panama": "PA", "zimbabwe": "ZW", "harare": "ZW", "johannesburg": "ZA",
    "sri-city": "IN", "noida": "IN", "gurgaon": "IN", "jaipur": "IN",
    "amritsar": "IN", "kishangarh": "IN", "muzaffarnagar": "IN", "agra": "IN",
    "jamaica": "JM", "bangalore": "IN", "aurangabad": "IN", "chhattisgarh": "IN",
    "jharkhand": "IN", "west-bengal": "IN", "tamilnadu": "IN", "karnataka": "IN",
    "andhra": "IN", "telangana": "IN", "odisha": "IN", "goa": "IN",
    "haryana": "IN", "punjab": "IN", "up-": "IN", "bihar": "IN",
}

def slug_of(page):
    return page.rstrip('/').split('/')[-1].replace('-whatsapp-group-links', '').replace('-whatsapp-group-link', '').replace('-group-links', '').replace('-whatsapp-grupas-linki', '')

def map_cat_country(name, page):
    slug = slug_of(page)
    low = (slug + ' ' + name).lower()
    cat = "Community & Social"
    for pat, c, _ in SLUG_RULES:
        if re.search(pat, low):
            cat = c
            break
    country = ""
    for key, cc in COUNTRY_SLUGS.items():
        if key in slug:
            country = cc
            break
    # name-based overrides
    nl = name.lower()
    if 'news' in nl:
        cat = "News"
    if 'job' in nl:
        cat = "Jobs"
    if 'quran' in nl or 'islamic' in nl:
        cat = "Islamic"
    return cat, country

def clean_title(t):
    t = html.unescape(t).strip()
    t = re.sub(r'\s+', ' ', t)
    return t[:140]

def build():
    fresh = json.load(open(W + "team24_fresh12.json"))
    ver = json.load(open(W + "team24_verify_fresh12.json"))
    pending_recheck = json.load(open(W + "team24_pending_recheck.json"))
    mined = json.load(open(W + "team24_mined12.json"))
    leads_in = json.load(open(PREV + "team24-whtspgrouplink-leads.json"))

    candidates, pending, dead, exclusions = [], [], [], []
    seen_codes = set()
    for code, v in ver.items():
        st = v["status"]
        name = clean_title(v.get("og_title") or "") or v.get("name", "")
        page = v.get("page", "") or fresh.get(code, {}).get("page", "")
        if st == "live":
            if code in seen_codes:
                continue
            seen_codes.add(code)
            cat, country = map_cat_country(name, page)
            desc = f"Join {name}, a WhatsApp group listed under {cat}."
            # screen
            nl = name.lower()
            if any(b in nl for b in ["porn", "xxx", "sex", "call girl", "escort", "hentai",
                                     "brazzers", "desi bhabhi", "hookup", "sexual home"]):
                exclusions.append({"code": code, "name": name, "reason": "adult/porn screen"})
                continue
            if any(b in nl for b in ["airdrop", "binary option", "paid hack", "venda de xit",
                                     "betting", "ai trading", "daily profit"]):
                exclusions.append({"code": code, "name": name, "reason": "scam screen"})
                continue
            candidates.append({"name": name, "category": cat, "country": country,
                               "description": desc, "invite": INV + code})
        elif st == "transport":
            cat, country = map_cat_country(name, page)
            pending.append({"name": name, "category": cat, "country": country,
                            "description": f"Join {name}, a WhatsApp group listed under {cat}.",
                            "invite": INV + code,
                            "reason": f"transport failure: {v.get('error','')} (http {v.get('http','')}) after 3 spaced attempts; WhatsApp 429 throttling"})
        else:
            dead.append(code)
    # old pending re-check: all 7 dead
    old_dead = [c for c, v in pending_recheck.items() if v["status"] == "dead"]
    old_live = [c for c, v in pending_recheck.items() if v["status"] == "live"]
    old_tr = [c for c, v in pending_recheck.items() if v["status"] == "transport"]

    mined_urls = sorted("https://whtspgrouplink.com/" + fn[:-5] + "/" for fn in mined)
    mined_set = set(mined)
    unmined = []
    for url in leads_in:
        slug = url.rstrip('/').split('/')[-1] + ".html"
        if slug not in mined_set:
            unmined.append(url)

    json.dump(candidates, open(W + "team24-whtspgrouplink-candidates.json", "w"), indent=1, ensure_ascii=False)
    json.dump(pending, open(W + "team24-whtspgrouplink-pending.json", "w"), indent=1, ensure_ascii=False)
    json.dump(unmined, open(W + "team24-whtspgrouplink-leads.json", "w"), indent=1, ensure_ascii=False)

    summary = {
        "team": 24,
        "slice": "whtspgrouplink.com",
        "wave": "20261112",
        "sources": mined_urls,
        "verified": len(candidates),
        "pending": len(pending),
        "leads": len(unmined),
        "dead": len(dead) + len(old_dead),
        "dead_codes_fresh": dead,
        "dead_codes_old_pending": old_dead,
        "transport_codes_fresh": [p["invite"].split("/")[-1] for p in pending],
        "old_pending_recheck": {"live": old_live, "dead": old_dead, "transport": old_tr},
        "exclusions": exclusions,
        "resume": ("All 357 listing pages mined; no unmined pages remain in this slice. "
                   + (f"Re-check {len(pending)} pending transport code(s) next wave (spaced, quiet window): " +
                      ", ".join(p["invite"].split('/')[-1] for p in pending) + ". " if pending else "No pending codes. ")
                   + "Next slice: fresh whtspgrouplink sitemap pages not yet mined by any team."),
        "notes": (
            "Mined 357/357 listing pages (4 Nov-11 failed-fetch pages brunei/vdm/spoken-english/welding-jobs all fetched OK; "
            "nagercoil failed once with RemoteDisconnected, retried OK). Extracted 6,813 unique invite codes; 6,790 already in the "
            "112,070-code union; only 23 fresh. Fresh verification (requests Session keep-alive, 3 spaced attempts): 0 live, 17 dead "
            "(HTTP 200 + empty og:title), 6 transport (HTTP 429 throttling at the tail of the run). Old Nov-11 pending re-check: all 7 "
            "codes now resolve HTTP 200 + empty og:title = DEAD (yesterday's transport failures were throttling, not live groups). "
            "Controls: known-live KrDwdK8EIkB6vgauHg5M7N -> live with og:title; fabricated ZZZZZZZZZZZZZZZZZZZZZZ -> dead. "
            "CALIBRATION FINDING: og:description is ALWAYS the generic 'WhatsApp Group Invite' even for dead/fabricated codes, so it "
            "must NOT be used as a live fallback — LIVE = non-empty og:title only. The first control run false-flagged the fabricated "
            "code via the description fallback; verifier fixed before any real checks. No live item triggered adult/scam screens "
            "(0 live, so 0 exclusions). Pages viber-group-links / discord-group-links / snapchat-group-links / wechat-group-links / "
            "zalo-group-links yielded 0-7 WhatsApp codes (mostly non-WhatsApp listings). '1000-members' page alone added 124 codes."
        ),
    }
    json.dump(summary, open(W + "team24-whtspgrouplink-summary.json", "w"), indent=1, ensure_ascii=False)
    print(f"verified={len(candidates)} pending={len(pending)} leads={len(unmined)} dead_fresh={len(dead)} dead_old={len(old_dead)} exclusions={len(exclusions)}")

if __name__ == "__main__":
    build()
