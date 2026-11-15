#!/usr/bin/env python3
"""team30: verify mined codes (groupizo fresh + groupda backfill).
Controls first; one requests.Session; 2 workers; 429/transport -> PENDING.
Screen live og:title; name = live og:title; generated descriptions.
Banks progress incrementally; resumable via team30-verify-progress.json.
"""
import json, re, time, sys, os, unicodedata
from concurrent.futures import ThreadPoolExecutor
import requests
from html import unescape

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/"
UNION = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
GENERIC = {"", "whatsapp", "whatsapp group invite", "whatsapp group", "whatsapp group link",
           "join whatsapp group", "whatsapp groups"}

try:
    import pycountry
    def iso(country_name):
        if not country_name:
            return ""
        try:
            return pycountry.countries.lookup(country_name).alpha_2
        except Exception:
            return ""
except Exception:
    _MAP = {"Uganda": "UG", "Indonesia": "ID", "Nigeria": "NG", "India": "IN", "Pakistan": "PK",
            "United States": "US", "South Africa": "ZA", "Kenya": "KE", "Bangladesh": "BD",
            "Nepal": "NP", "Sri Lanka": "LK", "Philippines": "PH", "Malaysia": "MY",
            "Thailand": "TH", "Vietnam": "VN", "Brazil": "BR", "Mexico": "MX", "Colombia": "CO",
            "Argentina": "AR", "Peru": "PE", "Chile": "CL", "Egypt": "EG", "Morocco": "MA",
            "Algeria": "DZ", "Tunisia": "TN", "Ghana": "GH", "Ethiopia": "ET", "Tanzania": "TZ",
            "United Kingdom": "GB", "Germany": "DE", "France": "FR", "Italy": "IT", "Spain": "ES",
            "Portugal": "PT", "Netherlands": "NL", "Turkey": "TR", "Saudi Arabia": "SA",
            "United Arab Emirates": "AE", "Qatar": "QA", "Kuwait": "KW", "Australia": "AU",
            "Canada": "CA", "Japan": "JP", "South Korea": "KR", "China": "CN", "Taiwan": "TW",
            "Hong Kong": "HK", "Singapore": "SG", "Russia": "RU", "Ukraine": "UA", "Romania": "RO",
            "Greece": "GR", "Sweden": "SE", "Norway": "NO", "Denmark": "DK", "Finland": "FI",
            "Ireland": "IE", "Poland": "PL", "Austria": "AT", "Switzerland": "CH", "Belgium": "BE",
            "Zambia": "ZM", "Zimbabwe": "ZW", "Cameroon": "CM", "Senegal": "SN", "Myanmar": "MM",
            "Cambodia": "KH", "Kazakhstan": "KZ", "Uzbekistan": "UZ", "New Zealand": "NZ", "Bahrain": "BH",
            "Jordan": "JO", "Lebanon": "LB", "Iraq": "IQ", "Iran": "IR", "Afghanistan": "AF",
            "Yemen": "YE", "Oman": "OM", "Syria": "SY", "Libya": "LY", "Sudan": "SD",
            "Somalia": "SO", "Mauritania": "MR", "Mali": "ML", "Niger": "NE", "Chad": "TD",
            "Ivory Coast": "CI", "Czech Republic": "CZ", "Czechia": "CZ", "Hungary": "HU",
            "Bulgaria": "BG", "Croatia": "HR", "Serbia": "RS", "Lithuania": "LT", "Latvia": "LV",
            "Estonia": "EE", "Slovakia": "SK", "Slovenia": "SI", "Georgia": "GE", "Armenia": "AM",
            "Azerbaijan": "AZ", "Kyrgyzstan": "KG", "Tajikistan": "TJ", "Turkmenistan": "TM",
            "Mongolia": "MN", "Jamaica": "JM", "Ecuador": "EC", "Bolivia": "BO", "Uruguay": "UY",
            "Paraguay": "PY", "Venezuela": "VE", "Panama": "PA", "Costa Rica": "CR",
            "Guatemala": "GT", "Dominican Republic": "DO", "Cuba": "CU", "Malta": "MT",
            "Cyprus": "CY", "Iceland": "IS", "Luxembourg": "LU", "Albania": "AL",
            "Bosnia and Herzegovina": "BA", "Montenegro": "ME", "North Macedonia": "MK",
            "Moldova": "MD", "Belarus": "BY", "Angola": "AO", "Mozambique": "MZ", "Malawi": "MW",
            "Botswana": "BW", "Namibia": "NA", "Madagascar": "MG", "Mauritius": "MU",
            "Rwanda": "RW", "South Sudan": "SS", "Gabon": "GA", "Lesotho": "LS",
            "Eswatini": "SZ", "Sierra Leone": "SL", "Liberia": "LR", "Guinea": "GN",
            "Benin": "BJ", "Togo": "TG", "Eritrea": "ER", "Djibouti": "DJ",
            "Comoros": "KM", "Seychelles": "SC", "Cape Verde": "CV", "Fiji": "FJ",
            "Trinidad and Tobago": "TT", "Barbados": "BB", "Guyana": "GY", "Haiti": "HT",
            "Honduras": "HN", "El Salvador": "SV", "Nicaragua": "NI", "Puerto Rico": "PR",
            "Brunei": "BN", "Papua New Guinea": "PG", "Timor-Leste": "TL"}
    def iso(country_name):
        return _MAP.get((country_name or "").strip(), "")

