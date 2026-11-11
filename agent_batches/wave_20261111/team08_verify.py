#!/usr/bin/env python3
"""TEAM 08 wave 20261111 — verify raw candidates (slow checker), classify, screen, bank.
Reads team08_raw_candidates.json + team08_fetch_log.json; writes verified/pending/leads/summary.
Checkpoints every 200 verifications."""
import json, re, os, time, threading, html
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
OG_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
OG_RE2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)

CATEGORIES = ["Education", "Jobs", "Entertainment", "Islamic", "News", "Sports", "Technology",
              "Health", "Business", "Gaming", "Friendship", "Community & Social", "Online Earning",
              "Crypto", "Cooking", "Poetry", "Travel", "Scholarship", "Freelance", "Real Estate",
              "Buy Sell", "Finance", "Funny"]
CAT_KW = [
    (r"scholarship|hec|csc|admission|study abroad|university admiss", "Scholarship"),
    (r"\bjob|jobs|vacanc|hiring|recruit|employment|naukri|rozgar|bharti", "Jobs"),
    (r"buy.?sell|buy and sell|sale|selling|marketplace|olx|deals?|offer|shopping|shop\b", "Buy Sell"),
    (r"real estate|propert|plot|house for sale|flat", "Real Estate"),
    (r"forex|trading|stock|invest|finance|loan|bank|insurance|mutual fund", "Finance"),
    (r"crypto|bitcoin|btc|ethereum|binance|usdt|forex signal", "Crypto"),
    (r"earn money|online earning|make money|earning|passive income|freelanc", "Online Earning"),
    (r"freelanc|fiverr|upwork|gig", "Freelance"),
    (r"pubg|bgmi|free fire|gaming|gamer|clash of|psl|esports", "Gaming"),
    (r"cricket|football|hockey|fifa|ipl|psl|sport|wrestl|kabaddi", "Sports"),
    (r"movie|music|song|drama|funny|meme|comedy|joke|entertainment|netflix|reel|tiktok|status video", "Entertainment"),
    (r"funny|meme|joke|comedy|haha", "Funny"),
    (r"islam|islamic|quran|naat|hamd|madrasa|masjid|muslim|ramadan|dua|hadees|hadith|tilawat|bayan|molana|mufti|peer|dars", "Islamic"),
    (r"news|breaking|headline|taza|khabar", "News"),
    (r"study|student|exam|test prep|css|ppsc|fpsc|upsc|ielts|english learn|learn english|school|college|university|academy|coaching|tuition|education|teacher|nursing|medical stud", "Education"),
    (r"health|doctor|hospital|fitness|weight loss|yoga|diet|skin|pharma|medicine", "Health"),
    (r"cook|recipe|food|kitchen|chef", "Cooking"),
    (r"poetry|poet|shayari|ghazal|urdu poetry|punjabi poetry", "Poetry"),
    (r"travel|tour|trip|visa|tourism|flight|hotel", "Travel"),
    (r"tech|program|python|developer|coding|software|seo|digital marketing|computer|ai\b|artificial intell", "Technology"),
    (r"business|entrepreneur|startup|marketing|sales|import export|wholesale", "Business"),
    (r"friend|friendship|dosti|chat|chatting|girls? (group|chat)|new friend|make friend|couple|love|dating|rishta|marriage", "Friendship"),
]
COUNTRY_KW = {
    "pakistan": "PK", "pakistani": "PK", "punjab": "PK", "sindh": "PK", "karachi": "PK", "lahore": "PK",
    "india": "IN", "indian": "IN", "delhi": "IN", "mumbai": "IN", "tamil": "IN", "kerala": "IN",
    "bangladesh": "BD", "bangladeshi": "BD", "nepal": "NP", "sri lanka": "LK", "afghanistan": "AF",
    "paraguay": "PY", "philippines": "PH", "filipino": "PH", "poland": "PL", "turkey": "TR", "turkish": "TR",
    "usa": "US", "america": "US", "united states": "US", "uk": "GB", "england": "GB", "britain": "GB",
    "uae": "AE", "dubai": "AE", "saudi": "SA", "qatar": "QA", "kuwait": "KW", "oman": "OM", "bahrain": "BH",
    "canada": "CA", "australia": "AU", "germany": "DE", "france": "FR", "spain": "ES", "italy": "IT",
    "nigeria": "NG", "kenya": "KE", "ghana": "GH", "south africa": "ZA", "egypt": "EG", "morocco": "MA",
    "brazil": "BR", "brasil": "BR", "mexico": "MX", "argentina": "AR", "colombia": "CO", "peru": "PE",
    "chile": "CL", "uruguay": "UY", "bolivia": "BO", "ecuador": "EC", "venezuela": "VE",
    "indonesia": "ID", "malaysia": "MY", "thailand": "TH", "vietnam": "VN", "japan": "JP", "korea": "KR",
    "china": "CN", "russia": "RU", "ukraine": "UA", "romania": "RO", "portugal": "PT", "netherlands": "NL",
    "belgium": "BE", "sweden": "SE", "norway": "NO", "denmark": "DK", "finland": "FI", "austria": "AT",
    "greece": "GR", "somalia": "SO", "ethiopia": "ET", "uganda": "UG", "tanzania": "TZ", "zimbabwe": "ZW",
    "sierra leone": "SL", "san marino": "SM", "russian": "RU",
}
SCAM_PATTERNS = [
    r"b[\s\-]?love", r"forsage", r"shey[iy]", r"holiverse", r"meta[\s\-]?whale",
    r"fixed match", r"betting (tip|signal|group).*guarante", r"double your (money|bitcoin|investment)",
    r"100% (profit|guaranteed|win)", r"airdrop (scam|bot)", r"trust wallet.*doubl",
]
PORN_PATTERNS = [r"xxx", r"porn", r"sex video", r"sex group", r"nude", r"adult video", r"🔞", r"18\+ (sex|porn|video|nude)",
                  r"video ?call (girl|girls|bhabhi|aunty|sexy)", r"call girl", r"discharge",
                  r"sexy (video|call|chat|girl)", r"hot (bhabhi|aunty|girl|sexy)",
                  r"ویڈیو کال", r"ڈسچارچ", r"سیکسی", r"کال گرل"]
