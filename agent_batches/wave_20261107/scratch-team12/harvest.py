#!/usr/bin/env python3
"""Team 12 wave 20261107: whatsappkanali + linkado harvest + verify."""
import json, re, time, html, requests
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261107/"
SCRATCH = WAVE + "scratch-team12/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}

CANON = ["Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health",
         "Business","Gaming","Friendship","Community & Social","Online Earning","Crypto","Cooking",
         "Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell","Finance","Funny"]
BLOCK_WORDS = ["porn","xxx","nudes","nude","sex video","escort","call girl","randi","fuck","dick",
               "pussy","boobs","anal","bokep","onlyfans","sexchat","sexy video","xxx video"]
BLOCK_EMOJI = ["🥵","🍆","🍑","🔞","💦","👅","👄","💋"]
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{7,}\d")
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})\b")
INVITE_RE = re.compile(r"^https://chat\.whatsapp\.com/(invite/)?[A-Za-z0-9]{22}$")

union = set(json.load(open(WAVE + "dedupe_union.json")))
print("union:", len(union), flush=True)

WK_CAT = {"sohbet":"Friendship","is-ilanlari":"Jobs","egitim":"Education","spor":"Sports",
 "teknoloji":"Technology","haber":"News","din":"Islamic","ticaret":"Business","eglence":"Entertainment",
 "film-dizi":"Entertainment","kitap":"Education","topluluk":"Community & Social","alisveris":"Buy & Sell",
 "e-ticaret":"Business","emlak":"Real Estate","meslek-gruplari":"Business","kisisel-gelisim":"Education",
 "hobi":"Community & Social","universite":"Education","ogrenci":"Education","egitim-ders":"Education",
 "yemek":"Cooking","futbol":"Sports","muzik":"Entertainment","indirim":"Buy & Sell","saglik":"Health",
 "gezi-seyahat":"Travel","kultur-sanat":"Community & Social","hizmetler":"Business",
 "freelance-is":"Freelance","tanisma-arkadas":"Friendship","oyun":"Gaming","saglik-gruplari":"Health"}
LK_CAT = {"amizade":"Friendship","namoro":"Friendship","dinheiro":"Finance","games":"Gaming",
 "figurinhas":"Funny","comprar-e-venda":"Buy & Sell","trabalho":"Jobs","educacao":"Education",
 "tecnologia":"Technology","esportes":"Sports","musica":"Entertainment","series":"Entertainment",
 "fitness":"Health","religiao":"Community & Social","links":"Community & Social",
 "carros":"Community & Social","cidades":"Community & Social","lgbt":"Community & Social",
 "moda-e-beleza":"Community & Social","politica":"News","status":"Community & Social"}

def clean_name(n):
    n = html.unescape(n or "").strip()
    n = re.sub(r"\s+", " ", n)
    return n

def blocked(name, ogtitle=""):
    s = (name + " " + ogtitle).lower()
    if any(w in s for w in BLOCK_WORDS): return True
    if any(e in (name + ogtitle) for e in BLOCK_EMOJI): return True
    return False

def get(sess, url, timeout=60):
    for attempt in range(2):
        try:
            r = sess.get(url, headers=UA, timeout=timeout)
            if r.status_code == 200 and len(r.content) > 500:
                return r.text
            print("  fetch non-200/small:", url, r.status_code, len(r.content), flush=True)
            return None
        except Exception as e:
            print("  fetch err:", url, repr(e)[:120], flush=True)
            time.sleep(2)
    return None

# ---------------- whatsappkanali ----------------
def parse_wk(text, default_cat):
    """Return list of dicts {name, category, code, image}."""
    out = []
    for m in CODE_RE.finditer(text):
        code = m.group(1)
        start = max(0, m.start() - 1500)
        win = text[start:m.start()]
        # last title/categorySlug/imageUrl before this invite
        titles = re.findall(r'\\"title\\":\\"((?:[^\\]|\\.)*?)\\"', win)
        slugs = re.findall(r'\\"categorySlug\\":\\"([^\\"]*)\\"', win)
        imgs = re.findall(r'\\"imageUrl\\":\\"([^\\"]*)\\"', win)
        name = clean_name(titles[-1]) if titles else ""
        slug = slugs[-1] if slugs else ""
        cat = WK_CAT.get(slug, default_cat or "Community & Social")
        out.append({"name": name, "category": cat, "code": code, "slug": slug})
    return out