CATMAP = {
    "Funny": "Funny", "Education": "Education", "Business": "Business",
    "Buy Sell": "Buy Sell", "Buy-Sell": "Buy Sell",
    "Community & Social": "Community & Social", "Community and Social": "Community & Social",
    "Community": "Community & Social", "Finance": "Finance", "Friendship": "Community & Social",
    "Gaming": "Gaming", "Islamic": "Islamic", "Jobs": "Jobs",
    "Online Earning": "Earning", "Earning": "Earning", "Sports": "Sports",
    "Entertainment": "Entertainment", "Health": "Health", "News": "News",
    "Technology": "Technology", "Cooking": "Cooking", "Crypto": "Crypto",
    "Poetry": "Poetry", "Real Estate": "Real Estate", "Travel": "Travel",
    "Scholarship": "Scholarship", "Freelance": "Freelance", "Music": "Entertainment",
    "Movies": "Entertainment", "Dating": "Community & Social", "Study": "Education",
    "Religion": "Community & Social", "Language Learning": "Education",
    "Religious": "Community & Social", "General": "Community & Social",
    "Food": "Cooking", "Fitness": "Health",
    "Fashion": "Community & Social", "Cars": "Community & Social", "Animals": "Community & Social",
    "Pets": "Community & Social", "Books": "Education", "Language": "Education",
    "Science": "Education", "Politics": "News", "World": "News", "Shopping": "Buy Sell",
    "BuySell": "Buy Sell", "Adult": "Community & Social", "Chat": "Community & Social",
    "Chatting": "Community & Social", "City": "Community & Social", "District": "Community & Social",
    "Tourist": "Travel", "Travel": "Travel", "Songs": "Entertainment", "Drama": "Entertainment",
    "Movie": "Entertainment", "Actors": "Entertainment", "Media": "Entertainment",
    "Game": "Gaming", "Games": "Gaming", "Sports": "Sports", "Spiritual": "Islamic",
    "Christian": "Community & Social", "Bulk Whatsapp Group": "Community & Social",
    "Whatsapp Group": "Community & Social", "Money": "Finance", "Banking": "Finance",
    "Exam": "Education", "Engineering": "Education", "Software": "Technology",
    "Android": "Technology", "Device": "Technology", "Bike": "Community & Social",
    "Family": "Community & Social", "Friends": "Community & Social",
    "Relationship": "Community & Social", "Matrimonial": "Community & Social",
    "Social Service": "Community & Social", "Foundation": "Community & Social",
    "Yoga": "Health", "Food": "Cooking", "Bollywood": "Entertainment", "IPL": "Sports",
    "News": "News", "News-2": "News", "Political": "News", "Police": "Community & Social",
    "Insurance": "Business", "Fashion": "Community & Social", "Beauty": "Community & Social",
    "Singer": "Entertainment", "Music-Songs": "Entertainment", "Korean": "Entertainment",
    "China": "Community & Social", "Russia": "Community & Social", "Germany": "Community & Social",
    "France": "Community & Social", "Jamaica": "Community & Social", "Delhi": "Community & Social",
    "Dubai": "Community & Social", "India": "Community & Social", "UK": "Community & Social",
    "Canada": "Community & Social", "Australia": "Community & Social",
}
# groupda cat_path -> canonical
GD_CATMAP = {
    "entertainment": "Entertainment", "education": "Education", "jobs": "Jobs",
    "technology": "Technology", "news": "News", "news-2": "News", "sports": "Sports",
    "movie": "Entertainment", "movies": "Entertainment", "music": "Entertainment",
    "music-songs": "Entertainment", "songs": "Entertainment", "drama": "Entertainment",
    "game": "Gaming", "games": "Gaming", "health": "Health", "finance": "Finance",
    "money": "Finance", "banking": "Finance", "business": "Business",
    "cooking": "Cooking", "food": "Cooking", "travel": "Travel", "tourist": "Travel",
    "religion": "Community & Social", "spiritual": "Islamic", "christian": "Community & Social",
    "books": "Education", "language": "Education", "exam": "Education",
    "buysell": "Buy Sell", "fashion": "Community & Social", "beauty": "Community & Social",
    "pets": "Community & Social", "actors": "Entertainment", "media": "Entertainment",
    "political": "News", "yoga": "Health", "bollywood": "Entertainment", "ipl": "Sports",
    "friends": "Community & Social", "family": "Community & Social",
    "relationship": "Community & Social", "matrimonial": "Community & Social",
    "chat": "Community & Social", "chatting": "Community & Social",
    "city": "Community & Social", "district": "Community & Social",
    "dating": "Community & Social", "adult": "Community & Social",
    "bulk-whatsapp-group": "Community & Social", "whatsapp-group": "Community & Social",
    "telegram-channel": "Community & Social", "android": "Technology",
    "device": "Technology", "software": "Technology", "engineering": "Education",
    "bike": "Community & Social", "police": "Community & Social",
    "insurance": "Business", "singer": "Entertainment", "korean": "Entertainment",
    "social-service": "Community & Social", "foundation": "Community & Social",
    "animal": "Community & Social", "russia": "Community & Social",
    "germany": "Community & Social", "france": "Community & Social",
    "jamaica": "Community & Social", "delhi": "Community & Social",
    "dubai": "Community & Social", "india": "Community & Social",
    "uk": "Community & Social", "canada": "Community & Social",
    "australia": "Community & Social", "china": "Community & Social",
}

