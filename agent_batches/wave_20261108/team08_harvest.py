#!/usr/bin/env python3
"""Team 08 wave 20261108 slice-08 harvester. Stdlib+requests only."""
import json, re, time, sys, html, random
from urllib.parse import urlparse, urljoin
import requests
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}
WUA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
       "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
       "Accept-Language": "en-US,en;q=0.9"}

def log(msg):
    print(msg, flush=True)
    try:
        with open(BASE + "team08-harvest-log.txt", "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass

def write_json_retry(path, data):
    txt = json.dumps(data, ensure_ascii=False, indent=1)
    for i in range(6):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            return True
        except Exception as e:
            log(f"WRITE RETRY {i} {path}: {e}")
            time.sleep(2)
    return False

leads = json.load(open(BASE + "leads_slice_08.json"))
union = set(json.load(open(BASE + "dedupe_union.json")))
log(f"leads={len(leads)} union={len(union)}")
slice_urls = set(e["url"] for e in leads)

SKIP_SUB = ["groupwa.link", "whts.club", "groupda.pk",
            "grouplink.com.in/kota-coaching", "grouplink.com.in/bank-exam",
            "groupjoin.link/country/nigeria"]
# groupjoin Nigeria deep pagination retired per rule 5; other groupjoin ok

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})\b")
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
OGTITLE_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', re.I)
OGTITLE_RE2 = re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', re.I)
TAG_RE = re.compile(r"<[^>]+>")

def clean_text(s):
    s = html.unescape(TAG_RE.sub(" ", s or ""))
    return re.sub(r"\s+", " ", s).strip()

ADULT_EMOJI = ["🥵","🍆","🍑","🔞","💦","👅","👄","💋"]
BLOCK_WORDS = [r"\bxxx\b", r"\bporn\b", r"\bsex\b", r"escort", r"call girl", r"call-girl",
               r"paypal loader", r"bitfinex", r"counterfeit currency", r"carding",
               r"onlyfans", r"hentai", r"\bxxxvideo", r"sex video", r"adult video",
               r"fake currency", r"money mule", r"whatsapp channel"]
def blocked(text):
    t = (text or "").lower()
    if any(e in text for e in ADULT_EMOJI):
        return True
    for p in BLOCK_WORDS:
        if re.search(p, t):
            return True
    return False

CAT_KW = [
    (r"scholarship", "Scholarship"),
    (r"study abroad|study-abroad", "Scholarship"),
    (r"crypto|bitcoin|binance|usdt|forex trad", "Crypto"),
    (r"online earning|earn money|earning|make money|earning app", "Online Earning"),
    (r"freelance|fiverr|upwork", "Freelance"),
    (r"real estate|property|plot|house for sale", "Real Estate"),
    (r"buy.?sell|buy and sell|shopping|buying selling", "Buy & Sell"),
    (r"stock market|finance|investment|invest", "Finance"),
    (r"islamic|quran|muslim|tabligh|religious|naat|madrasa", "Islamic"),
    (r"poetry|shayari|shayri|urdu poetry|punjabi poetry", "Poetry"),
    (r"cooking|recipe|food", "Cooking"),
    (r"travel|tourism|tour", "Travel"),
    (r"health|fitness|medical|doctor", "Health"),
    (r"technology|tech |programming|coding|software", "Technology"),
    (r"university|college|school|education|study|exam|coaching|student|admission|bank exam|kota", "Education"),
    (r"job|career|govt|government job|hiring|vacancy", "Jobs"),
    (r"cricket|football|soccer|sports|ipl|psl|fifa", "Sports"),
    (r"pubg|free fire|gaming|game|bgmi|esports", "Gaming"),
    (r"movie|film|music|song|entertainment|netflix|bollywood|hollywood|tamil movie", "Entertainment"),
    (r"news|breaking", "News"),
    (r"funny|joke|joker|meme|comedy", "Funny"),
    (r"girl|friendship|friend|socialite|dating", "Friendship"),
    (r"business", "Business"),
    (r"community|social", "Community & Social"),
]
def infer_category(ctx):
    t = (ctx or "").lower()
    for pat, cat in CAT_KW:
        if re.search(pat, t):
            return cat
    return "Community & Social"

