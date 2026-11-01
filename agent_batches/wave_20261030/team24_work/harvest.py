#!/usr/bin/env python3
"""TEAM24 harvester: fetch directory pages, extract (name, code), dedupe, verify."""
import json, re, subprocess, sys, time, html as htmllib

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261030"
DEDUP = WAVE + "/dedupe_union_codes.txt"
WORK = WAVE + "/team24_work"

CODE_RE = re.compile(r"https?://chat\.whatsapp\.com/([A-Za-z0-9_-]{22})")
PORN_RE = re.compile(r"porn|pornhub|xxx|nudes|sex video|escort|call girl|randi|fuck|dick|pussy|boobs|anal", re.I)
PHONE_RE = re.compile(r"\+?\d[\d\s-]{7,}\d")

CAT_RULES = [
    (re.compile(r"quran|islam|muslim|namaz|allah|madrasa|deen", re.I), "Islamic"),
    (re.compile(r"scholarship", re.I), "Scholarship"),
    (re.compile(r"pubg|bgmi|free fire|gaming|gamer|minecraft|clan|squad|ludo", re.I), "Gaming"),
    (re.compile(r"cricket|football|padel|tennis|hockey|ipl|psl|fifa|sport|gym|fitness|yoga", re.I), "Sports"),
    (re.compile(r"crypto|bitcoin|forex|trading|signal|binance|nifty|banknifty|share market|stock", re.I), "Crypto"),
    (re.compile(r"earn|earning|money online|work from home|online work|passive income", re.I), "Online Earning"),
    (re.compile(r"job|career|vacancy|recruit|hiring|naukri|rojgar|placement|interview", re.I), "Jobs"),
    (re.compile(r"freelanc", re.I), "Freelance"),
    (re.compile(r"real estate|property|plot|flat|apartment|housing", re.I), "Real Estate"),
    (re.compile(r"buy|sell|rent|bazaar|market place|marketplace|olx|deal|offer|shop|store", re.I), "Buy & Sell"),
    (re.compile(r"business|startup|entrepreneur|investor|import|export|wholesale", re.I), "Business"),
    (re.compile(r"study|school|college|university|exam|teacher|tuition|tuition|tutor|ssc|neet|jee|iit|academic|spoken english|learn english|course|class|coaching|admission|student", re.I), "Education"),
    (re.compile(r"movie|film|drama|netflix|music|song|meme|funny|comedy|entertainment|tiktok|youtube", re.I), "Entertainment"),
    (re.compile(r"health|medical|doctor|hospital|clinic|dental|pharma", re.I), "Health"),
    (re.compile(r"news|breaking|headlines|update", re.I), "News"),
    (re.compile(r"cook|food|recipe|kitchen|biryani", re.I), "Cooking"),
    (re.compile(r"poet|shayari|shayri|ghazal|nazm", re.I), "Poetry"),
    (re.compile(r"travel|visa|tourism|tour|ticket|flight|immigration", re.I), "Travel"),
    (re.compile(r"girl|boy|friend|dating|matrimonial|rishta|masti|shugal|gup ?shup|chat", re.I), "Friendship"),
]
CTRY_RULES = [
    (re.compile(r"qatar|doha", re.I), "QA"),
    (re.compile(r"pakistan|lahore|karachi|islamabad|peshawar|quetta|punjab|sindh|baloch", re.I), "PK"),
    (re.compile(r"india|indian|delhi|mumbai|chennai|kolkata|bangalore|hyderabad|ahmedabad|pune|kerala|tamil|hindi|bharat", re.I), "IN"),
    (re.compile(r"bangladesh|dhaka|bangla", re.I), "BD"),
    (re.compile(r"\b usa\b|america|united states|new york|texas|california", re.I), "US"),
    (re.compile(r"\buk\b|london|england|britain|british", re.I), "GB"),
    (re.compile(r"dubai|abu dhabi|\buae\b|emirates", re.I), "AE"),
    (re.compile(r"saudi|riyadh|jeddah", re.I), "SA"),
    (re.compile(r"canada|toronto|vancouver", re.I), "CA"),
    (re.compile(r"australia|sydney|melbourne", re.I), "AU"),
    (re.compile(r"nigeria|lagos", re.I), "NG"),
    (re.compile(r"kenya|nairobi", re.I), "KE"),
    (re.compile(r"nepal|kathmandu", re.I), "NP"),
    (re.compile(r"sri lanka|colombo|lanka", re.I), "LK"),
    (re.compile(r"philippines|manila|pinoy", re.I), "PH"),
    (re.compile(r"indonesia|jakarta", re.I), "ID"),
    (re.compile(r"malaysia|kuala lumpur", re.I), "MY"),
    (re.compile(r"germany|berlin|deutschland", re.I), "DE"),
    (re.compile(r"france|paris", re.I), "FR"),
    (re.compile(r"italy|rome|milan", re.I), "IT"),
    (re.compile(r"spain|madrid|barcelona", re.I), "ES"),
    (re.compile(r"turkey|istanbul", re.I), "TR"),
    (re.compile(r"oman|muscat", re.I), "OM"),
    (re.compile(r"kuwait", re.I), "KW"),
    (re.compile(r"bahrain", re.I), "BH"),
    (re.compile(r"south africa", re.I), "ZA"),
]

