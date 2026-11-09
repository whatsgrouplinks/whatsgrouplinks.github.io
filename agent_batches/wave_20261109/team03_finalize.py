#!/usr/bin/env python3
"""Team 03 finalize: screen live codes, categorize, write candidates/pending/leads/summary."""
import json, re, html

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
CATS = ["Gaming", "Education", "Online Earning", "Community & Social", "Business",
        "Friendship", "Finance", "Buy Sell", "Islamic", "Entertainment", "Jobs",
        "Technology", "Funny", "Sports", "Health", "News"]

fresh = {r["code"]: r for r in json.load(open(f"{WAVE}/team03-fresh.json"))}
ver = json.load(open(f"{WAVE}/team03-verify.json"))
raw = json.load(open(f"{WAVE}/team03-raw.json"))
discovered = json.load(open(f"{WAVE}/team03-discovered-leads.json"))

PHONE_RE = re.compile(r'\+?\d[\d\s\-()]{7,}\d')
URL_RE = re.compile(r'https?://\S+|www\.\S+')
SRC_RE = re.compile(r'(?i)\b(groupsinvite|groupchatconnect|groupsor|groupjoin|ongrupos|whatsapp group invite link|group/channel chat invite)\b')
PROHIB_RE = re.compile(r'[^.!?\n]*(not allowed|prohibit|na\s*karein|don\'?t\s+share|do\s+not\s+share|no\s+porn|no\s+xxx|strictly\s+prohibited|not\s+share|allowed\s+nahi|mana\s+hai|DILARANG\s+SHARE[^.!?\n]*pronO|DILARANG\s+SPAM)[^.!?\n]*[.!?\n]?', re.I)
DROP_RE = re.compile(r'porn|xxx|sex(y|ual)?|hookup|escort|cam[- ]?girl|camgirl|nude|naked|onlyfans|b[- ]?love|forsage|shey?i\b|airdrop|free\s*money|double\s*your\s*money|desi\s*viral', re.I)

AR_COUNTRY = {"مصر": "EG", "عمان": "OM", "الأردن": "JO", "غانا": "GH",
              "الولايات المتحدة": "US", "السعودية": "SA", "اليمن": "YE",
              "فلسطين": "PS", "المغرب": "MA", "الجزائر": "DZ", "العراق": "IQ",
              "سوريا": "SY", "لبنان": "LB", "تركيا": "TR", "الهند": "IN",
              "باكستان": "PK", "بنغلاديش": "BD", "إندونيسيا": "ID",
              "ماليزيا": "MY", "نيجيريا": "NG", "كينيا": "KE", "أمريكا": "US",
              "الإمارات": "AE", "قطر": "QA", "الكويت": "KW", "البحرين": "BH",
              "ليبيا": "LY", "تونس": "TN", "السودان": "SD", "الأردن": "JO"}
AR_CAT = {"رياضة": "Sports", "دين": "Islamic", "أعمال": "Business",
          "تعليم": "Education", "أخرى": "Community & Social",
          "ترفيه": "Entertainment", "صحة": "Health", "أخبار": "News",
          "تقنية": "Technology", "زواج": "Friendship", "حب": "Friendship"}

def clean_text(s):
    s = html.unescape(s or "")
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def strip_prohibitions(s):
    return PROHIB_RE.sub(' ', s or '')

def screen_text(name, og, desc):
    t = strip_prohibitions(f"{name} {og} {desc}")
    m = DROP_RE.search(t)
    return m.group(0) if m else None

def parse_gcc(desc):
    cat, ctry = "Community & Social", "IN"
    m = re.search(r'ضمن تصنيف\s+(\S+)\s+من\s+(\S+)', desc or "")
    if m:
        cat = AR_CAT.get(m.group(1), "Community & Social")
        ctry = AR_COUNTRY.get(m.group(2), "IN")
    return cat, ctry