sess = requests.Session()
wk_raw = {}  # code -> record
wk_urls = ["https://whatsappkanali.com/?page=1", "https://whatsappkanali.com/?page=2",
           "https://whatsappkanali.com/?page=3",
           "https://whatsappkanali.com/kategori/sohbet?page=4",
           "https://whatsappkanali.com/kategori/is-ilanlari?page=3",
           "https://whatsappkanali.com/kategori/egitim?page=3",
           "https://whatsappkanali.com/kategori/spor?page=2",
           "https://whatsappkanali.com/kategori/teknoloji?page=2",
           "https://whatsappkanali.com/kategori/haber?page=2",
           "https://whatsappkanali.com/kategori/din?page=2",
           "https://whatsappkanali.com/kategori/ticaret?page=2",
           "https://whatsappkanali.com/kategori/eglence?page=2",
           "https://whatsappkanali.com/kategori/film-dizi?page=2",
           "https://whatsappkanali.com/kategori/kitap?page=2",
           "https://whatsappkanali.com/kategori/topluluk?page=2",
           "https://whatsappkanali.com/kategori/alisveris?page=2",
           "https://whatsappkanali.com/kategori/e-ticaret?page=2",
           "https://whatsappkanali.com/kategori/emlak?page=2",
           "https://whatsappkanali.com/kategori/meslek-gruplari?page=2",
           "https://whatsappkanali.com/kategori/kisisel-gelisim?page=2",
           "https://whatsappkanali.com/kategori/hobi?page=2",
           "https://whatsappkanali.com/kategori/universite?page=2",
           "https://whatsappkanali.com/kategori/ogrenci?page=2",
           "https://whatsappkanali.com/kategori/egitim-ders?page=2",
           "https://whatsappkanali.com/kategori/yemek?page=2",
           "https://whatsappkanali.com/kategori/futbol?page=2",
           "https://whatsappkanali.com/kategori/muzik?page=2",
           "https://whatsappkanali.com/kategori/indirim?page=2",
           "https://whatsappkanali.com/kategori/saglik?page=2",
           "https://whatsappkanali.com/kategori/gezi-seyahat?page=2",
           "https://whatsappkanali.com/kategori/kultur-sanat?page=2",
           "https://whatsappkanali.com/kategori/hizmetler?page=2",
           "https://whatsappkanali.com/kategori/freelance-is?page=2",
           "https://whatsappkanali.com/kategori/tanisma-arkadas?page=2",
           "https://whatsappkanali.com/kategori/oyun?page=2",
           "https://whatsappkanali.com/sehir/istanbul/oyun",
           "https://whatsappkanali.com/sehir/kocaeli/sohbet",
           "https://whatsappkanali.com/sehir/tekirdag/sohbet"]
wk_failed = []
def fetch_wk(url):
    slug = None
    mm = re.search(r"/kategori/([^/?]+)", url)
    if mm: slug = mm.group(1)
    elif "/oyun" in url: slug = "oyun"
    elif "/sohbet" in url: slug = "sohbet"
    ss = requests.Session()
    t = get(ss, url, timeout=45)
    return url, slug, t
with ThreadPoolExecutor(max_workers=8) as ex:
    for url, slug, t in ex.map(fetch_wk, wk_urls):
        if t is None:
            wk_failed.append(url); continue
        recs = parse_wk(t, WK_CAT.get(slug) if slug else None)
        print(f"WK {url} -> {len(recs)} records", flush=True)
        for r in recs:
            if r["code"] not in wk_raw and r["name"]:
                wk_raw[r["code"]] = r
print("WK unique named records:", len(wk_raw), flush=True)
json.dump(wk_raw, open(SCRATCH + "wk_raw.json", "w"), ensure_ascii=False, indent=1)

