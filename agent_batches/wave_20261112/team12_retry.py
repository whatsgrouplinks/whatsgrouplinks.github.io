#!/usr/bin/env python3
"""TEAM 12 wave 20261112 — leads slice 8 failed-listing retry.
Re-fetch the 73 failed listing pages from wave_20261111 team08 leads file,
extract invite codes, verify fresh codes, screen, bank.
Checkpoints: team12-leads-slice8-progress.jsonl, partial outputs in wave dir."""
import json, re, os, time, threading, html, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
BUILD = "/home/hatch/workspace/whatsapp-groups-site"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{18,30})(?![A-Za-z0-9_-])")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
OG_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
OG_RE2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)
OGD_RE = re.compile(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)

CAT_KW = [
    (r"scholarship|hec|csc|admission|study abroad|university admiss", "Education"),
    (r"\bjob|jobs|vacanc|hiring|recruit|employment|naukri|rozgar|bharti", "Jobs"),
    (r"buy.?sell|buy and sell|sale|selling|marketplace|olx|deals?|offer|shopping|shop\b", "Buy & Sell"),
    (r"real estate|propert|plot|house for sale|flat", "Real Estate"),
    (r"forex|trading|stock|invest|finance|loan|bank|insurance|mutual fund", "Finance"),
    (r"crypto|bitcoin|btc|ethereum|binance|usdt|forex signal", "Crypto"),
    (r"earn money|online earning|make money|earning|passive income", "Finance"),
    (r"freelanc|fiverr|upwork|gig", "Business"),
    (r"pubg|bgmi|free fire|gaming|gamer|clash of|esports", "Gaming"),
    (r"cricket|football|hockey|fifa|ipl|psl|sport|wrestl|kabaddi", "Sports"),
    (r"movie|music|song|drama|netflix|reel|tiktok|status video|entertainment", "Entertainment"),
    (r"funny|meme|joke|comedy|haha", "Funny"),
    (r"islam|islamic|quran|naat|hamd|madrasa|masjid|muslim|ramadan|dua|hadees|hadith|tilawat|bayan|molana|mufti|peer|dars", "Islamic"),
    (r"news|breaking|headline|taza|khabar|newspaper", "News"),
    (r"study|student|exam|test prep|css|ppsc|fpsc|upsc|ielts|english learn|learn english|school|college|university|academy|coaching|tuition|education|teacher|nursing|medical stud", "Education"),
    (r"health|doctor|hospital|fitness|weight loss|yoga|diet|skin|pharma|medicine", "Health"),
    (r"cook|recipe|food|kitchen|chef", "Cooking"),
    (r"poetry|poet|shayari|ghazal|urdu poetry|punjabi poetry", "Poetry"),
    (r"travel|tour|trip|visa|tourism|flight|hotel", "Community & Social"),
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
}
SCAM_PATTERNS = [
    r"b[\s\-]?love", r"forsage", r"shey[iy]", r"holiverse", r"meta[\s\-]?whale",
    r"fixed match", r"betting (tip|signal|group).*guarante", r"double your (money|bitcoin|investment)",
    r"100% (profit|guaranteed|win)", r"airdrop (scam|bot)", r"trust wallet.*doubl",
    r"crypto.?airdrop", r"airdrop.*(free|claim|earn)", r"binary ?option", r"binary trad",
    r"venda de xit", r"paid.?hack", r"hack.*(paid|apk|panel)",
    r"betting|betting tips|sports bet|bet ?promo|betting group|betting recruitment",
    r"ai.?trad.*(profit|daily|earn)", r"daily profit", r"daily earning.*trading",
    r"hookup", r"brazzers", r"desi bhabhi", r"sexual home",
]
PORN_PATTERNS = [r"xxx", r"porn", r"sex video", r"sex group", r"nude", r"adult video", r"🔞", r"18\+ (sex|porn|video|nude)",
                 r"video ?call (girl|girls|bhabhi|aunty|sexy)", r"call girl", r"discharge",
                 r"sexy (video|call|chat|girl)", r"hot (bhabhi|aunty|girl|sexy)",
                 r"ویڈیو کال", r"ڈسچارچ", r"سیکسی", r"کال گرل", r"hentai", r"call.?girl|escort",
                 r"18\+ (sticker|video)", r"sex ?chat", r"sexy sticker"]
NEGATE_RE = re.compile(r"(?i)[^.!\\n]*(no|not allowed|prohibited|strictly prohibited|not allow|sem |proibido|não pode)[^.!\\n]*(porn|xxx|sex|nude|adult|pornografia)[^.!\\n]*[.!\\n]?")

def strip_negations(s):
    return NEGATE_RE.sub(" ", s or "")

def screen(text):
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

def clean_text(s):
    s = html.unescape(TAG_RE.sub(" ", s or ""))
    return re.sub(r"\s+", " ", s).strip()