JB_RE = re.compile(r'jb|jual|beli|store|shop|akun|top\s*up|rekber|japost', re.I)

def build_candidate(code, v, r):
    og = clean_text(v["og_title"])
    name = PHONE_RE.sub('', og).strip()
    name = re.sub(r'\s+', ' ', name)
    desc_raw = clean_text(r.get("desc") or "")
    src = r.get("source", "")
    country = "IN"
    category = "Community & Social"
    if src == "groupjoin.link API":
        country = (r.get("country_hint") or "IN").upper() or "IN"
        blob = f"{r.get('name','')} {' '.join(r.get('tags') or [])} {r.get('category_hint','')}"
        if JB_RE.search(blob):
            category = "Buy Sell"
        elif (r.get("category_hint") or "") == "Gaming":
            category = "Gaming"
        elif (r.get("category_hint") or "") == "Business":
            category = "Business"
        elif (r.get("category_hint") or "") == "Online Shopping":
            category = "Buy Sell"
        elif (r.get("category_hint") or "") == "Money":
            category = "Finance"
    elif src == "groupchatconnect.info":
        category, country = parse_gcc(desc_raw)
    elif src == "groupsinvite.link":
        # tags on the page are page-wide (include related groups' tags) — trust the
        # group NAME first, then only the first few tags (the group's own).
        nametags = ((r.get("name") or "") + " " + " ".join((r.get("tags") or [])[:5])).lower()
        if re.search(r'betta|aquarium|fish', nametags):
            category = "Community & Social"
        elif re.search(r'program|coding|developer|software|python|android', nametags):
            category = "Technology"
        elif re.search(r'gaming|game', nametags):
            category = "Gaming"
        country = "IN"
    elif src == "ongrupos.com":
        country = "BR"
        category = "Community & Social"
        if re.search(r'Religiao|religi', desc_raw, re.I):
            category = "Community & Social"

    # description: clean listing desc, strip source boilerplate/phones/urls/prohibitions
    d = strip_prohibitions(desc_raw)
    d = SRC_RE.sub('', d)
    d = URL_RE.sub('', d)
    d = PHONE_RE.sub('', d)
    d = re.sub(r'Welcome to my whatsapp group[^.]*\.\s*Please join my whatsapp group\.?\s*', '', d, flags=re.I)
    d = re.sub(r'\s+', ' ', d).strip(' .')
    # generic boilerplate descs are useless -> build from name/category
    if len(d) < 25 or 'Group/Channel Chat Invite' in d or 'اكتشف أيضاً مجموعات مشابهة' in d:
        d = ""
    if not d:
        d = DESC_FALLBACK.get(code, "")
    # cap to 2 sentences / 300 chars
    sents = re.split(r'(?<=[.!?])\s+', d)
    d = ' '.join(sents[:2])[:300].strip()
    return {"name": name, "category": category, "country": country,
            "description": d, "invite": f"https://chat.whatsapp.com/{code}"}