# ---------------- linkado ----------------
def lk_listing_ids(text):
    return list(dict.fromkeys(re.findall(r"/grupo/([0-9a-f]{24})", text)))

lk_urls = ["https://linkado.app/?page=1", "https://linkado.app/?page=2", "https://linkado.app/?page=3"]
for cat in ["amizade","namoro","dinheiro","games","figurinhas","comprar-e-venda","trabalho",
            "educacao","tecnologia","esportes","musica","series","fitness","religiao","links",
            "carros","cidades","lgbt","moda-e-beleza","politica","status"]:
    lk_urls.append(f"https://linkado.app/categoria/{cat}")

lk_ids = {}  # gid -> category
lk_failed = []
def fetch_lk(url):
    cat = "Community & Social"
    mm = re.search(r"/categoria/([^/?]+)", url)
    if mm: cat = LK_CAT.get(mm.group(1), "Community & Social")
    ss = requests.Session()
    t = get(ss, url, timeout=45)
    return url, cat, t
with ThreadPoolExecutor(max_workers=8) as ex:
    for url, cat, t in ex.map(fetch_lk, lk_urls):
        if t is None:
            lk_failed.append(url); continue
        ids = lk_listing_ids(t)
        print(f"LK {url} -> {len(ids)} grupo ids", flush=True)
        for gid in ids:
            lk_ids.setdefault(gid, cat)
print("LK unique grupo ids:", len(lk_ids), flush=True)
json.dump(lk_ids, open(SCRATCH + "lk_ids.json", "w"), ensure_ascii=False, indent=1)

# fetch grupo pages (RSC fetch first, fallback full page)
def fetch_grupo(gid):
    url = f"https://linkado.app/grupo/{gid}"
    try:
        r = sess.get(url, headers={**UA, "RSC": "1", "Next-Router-State-Tree": "%5B%22%22%2C%7B%7D%5D"}, timeout=45)
        if r.status_code == 200 and len(r.content) > 500:
            return r.text
    except Exception:
        pass
    try:
        r = sess.get(url, headers=UA, timeout=45)
        if r.status_code == 200 and len(r.content) > 500:
            return r.text
    except Exception as e:
        print("  grupo fetch err:", gid, repr(e)[:100], flush=True)
    return None

def parse_lk_grupo(text):
    m = CODE_RE.search(text)
    if not m: return None
    code = m.group(1)
    # name: og:title in head, or title in RSC
    og = re.search(r'<meta property=\\"og:title\\" content=\\"([^\\"]*)\\"', text)
    if not og:
        og = re.search(r'<meta property="og:title" content="([^"]*)"', text)
    name = clean_name(og.group(1)) if og else ""
    if not name:
        tm = re.findall(r'\\"title\\":\\"((?:[^\\]|\\.)*?)\\"', text)
        name = clean_name(tm[-1]) if tm else ""
    # description from RSC if present
    desc = ""
    dm = re.search(r'\\"description\\":\\"((?:[^\\]|\\.){0,400}?)\\"', text)
    if dm: desc = clean_name(dm.group(1))[:300]
    img = ""
    im = re.search(r'https://img\.linkado\.app/groups/[^"\\ ]+', text)
    return {"name": name, "code": code, "desc": desc}

lk_raw = {}
gids = list(lk_ids.items())
def fetch_one(item):
    gid, cat = item
    t = fetch_grupo(gid)
    if t is None: return None
    p = parse_lk_grupo(t)
    if p and p["name"]:
        p["category"] = cat
        return p
    return None
with ThreadPoolExecutor(max_workers=8) as ex:
    for n, p in enumerate(ex.map(fetch_one, gids), 1):
        if p and p["code"] not in lk_raw:
            lk_raw[p["code"]] = p
        if n % 50 == 0:
            print(f"LK grupo progress {n}/{len(gids)} raw={len(lk_raw)}", flush=True)
print("LK unique named records:", len(lk_raw), flush=True)
json.dump(lk_raw, open(SCRATCH + "lk_raw.json", "w"), ensure_ascii=False, indent=1)
print("WK failed:", wk_failed, flush=True)
print("LK failed listings:", lk_failed, flush=True)
print("HARVEST DONE", flush=True)
