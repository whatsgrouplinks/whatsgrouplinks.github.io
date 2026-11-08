#!/usr/bin/env python3
"""Team 08 finalize: rebuild the 3 output files from the harvest log (partial bank)."""
import json, re, time

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
ALLOWED_CATS = {"Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health",
    "Business","Gaming","Friendship","Community & Social","Online Earning","Crypto","Cooking",
    "Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell","Finance","Funny"}
ADULT_EMOJI = ["🥵","🍆","🍑","🔞","💦","👅","👄","💋"]

candidates = json.load(open(BASE + "team08-candidates.json"))
new_leads = json.load(open(BASE + "team08-newleads.json"))
union = set(json.load(open(BASE + "dedupe_union.json")))

def unescape_u(s):
    # turn literal \uXXXX sequences into real chars, leave everything else intact
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)

def log(msg):
    print(msg, flush=True)

# category/country inference (same as harvester) for pending records
CAT_KW = [
    (r"scholarship", "Scholarship"), (r"study abroad|study-abroad", "Scholarship"),
    (r"crypto|bitcoin|binance|usdt|forex trad", "Crypto"),
    (r"online earning|earn money|earning|make money|earning app", "Online Earning"),
    (r"freelance|fiverr|upwork", "Freelance"),
    (r"real estate|property|plot|house for sale", "Real Estate"),
    (r"buy.?sell|buy and sell|shopping|buying selling", "Buy & Sell"),
    (r"stock market|finance|investment|invest", "Finance"),
    (r"islamic|quran|muslim|tabligh|religious|naat|madrasa", "Islamic"),
    (r"poetry|shayari|shayri|urdu poetry|punjabi poetry", "Poetry"),
    (r"cooking|recipe|food", "Cooking"), (r"travel|tourism|tour", "Travel"),
    (r"health|fitness|medical|doctor", "Health"),
    (r"technology|tech |programming|coding|software", "Technology"),
    (r"university|college|school|education|study|exam|coaching|student|admission|bank exam|kota", "Education"),
    (r"job|career|govt|government job|hiring|vacancy", "Jobs"),
    (r"cricket|football|soccer|sports|ipl|psl|fifa", "Sports"),
    (r"pubg|free fire|gaming|game|bgmi|esports", "Gaming"),
    (r"movie|film|music|song|entertainment|netflix|bollywood|hollywood|tamil movie", "Entertainment"),
    (r"news|breaking", "News"), (r"funny|joke|joker|meme|comedy", "Funny"),
    (r"girl|friendship|friend|socialite|dating", "Friendship"),
    (r"business", "Business"), (r"community|social", "Community & Social"),
]
def infer_category(ctx):
    t = (ctx or "").lower()
    for pat, cat in CAT_KW:
        if re.search(pat, t):
            return cat
    return "Community & Social"
COUNTRY_KW = [
    ("pakistan|pakistani|lahore|karachi|punjabi|urdu|sindh", "PK"),
    ("india|indian|kerala|tamil|kota", "IN"), ("nigeria|nigerian", "NG"),
    ("kenya|kenyan", "KE"), ("ghana", "GH"), ("south africa|south-africa", "ZA"),
    ("sri lanka|sri-lanka", "LK"), ("bangladesh|bangladeshi", "BD"),
    ("saudi|riyadh|jeddah", "SA"), ("uae|dubai|emirates|abu dhabi", "AE"),
    ("egypt|egyptian|cairo", "EG"), ("indonesia|indonesian", "ID"),
    ("philippines|filipino", "PH"), ("vietnam|vietnamese", "VN"),
    ("malaysia|malaysian", "MY"), ("tanzania", "TZ"), ("zimbabwe", "ZW"),
    ("kuwait", "KW"), ("algeria", "DZ"), ("bahrain", "BH"), ("iraq", "IQ"),
    ("yemen", "YE"), ("nepal", "NP"), ("turkey|turkish", "TR"),
]
def infer_country(ctx):
    t = (ctx or "").lower()
    for pat, cc in COUNTRY_KW:
        if re.search(pat, t):
            return cc
    return "International"