DESC_FALLBACK = {
    "JnL0OLulKMAC1F1kUYsamm": "A programming club for coders to learn and discuss software development, apps, and gadgets. Members share coding tips, tutorials, and help each other with programming questions.",
    "KQRQHC2c4m01nTthq8ee8R": "A community for betta fish lovers in Delhi to share aquarium care tips, photos, and fishkeeping advice. Members discuss betta breeds, tank setups, and connect with fellow hobbyists.",
    "HUiq1QyHCHy6iyrG8uhrQD": "A fan community for George lovers to share posts, updates, and friendly chats. Members connect over shared admiration and everyday conversation.",
    "L2vcVPSoZ49Jrb7Vyurydg": "An Islamic community for reminders, faith discussions, and encouragement on the path to Paradise. Members share religious posts and support each other in good deeds.",
    "DRrOOLq3nZHGFchajbIvTJ": "A support group for Instagram users to exchange follows, likes, and growth tips. Members help each other grow their accounts and share social media advice.",
    "LDhEl14VtNiJrfSqDrgnjA": "A marketplace for buying and selling game accounts with trusted admin escrow services. Members trade accounts safely and join daily quizzes and giveaways.",
    "Df3wc7lTPXyCFQOlf5ZUys": "A trusted marketplace for buying and selling game accounts with middleman services. Members trade Mobile Legends and Free Fire accounts safely through the store admin.",
    "CitHq1tlP7AJBwaoWRsse5": "A marketplace group for buying and selling game accounts and Android app sets. Members trade accounts, join giveaways, and grow the community together.",
    "BUgjuZlJZwQ098sRu0pGSS": "A buy-and-sell group for game accounts with plenty of stock available. Members can browse account listings and trade with other gamers.",
    "D4MjpIpFsPwCRKDDU2oPhE": "A game account marketplace offering Free Fire and Mobile Legends accounts with quizzes and prizes. Members trade accounts and take part in daily giveaways.",
    "F5EZVqqQSv85a4HldMu3EW": "A game account trading group offering partner and owner slots for account sellers. Members join quizzes and giveaways for Free Fire and Mobile Legends accounts.",
    "DokQLBtzuTaF4JpeGwpLiJ": "A marketplace for buying and selling Mobile Legends accounts with top-up services and admin escrow. Members trade safely using the store's middleman service with clear group rules.",
}

candidates, screened, pending, dead = [], [], [], []
for code, v in ver.items():
    r = fresh[code]
    og = clean_text(v.get("og_title") or "")
    if v.get("http") == 0 or v.get("curl_rc", 0) not in (0,):
        pending.append({"code": code, "invite": f"https://chat.whatsapp.com/{code}",
                        "note": f"transport failure http={v.get('http')} curl_rc={v.get('curl_rc')}",
                        "source": r.get("source"), "listing_url": r.get("listing_url")})
        continue
    if v.get("http") != 200 or not og:
        dead.append({"code": code, "invite": f"https://chat.whatsapp.com/{code}",
                     "http": v.get("http"), "og_title": og, "source": r.get("source"),
                     "listing_url": r.get("listing_url"),
                     "note": "HTTP 200 but og:title empty after 2 spaced retry rounds (WhatsApp generic landing page = revoked/expired invite)"})
        continue
    # source-classified Adult -> drop
    if (r.get("category_hint") or "") == "Adult":
        screened.append({"code": code, "invite": f"https://chat.whatsapp.com/{code}",
                         "og_title": og, "reason": "source-classified Adult (groupjoin category=Adult, nsfw=1)",
                         "source": r.get("source")})
        continue
    hit = screen_text(r.get("name") or "", og, r.get("desc") or "")
    if hit:
        screened.append({"code": code, "invite": f"https://chat.whatsapp.com/{code}",
                         "og_title": og, "reason": f"screen keyword: {hit}",
                         "source": r.get("source")})
        continue
    if len(re.sub(r'[^\w]', '', og, flags=re.UNICODE)) < 2:
        screened.append({"code": code, "invite": f"https://chat.whatsapp.com/{code}",
                         "og_title": og, "reason": "junk og:title", "source": r.get("source")})
        continue
    candidates.append(build_candidate(code, v, r))

# leads: discovered, annotate channel-only ones
leads = []
for l in discovered:
    item = {"url": l["url"], "source": l["source"]}
    if "/channel/" in l["url"]:
        item["note"] = "channel-only page (verified Nov 9: WhatsApp/Telegram channel, no group invite)"
    leads.append(item)

json.dump(candidates, open(f"{WAVE}/team03-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{WAVE}/team03-pending.json", "w"), ensure_ascii=False, indent=1)
json.dump(leads, open(f"{WAVE}/team03-leads.json", "w"), ensure_ascii=False, indent=1)
json.dump(dead, open(f"{WAVE}/team03-dead.json", "w"), ensure_ascii=False, indent=1)
json.dump(screened, open(f"{WAVE}/team03-screened.json", "w"), ensure_ascii=False, indent=1)