PORN = [r"\bxxx\b", r"\bporn\b", r"\bsex\b", r"\bsexy\b", r"\bnude\b",
        r"18\+\s*(video|porn|sex|xxx)", r"\bdesi\s*(sex|porn|xxx)\b",
        r"\bhot\s*girl", r"call\s*girl", r"\baunty\s*(sex|porn|xxx|hot|nude)\b",
        r"\bsex\s*(video|chat|group)\b", r"\bporn\s*(video|hub|group)\b",
        r"\bhot\s*(video|aunty|bhabhi)\b", r"\bbhabhi\s*(sex|porn|hot|xxx)\b",
        r"\bitem\s*(girl|sex|porn)\b", r"18\+\s*only",
        r"\bnekopoi\b", r"\bhentai\b", r"\bnsfw\b", r"\bonlyfans\b",
        r"\bmms\b", r"\bleak\w*\s*(video|photo|pics|mms)\b",
        r"\b(hot|sexy)\s*(bhabhi|aunty|girl|video)\b"]
SCAM = [r"airdrop", r"binary\s*option", r"free\s*money", r"earn\s*\$?\d+\s*(daily|per day)",
        r"double\s*(your\s*)?money", r"investment\s*double", r"click\s*.*earn",
        r"free\s*\$?\d+", r"\bdouble\s*income\b"]
CASINO = [r"tigrinho", r"fortune\s*tiger", r"\bsinais\b", r"plataformas?\s*pagantes?",
          r"\bcasino\b", r"\bslots?\b", r"betting\s*signal", r"\bwjbet\b", r"\bbet\s*signal",
          r"aviator\s*signal", r"\bcrash\s*signal", r"\bmatka\b", r"\bsatta\b",
          r"\bkalyan\b.{0,20}\b(matka|satta|jodi|panel|chart)\b",
          r"\b(matka|satta|jodi|panel|chart)\b.{0,20}\bkalyan\b"]