COUNTRY_KW = [
    ("pakistan|pakistani|lahore|karachi|punjabi|urdu|sindh", "PK"),
    ("india|indian|kerala|tamil|kota", "IN"),
    ("nigeria|nigerian", "NG"),
    ("kenya|kenyan", "KE"),
    ("ghana", "GH"),
    ("south africa|south-africa", "ZA"),
    ("sri lanka|sri-lanka", "LK"),
    ("bangladesh|bangladeshi", "BD"),
    ("saudi|riyadh|jeddah", "SA"),
    ("uae|dubai|emirates|abu dhabi", "AE"),
    ("egypt|egyptian|cairo", "EG"),
    ("indonesia|indonesian", "ID"),
    ("philippines|filipino", "PH"),
    ("vietnam|vietnamese", "VN"),
    ("malaysia|malaysian", "MY"),
    ("tanzania", "TZ"),
    ("zimbabwe", "ZW"),
    ("kuwait", "KW"),
    ("algeria", "DZ"),
    ("bahrain", "BH"),
    ("iraq", "IQ"),
    ("yemen", "YE"),
    ("nepal", "NP"),
    ("turkey|turkish", "TR"),
]
def infer_country(ctx):
    t = (ctx or "").lower()
    for pat, cc in COUNTRY_KW:
        if re.search(pat, t):
            return cc
    return "International"

# ---------- Phase 1: fetch listing pages ----------
candidates = {}   # code -> {"ctx": str, "src_url": str}
new_leads = {}    # url -> label
attempted = []
skipped_retired = []
fetch_fail = []
s = requests.Session()
s.headers.update(UA)

for idx, entry in enumerate(leads):
    url = entry["url"]
    if any(x in url for x in SKIP_SUB):
        skipped_retired.append(url)
        log(f"[{idx}] SKIP retired {url}")
        continue
    attempted.append(url)
    try:
        r = s.get(url, timeout=25, allow_redirects=True)
        if r.status_code != 200 or not r.text or len(r.text) < 500:
            fetch_fail.append((url, r.status_code, len(r.text or "")))
            log(f"[{idx}] FETCH {r.status_code} len={len(r.text or '')} {url}")
            continue
        text = r.text
        mtitle = TITLE_RE.search(text)
        page_title = clean_text(mtitle.group(1)) if mtitle else ""
        codes = CODE_RE.findall(text)
        fresh = [c for c in dict.fromkeys(codes) if c not in union and c not in candidates]
        log(f"[{idx}] OK {r.status_code} len={len(text)} codes={len(codes)} fresh={len(fresh)} title={page_title[:80]} {url}")
        # context per code: preceding text snippet
        for code in fresh:
            # find first occurrence position
            mm = re.search(r"chat\.whatsapp\.com/(?:invite/)?" + re.escape(code), text)
            start = max(0, mm.start() - 600) if mm else 0
            snippet = clean_text(text[start:mm.start()]) if mm else ""
            ctx = (page_title + " | " + url + " | " + snippet[-400:])
            candidates[code] = {"ctx": ctx, "src_url": url}
        # harvest new listing-page leads: same-domain internal links
        dom = urlparse(url).netloc
        for href in dict.fromkeys(HREF_RE.findall(text)):
            if href.startswith("#") or href.startswith("javascript:"):
                continue
            absu = urljoin(url, href)
            p = urlparse(absu)
            if p.netloc != dom:
                continue
            if "chat.whatsapp.com" in absu:
                continue
            low = absu.lower()
            if any(k in low for k in ["whatsapp-group", "whatsapp_group", "/category/", "/country/",
                                       "group-links", "grouplinks", "groups/", "/tag/", "page=",
                                       "whatsapp-group-links"]):
                if absu not in slice_urls and absu not in new_leads and absu != url:
                    new_leads[absu] = dom
        time.sleep(0.4)
    except Exception as e:
        fetch_fail.append((url, "EXC", str(e)[:120]))
        log(f"[{idx}] EXC {type(e).__name__} {str(e)[:120]} {url}")
        time.sleep(0.5)

log(f"PHASE1 done attempted={len(attempted)} skipped_retired={len(skipped_retired)} fetch_fail={len(fetch_fail)} candidates={len(candidates)} new_leads={len(new_leads)}")
write_json_retry(BASE + "team08-candidates.json", candidates)
write_json_retry(BASE + "team08-newleads.json", [{"url": u, "source": lbl} for u, lbl in new_leads.items()])

