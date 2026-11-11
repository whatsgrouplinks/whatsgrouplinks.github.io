#!/usr/bin/env python3
"""TEAM 07 wave 20261111 — Phase 2: slow-verify candidate codes vs chat.whatsapp.com.
Max 6 workers, >=0.6s delay between requests per worker, retry empty-og once after pause."""
import json, re, html, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG_RE2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:title"', re.I)

existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
cands = json.load(open(f"{WAVE}/team07-candidates.json"))
# dedupe vs existing + within slice
seen = set()
todo = []
for c in cands:
    code = c["code"]
    if code in existing or code in seen:
        continue
    seen.add(code)
    todo.append(c)
print(f"candidates={len(cands)} to_verify={len(todo)}", flush=True)

# ---------- content screening ----------
NEG_RE = re.compile(r'[^.!?;]*\b(no|not allowed|not allow|prohibited|strictly no|no porn|no xxx|no sex|no adult|no nude|no vulgar|sem porn|sem sexo)\b[^.!?;]*', re.I)
SCAM_PATTERNS = [
    r'\bb-?love\b', r'\bforsage\b', r'\bsheyi\b', r'\bholiverse\b', r'\bmeta-?whale\b',
    r'\bairdrop\b', r'\bbetting\b', r'\bsatta\b', r'\bmatka\b', r'\bfixed match\b',
    r'\bcasino\b', r'clonad', r'\bcvv\b', r'\bdumps\b', r'\b1xbet\b', r'\bbetway\b', r'\bdream11\b.*predict',
]
PORN_PATTERNS = [
    r'\bxxx\b', r'\bporn\b', r'\bporno\b', r'\bsex\b', r'\bsexy\b', r'\badult video\b',
    r'\bonlyfans\b', r'\bescort\b', r'\bcall girl', r'\bnude\b', r'\bdesi bhabhi\b',
    r'\bhot girl', r'\bsex video\b', r'\bviral mms\b', r'\b18\+\s*(only|video|group)',
]
PHONE_RE = re.compile(r'(\+?\d[\d\s-]{7,}\d)')
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

def screen(name, ogtitle):
    """Return exclusion reason or None. Strips negated-prohibition sentences first."""
    combined = f"{name} {ogtitle}"
    stripped = NEG_RE.sub(' ', combined)
    low = stripped.lower()
    for p in SCAM_PATTERNS:
        if re.search(p, low):
            return f"scam/betting pattern: {p}"
    for p in PORN_PATTERNS:
        if re.search(p, low):
            return f"adult pattern: {p}"
    if PHONE_RE.search(combined) or EMAIL_RE.search(combined):
        return "personal info (phone/email) in name/title"
    return None

