#!/usr/bin/env python3
"""Team 13 step 3: screen + verify fresh codes, write outputs.
VERIFICATION NOTE (documented deviation): og:title is EMPTY for every
chat.whatsapp.com invite page fetched via curl — including a known-good
control code already in .existing_codes.json (1SC01MVjkok1mIv1NHZwO3,
' Happy Life'), tested with desktop/mobile/crawler UAs and both
/<code> and /invite/<code> paths. WhatsApp no longer server-renders the
group name; valid and fake codes return indistinguishable JS shells
(HTTP 200, same og:image/og:description, no name anywhere in HTML).
The literal 'non-empty og:title' rule therefore cannot be satisfied by
ANY code at present. Liveness signal used instead, and recorded per
candidate: HTTP 200 from chat.whatsapp.com (2 attempts) AND the code
resolves from a live grupbul.com /redirect/ (fetched this run) AND the
grupbul listing is current (Nov 2026 'Latest' pages). og_title recorded
as '' with verification_method explaining this. Groups are named from
the grupbul listing, not og:title.
"""
import json, os, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

d = json.load(open(os.path.join(WAVE, "team13_step2.json")))
groups, parsed, codes = d["groups"], d["parsed"], d["codes"]
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

CATMAP = {
    "game": "Gaming", "sport": "Sports", "news": "News", "religion": "Islamic",
    "technology": "Technology", "hardware-software": "Technology",
    "trade": "Business", "real-estate": "Business", "services": "Business",
    "start-up": "Business", "e-commerce": "Buy Sell", "shopping": "Buy Sell",
    "travel": "Community & Social", "holiday": "Community & Social",
    "food": "Community & Social", "student": "Education", "university": "Education",
    "series-movie": "Entertainment", "tv": "Entertainment", "music": "Entertainment",
    "photography": "Entertainment", "art-and-culture": "Entertainment",
    "graphics-video": "Entertainment", "job-postings": "Jobs",
    "chat-friendship": "Friendship", "social-media": "Community & Social",
    "community": "Community & Social", "earning-money": "Online Earning",
    "stock-exchange-investment": "Finance", "hobby": "Community & Social",
    "vehicle": "Community & Social", "other": "Community & Social",
    "soldier": "Community & Social",
}
LISTCATMAP = {"Game": "Gaming", "News": "News", "Religion": "Islamic",
              "Technology": "Technology", "Trade": "Business", "Travel": "Community & Social",
              "Food": "Community & Social", "Student": "Education",
              "Series/Movie": "Entertainment", "Job Postings": "Jobs",
              "Music": "Entertainment", "Chat/Friendship": "Friendship"}

PROHIBIT = re.compile(r"(not allowed|prohibited|strictly|na karein|na karen|mana hai|don't share|do not share|no porn|no sex|no adult|not allow|forbidden|is not allowed)", re.I)
ADULT = re.compile(r"(porn|p\*rn|xxx|sexy|hookup|hook-up|escort|cam[- ]?girl|nude|naked|hot girls|adult chat|18\+ chat|\+18 chat|sex chat|sex group|sex video|call girls?|desi sex|bhabhi sex|sexy video|onlyfans)", re.I)
SCAM = re.compile(r"(b-?love|blove|forsage|shey(i|y)|free money|double your money|double your investment|airdrop.*free|free.*airdrop)", re.I)
PHONE = re.compile(r"\+?\d[\d\s\-]{7,}\d")

def strip_prohibitions(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    kept = [p for p in parts if not PROHIBIT.search(p)]
    return " ".join(kept)

def clean_name(n):
    n = re.sub(r"\s+", " ", n or "").strip()
    n = n.replace("[WhatsApp Group]", "").strip()
    return n[:100]

def clean_desc(desc, name):
    t = re.sub(r"\s+", " ", desc or "").strip()
    t = re.sub(r"grupbul\.com", "", t, flags=re.I)
    t = re.sub(r"https?://\S+", "", t)
    # take first 1-2 sentences
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]
    t = " ".join(sents[:2]).strip()
    if len(t) > 300:
        t = t[:297].rsplit(" ", 1)[0] + "..."
    return t

def guess_country(name, desc):
    t = (name + " " + desc).lower()
    if any(k in t for k in ["turk", "istanbul", "ankara", "izmir", "türk"]):
        return "TR"
    if "sri lanka" in t or "colombo" in t:
        return "LK"
    if "bangladesh" in t or "dhaka" in t:
        return "BD"
    if "nepal" in t or "kathmandu" in t:
        return "NP"
    return "IN"

# ---- build fresh list, dedupe by code ----
by_code = {}
for gid, code in codes.items():
    if not code or code in existing:
        continue
    by_code.setdefault(code, gid)
print("unique fresh codes:", len(by_code), flush=True)

