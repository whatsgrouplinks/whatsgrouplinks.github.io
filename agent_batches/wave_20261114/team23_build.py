#!/usr/bin/env python3
"""team23: build candidates/pending/excluded from verify results + live-title screening."""
import json, re, html

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
CANON = ["Education", "Entertainment", "Sports", "Funny", "Community & Social", "Finance",
         "Buy Sell", "Islamic", "Health", "News", "Jobs", "Technology", "Gaming", "Business",
         "Cooking", "Crypto", "Poetry", "Real Estate", "Travel", "Scholarship", "Freelance", "Earning"]

PORN = re.compile(r"(?i)(sex|porn|xxx|xxnxx|xvideos|nude|bhabhi.{0,8}sex|video\s*call\s*(girl|service)|phone\s*sex|live\s*sex|sexy\s*girl|hot\s*(girl|video)|escort|call\s*girl|webcam|masturbat|blowjob|pussy|dick|boobs|erotic|adult\s*(video|sex|18)|leak\s*video|viral\s*leak|desi\s*mom|gujarati.{0,8}sex|rekha.{0,8}sex|priya.{0,8}sex|pooja.{0,8}sex|punjabi.{0,8}sex|college.{0,8}sex|monika.{0,8}sex|ran[iy].{0,8}sex|savit[aa].{0,8}bhabhi|komla\s*bhabhi|bhabhi\s*lover|mistress|private\s*\.\.video|vrial\s*video|verl\s*video|hot\s*video|all.{0,6}type\s*video|sexy|fuck|gay\s*porn|cp\s*video|child\s*sex)")
BET = re.compile(r"(?i)(satta|1x\s*bet|1xbet|casino|slot\s*game|aviator|tigrinho|fortune\s*tiger|sinais|plataformas\s*pagantes|wjbet|khaiwal|10\s*k[ae]\s*9[05]0|prediction|weekly\s*prediction|betting|bet\s*signal)")
SCAM = re.compile(r"(?i)(airdrop|free\s*money|binance\s*millionaire|double\s*your\s*money|treasure\s*nft|free\s*earn\s*from|investment\s*platform|gold\s*trading\s*edge|forex\s*signals?\s*free)")
# negated-prohibition / benign contexts that restore a false positive
RESTORE = re.compile(r"(?i)(no\s+(sex|porn|xxx)|sex\s+not\s+allowed|not\s+allowed.{0,20}sex|sexta-feira|chuta|18\+\s*(only\s*)?(age|group|verification)|only\s*18\+)")

def clean_name(t):
    t = html.unescape(t or "").strip()
    t = re.sub(r"\s+", " ", t)
    return t

def screen(title):
    """Return (keep, reason)."""
    t = title or ""
    if PORN.search(t) and not RESTORE.search(t):
        return False, "hard porn/xxx in live og:title"
    if ("💦" in t or "🍑" in t or "🍆" in t) and ("🥵" in t or "💦" in t or "🍑" in t or "🍆" in t) and re.search(r"(?i)(service|video|call|girl|chat|sexy|hot|desi|bhabhi|sex)", t):
        return False, "sexual-service emoji combo in live og:title"
    if BET.search(t):
        return False, "betting/casino/prediction in live og:title"
    if SCAM.search(t):
        return False, "crypto-airdrop/free-money scam in live og:title"
    return True, ""

CAT_KEYWORDS = [
    (r"(?i)(study|student|exam|education|school|college|university|learn|tutorial|coaching|scholarship|neb|entrance|tnpsc|ielts|bpsc|ppsc|fpsc|upsc|homework|home\s*work|academy)", "Education"),
    (r"(?i)(scholarship)", "Scholarship"),
    (r"(?i)(cricket|football|ipl|sport|ludo|free\s*fire|pubg|game|gaming|ff\s|tournament)", "Gaming"),
    (r"(?i)(news|breaking|updates|daily\s*news)", "News"),
    (r"(?i)(job|jobs|career|vacanc|naukri|hiring|recruit|बेरोजगार|abroad\s*jobs|delivery\s*boy)", "Jobs"),
    (r"(?i)(islam|islamic|quran|muslim|ramadan|allah|deen|taleem-e-rasool|لبیک)", "Islamic"),
    (r"(?i)(poetry|shayari|shayari|adab|novel|urdu\s*adab)", "Poetry"),
    (r"(?i)(health|fitness|weight\s*loss|ayurved|medical|doctor)", "Health"),
    (r"(?i)(crypto|bitcoin|binance|forex|trading|stock|nse|nepse)", "Crypto"),
    (r"(?i)(online\s*earning|earning|earn\s*money|without\s*investment)", "Earning"),
    (r"(?i)(buy\s*&?\s*sell|for\s+sale|for\s+sell|book\s+store|market\s+store|group\s+for\s+sell)", "Buy Sell"),
    (r"(?i)(finance|money|earning|earn|income|business|freelance|shop|buy|sell|store|market|resell)", "Business"),
    (r"(?i)(tech|technology|program|developer|python|php|seo|digital)", "Technology"),
    (r"(?i)(funny|fun|meme|joke|comedy|entertainment|movie|drama|song|music|video|status)", "Entertainment"),
    (r"(?i)(cook|recipe|food)", "Cooking"),
    (r"(?i)(travel|tourism|tour)", "Travel"),
    (r"(?i)(real\s*estate|property|plot|house\s*sale)", "Real Estate"),
    (r"(?i)(friend|friends|chat|community|girls|girl|colony|worldwide|introduction|newcomer)", "Community & Social"),
]

