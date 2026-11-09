#!/usr/bin/env python3
"""Team07 phase 2: extract structured candidates from fetched listing pages."""
import json, re, os, html, subprocess
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WAVE, "team07_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

leads = json.load(open(os.path.join(WAVE, "leads_slice_07.json")))
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

def read(idx):
    p = os.path.join(RAW, f"{idx:03d}.html")
    return open(p, encoding="utf-8", errors="ignore").read() if os.path.exists(p) else ""

def norm_code(code):
    code = code.split("?")[0].split("#")[0].strip().rstrip("/")
    return code

def clean(s):
    if not s: return ""
    s = html.unescape(s)
    s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
    s = s.replace("\\n", " ").replace("\\", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

CATMAP = {
    "dating": "Friendship", "friendship": "Friendship", "friends": "Friendship",
    "gaming": "Gaming", "games": "Gaming", "game": "Gaming",
    "education": "Education", "study": "Education", "learning": "Education",
    "earning": "Online Earning", "earn money": "Online Earning", "make money": "Online Earning",
    "business": "Business", "entrepreneurship": "Business", "negocios": "Business",
    "finance": "Finance", "crypto": "Finance", "stocks": "Finance", "investing": "Finance",
    "buy sell": "Buy Sell", "buy & sell": "Buy Sell", "marketplace": "Buy Sell", "compras": "Buy Sell",
    "islamic": "Islamic", "religion": "Islamic", "spiritual": "Islamic",
    "entertainment": "Entertainment", "movies": "Entertainment", "music": "Entertainment",
    "jobs": "Jobs", "career": "Jobs", "employment": "Jobs",
    "technology": "Technology", "tech": "Technology", "programming": "Technology",
    "funny": "Funny", "comedy": "Funny", "memes": "Funny", "humor": "Funny",
    "sports": "Sports", "fitness": "Sports", "football": "Sports", "cricket": "Sports",
    "health": "Health", "fitness": "Health",
    "news": "News", "politics": "News",
    "community": "Community & Social", "social": "Community & Social",
}

def map_cat(text):
    if not text: return "Community & Social"
    t = text.lower()
    for k, v in CATMAP.items():
        if k in t: return v
    return "Community & Social"

COUNTRY_NAMES = {"nigeria":"NG","india":"IN","pakistan":"PK","kenya":"KE","ghana":"GH","bangladesh":"BD",
 "usa":"US","united states":"US","uk":"GB","united kingdom":"GB","brazil":"BR","brasil":"BR","spain":"ES",
 "mexico":"MX","colombia":"CO","argentina":"AR","peru":"PE","chile":"CL","venezuela":"VE","ecuador":"EC",
 "bolivia":"BO","paraguay":"PY","uruguay":"UY","costa rica":"CR","panama":"PA","guatemala":"GT",
 "el salvador":"SV","cuba":"CU","dominican republic":"DO","nepal":"NP","sri lanka":"LK","indonesia":"ID",
 "philippines":"PH","egypt":"EG","south africa":"ZA","morocco":"MA","turkey":"TR","uae":"AE","saudi arabia":"SA"}

recs = {}  # code -> record
def add(code, name, category, country, desc, src):
    code = norm_code(code)
    if not code or len(code) < 15 or len(code) > 30: return
    if not re.fullmatch(r"[A-Za-z0-9_-]+", code): return
    if code in recs: return
    recs[code] = {"code": code, "name": clean(name)[:120], "category": category,
                   "country": country, "description": clean(desc)[:300], "src": src}

# ---- A. groupssor API (idx 69) ----
try:
    j = json.loads(read(69))
    for g in j:
        link = g.get("inviteLink", "")
        m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9_-]+)", link)
        if not m: continue
        add(m.group(1), g.get("name", ""), map_cat(g.get("category", "")),
            (g.get("country") or "IN")[:2].upper(), g.get("description", ""), "groupssor-api")
    print("groupssor records:", len(recs))
except Exception as e:
    print("groupssor err", e)

# ---- B. groupjoin.link (idx 0-24): RSC JSON blobs (backslash-escaped) ----
gj_pat = re.compile(r'"group_title":"((?:[^"\\]|\\.)*)".{0,2000}?"group_desc":"((?:[^"\\]|\\.)*)".{0,3000}?"link":"https://chat\.whatsapp\.com/([A-Za-z0-9_-]+)', re.S)
for idx in range(0, 25):
    t = read(idx).replace('\\"', '"')
    if not t: continue
    src_url = leads[idx]["url"]
    country = "KE" if "kenya" in src_url.lower() else ("GH" if "ghana" in src_url.lower() else "IN")
    for m in gj_pat.finditer(t):
        title = m.group(1)
        desc = m.group(2)
        seg = t[m.start():m.start()+4000]
        cm = re.search(r'"category_name":"([^"]+)"', seg)
        co = re.search(r'"iso2":"([A-Z]{2})"', seg)
        cat = map_cat(cm.group(1)) if cm else "Community & Social"
        cc = co.group(1) if co else country
        add(m.group(3), title, cat, cc, desc, f"groupjoin:{idx}")