NEGATE_RE = re.compile(r"(?i)[^.!\n]*(no|not allowed|prohibited|strictly prohibited|not allow)[^.!\n]*(porn|xxx|sex|nude|adult)[^.!\n]*[.!\n]?")

def strip_negations(s):
    return NEGATE_RE.sub(" ", s or "")

def screen(text):
    """Return exclusion reason or None. Screens after stripping negated-prohibition sentences.
    NFKD-normalizes so fancy-unicode spellings (e.g. mathematical sans-serif) match too."""
    import unicodedata
    t = unicodedata.normalize("NFKD", strip_negations(text or ""))
    low = t.lower()
    for p in SCAM_PATTERNS:
        if re.search(p, low):
            return f"scam signal in text ({p})"
    for p in PORN_PATTERNS:
        if re.search(p, low):
            return f"adult-signal in text ({p})"
    return None

def classify(text):
    low = (text or "").lower()
    for pat, cat in CAT_KW:
        if re.search(pat, low):
            return cat
    return "Community & Social"

def country_of(text):
    low = (text or "").lower()
    for kw, cc in COUNTRY_KW.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", low):
            return cc
    return ""

def clean_name(n):
    n = html.unescape(n or "")
    n = re.sub(r"<[^>]*", "", n)  # strip partial/complete tags incl. cut-off <a href="...
    n = re.sub(r"\s+", " ", n).strip(" -–—:|•·»\"'“”")
    return n[:120]

PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{8,}\d")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def scrub_pii(s):
    """Remove phone numbers / emails from a banked name (personal info must never be stored)."""
    s = PHONE_RE.sub(" ", s or "")
    s = EMAIL_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip(" -–—:|•·»\"'“”")
    return s

def og_title(html_text):
    m = OG_RE.search(html_text) or OG_RE2.search(html_text)
    if not m:
        return ""
    return html.unescape(m.group(1)).strip()

_tls = threading.local()

def _session():
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        _tls.s = s
    return s

def check_code(code):
    """Returns (status, ogtitle, err) status in live/dead/pending."""
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(2):
        try:
            r = _session().get(url, timeout=60)
            if r.status_code != 200:
                if attempt == 0:
                    time.sleep(3); continue
                return "dead", "", f"HTTP {r.status_code}"
            t = og_title(r.text)
            if not t:
                if attempt == 0:
                    time.sleep(3); continue
                return "dead", "", "empty og:title after retry"
            return "live", t, ""
        except requests.RequestException as e:
            if attempt == 0:
                time.sleep(3); continue
            return "pending", "", f"transport: {type(e).__name__}: {str(e)[:100]}"
    return "dead", "", "no og:title"