# false-positive restores: if any matches, keep (flag in summary instead of dropping)
RESTORE = [r"no\s+(porn|sex|xxx|nude)", r"not\s+(porn|sex|xxx)", r"porn\s*not\s*allowed",
           r"no\s+adult", r"sexta-feira", r"\bchuta\b", r"18\+\s*(only\s*)?(allowed|members|join|group)?$",
           r"\bfood\b", r"\bfitness\b", r"\bgym\b", r"\bworkout\b", r"\brecipe\b"]

def og_title(html):
    m = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', html, re.I | re.S)
    if not m:
        m = re.search(r'<meta\s+content=["\'](.*?)["\']\s+property=["\']og:title["\']', html, re.I | re.S)
    if not m:
        return ""
    return unescape(m.group(1)).strip()

def norm_title(title):
    """Fold fancy Unicode (mathematical bold etc.) to ASCII for screening."""
    t = unicodedata.normalize("NFKD", title or "")
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return t.casefold()

def screen(title):
    t = norm_title(title)
    for pat in RESTORE:
        if re.search(pat, t):
            return None  # restored / kept (false-positive guard)
    for pat in PORN:
        if re.search(pat, t):
            return "porn/xxx: " + pat
    for pat in CASINO:
        if re.search(pat, t):
            return "casino/betting: " + pat
    for pat in SCAM:
        if re.search(pat, t):
            return "scam/crypto-airdrop: " + pat
    return None

def fetch(session, code, attempts=3):
    url = "https://chat.whatsapp.com/" + code
    last_err = ""
    for a in range(attempts):
        try:
            r = session.get(url, headers=UA, timeout=75)
            if r.status_code == 429:
                return ("pending", "", "http 429 (attempt %d)" % (a + 1))
            if r.status_code != 200:
                last_err = "http %d" % r.status_code
                time.sleep(4)
                continue
            title = og_title(r.text or "")
            # live only if a real title: non-empty, non-generic, and contains
            # at least one letter/number after Unicode NFKD folding (fancy
            # bold + Urdu/Arabic-script titles count; "." / emoji-only do not)
            _nt = unicodedata.normalize("NFKD", title or "")
            _nt = "".join(ch for ch in _nt if not unicodedata.combining(ch))
            if title and title.lower().strip() not in GENERIC and any(ch.isalnum() for ch in _nt):
                return ("live", title, "")
            last_err = "empty/generic og:title"
            time.sleep(2)
        except requests.exceptions.RequestException:
            last_err = "transport:request-exception"
            time.sleep(2)
    if "429" in last_err or "transport" in last_err:
        return ("pending", "", last_err)
    return ("dead", "", last_err)

def build_queue():
    union = set(json.load(open(UNION)))
    queue = []  # dicts: code, source, category, country, meta
    seen = set()
    # groupizo
    try:
        mined = json.load(open(WAVE + "team30-mined-raw.json"))
    except Exception:
        mined = []
    gz_new = 0
    for m in mined:
        c = m.get("code", "")
        if not c or c in union or c in seen:
            continue
        seen.add(c)
        gz_new += 1
        queue.append({"code": c, "source": "groupizo",
                      "category": CATMAP.get(unescape((m.get("category_raw") or "").strip()), "Community & Social"),
                      "country": iso(m.get("country_name") or ""),
                      "name_hint": m.get("name", ""), "url": m.get("url", "")})
    # groupda: non-adult cat_paths first (freshest modified first), then adult
    try:
        gd = json.load(open(WAVE + "team30-groupda-mined.json"))
    except Exception:
        gd = []
    gd_new = [v for v in gd if not v["in_union"] and v["code"] not in seen]
    gd_new.sort(key=lambda v: v.get("post_modified", ""), reverse=True)
    non_adult = [v for v in gd_new if v.get("cat_path") != "adult"]
    adult = [v for v in gd_new if v.get("cat_path") == "adult"]
    # Cap groupda verification this run: freshest-first non-adult only; adult
    # deferred to resume (recorded in summary). Override via TEAM30_GD_CAP.
    gd_cap = int(os.environ.get("TEAM30_GD_CAP", "1200"))
    non_adult_capped = non_adult[:gd_cap]
    gd_deferred = len(non_adult) - len(non_adult_capped) + len(adult)
    for v in non_adult_capped:
        c = v["code"]
        if c in seen:
            continue
        seen.add(c)
        queue.append({"code": c, "source": "groupda",
                      "category": GD_CATMAP.get(v.get("cat_path", ""), "Community & Social"),
                      "country": "",
                      "name_hint": v.get("post_title", ""), "url": v.get("post_link", "")})
    return queue, len(mined), gz_new, len(gd_new), len(non_adult), len(adult), gd_deferred