def categorize(title, dir_cat, api_cat, site=""):
    for pat, cat in CAT_KEYWORDS:
        if re.search(pat, title or ""):
            return cat
    # directory-category fallback only for groupsor.in (its own category dirs);
    # groupssor API categories were assigned to a different submitted name, so
    # they must not override the live title.
    if site == "groupsor.in":
        m = {"education": "Education", "jobs": "Jobs", "jobs-career": "Jobs",
             "government-jobs": "Jobs", "news": "News", "entertainment": "Entertainment",
             "entertainment-masti": "Entertainment", "friendship": "Community & Social",
             "gaming": "Gaming", "business": "Business", "crypto": "Crypto",
             "pakistan": "Community & Social", "indian": "Community & Social"}
        for src in (dir_cat, api_cat):
            if src and src.lower() in m:
                return m[src.lower()]
    return "Community & Social"

def describe(name, cat, country):
    cl = cat.lower()
    base = f"Join {name}, an active WhatsApp group for {cl}."
    if country:
        base += f" Connect with members from {country} and chat daily."
    else:
        base += " Connect with members, share updates and chat daily."
    return base

def main():
    # batch1 (26 codes, dir-mined)
    v1 = json.load(open(f"{WD}/team23_verify_results.json"))
    # batch2 (groupssor SA + groupsorin)
    try:
        v2 = json.load(open(f"{WD}/team23_verify2_results.json"))
    except Exception:
        v2 = {}
    # retry pass overwrites pending entries it resolved
    try:
        vr = json.load(open(f"{WD}/team23_verify2_retry.json"))
        for c, d in vr.items():
            v2[c] = d
    except Exception:
        pass
    # batch3 (groupslink.pk)
    try:
        v3 = json.load(open(f"{WD}/team23_verify3_results.json"))
    except Exception:
        v3 = {}
    allv = {}
    for c, d in v1.items():
        allv[c] = d
    for c, d in v2.items():
        allv[c] = d
    for c, d in v3.items():
        allv[c] = d
    candidates, pending, excluded, dead = [], [], [], []
    seen = set()
    for code, d in allv.items():
        st = d.get("status")
        if st == "pending":
            pending.append({"code": code, "reason": d.get("err", ""), "source": d.get("site", "")})
            continue
        if st != "live":
            dead.append(code)
            continue
        title = clean_name(d.get("og_title", ""))
        if not title or title.lower().startswith("http"):
            title = clean_name(d.get("dir_name", "")) or code
        keep, reason = screen(title)
        if not keep:
            excluded.append({"code": code, "name": title, "reason": reason, "source": d.get("site", "")})
            continue
        country = (d.get("country") or "").upper()
        if d.get("site") == "groupsor.in":
            cat_dir = d.get("api_category", "")
            if cat_dir == "pakistan":
                country = country or "PK"
            elif cat_dir == "indian":
                country = country or "IN"
        # title-based country inference (explicit markers only)
        t_low = (title or "").lower()
        if not country:
            if re.search(r"bpsc|ppsc|fpsc|virtual university|\bvu\b|gojra|tlp|balochistan|punjab.*pakistan", t_low):
                country = "PK"
            elif re.search(r"zomato|swiggy|upsc|ssc\s*cgl|kerala|tamil\s*nadu|mumbai|delhi", t_low):
                country = "IN"
        cat = categorize(title, d.get("api_category", ""), d.get("dir_name", ""), d.get("site", ""))
        name = title
        if code in seen:
            continue
        seen.add(code)
        candidates.append({
            "name": name,
            "category": cat,
            "country": country if country in ("IN", "PK", "BD", "LK", "NP") else "",
            "description": describe(name, cat, country if country in ("IN", "PK", "BD", "LK", "NP") else ""),
            "invite": f"https://chat.whatsapp.com/{code}",
        })
    json.dump(candidates, open(f"{WD}/team23-candidates.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(f"{WD}/team23-pending.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"dead": dead, "excluded_live_title": excluded},
              open(f"{WD}/team23_dead_excluded.json", "w"), ensure_ascii=False, indent=1)
    print("candidates:", len(candidates), "pending:", len(pending),
          "excluded:", len(excluded), "dead:", len(dead))
    for c in candidates:
        print("CAND", c["name"], "|", c["category"], "|", c["country"], "|", c["invite"])
    for e in excluded:
        print("EXCL", e["code"], e["name"], "|", e["reason"])

if __name__ == "__main__":
    main()