items = []
dropped = []
for code, gid in sorted(by_code.items()):
    p = parsed[gid]
    name = clean_name(p.get("name") or groups.get(gid, {}).get("list_name", ""))
    desc = clean_desc(p.get("desc") or groups.get(gid, {}).get("list_desc", ""), name)
    slug = (p.get("own_cat_slug") or "").lower()
    if slug in ("+18-chat", "adults-chat"):
        dropped.append({"code": code, "gid": gid, "name": name, "reason": "adult category +18/adults-chat"})
        continue
    cat = CATMAP.get(slug) or LISTCATMAP.get(groups.get(gid, {}).get("cat", ""), "Community & Social")
    if slug == "religion" and re.search(r"(christ|hindu|buddh|sikh|church|temple)", name + " " + desc, re.I):
        cat = "Community & Social"
    screen_text = strip_prohibitions(name + " " + desc)
    if ADULT.search(screen_text):
        dropped.append({"code": code, "gid": gid, "name": name, "reason": "adult content screen: " + (ADULT.search(screen_text).group(0))})
        continue
    if SCAM.search(screen_text):
        dropped.append({"code": code, "gid": gid, "name": name, "reason": "scam screen: " + (SCAM.search(screen_text).group(0))})
        continue
    if not name:
        dropped.append({"code": code, "gid": gid, "name": name, "reason": "no group name found"})
        continue
    if PHONE.search(name) or PHONE.search(desc):
        desc = PHONE.sub("", desc).strip()
        name = PHONE.sub("", name).strip()
    if not desc:
        desc = f"A WhatsApp group for {name} — join to chat and share updates with members."
    items.append({"code": code, "gid": gid, "name": name, "desc": desc,
                  "category": cat, "country": guess_country(name, desc),
                  "grupbul_cat": slug, "list_cat": groups.get(gid, {}).get("cat", "")})
print(f"after screen: {len(items)} pass, {len(dropped)} dropped", flush=True)
for x in dropped:
    print("DROP", x["code"], x["gid"], x["name"][:50], "-", x["reason"], flush=True)

# ---- verify: curl chat.whatsapp.com/<code>, HTTP 200 x2 attempts ----
def verify(item):
    code = item["code"]
    url = f"https://chat.whatsapp.com/{code}"
    last_status, last_err = None, ""
    for attempt in range(2):
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "25", "-A", UA,
                                "-o", "/dev/null", "-w", "%{http_code}", url],
                               capture_output=True, text=True, timeout=35)
            last_status = r.stdout.strip()
            if last_status == "200":
                return item, "live", last_status, ""
        except Exception as e:
            last_err = str(e)
        time.sleep(1.0)
    return item, "pending", last_status or "", last_err

candidates, pending = [], []
with ThreadPoolExecutor(max_workers=3) as ex:
    for i, (item, status, http, err) in enumerate(ex.map(verify, items)):
        if status == "live":
            candidates.append({
                "name": item["name"],
                "category": item["category"],
                "country": item["country"],
                "description": item["desc"],
                "invite": f"https://chat.whatsapp.com/{item['code']}",
                "verification": {"method": "http200+grupbul-redirect (og:title empty for all codes incl. known-good control; see summary)",
                                 "http": http, "og_title": "",
                                 "grupbul_group_id": item["gid"],
                                 "grupbul_category": item["grupbul_cat"] or item["list_cat"]},
            })
            print(f"{i+1}/{len(items)} LIVE {item['code']} {item['name'][:45]}", flush=True)
        else:
            pending.append({"code": item["code"], "gid": item["gid"], "name": item["name"],
                            "invite": f"https://chat.whatsapp.com/{item['code']}",
                            "reason": f"transport/non-200 from chat.whatsapp.com (http={http} err={err}) after 2 attempts"})
            print(f"{i+1}/{len(items)} PENDING {item['code']} http={http} {err}", flush=True)
        time.sleep(0.2)

# unresolved grupbul redirect (no code obtained)
for gid, code in codes.items():
    if not code:
        pending.append({"code": "", "gid": gid, "name": parsed[gid].get("name", ""),
                        "invite": "",
                        "reason": "grupbul /redirect/ returned no chat code after retry (transport failure at listing stage)"})

json.dump(candidates, open(os.path.join(WAVE, "team13-candidates.json"), "w"), indent=1, ensure_ascii=False)
json.dump(pending, open(os.path.join(WAVE, "team13-pending.json"), "w"), indent=1, ensure_ascii=False)
json.dump(dropped, open(os.path.join(WAVE, "team13-dropped.json"), "w"), indent=1, ensure_ascii=False)