def guess_name(h, mstart):
    win = h[max(0, mstart-900):mstart]
    win = re.sub(r"<[^>]*$", "", win)
    for tag in ("<li", "<tr", "<h3", "<h2", "<td", "<div"):
        idx = win.lower().rfind(tag)
        if idx >= 0:
            seg = clean_text(win[idx:])
            break
    else:
        seg = clean_text(win)
    seg = re.sub(r"(?i)\s*(join|join group|join now|join chat|click here|👉|➡️)\s*$", "", seg)
    seg = re.sub(r"[\-–—:|•·»]+\s*$", "", seg).strip()
    if len(seg) > 120:
        parts = re.split(r"[|\n]", seg)
        seg = parts[-1].strip() if parts else seg
    if len(seg) > 120:
        seg = seg[-120:]
    return seg

PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{8,}\d")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def clean_name(n):
    n = html.unescape(n or "")
    n = re.sub(r"<[^>]*", "", n)
    n = PHONE_RE.sub(" ", n)
    n = EMAIL_RE.sub(" ", n)
    n = re.sub(r"\s+", " ", n).strip(" -–—:|•·»\"'“”")
    return n[:120]

def og_title(t):
    m = OG_RE.search(t) or OG_RE2.search(t)
    if m:
        return html.unescape(m.group(1)).strip()
    m = OGD_RE.search(t)
    return html.unescape(m.group(1)).strip() if m else ""

_tls = threading.local()
def _session():
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        _tls.s = s
    return s

def fetch_one(url):
    for attempt in range(2):
        try:
            r = _session().get(url, timeout=60, allow_redirects=True)
            if r.status_code != 200 or not r.text:
                if attempt == 0:
                    time.sleep(5); continue
                return url, r.status_code, [], "", 0, ""
            h = r.text
            title = clean_text(TITLE_RE.search(h).group(1)) if TITLE_RE.search(h) else ""
            cands, seen = [], set()
            for m in CODE_RE.finditer(h):
                code = m.group(1)
                if code in seen or code.lower() == "invite":
                    continue
                seen.add(code)
                cands.append({"code": code, "name": guess_name(h, m.start()),
                              "listing": url, "page_title": title[:160]})
            return url, r.status_code, cands, title[:160], len(h), ""
        except requests.RequestException as e:
            if attempt == 0:
                time.sleep(5); continue
            return url, 0, [], str(e)[:120], 0, f"transport: {type(e).__name__}"
    return url, 0, [], "", 0, "unknown"

def check_code(code):
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

def log(msg):
    line = json.dumps({"t": time.strftime("%H:%M:%S"), "msg": msg})
    with open(os.path.join(WAVE, "team12-leads-slice8-progress.jsonl"), "a") as f:
        f.write(line + "\n")
    print(msg, flush=True)