# ---------- Phase 2: verify codes ----------
verified = []
pending = []
seen_codes = set()

def check_code(code):
    info = candidates[code]
    ctx = info["ctx"]
    # pacing
    time.sleep(0.6)
    title = ""
    status = None
    err = None
    for attempt in range(2):
        try:
            ws = requests.Session()
            ws.headers.update(WUA)
            r = ws.get(f"https://chat.whatsapp.com/{code}", timeout=20, allow_redirects=True)
            status = r.status_code
            if status == 200:
                m = OGTITLE_RE.search(r.text) or OGTITLE_RE2.search(r.text)
                title = html.unescape(m.group(1)).strip() if m else ""
                if title:
                    break
                # empty title: retry once after pause
                time.sleep(3)
            else:
                break
        except Exception as e:
            err = str(e)[:120]
            time.sleep(2)
    return code, title, status, err

codes_list = list(candidates.keys())
log(f"PHASE2 verifying {len(codes_list)} codes")
import threading
lock = threading.Lock()
count = [0]
def worker(code):
    c, title, status, err = check_code(code)
    with lock:
        count[0] += 1
        n = count[0]
    if err and not title and status is None:
        pending.append({"code": c, "reason": "transport", "err": err, "ctx": candidates[c]["ctx"]})
        log(f"[{n}/{len(codes_list)}] PENDING transport {c} err={err}")
        return
    if status != 200 or not title:
        log(f"[{n}/{len(codes_list)}] DEAD status={status} title_empty code={c}")
        return
    low = title.lower()
    if title in ("WhatsApp Group", "Join this group on WhatsApp", "WhatsApp", "Join group on WhatsApp"):
        log(f"[{n}/{len(codes_list)}] DEAD generic title={title!r} code={c}")
        return
    if "channel" in low:
        log(f"[{n}/{len(codes_list)}] DROP channel title={title!r} code={c}")
        return
    if blocked(title) or blocked(candidates[c]["ctx"][:200] + " " + title):
        # only block on title/name itself for emoji/xxx etc; ctx block check limited to title to avoid false positives from page noise
        if blocked(title):
            log(f"[{n}/{len(codes_list)}] DROP blocked title={title!r} code={c}")
            return
    name = title.strip()
    if len(name) < 2 or len(name) > 120:
        log(f"[{n}/{len(codes_list)}] DROP bad name len title={title!r} code={c}")
        return
    cat = infer_category(candidates[c]["ctx"] + " " + name)
    cc = infer_country(candidates[c]["ctx"] + " " + name)
    desc = f"Join {name}, a WhatsApp group listed under {cat}. Connect with members, share updates and stay in touch with the community."
    verified.append({"name": name, "category": cat, "country": cc,
                     "description": desc, "invite": f"https://chat.whatsapp.com/{c}", "image": ""})
    log(f"[{n}/{len(codes_list)}] LIVE {name!r} cat={cat} cc={cc} code={c}")

with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(worker, codes_list))

# dedupe verified by code (already unique) and sort
verified_sorted = sorted(verified, key=lambda x: x["invite"])
pending_out = []
for p in pending:
    c = p["code"]
    ctx = candidates[c]["ctx"]
    cat = infer_category(ctx)
    cc = infer_country(ctx)
    pending_out.append({"name": "Pending group", "category": cat, "country": cc,
                        "description": "Join this WhatsApp group listed under " + cat + ".",
                        "invite": f"https://chat.whatsapp.com/{c}", "image": "", "reason": "transport"})

write_json_retry(BASE + "team08-leads-harvest-h.json", verified_sorted)
write_json_retry(BASE + "team08-leads-harvest-h-pending.json", pending_out)
write_json_retry(BASE + "team08-leads-harvest-h-leads.json",
                 [{"url": u, "source": lbl} for u, lbl in list(new_leads.items())[:300]])
log(f"DONE attempted={len(attempted)} skipped_retired={len(skipped_retired)} fetch_fail={len(fetch_fail)} candidates={len(candidates)} verified={len(verified_sorted)} pending={len(pending_out)} new_leads={len(new_leads)}")
log("SKIPPED_RETIRED: " + json.dumps(skipped_retired))
log("FETCH_FAIL: " + json.dumps(fetch_fail)[:3000])