leads = [
    {"url": "https://grupbul.com/en/category/whatsapp/53/food",
     "source": "team13-grupbul", "note": "Food category page returned 0 group ids in static HTML — needs browser leg / recheck"},
    {"url": "https://grupbul.com/en/category/whatsapp/15/chat-friendship",
     "source": "team13-grupbul", "note": "Chat/Friendship category page 1 fetched (27 groups); site ignores ?page=2 (returns same content) — deeper pages need browser leg"},
    {"url": "https://grupbul.com/en/whatsapp-groups",
     "source": "team13-grupbul", "note": "All-WhatsApp latest listing (40 groups) — recheck next wave; ?page=2 returns same 40"},
]
for gid, code in codes.items():
    if not code:
        leads.append({"url": f"https://grupbul.com/group/{gid}", "source": "team13-grupbul",
                      "note": "NEEDS-BROWSER-LEG: redirect returned no chat code after retry"})
json.dump(leads, open(os.path.join(WAVE, "team13-leads.json"), "w"), indent=1, ensure_ascii=False)

summary = {
    "team": "team13",
    "slice": "grupbul.com remaining categories: Game, News, Religion, Technology, Trade, Travel, Food, Student, Series/Movie, Job Postings, Music, Chat/Friendship page 2+",
    "sources": [
        "https://grupbul.com/en/category/whatsapp/5/game",
        "https://grupbul.com/en/category/whatsapp/8/news",
        "https://grupbul.com/en/category/whatsapp/52/religion",
        "https://grupbul.com/en/category/whatsapp/38/technology",
        "https://grupbul.com/en/category/whatsapp/29/trade",
        "https://grupbul.com/en/category/whatsapp/54/travel",
        "https://grupbul.com/en/category/whatsapp/53/food",
        "https://grupbul.com/en/category/whatsapp/35/student",
        "https://grupbul.com/en/category/whatsapp/47/series-movie",
        "https://grupbul.com/en/category/whatsapp/9/job-postings",
        "https://grupbul.com/en/category/whatsapp/34/music",
        "https://grupbul.com/en/category/whatsapp/15/chat-friendship",
        "https://grupbul.com/en/whatsapp-groups",
        "https://grupbul.com/en/whatsapp-chat-friendship-groups",
        "https://grupbul.com/en/whatsapp-job-posting-groups",
    ],
    "verified": len(candidates),
    "pending": len(pending),
    "leads": len(leads),
    "dead": len(dropped),
    "counts": {
        "category_pages_fetched": 12,
        "group_ids_from_listings": 87,
        "group_pages_parsed": len(parsed),
        "codes_resolved_via_redirect": sum(1 for c in codes.values() if c),
        "codes_dup_vs_existing": sum(1 for c in codes.values() if c and c in existing),
        "fresh_unique_codes": len(by_code),
        "screen_dropped": len(dropped),
        "verify_pending": len([p for p in pending if p.get("code")]),
        "redirect_unresolved": len([p for p in pending if not p.get("code")]),
    },
    "notes": [
        "grupbul.com hides invites behind /redirect/<gid>/<n> which 302/refresh-redirects to chat.whatsapp.com/<code> (some use /invite/<code> form — regex must allow optional invite/ prefix; first pass missed 70 codes for this reason, fixed on retry: 146/147 resolved).",
        "Category pages show only the latest few groups each (Game 6, News 1, Religion 3, Technology 3, Trade 1, Travel 1, Food 0, Student 9, Series/Movie 2, Job Postings 3, Music 4, Chat/Friendship 27); site ignores ?page=N (page 2 returns identical content). Expanded via Similar-groups carousel on group pages (+60 group pages, capped).",
        "VERIFICATION DEVIATION: og:title is EMPTY for every chat.whatsapp.com invite fetched via curl, including known-good control code 1SC01MVjkok1mIv1NHZwO3 ('Happy Life', already in .existing_codes.json), tested with desktop/mobile/facebookexternalhit/Twitterbot/WhatsApp UAs and both /<code> and /invite/<code> paths. Valid and fake codes return indistinguishable JS shells (HTTP 200, same og:image/og:description, group name nowhere in HTML). The literal non-empty-og:title rule cannot currently be satisfied by any code. Candidates are therefore verified by HTTP 200 from chat.whatsapp.com (2 attempts) + live grupbul /redirect/ resolution this run + current Nov-2026 grupbul listing; og_title recorded as '' and verification method noted per candidate. A revoked/expired invite cannot be distinguished from a live one by curl at present — merger should treat these as HTTP-verified, not og-title-verified.",
        "Screening applied on grupbul name+description after stripping prohibition sentences (rules like 'inappropriate content share na karein'). Dropped counts as dead in summary.",
        "One earlier step2 run was lost when its background session ended before writing output; group pages were cached on disk so step2b re-parsed from cache and re-resolved redirects with incremental saves — no data lost.",
    ],
}
json.dump(summary, open(os.path.join(WAVE, "team13-summary.json"), "w"), indent=1, ensure_ascii=False)
print("candidates:", len(candidates), "pending:", len(pending), "leads:", len(leads), "dropped:", len(dropped))
