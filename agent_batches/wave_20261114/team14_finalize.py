#!/usr/bin/env python3
"""team14 finalize: screen live titles, dedupe vs union AND prior-wave candidates,
categorize, write candidates/leads/pending/summary."""
import json, re, glob, os

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
W13 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UNION = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"

ver = json.load(open(f"{WAVE}/team14-verify-checkpoint.json"))
fetch = json.load(open(f"{WAVE}/team14-fetch-checkpoint.json"))
union = set(json.load(open(UNION)))

# prior banked candidates (wave13 all teams + wave14 files present now)
prior = {}
for p in glob.glob(f"{W13}/*-candidates.json") + glob.glob(f"{WAVE}/*-candidates.json"):
    if "team14-" in p:
        continue
    try:
        data = json.load(open(p))
        for c in data:
            code = c["invite"].rsplit("/", 1)[-1]
            prior.setdefault(code, os.path.basename(p))
    except Exception as e:
        print("skip", p, e)

live = ver["live"]
dead = ver["dead"]
pending = ver["pending"]

# content screen on live og:title
BAD = re.compile(r"(?i)\b(porn|xxx|sexo expl[ií]cito|putas|onlyfans|escort|tigrinho|fortune tiger|sinais|plataformas pagantes|wjbet|casino|slots|apostas|betting|airdrop|free money|dinheiro gr[aá]tis|ganhar dinheiro|renda extra|binary|op[cç][oõ]es bin[aá]rias|binarias)\b")
CLOSED = re.compile(r"(?i)closed group|moved to new group")

excluded = []   # {code, reason}
dupes_union = []
dupes_prior = []
cands = {}      # code -> live record

for code, v in live.items():
    title = v["title"]
    if CLOSED.search(title):
        excluded.append({"code": code, "reason": f"live og:title '{title}' - group closed/moved, not banked"})
        continue
    if BAD.search(title):
        excluded.append({"code": code, "reason": f"live og:title '{title}' - banned content signal"})
        continue
    if code in union:
        dupes_union.append(code)
        continue
    if code in prior:
        dupes_prior.append({"code": code, "reason": f"already banked as candidate in {prior[code]} (wave13)"})
        continue
    cands[code] = v

# also count union dupes among all raw (incl dead, for honest counts)
raw = fetch["raw"]
raw_union_dupes = [c for c in raw if c in union]
raw_prior_dupes = [c for c in raw if c in prior and c not in union]

print(f"live={len(live)} excluded={len(excluded)} dupes_union(live)={len(dupes_union)} "
      f"dupes_prior(live)={len(dupes_prior)} candidates={len(cands)}")
print(f"raw unique={len(raw)} raw in union={len(raw_union_dupes)} raw in prior-only={len(raw_prior_dupes)} "
      f"dead={len(dead)} pending={len(pending)}")
for c in sorted(cands):
    print(" KEEP", c, "|", cands[c]["title"])
for e in excluded:
    print(" EXCLUDED", e)
for d in dupes_prior:
    print(" DUPE-PRIOR", d)

# ---------- categorize ----------
CAT_RULES = [
    (re.compile(r"(?i)language exchange|learn english|business english|english\b.*\b(language|skills)|intercambio de idiomas.*(ingl[eé]s|english)"), "Education"),
    (re.compile(r"(?i)cine|cinema|film|theatre|teatro"), "Entertainment"),
    (re.compile(r"(?i)f[úu]tbol|football|soccer|fc\b"), "Sports"),
    (re.compile(r"(?i)hot ?pot|cooking|cocina|food|comida"), "Cooking"),
    (re.compile(r"(?i)compra y venta|buy ?sell|second hand|segunda mano"), "Buy Sell"),
    (re.compile(r"(?i)\bIA\b|artificial intelligence|inteligencia artificial|techie|technology|microsoft"), "Technology"),
    (re.compile(r"(?i)business|networking|startup|book club|copywrit|marketing|growth minds|funnel|emprend"), "Business"),
    (re.compile(r"(?i)families|familias|conscious families|crianza"), "Community & Social"),
    (re.compile(r"(?i)travel|viajes|wander"), "Travel"),
    (re.compile(r"(?i)health|bienestar|wellbeing|breathing|meditat"), "Health"),
]
SPAIN_WORDS = re.compile(r"(?i)madrid|valencia|barcelona|m[aá]laga|alicante|granada|sevilla|torrevieja|mallorca|palma|espa[nñ]a|catalu|andaluc|tetu[aá]n|tarragona|val[eè]ncia")

def categorize(title, tags):
    text = title + " " + " ".join(tags)
    for rx, cat in CAT_RULES:
        if rx.search(text):
            return cat
    return "Community & Social"

def country_of(title, tags):
    text = title + " " + " ".join(tags)
    if SPAIN_WORDS.search(text):
        return "ES"
    return ""

def clean_name(t):
    return re.sub(r"\s+", " ", t).strip()