def write_outputs(results, controls, counts_extra, partial=False):
    candidates, pending, excluded = [], [], []
    n_dead = 0
    seen_codes = set()
    for r in results:
        code = r["code"]
        if code in seen_codes:
            continue
        seen_codes.add(code)
        if r["status"] == "pending":
            pending.append({"code": code, "reason": r["reason"], "name": r.get("title", "") or r.get("name_hint", ""),
                            "invite": "https://chat.whatsapp.com/" + code, "source": r["source"]})
            continue
        if r["status"] == "dead":
            n_dead += 1
            continue
        sreason = screen(r["title"])
        if sreason:
            excluded.append({"code": code, "reason": "excluded: " + sreason + " | title=" + r["title"],
                             "source": r["source"]})
            continue
        name = re.sub(r"^[\u200b\ufeff\s]+", "", r["title"])[:120].strip()
        cat = r["category"] or "Community & Social"
        country = r["country"] or ""
        desc = "Join %s, an active WhatsApp group for %s." % (name, cat.lower())
        desc += " Connect with members, share updates and stay in touch."
        candidates.append({"name": name, "category": cat, "country": country,
                           "description": desc, "invite": "https://chat.whatsapp.com/" + code})
    gz_total, gd_total, gz_new, gd_new, gd_nonadult, gd_adult = counts_extra
    n_dup = (gz_total - gz_new) + (gd_total - gd_new)
    json.dump(candidates, open(WAVE + "team30-candidates.json", "w"), indent=2, ensure_ascii=False)
    json.dump(candidates, open(WAVE + "team30-leads.json", "w"), indent=2, ensure_ascii=False)
    json.dump(pending, open(WAVE + "team30-pending.json", "w"), indent=2, ensure_ascii=False)
    return candidates, pending, excluded, n_dead, n_dup

