#!/usr/bin/env python3
"""Team 02 wave 20261110 slice 2 finalize: screen live codes, build the four
output files. Writes ONLY into wave_20261110."""
import json, re, html

WAVE10 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
WAVE09 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"

ex = {x["code"]: x for x in json.load(open(f"{WAVE10}/team02-extracted.json"))}
vf = {x["code"]: x for x in json.load(open(f"{WAVE10}/team02-verify.json"))}
problems = json.load(open(f"{WAVE10}/team02-fetch-problems.json"))
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
existing_lower = {c.lower() for c in existing}
slice_urls = {x["url"] for x in json.load(open(f"{WAVE09}/leads_slice_02.json"))}

SCAM_PATTERNS = [
    r"b[\s\-]?love", r"forsage", r"sheyi", r"airdrop", r"paypal loader",
    r"bitfinex", r"counterfeit currency", r"crypto[\s\-]?doubling",
    r"double (your|the|bitcoin|crypto|money|investment)", r"carding",
    r"\bmlm\b.*new plan", r"new plan.*\bmlm\b", r"earn.{0,20}(rs\.?|₹|\$|money).{0,20}(daily|per day|double)",
    r"investment.*double", r"free money", r"money (doubling|multiplier)",
    r"fake (currency|note)", r"loader", r"cc (shop|dumps)", r"western union.*hack",
]
ADULT_PATTERNS = [
    r"🔞", r"🥵", r"\bsexy\b", r"hookup", r"\bescort\b", r"\bporn\b", r"\bxxx\b",
    r"18\+.*(sex|sexy|hot|girl|bhabhi|aunty|video call|nude)",
    r"(sex|sexy|hot|nude).*(18\+|🔞)", r"\bhot (girls?|bhabhi|aunty)\b",
    r"\bdesi (sex|porn|mms)\b", r"\bmms\b.*(sex|leak)", r"adult (video|content|group)",
    r"onlyfans", r"\bcam (girl|sex)\b", r"night (fun|sex)",
]

def screen(blob):
    b = blob.lower()
    for p in SCAM_PATTERNS:
        if re.search(p, b):
            return f"scam/phishing signal ({p})"
    for p in ADULT_PATTERNS:
        if re.search(p, b):
            return f"adult-sexual signal ({p})"
    return None

CAT_RULES = [
    ("Jobs", ["job", "vacancy", "vacancies", "career", "employment", "recruit", "hiring", "naukri", "rojgar"]),
    ("Education", ["study", "education", "exam", "ielts", "university", "school", "learn", "course", "tutorial", "student", "coaching", "gk ", "general knowledge"]),
    ("Islamic", ["islam", "islamic", "quran", "qur'an", "muslim", "allah", "namaz", "hadith", "naat", "madrasa"]),
    ("Sports", ["cricket", "football", "sports", "ipl", "match", "e-football", "efootball", "psl"]),
    ("Gaming", ["gaming", "game", "pubg", "free fire", "gamer", "bgmi", "ludo"]),
    ("Funny", ["funny", "joke", "meme", "comedy", "laugh", "humor", "humour"]),
    ("Health", ["health", "fitness", "doctor", "medical", "hospital", "ayurved", "weight loss", "yoga"]),
    ("News", ["news", "breaking", "headlines", "samachar", "khabar"]),
    ("Finance", ["crypto", "bitcoin", "forex", "trading", "invest", "stock", "share market", "earn money", "income", "business idea"]),
    ("Buy Sell", ["buy", "sell", "shopping", "store", "market", "shop", "sale", "price", "order now", "product"]),
    ("Technology", ["tech", "developer", "coding", "programming", "web development", "software", "app", "android", "computer", "python", "javascript"]),
    ("Entertainment", ["movie", "music", "song", "entertainment", "video", "drama", "serial", "film", "bollywood", "status"]),
    ("Business", ["business", "entrepreneur", "startup", "marketing", "digital marketing"]),
]

def categorize(blob):
    b = " " + blob.lower() + " "
    for cat, kws in CAT_RULES:
        for kw in kws:
            if kw in b:
                return cat
    return "Community & Social"

def clean_name(name):
    n = re.sub(r"\s+", " ", name).strip()
    return n[:80]

def clean_description(rec, name, cat):
    d = rec.get("description", "") or ""
    d = html.unescape(d)
    d = re.sub(r"https?://\S+", "", d)
    d = re.sub(r"chat\.whatsapp\.com\S+", "", d)
    d = re.sub(r"\+?\d[\d\s\-]{7,}\d", "", d)  # phone-like numbers
    d = re.sub(r"groupsinvite\.link\S*", "", d, flags=re.I)
    d = re.sub(r"Group Description:\s*", "", d)
    d = re.sub(r"[•\-\*]{2,}", " ", d)
    d = re.sub(r"\s+", " ", d).strip(" .,-")
    # keep at most 2 sentences
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", d) if s.strip()]
    sents = [s for s in sents if len(s) > 12]
    if sents:
        d = " ".join(sents[:2])
        if not d.endswith((".", "!", "?")):
            d += "."
        if len(d) > 280:
            d = d[:277].rsplit(" ", 1)[0] + "."
        return d
    generic = {
        "Technology": f"A community for {name} — members share tech tips, tutorials and help each other with technology topics.",
        "Jobs": f"A group sharing job openings, career updates and employment news for members looking for work.",
        "Education": f"A study group for {name} — members share learning material, exam tips and educational updates.",
        "Islamic": f"A community group for {name} — members share Islamic reminders, learning and discussion.",
        "Sports": f"A sports fans group for {name} — members share match updates, scores and discussion.",
        "Entertainment": f"An entertainment group for {name} — members share videos, music and fun updates.",
        "Community & Social": f"A community group for {name} — members chat, share updates and connect with each other.",
    }
    return generic.get(cat, f"A community group for {name} — members chat, share updates and connect with each other.")