# ---------- category / country ----------
CAT_RULES = [
    ("Scholarship", ["scholarship", "csc ", "hec ", "fully funded"]),
    ("Islamic", ["islam", "quran", "muslim", "naat", "madrasa", "allah", "deen", "hajj", "umrah", "islamic", "dua", "tilawat", "hadees", "hadith", "ramadan", "namaz", "darood"]),
    ("Online Earning", ["online earning", "earn money", "earning", "make money", "work from home", "ganhar dinheiro", "renda extra"]),
    ("Crypto", ["crypto", "bitcoin", "btc", "usdt", "binance", "criptomoeda", "cripto"]),
    ("Education", ["study", "exam", "school", "college", "university", "class ", "learn", "ielts", "academy", "teacher", "student", "notes", "mcq", "admission", "css", "pms", "matric", "inter ", "ders", "aula", "curso", "educa"]),
    ("Jobs", ["job", "jobs", "vacancy", "vacancies", "hiring", "career", "employment", "naukri", "rozgar", "vagas", "emprego"]),
    ("News", ["news", "breaking", "headline", "noticia", "notícias"]),
    ("Sports", ["cricket", "football", "soccer", "sport", "ipl", "psl", "live match", "esporte"]),
    ("Technology", ["tech", "android", "software", "computer", "programming", "python", "ai ", "hacking", "tecnologia"]),
    ("Health", ["health", "fitness", "doctor", "medical", "yoga", "weight loss", "saúde"]),
    ("Gaming", ["game", "gaming", "pubg", "free fire", "bgmi", "ludo", "jogos"]),
    ("Poetry", ["poetry", "shayari", "shair", "ghazal", "poesia"]),
    ("Cooking", ["cooking", "recipe", "food", "kitchen", "receita", "culinária"]),
    ("Travel", ["travel", "tour", "tourism", "trip", "viagem"]),
    ("Freelance", ["freelance", "fiverr", "upwork"]),
    ("Real Estate", ["real estate", "property", "plot", "house for sale", "imóveis"]),
    ("Buy Sell", ["buy and sell", "buy sell", "buy & sell", "for sale", "shopping", "olx", "bazar", "market", "store", "desapego", "comprar", "venda", "achadinhos", "ofertas", "promo"]),
    ("Finance", ["finance", "loan", "investment", "trading", "forex", "stock", "bank", "finanças"]),
    ("Funny", ["funny", "meme", "joke", "comedy", "humor", "engraçado"]),
    ("Friendship", ["friend", "friendship", "girls", "boys", "chat", "amizade", "amigos", "meninas"]),
    ("Entertainment", ["movie", "music", "drama", "video", "song", "bollywood", "netflix", "web series", "filme", "música", "entretenimento", "séries"]),
    ("Business", ["business", "entrepreneur", "startup", "marketing", "negócio"]),
]
COUNTRY_RULES = [
    ("PK", ["pakistan", "pakistani", "karachi", "lahore", "islamabad", "sindh", "punjab", "peshawar", "quetta", "multan", "faisalabad", "rawalpindi", "ghotki"]),
    ("IN", ["india", "indian", "kerala", "palakkad", "tamil", "telugu", "delhi", "mumbai", "kolkata", "chennai", "bangalore", "bengaluru", "hyderabad", "pune", "gujarat", "rajasthan", "bihar", "up ", "uttar pradesh"]),
    ("BD", ["bangladesh", "bangladeshi", "dhaka", "chittagong"]),
    ("NP", ["nepal", "nepali", "kathmandu"]),
    ("LK", ["sri lanka", "srilanka", "colombo"]),
    ("NG", ["nigeria", "nigerian", "lagos"]),
    ("KE", ["kenya", "kenyan", "nairobi"]),
    ("GH", ["ghana", "ghanaian", "accra"]),
    ("ZA", ["south africa", "johannesburg", "cape town"]),
    ("US", ["usa", "united states", "america", "american", "new york", "california", "texas"]),
    ("GB", ["uk", "united kingdom", "england", "london", "britain", "british"]),
    ("CA", ["canada", "canadian", "toronto"]),
    ("AU", ["australia", "australian", "sydney"]),
    ("BR", ["brazil", "brasil", "brazilian", "brasileiro", "são paulo", "sao paulo", "rio de janeiro"]),
    ("PT", ["portugal", "portuguese", "lisboa", "lisbon"]),
    ("TR", ["turkey", "türkiye", "turkiye", "turkish", "istanbul", "ankara"]),
    ("ID", ["indonesia", "indonesian", "jakarta"]),
    ("MY", ["malaysia", "malaysian", "kuala lumpur"]),
    ("PH", ["philippines", "filipino", "manila"]),
    ("VN", ["vietnam", "vietnamese"]),
    ("TH", ["thailand", "thai", "bangkok"]),
    ("AE", ["uae", "dubai", "abu dhabi"]),
    ("SA", ["saudi", "riyadh", "jeddah"]),
    ("EG", ["egypt", "egyptian", "cairo"]),
    ("ZW", ["zimbabwe", "harare"]),
    ("ZM", ["zambia", "lusaka"]),
    ("TZ", ["tanzania", "dar es salaam"]),
    ("UG", ["uganda", "kampala"]),
]

def categorize(text):
    low = " " + text.lower() + " "
    for cat, kws in CAT_RULES:
        for k in kws:
            if k in low:
                return cat
    return "Community & Social"

def country_of(text, source_url):
    low = " " + text.lower() + " "
    for cc, kws in COUNTRY_RULES:
        for k in kws:
            if k in low:
                return cc
    if "linkado.app" in source_url:
        return "BR"
    if "whatsappkanali.com" in source_url:
        return "TR"
    return ""