DESC_TAIL = {
    "Education": "Practice, learn and share resources with other members.",
    "Entertainment": "Share recommendations, discuss favourites and enjoy the fun together.",
    "Sports": "Follow the game, share news and chat with fellow fans.",
    "Cooking": "Share recipes, tips and foodie finds with fellow members.",
    "Buy Sell": "Buy, sell and swap items with other members in the area.",
    "Technology": "Share news, tips and ideas about technology with other members.",
    "Business": "Network, share opportunities and grow together.",
    "Travel": "Share travel ideas, tips and experiences with fellow travellers.",
    "Health": "Share tips and support for a healthier lifestyle.",
    "Community & Social": "Meet new people, share local plans and stay connected.",
}
def description(name, cat, country):
    base = f"Join {name}, an active WhatsApp group for {cat.lower()}."
    if country == "ES":
        base += " A Spain-based community group."
    return base + " " + DESC_TAIL.get(cat, "Meet new people and stay connected.")

out = []
for code in sorted(cands, key=lambda c: clean_name(cands[c]["title"]).lower()):
    v = cands[code]
    name = clean_name(v["title"])
    cat = categorize(name, v["tags"])
    country = country_of(name, v["tags"])
    out.append({
        "name": name,
        "category": cat,
        "country": country,
        "description": description(name, cat, country),
        "invite": f"https://chat.whatsapp.com/{code}",
    })

json.dump(out, open(f"{WAVE}/team14-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump([], open(f"{WAVE}/team14-leads.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{WAVE}/team14-pending.json", "w"), ensure_ascii=False, indent=1)

fetched_ids = sorted(fetch["done"])
summary = {
    "team": "team14",
    "slice": "whatshub.es sitemap group IDs 801-1600 (460 sitemap ids; all fetched, 0 fetch failures)",
    "sources": [
        "https://www.whatshub.es/sitemap.xml",
        "https://www.whatshub.es/grupo/<id> for all 460 ids in 801-1600",
    ],
    "prior_wave13_team15_note": "wave13 team15 fetched whatshub.es sitemap ids 1-800 (first ~200 pages before throttling); my slice 801-1600 does not overlap it. BUT its related-card mining also surfaced codes from grupo pages outside 1-800, and 27 of my live codes were already banked in wave13 team15-candidates.json - excluded as dupes below (union file does not contain them; flag for coordinator: union appears stale vs wave13 candidates).",
    "controls": {
        "live": "KrDwdK8EIkB6vgauHg5M7N -> og:title 'JAY - PHP & Python Full Stack Developer' (PASS, re-run at each verify pass)",
        "fabricated": "ZzZzZzZzZzZzZzZzZzZzZzZz -> empty og:title after retries (PASS, dead)",
    },
    "counts": {
        "pages_fetched": len(fetched_ids),
        "pages_failed": 0,
        "raw_unique_codes_mined": len(raw),
        "raw_note": "raw counts UNIQUE codes mined from related-group cards (occurrences not tracked); main-group invite is hidden on whatshub.es so codes come from related cards only",
        "verified_live": len(live),
        "candidates": len(out),
        "dupes_vs_union_all_raw": len(raw_union_dupes),
        "dupes_vs_prior_wave_candidates_live": len(dupes_prior),
        "dupes_vs_prior_wave_candidates_all_raw": len(raw_prior_dupes),
        "dead": len(dead),
        "excluded": len(excluded),
        "pending": len(pending),
        "leads": 0,
    },
    "dead_codes": dead,
    "excluded": excluded,
    "dupes_vs_prior_wave_candidates": dupes_prior,
    "dupes_vs_union_live": dupes_union,
    "pending": pending,
    "leads": [],
    "fetch_notes": "requests+proxy failed ~50% wave-wide (ProxyError/ReadTimeout bursts, incl. a stall at id 1049-1050); switched to curl subprocess fetcher which completed all 460 ids with 0 failures. 2.5-5s pauses between pages. One mid-run service restart killed the fetcher; resumed from checkpoint, no data lost.",
    "verify_notes": "One requests.Session (keep-alive) per verify run, browser UA, 60-90s timeout; empty og:title retried 2-3x spaced before dead; 429/transport would be pending (none occurred). 2 dead codes (FCoA50XNMxo0XMSiUv7rPQ, CSZpySWsOGUJwZHiWrDPRh) were also dead in wave13 team15 - consistent. Names are live og:titles (verified group names); categories from tags+title; country ES where Spanish city/region indicated, else empty.",
    "resume_point": "Slice COMPLETE: all 460 sitemap ids 801-1600 fetched, all fresh codes verified. No unfetched ids, no pending codes, no leads to resume.",
}
json.dump(summary, open(f"{WAVE}/team14-summary.json", "w"), ensure_ascii=False, indent=1)
print(f"WROTE candidates={len(out)} leads=0 pending={len(pending)} summary done")