verified = {}
pending = {}
live_re = re.compile(r"LIVE '(.*)' cat=(.+) cc=(\S+) code=([A-Za-z0-9]{22})")
pend_re = re.compile(r"PENDING transport ([A-Za-z0-9]{22})")
checked = set()
for line in open(BASE + "team08-harvest-log.txt", encoding="utf-8", errors="ignore"):
    m = live_re.search(line)
    if m:
        name, cat, cc, code = m.groups()
        name = unescape_u(name)
        checked.add(code)
        if code in verified:
            continue
        verified[code] = {"name": name, "category": cat, "country": cc,
            "description": f"Join {name}, a WhatsApp group listed under {cat}. Connect with members, share updates and stay in touch with the community.",
            "invite": f"https://chat.whatsapp.com/{code}", "image": ""}
        continue
    m2 = pend_re.search(line)
    if m2:
        code = m2.group(1)
        checked.add(code)
        if code in verified or code in pending:
            continue
        ctx = candidates.get(code, {}).get("ctx", "")
        cat = infer_category(ctx); cc = infer_country(ctx)
        pending[code] = {"name": "Pending group", "category": cat, "country": cc,
            "description": "Join this WhatsApp group listed under " + cat + ".",
            "invite": f"https://chat.whatsapp.com/{code}", "image": "", "reason": "transport"}
        continue
    m3 = re.search(r"code=([A-Za-z0-9]{22})", line)
    if m3 and ("DEAD" in line or "DROP" in line):
        checked.add(m3.group(1))

# screening: drop scam/illicit + degenerate names; fix mis-inferred categories
DROP_NAME_SUB = ["pearlvine", "virus_data_hack", "virus_data_heck"]
CAT_FIX = {"Pocket option": "Finance", "जय श्री राम": "Community & Social",
           "એજ્યુકેશન ન્યુઝ ગ્રુપ 47": "Education"}
for code, rec in list(verified.items()):
    nl = rec["name"].lower()
    if any(s in nl for s in DROP_NAME_SUB) or rec["name"].strip() == "...":
        del verified[code]
        continue
    if rec["name"] in CAT_FIX:
        rec["category"] = CAT_FIX[rec["name"]]
        rec["description"] = (f"Join {rec['name']}, a WhatsApp group listed under "
                              f"{rec['category']}. Connect with members, share updates and stay in touch with the community.")

# validation
bad = []
for code, rec in list(verified.items()):
    if code in union:
        bad.append(("in-union", code)); del verified[code]
    elif rec["category"] not in ALLOWED_CATS:
        bad.append(("bad-cat", code, rec["category"])); del verified[code]
    elif any(e in rec["name"] for e in ADULT_EMOJI):
        bad.append(("adult-emoji", code)); del verified[code]
    elif not re.fullmatch(r"[A-Za-z0-9]{22}", code):
        bad.append(("bad-code", code)); del verified[code]
assert len(set(verified)) == len(verified)
# a code pending in phase 1 then verified live on re-check: verified wins
for _c in list(set(verified) & set(pending)):
    del pending[_c]

verified_sorted = sorted(verified.values(), key=lambda x: x["invite"])
pending_sorted = sorted(pending.values(), key=lambda x: x["invite"])
leads_out = [{"url": d["url"], "source": d["source"]} for d in new_leads[:300]]
# leads: listing pages only, never invite urls
leads_out = [l for l in leads_out if "chat.whatsapp.com" not in l["url"]]

def write_json_retry(path, data):
    txt = json.dumps(data, ensure_ascii=False, indent=1)
    for i in range(6):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            return True
        except Exception as e:
            print(f"WRITE RETRY {i} {path}: {e}", flush=True)
            time.sleep(2)
    return False

write_json_retry(BASE + "team08-leads-harvest-h.json", verified_sorted)
write_json_retry(BASE + "team08-leads-harvest-h-pending.json", pending_sorted)
write_json_retry(BASE + "team08-leads-harvest-h-leads.json", leads_out)
log(f"FINALIZE checked={len(checked)} verified={len(verified_sorted)} pending={len(pending_sorted)} leads={len(leads_out)} bad_dropped={bad}")
from collections import Counter
log("cats: " + json.dumps(Counter(r['category'] for r in verified_sorted), ensure_ascii=False))
log("countries: " + json.dumps(Counter(r['country'] for r in verified_sorted), ensure_ascii=False))
log("remaining_unchecked_candidates=" + str(len(candidates) - len(checked)))
