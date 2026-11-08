#!/usr/bin/env python3
"""TEAM37 — parse wglfinder pages, dedupe, verify via og:title, write outputs."""
import re, json, html as h, os, time
import requests
from concurrent.futures import ThreadPoolExecutor

W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261104")
PAGES = os.path.join(W, "team37_pages")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# slug -> (category, country)
SLUG_META = {
 "pune-whatsapp-group-link": ("Regional","IN"),
 "cricket-whatsapp-group-link": ("Sports","International"),
 "ipl-2026-schedule-whatsapp-group-links": ("Sports","IN"),
 "ssc-gd-whatsapp-group-link": ("Education","IN"),
 "indian-whatsapp-group-link": ("Regional","IN"),
 "gk-whatsapp-group-link": ("Education","IN"),
 "government-job-whatsapp-group-link": ("Jobs","IN"),
 "private-job-whatsapp-group-link": ("Jobs","IN"),
 "shree-ram-sena-whatsapp-group-link-2026": ("Regional","IN"),
 "republic-day-whatsapp-group-link-2026": ("Community","IN"),
 "ayodhya-whatsapp-group-link-2026": ("Regional","IN"),
 "kenya-whatsapp-group-link": ("Regional","KE"),
 "ms-dhoni-fans-whatsapp-group-link": ("Sports","IN"),
 "india-whatsapp-group-link-2026": ("Regional","IN"),
 "kuwait-whatsapp-group-link": ("Regional","KW"),
 "bjp-whatsapp-group-link": ("Community","IN"),
 "uk-whatsapp-group-link": ("Regional","GB"),
 "ayodhya-darshan-whatsapp-group-link": ("Regional","IN"),
 "college-whatsapp-group-link": ("Education","International"),
 "adre-whatsapp-group-link": ("Education","IN"),
 "upsc-whatsapp-group-link": ("Education","IN"),
 "valentines-day-whatsapp-group-links-2026": ("Friendship","International"),
 "funny-whatsapp-group-link": ("Funny","International"),
 "tamil-whatsapp-group-link": ("Regional","IN"),
 "bajrang-dal-indore-whatsapp-group-link-2026": ("Regional","IN"),
 "germany-whatsapp-group-link": ("Regional","DE"),
 "telegu-whatsapp-group-link": ("Regional","IN"),
 "canada-whatsapp-group-link": ("Regional","CA"),
 "bangladesh-whatsapp-group-link": ("Regional","BD"),
 "arabic-whatsapp-group-link": ("Regional","SA"),
 "delhi-job-whatsapp-group-link": ("Jobs","IN"),
 "daily-newspaper-whatsapp-group-link": ("News","International"),
 "bangalore-whatsapp-group-link": ("Regional","IN"),
 "pakistani-whatsapp-group-link": ("Regional","PK"),
 "bajrang-dal-whatsapp-group-link": ("Regional","IN"),
 "binance-whatsapp-group-link": ("Crypto","International"),
 "job-whatsapp-group-link": ("Jobs","International"),
 "america-whatsapp-group-link": ("Regional","US"),
 "active-whatsapp-group-links": ("Other","International"),
 "china-toys-whatsapp-group-link": ("Buy-Sell","CN"),
 "china-whatsapp-group-link": ("Regional","CN"),
 "dubai-whatsapp-group-link": ("Regional","AE"),
 "kannada-whatsapp-group-link": ("Regional","IN"),
 "bangalore-jobs-whatsapp-group-link": ("Jobs","IN"),
 "user-submitted-groups": ("Other","International"),
}

PORN_RE = re.compile(
    r'porn|pornhub|\bxxx\b|nude|sex\s*video|escort|call\s*girl|callgirls?|\bfuck\b|dick|pussy|boobs?|\banal\b|bokep|'
    r'مزا\s*دینے|مزہ\s*دینے|مزے\s*دینے|🥵|🍆|🍑|🔞|💦|👅|👄|💋',
    re.I)
SCAM_RE = re.compile(
    r'satta|matka|fix\s*number|hyip|double\s*your\s*money|paypal\s*receiver|money\s*mule|loader',
    re.I)