print("after groupjoin:", len(recs))

# ---- C. ongrupos (idx 126-160): /grupo/<code> + card title ----
for idx in range(126, 161):
    t = read(idx)
    if not t: continue
    # find all grupo links with preceding title: split by card anchors
    for m in re.finditer(r'href="https://ongrupos\.com/grupo/([A-Za-z0-9_-]{20,})"', t):
        code = m.group(1)
        # title: nearest preceding <h2/h3> or alt text within 1500 chars before
        seg = t[max(0, m.start()-2000):m.start()]
        titles = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', seg, re.S)
        name = clean(re.sub(r"<[^>]+>", " ", titles[-1])) if titles else ""
        add(code, name, "Community & Social", "BR", "", f"ongrupos:{idx}")
print("after ongrupos:", len(recs))

# ---- D. groupsinvite (idx 162-183): /group/link/<code> cards ----
for idx in range(162, 184):
    t = read(idx)
    if not t: continue
    # split into group-item blocks
    blocks = re.split(r'<div class="group-item">', t)
    for b in blocks[1:]:
        lm = re.search(r'/group/link/([A-Za-z0-9_-]{15,})/', b)
        if not lm: continue
        nm = re.search(r'class="group-name-link"[^>]*>([^<]+)</a>', b)
        dm = re.search(r'data-full-description="([^"]*)"', b)
        cm = re.search(r'class="category-chip"[^>]*>([^<]+)</a>', b)
        co = re.search(r'/group/country/([^/]+)/', b)
        country = COUNTRY_NAMES.get(clean(co.group(1)).lower(), "IN") if co else "IN"
        add(lm.group(1), nm.group(1) if nm else "", map_cat(cm.group(1) if cm else ""),
            country, dm.group(1) if dm else "", f"groupsinvite:{idx}")
print("after groupsinvite:", len(recs))

# ---- E. igrupos detail pages ----
ig_ids = {}
for idx in range(71, 126):
    t = read(idx)
    if not t: continue
    src_url = leads[idx]["url"]
    cc = "ES"
    mm = re.search(r"/ciudades/([A-Z]{2})/", src_url)
    if mm: cc = mm.group(1)
    elif "chicago" in src_url or "illinois" in src_url or "berwyn" in src_url or "cicero" in src_url or "elmwood" in src_url or "forest-park" in src_url or "lockport" in src_url or "oak-park" in src_url or "stickney" in src_url: cc = "US"
    for gid in set(re.findall(r'/grupo/(\d{4,})', t)):
        ig_ids.setdefault(gid, cc)
print("igrupos unique detail ids:", len(ig_ids))

IGDIR = os.path.join(WAVE, "team07_raw_igrupos")
os.makedirs(IGDIR, exist_ok=True)
def fetch_ig(item):
    gid, cc = item
    out = os.path.join(IGDIR, f"{gid}.html")
    if not (os.path.exists(out) and os.path.getsize(out) > 0):
        try:
            subprocess.run(["curl", "-sS", "-L", "--max-time", "40", "-A", UA,
                            "-o", out, f"https://www.igrupos.com/grupo/{gid}"],
                           capture_output=True, timeout=55)
        except Exception:
            return gid, cc, None
    try:
        t = open(out, encoding="utf-8", errors="ignore").read()
    except Exception:
        return gid, cc, None
    m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', t)
    if not m: return gid, cc, None
    title = re.search(r'<title>([^<]*)</title>', t)
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    return gid, cc, (m.group(1), clean(title.group(1)) if title else "",
                     clean(desc.group(1)) if desc else "")

with ThreadPoolExecutor(max_workers=6) as ex:
    ig_results = list(ex.map(fetch_ig, sorted(ig_ids.items())))
ig_ok = 0
for gid, cc, r in ig_results:
    if r:
        add(r[0], r[1], "Community & Social", cc, r[2], f"igrupos:{gid}")
        ig_ok += 1
print("igrupos details with code:", ig_ok, "total recs:", len(recs))

# ---- dedupe vs existing ----
fresh = {c: r for c, r in recs.items() if c not in existing}
print("fresh (not in existing 106883):", len(fresh), " already-known:", len(recs) - len(fresh))
json.dump(list(fresh.values()), open(os.path.join(WAVE, "team07_extracted.json"), "w"), indent=1, ensure_ascii=False)
json.dump(list(recs.values()), open(os.path.join(WAVE, "team07_extracted_all.json"), "w"), indent=1, ensure_ascii=False)
print("saved team07_extracted.json")