def main():
    urls = json.load(open(os.path.join(PREV, "team08-leads-slice8-leads.json")))
    existing = set(json.load(open(os.path.join(BUILD, ".existing_codes.json"))))
    log(f"input leads {len(urls)} existing-codes {len(existing)}")

    # ---- CONTROLS FIRST ----
    groups = json.load(open(os.path.join(BUILD, "groups.json")))
    live_code = None
    for g in groups:
        inv = g.get("invite", "")
        m = CODE_RE.search(inv or "")
        if m:
            live_code = m.group(1)
            break
    fake_code = "ZZZZZZZZZZZZZZZZZZZZ"
    st, ogt, err = check_code(live_code)
    log(f"CONTROL known-live {live_code}: status={st} og_title={ogt[:80]!r} err={err}")
    assert st == "live" and ogt, "CONTROL FAILED: known-live code did not show og:title"
    st2, ogt2, err2 = check_code(fake_code)
    log(f"CONTROL fabricated {fake_code}: status={st2} og_title={ogt2[:80]!r} err={err2}")
    assert st2 == "dead" and not ogt2, "CONTROL FAILED: fabricated code showed og:title"

    # ---- FETCH phase (4 workers) ----
    fetch_log = {}
    raw = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(fetch_one, u): u for u in urls}
        for fut in as_completed(futs):
            url, status, cands, title, nbytes, err = fut.result()
            fetch_log[url] = {"status": status, "codes": len(cands), "title": title, "bytes": nbytes, "err": err}
            raw.extend(cands)
            log(f"fetch {status} codes={len(cands)} bytes={nbytes} {url[:100]} {err}")
    json.dump(fetch_log, open(os.path.join(WAVE, "team12-leads-slice8-fetch-log.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(raw, open(os.path.join(WAVE, "team12-leads-slice8-raw.json"), "w"), indent=1, ensure_ascii=False)
    still_failed = [u for u, r in fetch_log.items() if r["status"] != 200]
    code_less = [u for u, r in fetch_log.items() if r["status"] == 200 and r["codes"] == 0]
    log(f"fetch done: ok={len(urls)-len(still_failed)} still-failing={len(still_failed)} code-less={len(code_less)} raw-codes={len(raw)}")

    # ---- dedupe within slice (keep longest clean name), then vs existing ----
    by_code = {}
    for c in raw:
        code = c["code"]
        if code not in by_code or len(clean_name(c.get("name", ""))) > len(clean_name(by_code[code].get("name", ""))):
            by_code[code] = c
    log(f"raw {len(raw)} unique-in-slice {len(by_code)}")
    fresh = {k: v for k, v in by_code.items() if k not in existing}
    log(f"already-in-existing {len(by_code)-len(fresh)} fresh-to-verify {len(fresh)}")

    # ---- pre-screen on banked name + page title ----
    exclusions, todo = [], []
    for code, c in fresh.items():
        text = f"{c.get('name','')} {c.get('page_title','')}"
        reason = screen(text)
        if reason:
            exclusions.append({"code": code, "reason": f"banked-name screen: {reason}"})
            continue
        todo.append((code, c))
    log(f"pre-screen excluded {len(exclusions)} todo {len(todo)}")

    # ---- verify (paced, 4 workers) ----
    verified, pending = [], []
    dead = 0
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

    vfile = os.path.join(WAVE, "team12-leads-slice8-candidates.json")
    pfile = os.path.join(WAVE, "team12-leads-slice8-pending.json")
    done_codes = set()
    if os.path.exists(vfile):
        verified = json.load(open(vfile)); done_codes |= {v["invite"].rsplit("/", 1)[-1] for v in verified}
    if os.path.exists(pfile):
        pending = json.load(open(pfile)); done_codes |= {p["invite"].rsplit("/", 1)[-1] for p in pending}
    todo = [(c, cc) for (c, cc) in todo if c not in done_codes]
    log(f"resume: already done {len(done_codes)} remaining to verify {len(todo)}")

    n = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(paced_check, item): item for item in todo}
        for fut in as_completed(futs):
            code, c, status, ogt, err = fut.result()
            n += 1
            if status == "live":
                name = clean_name(c.get("name", "")) or clean_name(ogt)
                text = f"{name} {ogt} {c.get('page_title','')}"
                reason = screen(text)
                if reason:
                    exclusions.append({"code": code, "reason": f"live-title screen: {reason}"})
                    log(f"verify {code} LIVE but EXCLUDED: {reason} og={ogt[:60]!r}")
                    continue
                cat = classify(text)
                cc = country_of(text)
                desc = f"Join {name}, a WhatsApp group listed under {cat}."
                verified.append({"name": name, "category": cat, "country": cc,
                                 "description": desc,
                                 "invite": f"https://chat.whatsapp.com/{code}"})
                log(f"verify {code} LIVE cat={cat} name={name[:60]!r}")
            elif status == "pending":
                pending.append({"name": clean_name(c.get("name", "")), "category": classify(f"{c.get('name','')} {c.get('page_title','')}"),
                                "country": country_of(f"{c.get('name','')} {c.get('page_title','')}"),
                                "description": f"Join {clean_name(c.get('name','')) or code}, a WhatsApp group.",
                                "invite": f"https://chat.whatsapp.com/{code}",
                                "error": err})
                log(f"verify {code} PENDING {err}")
            else:
                dead += 1
            if n % 50 == 0:
                json.dump(verified, open(vfile, "w"), indent=1, ensure_ascii=False)
                json.dump(pending, open(pfile, "w"), indent=1, ensure_ascii=False)
                log(f"checkpoint {n}/{len(todo)} verified={len(verified)} pending={len(pending)} dead={dead}")

    json.dump(verified, open(vfile, "w"), indent=1, ensure_ascii=False)
    json.dump(pending, open(pfile, "w"), indent=1, ensure_ascii=False)

    # ---- leads: pages still failing or still code-less (banked, not guessed) ----
    leads = sorted(set(still_failed + code_less))
    json.dump(leads, open(os.path.join(WAVE, "team12-leads-slice8-leads.json"), "w"), indent=1, ensure_ascii=False)

    summary = {
        "team": 12, "slice": "leads slice 8 failed-listing retry", "wave": "20261112",
        "input_leads": len(urls),
        "controls": {"known_live_code": live_code, "known_live_result": "live with og:title",
                     "fabricated_code": fake_code, "fabricated_result": "dead, empty og:title"},
        "fetch": {"ok_200": len(urls) - len(still_failed), "still_failing": len(still_failed),
                  "code_less_200": len(code_less), "raw_codes_extracted": len(raw)},
        "verified": len(verified), "pending": len(pending), "leads": len(leads), "dead": dead,
        "already_in_existing": len(by_code) - len(fresh),
        "exclusions": exclusions,
        "still_failing_urls": still_failed,
        "code_less_urls": code_less,
        "resume_point": "fetch+verify complete for all 73 input URLs; remaining work = re-retry team12-leads-slice8-leads.json in a later wave",
    }
    json.dump(summary, open(os.path.join(WAVE, "team12-leads-slice8-summary.json"), "w"), indent=1, ensure_ascii=False)
    log(f"DONE verified={len(verified)} pending={len(pending)} leads={len(leads)} dead={dead} exclusions={len(exclusions)}")

if __name__ == "__main__":
    main()