def clean_name(txt):
    txt = h.unescape(re.sub(r'<[^>]+>', ' ', txt))
    txt = re.sub(r'\s+', ' ', txt).strip()
    txt = re.sub(r'[⇒=>»\-–|·:\s]+$', '', txt).strip()
    return txt

def parse_page(path):
    pg = open(path, encoding='utf-8', errors='replace').read()
    rows = []
    # find every data-group-link occurrence (skip /invite/ channels)
    for m in re.finditer(r'data-group-link="(https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24}))"', pg):
        url, code = m.group(1), m.group(2)
        pos = m.start()
        # enclosing <li> ?
        li_start = pg.rfind('<li', 0, pos)
        name = ''
        if li_start != -1:
            li_end = pg.find('</li>', pos)
            block = pg[li_start:li_end if li_end != -1 else pos]
            a_pos = block.find('<a ')
            pre = block[:a_pos if a_pos != -1 else len(block)]
            name = clean_name(pre)
            if len(name) > 90:
                name = name[:90].rsplit(' ', 1)[0]
        rows.append((name, code, url))
    # page title as fallback name context
    t = re.search(r'<title>(.*?)</title>', pg, re.S)
    ptitle = clean_name(t.group(1)) if t else ''
    return rows, ptitle

union = set(json.load(open(os.path.join(W, "dedupe_union.json"))))
print("union size:", len(union), flush=True)

cands = []  # (name, code, slug, cat, country)
seen = set()
porn_drops = 0
scam_drops = 0
for slug in open(os.path.join(PAGES, "slug_list.txt")).read().split():
    path = os.path.join(PAGES, slug + ".html")
    if not os.path.exists(path) or os.path.getsize(path) < 5000:
        print(f"SKIP (no fetch) {slug}", flush=True)
        continue
    cat, country = SLUG_META[slug]
    rows, ptitle = parse_page(path)
    new = 0
    for name, code, url in rows:
        if code in union or code in seen:
            continue
        if PORN_RE.search(name or ''):
            porn_drops += 1
            continue
        if SCAM_RE.search(name or ''):
            scam_drops += 1
            continue
        seen.add(code)
        cands.append((name, code, slug, cat, country))
        new += 1
    print(f"{slug}: rows={len(rows)} fresh={new}", flush=True)

json.dump([[n, c, s, k, y] for n, c, s, k, y in cands],
          open(os.path.join(W, "team37_candidates.json"), "w"), ensure_ascii=False)
print(f"candidates={len(cands)} porn_dropped={porn_drops} scam_dropped={scam_drops}", flush=True)