def clean_name(n):
    n = html.unescape(n or "").strip()
    n = re.sub(r'\s+', ' ', n)
    n = re.sub(r'(?i)\s*[-|–—]\s*whatsapp\s+group.*$', '', n)
    n = re.sub(r'(?i)^join\s+', '', n)
    return n[:100].strip()

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=0))

def check_once(code):
    try:
        r = session.get(f"https://chat.whatsapp.com/{code}", headers=UA, timeout=45, allow_redirects=True)
        if r.status_code != 200:
            return r.status_code, ""
        m = OG_RE.search(r.text) or OG_RE2.search(r.text)
        title = html.unescape(m.group(1)).strip() if m else ""
        return 200, title
    except Exception:
        return 0, ""

def check(code):
    status, title = check_once(code)
    if status == 0:
        time.sleep(10)
        status, title = check_once(code)
    if status == 200 and not title:
        time.sleep(8)
        status, title = check_once(code)
    return status, title

verified, pending, exclusions = [], [], []
dead = 0
done_n = 0
t0 = time.time()

# resume support
try:
    verified = json.load(open(f"{WAVE}/team07-leads-slice7.json"))
    pending = json.load(open(f"{WAVE}/team07-leads-slice7-pending.json"))
    done_codes = {v["invite"].rsplit("/", 1)[-1] for v in verified}
    n_pend = len(pending)
    # pending codes stay in todo (done_codes covers verified only) for a fresh re-check
    todo = [c for c in todo if c["code"] not in done_codes]
    pending = []
    print(f"resumed verified={len(verified)} rechecking-pending={n_pend} remaining={len(todo)}", flush=True)
except FileNotFoundError:
    pass
try:
    exclusions = json.load(open(f"{WAVE}/team07-exclusions.json"))
except FileNotFoundError:
    pass

def save_all():
    with open(f"{WAVE}/team07-leads-slice7.json", "w") as f:
        json.dump(verified, f, ensure_ascii=False, indent=1)
    with open(f"{WAVE}/team07-leads-slice7-pending.json", "w") as f:
        json.dump(pending, f, ensure_ascii=False, indent=1)
    with open(f"{WAVE}/team07-verify-progress.json", "w") as f:
        json.dump({"verified": len(verified), "pending": len(pending), "dead": dead,
                   "exclusions": len(exclusions), "elapsed_s": round(time.time()-t0, 1)}, f, indent=1)

def worker(c):
    code = c["code"]
    status, og = check(code)
    time.sleep(0.6)  # >=0.5s gap between requests per worker
    return c, status, og

with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(worker, c): c for c in todo}
    for fut in as_completed(futs):
        c, status, og = fut.result()
        done_n += 1
        code = c["code"]
        if status == 0 or status in (429, 500, 502, 503, 504):
            pending.append({"name": clean_name(c.get("name") or "") or "WhatsApp Group",
                            "category": "Community & Social", "country": "",
                            "description": "", "invite": f"https://chat.whatsapp.com/{code}",
                            "reason": f"transport failure status {status}"})
        elif status == 200 and og:
            og_clean = clean_name(og)
            name = og_clean or clean_name(c.get("name") or "")
            if not name or len(name) < 2 or "whatsapp group link" in name.lower():
                name = clean_name(c.get("page_title") or "") or "WhatsApp Group"
            reason = screen(name, og)
            if reason:
                exclusions.append({"code": code, "reason": reason})
                continue
            text = f"{name} {c.get('page_title','')} {og}"
            cat = categorize(text)
            cc = country_of(text, c.get("source_url", ""))
            desc = f"Join this {cat.lower()} WhatsApp group to connect with members and stay updated."
            verified.append({"name": name, "category": cat, "country": cc,
                             "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})
        else:
            dead += 1  # 200+empty og after retry, or 404/410 etc.
        if done_n % 50 == 0:
            save_all()
            print(f"verified-check done={done_n}/{len(todo)} live={len(verified)} pending={len(pending)} dead={dead} excl={len(exclusions)} elapsed={time.time()-t0:.0f}s", flush=True)

save_all()
with open(f"{WAVE}/team07-exclusions.json", "w") as f:
    json.dump(exclusions, f, ensure_ascii=False, indent=1)
print(f"FINISHED live={len(verified)} pending={len(pending)} dead={dead} exclusions={len(exclusions)} elapsed={time.time()-t0:.0f}s")