def main():
    queue, n_gz_mined, gz_new, gd_new, gd_nonadult, gd_adult, gd_deferred = build_queue()
    gz_total = sum(1 for m in json.load(open(WAVE + "team30-mined-raw.json")) if m.get("code"))
    gd_total = len(json.load(open(WAVE + "team30-groupda-mined.json")))
    counts_extra = (gz_total, gd_total, gz_new, gd_new, gd_nonadult, gd_adult)
    print("queue:", len(queue), "gz mined:", n_gz_mined, "gz new:", gz_new,
          "gd new:", gd_new, "gd non-adult:", gd_nonadult, "gd adult:", gd_adult,
          "gd deferred this run:", gd_deferred, flush=True)
    session = requests.Session()
    # ---- CONTROLS ----
    st, title, err = fetch(session, "KrDwdK8EIkB6vgauHg5M7N")
    ctrl_live = (st == "live" and title == "JAY - PHP & Python Full Stack Developer")
    print("CONTROL live:", st, repr(title), "PASS" if ctrl_live else "FAIL", flush=True)
    st2, title2, err2 = fetch(session, "ZzZzZzZzZzZzZzZzZzZzZzZz")
    ctrl_fake = (st2 == "dead" and title2 == "")
    print("CONTROL fabricated:", st2, repr(title2), "PASS" if ctrl_fake else "FAIL", flush=True)
    controls = {"live_KrDwdK8EIkB6vgauHg5M7N": {"expected": "JAY - PHP & Python Full Stack Developer", "got": title, "status": st, "pass": ctrl_live},
                "fabricated_ZzZzZzZzZzZzZzZzZzZzZzZz": {"expected": "empty/dead", "got": title2, "status": st2, "pass": ctrl_fake}}
    if not (ctrl_live and ctrl_fake):
        print("CONTROLS FAILED — STOPPING", flush=True)
        json.dump({"team": "team30", "controls": controls, "stopped": True},
                  open(WAVE + "team30-summary.json", "w"), indent=2)
        sys.exit(1)

    # resume support
    prog_path = WAVE + "team30-verify-progress.json"
    done = {}
    try:
        done = {r["code"]: r for r in json.load(open(prog_path))}
        print("resuming verify with", len(done), "already checked", flush=True)
    except Exception:
        pass
    todo = [q for q in queue if q["code"] not in done]
    print("to verify:", len(todo), flush=True)
    results = list(done.values())
    BATCH = 15
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i + BATCH]
        with ThreadPoolExecutor(max_workers=5) as ex:
            outs = list(ex.map(lambda q: fetch(session, q["code"]), batch))
        for q, (s, t, e) in zip(batch, outs):
            results.append({"code": q["code"], "source": q["source"], "status": s,
                            "title": t, "reason": e, "category": q["category"],
                            "country": q["country"], "name_hint": q["name_hint"], "url": q["url"]})
        json.dump(results, open(prog_path, "w"), indent=1, ensure_ascii=False)
        nl = sum(1 for r in results if r["status"] == "live")
        print(f"{i+len(batch)}/{len(todo)} live={nl} done={len(results)}", flush=True)
        if (i + BATCH) % 300 == 0 or i + BATCH >= len(todo):
            write_outputs(results, controls, counts_extra, partial=True)
            print("checkpoint outputs written", flush=True)
        if i + BATCH < len(todo):
            time.sleep(3)

    candidates, pending, excluded, n_dead, n_dup = write_outputs(results, controls, counts_extra)
    summary = {
        "team": "team30",
        "slice": "groupizo.com + groupda.com fresh poll",
        "sources": [
            "groupizo.com sitemap groups 1-12 (2332 urls); fresh = lastmod >= 2026-11-12 (434 urls); detail page -> /verify/<slug> -> code",
            "groupda.com wp-json wp/v2/posts orderby=modified desc (2300 posts fetched, sitemap lists 2654); newest post modified 2026-09-15 (Telegram carding, no WhatsApp codes); code-bearing posts mined for codes not in union",
            "groupda HTML post pages are Cloudflare-challenged under desktop UA; mobile UA returns full page; wp-json route used instead",
        ],
        "controls": controls,
        "counts": {"raw_mined_groupizo": gz_total, "raw_mined_groupda_unique": gd_total,
                   "queued_for_verify": len(queue), "verified_live": len(candidates),
                   "dupes_vs_union_or_within_team": n_dup, "dead": n_dead,
                   "excluded": len(excluded), "pending": len(pending), "leads": len(candidates),
                   "groupda_codes_deferred_unverified": gd_deferred},
        "excluded": excluded,
        "pending_detail": pending,
        "resume_point": "verify progress banked in team30-verify-progress.json (%d codes checked). groupda codes not in union: %d (non-adult %d, adult %d); %d deferred unverified this run (adult cat_path + non-adult beyond the 1200 freshest-first cap); all listed in team30-groupda-mined.json with in_union flags — rerun team30_verify.py with TEAM30_GD_CAP=<n> to continue. groupizo fresh set fully mined in team30-mined-raw.json." % (len(results), gd_new, gd_nonadult, gd_adult, gd_deferred),
        "notes": "Names taken from live og:title (capped 120 chars). Category from groupizo breadcrumb / groupda post path, mapped to canonical list; country from groupizo breadcrumb via ISO lookup, groupda country left empty (not guessed). Descriptions generated, never copied. No source name/link stored. Girls/friendship kept; hard porn/casino/scam dropped on live title with false-positive restores (negated prohibitions, sexta-feira, chuta, 18+ age gates, food/fitness).",
    }
    json.dump(summary, open(WAVE + "team30-summary.json", "w"), indent=2, ensure_ascii=False)
    print("DONE", summary["counts"], flush=True)

if __name__ == "__main__":
    main()