# ---------- verification ----------
import threading
TLS = threading.local()
def session():
    if not getattr(TLS, 's', None):
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept": "text/html,*/*;q=0.9"})
        TLS.s = s
    return TLS.s

def og_title(code):
    try:
        r = session().get(f"https://chat.whatsapp.com/{code}", timeout=55)
        t = r.text
        m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', t)
        if not m:
            m = re.search(r"<meta[^>]+property='og:title'[^>]+content='([^']*)'", t)
        return h.unescape(m.group(1)).strip() if m else ""
    except Exception:
        return None

CAT_KW = [
    (r'\bcricket\b|ipl|football|soccer|sport', "Sports"),
    (r'\bgaming\b|game\b|pubg|free fire|bgmi', "Gaming"),
    (r'\bjob\b|jobs\b|hiring|career|vacan|recruit|test prep|exam|ssc|upsc|naukri|rozgar', "Jobs"),
    (r'study|educat|school|college|university|learn|tutorial|\bgk\b|notes|coaching', "Education"),
    (r'movie|film|netflix|cinema', "Movies"),
    (r'music|song|\bdj\b', "Music"),
    (r'news|newspaper|daily', "News"),
    (r'islam|quran|hadith|ramadan|allah|muhammad|masjid|\bdua\b|namaz|naat', "Islamic"),
    (r'business|trade|import|export|entrepreneur|startup', "Business"),
    (r'forex|crypto|bitcoin|binance|invest', "Crypto"),
    (r'finance|trading|money|earning|loan', "Finance"),
    (r'sell|buy|shop|market|store|deal\b|bazaar|olx|toys', "Buy-Sell"),
    (r'health|doctor|medical|fitness|diet|hospital', "Health"),
    (r'tech|software|\bapp\b|\bai\b|computer|programming', "Technology"),
    (r'travel|tour|hotel|flight|visa', "Travel"),
    (r'food|recipe|cook|restaurant|biryani', "Food"),
    (r'\bpet\b|\bcat\b|\bdog\b|animal', "Pets"),
    (r'funny|joke|meme|comedy|humor', "Funny"),
    (r'girl|ladies|women|bhabhi', "Girls"),
    (r'friend|dosti|\bdost\b|masti|gupshup|chat\b', "Friendship"),
    (r'pakistan|india|kenya|\buk\b|canada|german|arab|america|china|dubai|tamil|telugu|kannada|bangla|punjab|sindh|karachi|lahore|desi|kuwait|bangalore|delhi|pune', "Regional"),
]
def refine_cat(name, slug_cat):
    t = (name or "").lower()
    for pat, cat in CAT_KW:
        if re.search(pat, t):
            return cat
    return slug_cat

COUNTRY_WORD = {"PK":"Pakistani","IN":"Indian","KE":"Kenyan","KW":"Kuwaiti","GB":"British",
 "DE":"German","CA":"Canadian","BD":"Bangladeshi","SA":"Arabic","US":"American","CN":"Chinese",
 "AE":"Dubai","International":"international"}

DESC_TPL = [
 "Active {catw} WhatsApp group for {cw} members: {t}. Join to chat, share updates and connect with the {cw} community.",
 "Join this {catw} WhatsApp group and connect with {cw} members around {t}. Daily chat, updates and friendly discussion.",
 "{t} — a lively {catw} WhatsApp group for {cw} people to chat, share news and stay connected every day.",
]
def make_desc(name, title, cat, country):
    t = (title or name or "").strip()
    t = re.sub(r'\s+', ' ', t)
    if len(t) > 70:
        t = t[:70].rsplit(' ', 1)[0]
    cw = COUNTRY_WORD.get(country, country)
    catw = cat.lower()
    tpl = DESC_TPL[hash(t) % 3]
    return tpl.format(catw=catw, cw=cw, t=t)

verified, pending = [], []
porn2 = 0
def work(item):
    name, code, slug, scat, country = item
    title = og_title(code)
    return item, title

with ThreadPoolExecutor(max_workers=24) as ex:
    results = list(ex.map(work, cands))

for (name, code, slug, scat, country), title in results:
    if title is None:
        pending.append({"name": name or f"Group {code[:6]}", "category": scat,
                        "country": country, "description": f"WhatsApp group from a {scat.lower()} directory page for {COUNTRY_WORD.get(country, country)} members.",
                        "invite": f"https://chat.whatsapp.com/{code}", "image": "",
                        "note": "transport failure"})
        print("PENDING", code, flush=True)
    elif title == "":
        print("DEAD", code, flush=True)
    else:
        if PORN_RE.search(title):
            porn2 += 1
            print("PORN DROP (og:title)", code, flush=True)
            continue
        nm = name if name and len(name) >= 3 else title
        nm = re.sub(r'\s+', ' ', nm).strip()
        cat = refine_cat(nm, scat)
        verified.append({"name": nm, "category": cat, "country": country,
                         "description": make_desc(nm, title, cat, country),
                         "invite": f"https://chat.whatsapp.com/{code}", "image": ""})
        print("OK", code, nm[:45], flush=True)

json.dump(verified, open(os.path.join(W, "team37-wglfinder.json"), "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(os.path.join(W, "team37-unverified-pending.json"), "w"), ensure_ascii=False, indent=1)
print(f"VERIFIED={len(verified)} PENDING={len(pending)} porn_total={porn_drops+porn2} scam_dropped={scam_drops}", flush=True)
