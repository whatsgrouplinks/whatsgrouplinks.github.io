#!/usr/bin/env python3
"""TEAM 07 — gentle recheck of pending codes (3 workers, 60s timeout, 2s gap).
Also re-screens already-verified entries with updated patterns and fixed categories."""
import json, re, html, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG_RE2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:title"', re.I)

NEG_RE = re.compile(r'[^.!?;]*\b(no|not allowed|not allow|prohibited|strictly no|no porn|no xxx|no sex|no adult|no nude|no vulgar|sem porn|sem sexo)\b[^.!?;]*', re.I)
SCAM_PATTERNS = [
    r'\bb-?love\b', r'\bforsage\b', r'\bsheyi\b', r'\bholiverse\b', r'\bmeta-?whale\b',
    r'\bairdrop\b', r'\bbetting\b', r'bett\b', r'\bbet\b', r'aposta', r'\b1xbet\b',
    r'\bsatta\b', r'\bmatka\b', r'\bfixed match\b', r'\bcasino\b', r'clonad',
    r'\bcvv\b', r'\bdumps\b', r'vendas? de documentos?', r'documentos falsos',
    r'\b18\+', '🔞',
]
PORN_PATTERNS = [
    r'\bxxx\b', r'\bporn\b', r'\bporno\b', r'\bsex\b', r'\bsexy\b', r'\badult video\b',
    r'\bonlyfans\b', r'\bescort\b', r'\bcall girl', r'\bnude\b', r'\bdesi bhabhi\b',
    r'\bhot girl', r'\bsex video\b', r'\bviral mms\b', r'no sigilo',
]
PHONE_RE = re.compile(r'(\+?\d[\d\s-]{7,}\d)')
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

def screen(name, ogtitle):
    combined = f"{name} {ogtitle}"
    stripped = NEG_RE.sub(' ', combined)
    low = stripped.lower()
    for p in SCAM_PATTERNS:
        if re.search(p, low):
            return f"scam/fraud pattern: {p}"
    for p in PORN_PATTERNS:
        if re.search(p, low):
            return f"adult pattern: {p}"
    if PHONE_RE.search(combined) or EMAIL_RE.search(combined):
        return "personal info (phone/email) in name/title"
    return None

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
    ("Business", ["business", "entrepreneur", "startup", "marketing", "negócio", "agency", "agência"]),
    ("Buy Sell", ["buy and sell", "buy sell", "buy & sell", "for sale", "shopping", "olx", "bazar", "marketplace", "store", "desapego", "comprar", "venda", "achadinhos", "ofertas", "promo"]),
    ("Finance", ["finance", "loan", "investment", "trading", "forex", "stock", "bank", "finanças"]),
    ("Funny", ["funny", "meme", "joke", "comedy", "humor", "engraçado"]),
    ("Friendship", ["friend", "friendship", "girls", "boys", "chat", "amizade", "amigos", "meninas"]),
    ("Entertainment", ["movie", "music", "drama", "video", "song", "bollywood", "netflix", "web series", "filme", "música", "entretenimento", "séries"]),
]
COUNTRY_RULES = [
    ("PK", ["pakistan", "pakistani", "karachi", "lahore", "islamabad", "sindh", "punjab", "peshawar", "quetta", "multan", "faisalabad", "rawalpindi", "ghotki"]),
    ("IN", ["india", "indian", "kerala", "palakkad", "tamil", "telugu", "delhi", "mumbai", "kolkata", "chennai", "bangalore", "bengaluru", "hyderabad", "pune", "gujarat", "rajasthan", "bihar", "uttar pradesh"]),
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

verified = json.load(open(f"{WAVE}/team07-leads-slice7.json"))
pending = json.load(open(f"{WAVE}/team07-leads-slice7-pending.json"))
cands = {c["code"]: c for c in json.load(open(f"{WAVE}/team07-candidates.json"))}
try:
    exclusions = json.load(open(f"{WAVE}/team07-exclusions.json"))
except FileNotFoundError:
    exclusions = []
excl_codes = {e["code"] for e in exclusions}

# --- re-screen already-verified with updated patterns; fix categories ---
kept, moved = [], 0
for v in verified:
    code = v["invite"].rsplit("/", 1)[-1]
    reason = screen(v["name"], "")
    if reason and code not in excl_codes:
        exclusions.append({"code": code, "reason": reason})
        excl_codes.add(code)
        moved += 1
        continue
    c = cands.get(code, {})
    text = f"{v['name']} {c.get('page_title','')}"
    v["category"] = categorize(text)
    if not v.get("country"):
        v["country"] = country_of(text, c.get("source_url", ""))
    kept.append(v)
verified = kept
print(f"re-screened verified: kept={len(kept)} moved_to_exclusions={moved}", flush=True)

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=0))

def check_once(code):
    try:
        r = session.get(f"https://chat.whatsapp.com/{code}", headers=UA, timeout=60, allow_redirects=True)
        if r.status_code != 200:
            return r.status_code, ""
        m = OG_RE.search(r.text) or OG_RE2.search(r.text)
        return 200, html.unescape(m.group(1)).strip() if m else ""
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

new_pending, dead2, live2 = [], 0, 0
done_n = 0
t0 = time.time()

def save_all():
    with open(f"{WAVE}/team07-leads-slice7.json", "w") as f:
        json.dump(verified, f, ensure_ascii=False, indent=1)
    with open(f"{WAVE}/team07-leads-slice7-pending.json", "w") as f:
        json.dump(new_pending, f, ensure_ascii=False, indent=1)
    with open(f"{WAVE}/team07-exclusions.json", "w") as f:
        json.dump(exclusions, f, ensure_ascii=False, indent=1)
    with open(f"{WAVE}/team07-recheck-progress.json", "w") as f:
        json.dump({"rechecked": done_n, "total_pending": len(pending), "live_added": live2,
                   "dead_now": dead2, "still_pending": len(new_pending),
                   "verified_total": len(verified), "elapsed_s": round(time.time()-t0, 1)}, f, indent=1)

def worker(p):
    code = p["invite"].rsplit("/", 1)[-1]
    status, og = check(code)
    time.sleep(2.0)
    return p, code, status, og

todo = list(pending)
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(worker, p): p for p in todo}
    for fut in as_completed(futs):
        p, code, status, og = fut.result()
        done_n += 1
        if status == 0 or status in (429, 500, 502, 503, 504):
            new_pending.append(p)
        elif status == 200 and og:
            c = cands.get(code, {})
            name = clean_name(og) or clean_name(c.get("name") or "") or "WhatsApp Group"
            reason = screen(name, og)
            if reason:
                if code not in excl_codes:
                    exclusions.append({"code": code, "reason": reason})
                    excl_codes.add(code)
                dead2 += 0
                continue
            text = f"{name} {c.get('page_title','')} {og}"
            cat = categorize(text)
            cc = country_of(text, c.get("source_url", ""))
            verified.append({"name": name, "category": cat, "country": cc,
                             "description": f"Join this {cat.lower()} WhatsApp group to connect with members and stay updated.",
                             "invite": f"https://chat.whatsapp.com/{code}"})
            live2 += 1
        else:
            dead2 += 1
        if done_n % 50 == 0:
            save_all()
            print(f"recheck done={done_n}/{len(todo)} live_added={live2} dead_now={dead2} still_pending={len(new_pending)} elapsed={time.time()-t0:.0f}s", flush=True)

save_all()
print(f"RECHECK FINISHED live_added={live2} dead_now={dead2} still_pending={len(new_pending)} verified_total={len(verified)} exclusions={len(exclusions)} elapsed={time.time()-t0:.0f}s")