def categorize(name, default_cat):
    for rx, cat in CAT_RULES:
        if rx.search(name):
            return cat
    return default_cat

def detect_country(name, default_ctry):
    for rx, c in CTRY_RULES:
        if rx.search(name):
            return c
    return default_ctry

def load_dedupe():
    s = set()
    with open(DEDUP) as f:
        for line in f:
            c = line.strip()
            if c:
                s.add(c)
    return s

def fetch(url, tries=3):
    for i in range(tries):
        try:
            r = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "30", url],
                               capture_output=True, text=True, timeout=40)
            if r.returncode == 0 and len(r.stdout) > 1000:
                return r.stdout
        except Exception:
            pass
        time.sleep(2)
    return ""

def clean_text(t):
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmllib.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def extract(page_html):
    """Return list of (name, code). Name = text of enclosing li/tr/p before the anchor."""
    items = []
    # split into blocks to localize names
    blocks = re.split(r"</(?:li|tr|p|div)>", page_html, flags=re.I)
    for blk in blocks:
        m = CODE_RE.search(blk)
        if not m:
            continue
        code = m.group(1)
        # remove the anchor tag itself, take remaining text as name
        blk2 = re.sub(r"<a\b[^>]*>.*", "", blk, flags=re.I | re.S)
        name = clean_text(blk2)
        # trim trailing separators like '-' '–' '|'
        name = re.sub(r"[\s\-–—|:>»]+$", "", name).strip()
        # if name too long, take last 120 chars (name usually right before link)
        if len(name) > 120:
            name = name[-120:].strip()
        items.append((name, code))
    return items

def verify(code):
    url = "https://chat.whatsapp.com/" + code
    try:
        r = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "20", url],
                           capture_output=True, text=True, timeout=30)
        body = r.stdout
        if not body:
            return False, ""
        mt = re.search(r'<meta property="og:title" content="([^"]*)"', body)
        title = htmllib.unescape(mt.group(1)).strip() if mt else ""
        if "Couldn't look up link" in body:
            return False, ""
        if title:
            return True, title
        return False, ""
    except Exception:
        return False, ""

def main():
    pages_file = sys.argv[1] if len(sys.argv) > 1 else WORK + "/pages.json"
    out_prefix = sys.argv[2] if len(sys.argv) > 2 else WORK + "/r1"
    extra_dedupe = sys.argv[3] if len(sys.argv) > 3 else None
    dedupe = load_dedupe()
    if extra_dedupe:
        for line in open(extra_dedupe):
            c = line.strip()
            if c:
                dedupe.add(c)
    print("dedupe loaded:", len(dedupe), flush=True)
    pages = json.load(open(pages_file))
    seen = set()
    candidates = []  # (name, code, category, country, source_page)
    for p in pages:
        url, cat, ctry = p["url"], p["category"], p["country"]
        html = fetch(url)
        print(f"fetched {url} bytes={len(html)}", flush=True)
        if not html:
            continue
        for name, code in extract(html):
            if code in dedupe or code in seen:
                continue
            seen.add(code)
            candidates.append((name, code, cat, ctry, url))
    print("candidates:", len(candidates), flush=True)
    manual_file = sys.argv[4] if len(sys.argv) > 4 else WORK + "/manual.json"
    try:
        manual_items = json.load(open(manual_file))
    except Exception:
        manual_items = []
    for m in manual_items:
        if m["code"] not in dedupe and m["code"] not in seen:
            seen.add(m["code"])
            candidates.append((m["name"], m["code"], m["category"], m["country"], m["source_page"]))
    print("candidates+manual:", len(candidates), flush=True)
    verified, pending, rejected = [], [], []
    for name, code, cat, ctry, url in candidates:
        ok, title = verify(code)
        time.sleep(0.5)
        if not ok:
            pending.append({"code": code, "source_page": url, "note": "fetch ok but og:title empty/dead"})
            print(f"DEAD {code} name={name[:40]}", flush=True)
            continue
        if PORN_RE.search(name) or PORN_RE.search(title):
            rejected.append({"code": code, "name": name})
            print(f"PORN-BLOCK {code} name={name[:40]}", flush=True)
            continue
        if PHONE_RE.search(name):
            name = re.sub(r"\+?\d[\d\s-]{7,}\d", "", name).strip()
        verified.append({"name": name or title,
                         "category": categorize(name or title, cat),
                         "country": detect_country(name or title, ctry),
                         "description": "", "image": "",
                         "invite": "https://chat.whatsapp.com/" + code,
                         "_ogtitle": title, "_src": url})
        print(f"LIVE {code} name={name[:40]}", flush=True)
    json.dump(verified, open(out_prefix + "_verified_raw.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(out_prefix + "_pending_raw.json", "w"), ensure_ascii=False, indent=1)
    json.dump(rejected, open(out_prefix + "_rejected_raw.json", "w"), ensure_ascii=False, indent=1)
    print(f"done: verified={len(verified)} pending={len(pending)} rejected={len(rejected)}", flush=True)

if __name__ == "__main__":
    main()