from collections import Counter
print("candidates:", len(candidates))
for c in candidates:
    print(" -", c["category"], c["country"], "|", c["name"][:50], "|", c["invite"])
print("screened dropped:", len(screened), [s["code"] for s in screened])
print("pending:", len(pending), "| dead:", len(dead), "| leads:", len(leads))

summary = {
    "team": "team03",
    "slice": "leads_slice_03.json (184 listing URLs)",
    "sources": {"groupsinvite.link": 93, "groupchatconnect.info": 63,
                "ongrupos.com": 24, "groupjoin.link API (team04-page2)": 4},
    "listings_processed": 184,
    "records_extracted": len(raw),
    "codes_with_invite": sum(1 for r in raw if r.get("code")),
    "dup_codes_skipped": 101,
    "fresh_codes_checked": len(ver),
    "verified": len(candidates),
    "pending": len(pending),
    "leads": len(leads),
    "dead": len(dead),
    "screened_dropped": len(screened),
    "notes": [
        "groupsinvite.link: detail page has no invite; real code is on /group/rules/<slug>/ (verified pattern). 1 listing (kdo0bov5zsn7wu9y1s8s0z, Delhi group) has a rules page with NO join link at all = dead listing.",
        "groupchatconnect.info: two join flows exist — /go/<token> (token IS the invite code) and /go.php?id=N -> /join.php?id=N -> groupsor.link /group/join/<token> -> /group/rules/<token> (token == code, verified on 7 pages). 9 go.php groupe pages recovered; for 266/368 the groupsor rules page returned empty bodies repeatedly, so the token was used as the code (pattern verified on siblings; WhatsApp check arbitrated — both 266/368 came back dead/empty, so no harm).",
        "groupchatconnect.info /channel/* (16 of 63): ALL verified channel-only pages (WhatsApp/Telegram channels, no group invite) — excluded, annotated in leads file.",
        "ongrupos.com: path segment IS the invite code; /join-group/<code> 301s to chat.whatsapp.com/<code>. All 18 fresh ongrupos codes dead (200 + empty og:title after retries).",
        "groupjoin.link API: link field carries chat.whatsapp.com/invite/<code>; 60 rows from 4 tag pages, 51 fresh, 10 live.",
        "Verification: curl slow checker, max 3 parallel, >=0.6s gap. 15 live first pass; 107 ambiguous (HTTP 200 + empty og:title = WhatsApp generic landing page) retried twice spaced 60s/120s — 0 resolved, all marked dead. 0 transport failures, 0 non-200.",
        "Screen: 3 live codes dropped — all source-classified Adult by groupjoin (category=Adult, nsfw=1): Chtsx36WdKxH1jRW83xkkY (GB ISIANN BY ZEUSS), GHoufrxcM99KD55HPl70Zb (JB ALL GAME NUR4You), G31D9HB13F94AHbbQ6BMez (Viral Videos, PK). nsfw=1 alone did NOT drop others — groupjoin flags most JB trading groups nsfw=1; only the Adult category did. DokQLBtzuTaF4JpeGwpLiJ kept: its desc contains a PROHIBITION sentence against sharing porn ('DILARANG SHARE ... pronO'), stripped per rule.",
        "Low yield cause: slice is old listings (groupjoin rows created 2024, updated Sep 2025; groupsinvite/ongrupos slugs old) — most invites revoked/expired, not a checker fault: live titles were returned steadily through the run (2,2,2,6,9,15) and manual curl spot-checks returned the same empty-title generic page.",
        "Discovered leads: 571 new listing URLs (groupsinvite related groups, GCC related groupes, ongrupos related grupos); channel URLs annotated channel-only.",
    ],
}
json.dump(summary, open(f"{WAVE}/team03-summary.json", "w"), ensure_ascii=False, indent=1)
print("summary written")
