#!/usr/bin/env python3
"""TEAM37 — parse user-submitted-groups directory cards, dedupe, verify, merge."""
import re, json, html as h, os
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261104")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

PORN_RE = re.compile(
    r'porn|pornhub|\bxxx\b|nude|sex\s*video|escort|call\s*girl|callgirls?|\bfuck\b|dick|pussy|boobs?|\banal\b|bokep|'
    r'مزا\s*دینے|مزہ\s*دینے|مزے\s*دینے|🥵|🍆|🍑|🔞|💦|👅|👄|💋', re.I)
SCAM_RE = re.compile(r'satta|matka|fix\s*number|hyip|double\s*your\s*money|paypal\s*receiver|money\s*mule|loader', re.I)

CAT_KW = [
    (r'\bcricket\b|ipl|football|soccer|sport', "Sports"),
    (r'\bgaming\b|game\b|pubg|free fire|bgmi', "Gaming"),
    (r'\bjob\b|jobs\b|hiring|career|vacan|recruit|naukri|rozgar', "Jobs"),
    (r'study|educat|school|college|university|learn|tutorial|\bgk\b|notes|coaching|exam|ssc|upsc', "Education"),
    (r'movie|film|netflix|cinema', "Movies"),
    (r'music|song|\bdj\b', "Music"),
    (r'news|newspaper|daily', "News"),
    (r'islam|quran|hadith|ramadan|allah|muhammad|masjid|\bdua\b|namaz|naat', "Islamic"),
    (r'business|trade|import|export|entrepreneur|startup|solar', "Business"),
    (r'forex|crypto|bitcoin|binance|invest', "Crypto"),
    (r'finance|trading|money|earning|loan', "Finance"),
    (r'sell|buy|shop|market|store|deal\b|bazaar|olx|toys|online store', "Buy-Sell"),
    (r'health|doctor|medical|fitness|diet|hospital', "Health"),
    (r'tech|software|\bapp\b|\bai\b|computer|programming', "Technology"),
    (r'travel|tour|hotel|flight|visa', "Travel"),
    (r'food|recipe|cook|restaurant|biryani', "Food"),
    (r'\bpet\b|\bcat\b|\bdog\b|animal', "Pets"),
    (r'funny|joke|meme|comedy|humor|shayari', "Funny"),
    (r'girl|ladies|women|bhabhi', "Girls"),
    (r'friend|dosti|\bdost\b|masti|gupshup|chat\b', "Friendship"),
    (r'pakistan|india|kenya|\buk\b|canada|german|arab|america|china|dubai|tamil|telugu|kannada|bangla|punjab|sindh|karachi|lahore|desi|kuwait|bangalore|delhi|pune|karnataka', "Regional"),
]
SITE_CAT_MAP = {"business":"Business","jobs":"Jobs","education":"Education","entertainment":"Entertainment",
 "friendship":"Friendship","news":"News","sports":"Sports","gaming":"Gaming","technology":"Technology",
 "health":"Health","travel":"Travel","music":"Music","movies":"Movies","food":"Food","finance":"Finance",
 "crypto":"Crypto","islamic":"Islamic","funny":"Funny","community":"Community","shopping":"Buy-Sell",
 "buy-sell":"Buy-Sell","girls":"Girls","regional":"Regional","dating":"Friendship"}
def refine_cat(name, badge):
    b = (badge or "").strip().lower()
    if b in SITE_CAT_MAP: return SITE_CAT_MAP[b]
    t = (name + " " + b).lower()
    for pat, cat in CAT_KW:
        if re.search(pat, t): return cat
    return "Other"