def main():
    cands = json.load(open(os.path.join(WAVE, "team08_raw_candidates.json")))
    existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
    # dedupe within slice: keep entry with longest clean name
    by_code = {}
    for c in cands:
        code = c["code"]
        if code not in by_code or len(clean_name(c.get("name", ""))) > len(clean_name(by_code[code].get("name", ""))):
            by_code[code] = c
    print(f"raw {len(cands)} unique-in-slice {len(by_code)}", flush=True)
    fresh = {k: v for k, v in by_code.items() if k not in existing}
    print(f"already-in-existing {len(by_code)-len(fresh)} fresh-to-verify {len(fresh)}", flush=True)

    verified, pending, exclusions = [], [], []
    dead = 0
    # pre-screen on banked name+title
    todo = []
    for code, c in fresh.items():
        text = f"{c.get('name','')} {c.get('page_title','')}"
        reason = screen(text)
        if reason:
            exclusions.append({"code": code, "reason": f"banked-name screen: {reason}"})
            continue
        todo.append((code, c))
    print(f"pre-screen excluded {len(exclusions)} todo {len(todo)}", flush=True)

    # slow checker: global pacing >=0.4s between request starts + per-call retry sleeps
    pace_lock = threading.Lock()
    last_start = [0.0]
    def paced_check(item):
        code, c = item
        with pace_lock:
            wait = 0.4 - (time.time() - last_start[0])
            if wait > 0:
                time.sleep(wait)
            last_start[0] = time.time()
        status, ogt, err = check_code(code)
        return code, c, status, ogt, err

    vfile = os.path.join(WAVE, "team08-leads-slice8.json")
    pfile = os.path.join(WAVE, "team08-leads-slice8-pending.json")
    # resume support: skip codes already in output files
    done_codes = set()
    if os.path.exists(vfile):
        verified = json.load(open(vfile)); done_codes |= {v["invite"].rsplit("/", 1)[-1] for v in verified}
    if os.path.exists(pfile):
        pending = json.load(open(pfile)); done_codes |= {v["invite"].rsplit("/", 1)[-1] for v in pending}
    todo = [t for t in todo if t[0] not in done_codes]
    print(f"resuming: already banked {len(done_codes)} remaining {len(todo)}", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(paced_check, t): t for t in todo}
        for i, f in enumerate(as_completed(futs)):
            code, c, status, ogt, err = f.result()
            if status == "live":
                reason = screen(ogt)
                if reason:
                    exclusions.append({"code": code, "reason": f"og:title screen: {reason} (og:title={ogt[:80]!r})"})
                    continue
                name = scrub_pii(clean_name(ogt)) or scrub_pii(clean_name(c.get("name", ""))) or "WhatsApp Group"
                text = f"{name} {c.get('page_title','')} {c.get('listing','')}"
                cat = classify(text)
                cc = country_of(f"{c.get('page_title','')} {c.get('listing','')} {name}")
                desc = f"A {cat.lower()} WhatsApp group"
                if cc:
                    desc += f" for members in {cc}"
                desc += f" — {name}. Join to chat and share updates with members."
                verified.append({"name": name, "category": cat, "country": cc,
                                 "description": desc[:300], "invite": f"https://chat.whatsapp.com/{code}"})
            elif status == "pending":
                pending.append({"name": clean_name(c.get("name", "")), "category": classify(f"{c.get('name','')} {c.get('page_title','')}"),
                                "country": country_of(f"{c.get('page_title','')} {c.get('listing','')}"),
                                "description": "", "invite": f"https://chat.whatsapp.com/{code}",
                                "reason": err})
            else:
                dead += 1
            if (i+1) % 200 == 0:
                json.dump(verified, open(vfile, "w"), ensure_ascii=False)
                json.dump(pending, open(pfile, "w"), ensure_ascii=False)
                print(f"{i+1}/{len(todo)} verified={len(verified)} pending={len(pending)} dead={dead} excl={len(exclusions)} elapsed={time.time()-t0:.0f}s", flush=True)
    json.dump(verified, open(vfile, "w"), ensure_ascii=False)
    json.dump(pending, open(pfile, "w"), ensure_ascii=False)
    json.dump({"dead": dead, "exclusions": exclusions, "fresh": len(fresh),
               "dup_existing": len(by_code)-len(fresh)},
              open(os.path.join(WAVE, "team08_verify_state.json"), "w"), ensure_ascii=False)
    print(f"VERIFY DONE verified={len(verified)} pending={len(pending)} dead={dead} excl={len(exclusions)} elapsed={time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