live = [c for c, v in vf.items()
        if v["attempts"][-1]["http"] == "200" and v["attempts"][-1]["og_title"]]
dead_verify = [c for c, v in vf.items() if c not in live
               and v["attempts"][-1]["http"] not in ("ERR", "?", "")]
transport_verify = [c for c, v in vf.items()
                    if v["attempts"][-1]["http"] in ("ERR", "?", "")]

candidates = []
exclusions = []
for code in sorted(live):
    rec = ex[code]
    name = clean_name(vf[code]["attempts"][-1]["og_title"])
    blob = f"{name} {rec['title']} {rec['description']}"
    reason = screen(blob)
    if reason:
        exclusions.append({"code": code, "reason": reason})
        continue
    cat = categorize(blob)
    candidates.append({
        "name": name,
        "category": cat,
        "country": rec["country"],
        "description": clean_description(rec, name, cat),
        "invite": f"https://chat.whatsapp.com/{code}",
    })

pending = []
for p in problems["transport_fail"]:
    pending.append({"url": p["url"], "source": p.get("source", ""),
                    "stage": p.get("stage", ""), "reason": p.get("note", ""),
                    "title": p.get("title", "")})
for code in sorted(transport_verify):
    rec = ex[code]
    pending.append({"code": code, "invite": f"https://chat.whatsapp.com/{code}",
                    "url": rec["listing_url"], "source": rec.get("source", ""),
                    "stage": "verify", "reason": "transport failure (curl error/timeout, no HTTP status)",
                    "title": rec["title"]})

raw_leads = json.load(open(f"{WAVE10}/team02-new-leads-raw.json"))
leads = []
seen = set()
for l in raw_leads:
    u = l["url"]
    lid = u.rstrip("/").split("/")[-1].lower()
    if u in slice_urls or u in seen or lid in existing_lower:
        continue
    seen.add(u)
    leads.append({"url": u, "source": l["source"]})
leads.sort(key=lambda x: x["url"])

json.dump(candidates, open(f"{WAVE10}/team02-leads-slice2.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{WAVE10}/team02-leads-slice2-pending.json", "w"), ensure_ascii=False, indent=1)
json.dump(leads, open(f"{WAVE10}/team02-leads-slice2-leads.json", "w"), ensure_ascii=False, indent=1)

n_new = sum(1 for r in ex.values() if r["status"] == "new")
n_dup = sum(1 for r in ex.values() if r["status"] != "new")
summary = {
    "team": 2,
    "slice": "leads slice 2",
    "sources": ["groupsinvite.link"],
    "verified": len(candidates),
    "pending": len(pending),
    "leads": len(leads),
    "dead": len(dead_verify) + len(problems["dead"]),
    "exclusions": exclusions,
    "resume": "Re-ran wave_20261109 leads_slice_02.json (184 groupsinvite.link listing pages) fresh for wave 20261110: fetched each listing page + its /group/rules/ page, extracted invite codes, deduped against the 108,364-code union (.existing_codes.json + groups.json invites), verified fresh codes with curl (HTTP 200 + non-empty og:title, 2 spaced retries).",
    "notes": (
        f"Fetched 184/184 listing pages. Extracted invite codes from {len(ex)} listings: "
        f"{n_new} fresh vs union, {n_dup} already in union. "
        f"Verified {len(vf)} fresh codes: {len(live)} live, {len(dead_verify)} dead "
        f"(HTTP 200 with empty og:title on all attempts = revoked/expired invites), "
        f"{len(transport_verify)} transport-pending at verify stage. "
        f"{len(problems['dead'])} listings had no invite code on the rules page; "
        f"{len(problems['transport_fail'])} listing/rules fetch transport failures. "
        f"Screened live codes: {len(candidates)} kept, {len(exclusions)} excluded (see exclusions). "
        f"Note: wave-09's 2 live codes (Web development 76CAcBHxNRQ32Fx0oTecPs and the MLM one) are now in the union, so neither is fresh this run. "
        f"Discovered {len(raw_leads)} related listing URLs; {len(leads)} are genuinely new leads after removing slice URLs and ids already in the union. "
        f"No source names/links, phone numbers or personal info in any banked item."
    ),
}
json.dump(summary, open(f"{WAVE10}/team02-leads-slice2-summary.json", "w"), ensure_ascii=False, indent=1)
print(f"verified={len(candidates)} pending={len(pending)} leads={len(leads)} dead={summary['dead']} exclusions={len(exclusions)}")