def clean(s):
    return re.sub(r'\s+', ' ', h.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

pg = open(os.path.join(W, "team37_pages", "user-submitted-groups.html"),
          encoding='utf-8', errors='replace').read()
cards = re.split(r'<div class="group-info"', pg)[1:]
print("cards found:", len(cards))
union = set(json.load(open(os.path.join(W, "dedupe_union.json"))))

cands, seen = [], set()
porn_drops = scam_drops = skipped = 0
for c in cards:
    m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})\?', c)
    if not m: skipped += 1; continue
    code = m.group(1)
    if code in union or code in seen: continue
    nm = re.search(r'<h3><a[^>]*>(.*?)</a></h3>', c, re.S)
    name = clean(nm.group(1)) if nm else ""
    if PORN_RE.search(name): porn_drops += 1; continue
    if SCAM_RE.search(name): scam_drops += 1; continue
    img = re.search(r'<img[^>]*src="([^"]+)"', c)
    image = h.unescape(img.group(1)).replace('&#038;', '&') if img else ""
    if 'whatsapp.net' not in image or 'static.whatsapp.net' in image: image = ""
    badge = re.search(r'class="category-badge">([^<]+)<', c)
    badge = clean(badge.group(1)) if badge else ""
    seen.add(code)
    cands.append((name, code, badge, image))
print(f"fresh candidates={len(cands)} porn={porn_drops} scam={scam_drops} skipped_nohref={skipped}")

TLS = threading.local()
def session():
    if not getattr(TLS, 's', None):
        s = requests.Session(); s.headers.update({"User-Agent": UA}); TLS.s = s
    return TLS.s
def og_title(code):
    try:
        r = session().get(f"https://chat.whatsapp.com/{code}", timeout=55)
        m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', r.text)
        return h.unescape(m.group(1)).strip() if m else ""
    except Exception:
        return None

def work(item):
    return item, og_title(item[1])

COUNTRY_WORD = {"PK":"Pakistani","IN":"Indian","KE":"Kenyan","KW":"Kuwaiti","GB":"British",
 "DE":"German","CA":"Canadian","BD":"Bangladeshi","SA":"Arabic","US":"American","CN":"Chinese",
 "AE":"Dubai","International":"international"}
DESC_TPL = [
 "Active {catw} WhatsApp group: {t}. Join to chat, share updates and connect with members every day.",
 "Join this {catw} WhatsApp group and connect with members around {t}. Daily chat, updates and friendly discussion.",
 "{t} — a lively {catw} WhatsApp group where members chat, share news and stay connected.",
]
def make_desc(name, title, cat):
    t = re.sub(r'\s+', ' ', (title or name or "").strip())
    if len(t) > 70: t = t[:70].rsplit(' ', 1)[0]
    return DESC_TPL[hash(t) % 3].format(catw=cat.lower(), t=t)

verified = json.load(open(os.path.join(W, "team37-wglfinder.json")))
pending = json.load(open(os.path.join(W, "team37-unverified-pending.json")))
porn2 = 0
with ThreadPoolExecutor(max_workers=24) as ex:
    results = list(ex.map(work, cands))
for (name, code, badge, image), title in results:
    if title is None:
        pending.append({"name": name or f"Group {code[:6]}", "category": refine_cat(name, badge),
                        "country": "International",
                        "description": "WhatsApp group from a user-submitted directory listing.",
                        "invite": f"https://chat.whatsapp.com/{code}", "image": image,
                        "note": "transport failure"})
        print("PENDING", code, name[:40])
    elif title == "":
        print("DEAD", code, name[:40])
    else:
        if PORN_RE.search(title): porn2 += 1; print("PORN DROP (og:title)", code); continue
        nm = re.sub(r'\s+', ' ', (name if name and len(name) >= 3 else title)).strip()
        cat = refine_cat(nm, badge)
        verified.append({"name": nm, "category": cat, "country": "International",
                         "description": make_desc(nm, title, cat),
                         "invite": f"https://chat.whatsapp.com/{code}", "image": image})
        print("OK", code, nm[:45])
json.dump(verified, open(os.path.join(W, "team37-wglfinder.json"), "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(os.path.join(W, "team37-unverified-pending.json"), "w"), ensure_ascii=False, indent=1)
print(f"TOTAL verified={len(verified)} pending={len(pending)} porn_total_extra={porn2}")
