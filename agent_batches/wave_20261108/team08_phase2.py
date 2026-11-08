#!/usr/bin/env python3
"""Team 08 phase-2 resume: verify remaining candidates, faster timeouts."""
import json, re, time, html, threading
import requests
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
WUA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
       "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
       "Accept-Language": "en-US,en;q=0.9"}
OGTITLE_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', re.I)
OGTITLE_RE2 = re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', re.I)
ADULT_EMOJI = ["🥵","🍆","🍑","🔞","💦","👅","👄","💋"]
BLOCK_WORDS = [r"\bxxx\b", r"\bporn\b", r"\bsex\b", r"escort", r"call girl", r"call-girl",
               r"paypal loader", r"bitfinex", r"counterfeit currency", r"carding",
               r"onlyfans", r"hentai", r"\bxxxvideo", r"sex video", r"adult video",
               r"fake currency", r"money mule"]
def blocked(text):
    t = (text or "").lower()
    if any(e in text for e in ADULT_EMOJI):
        return True
    return any(re.search(p, t) for p in BLOCK_WORDS)

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

# reuse category/country inference from phase1 by importing logic inline (copy)
CAT_KW = [
    (r"scholarship", "Scholarship"), (r"study abroad|study-abroad", "Scholarship"),
    (r"crypto|bitcoin|binance|usdt|forex trad", "Crypto"),
    (r"online earning|earn money|earning|make money|earning app", "Online Earning"),
    (r"freelance|fiverr|upwork", "Freelance"),
    (r"real estate|property|plot|house for sale", "Real Estate"),
    (r"buy.?sell|buy and sell|shopping|buying selling", "Buy & Sell"),
    (r"stock market|finance|investment|invest", "Finance"),
    (r"islamic|quran|muslim|tabligh|religious|naat|madrasa", "Islamic"),
    (r"poetry|shayari|shayri|urdu poetry|punjabi poetry", "Poetry"),
    (r"cooking|recipe|food", "Cooking"), (r"travel|tourism|tour", "Travel"),
    (r"health|fitness|medical|doctor", "Health"),
    (r"technology|tech |programming|coding|software", "Technology"),
    (r"university|college|school|education|study|exam|coaching|student|admission|bank exam|kota", "Education"),
    (r"job|career|govt|government job|hiring|vacancy", "Jobs"),
    (r"cricket|football|soccer|sports|ipl|psl|fifa", "Sports"),
    (r"pubg|free fire|gaming|game|bgmi|esports", "Gaming"),
    (r"movie|film|music|song|entertainment|netflix|bollywood|hollywood|tamil movie", "Entertainment"),
    (r"news|breaking", "News"), (r"funny|joke|joker|meme|comedy", "Funny"),
    (r"girl|friendship|friend|socialite|dating", "Friendship"),
    (r"business", "Business"), (r"community|social", "Community & Social"),
]
def infer_category(ctx):
    t = (ctx or "").lower()
    for pat, cat in CAT_KW:
        if re.search(pat, t):
            return cat
    return "Community & Social"
COUNTRY_KW = [
    ("pakistan|pakistani|lahore|karachi|punjabi|urdu|sindh", "PK"),
    ("india|indian|kerala|tamil|kota", "IN"), ("nigeria|nigerian", "NG"),
    ("kenya|kenyan", "KE"), ("ghana", "GH"), ("south africa|south-africa", "ZA"),
    ("sri lanka|sri-lanka", "LK"), ("bangladesh|bangladeshi", "BD"),
    ("saudi|riyadh|jeddah", "SA"), ("uae|dubai|emirates|abu dhabi", "AE"),
    ("egypt|egyptian|cairo", "EG"), ("indonesia|indonesian", "ID"),
    ("philippines|filipino", "PH"), ("vietnam|vietnamese", "VN"),
    ("malaysia|malaysian", "MY"), ("tanzania", "TZ"), ("zimbabwe", "ZW"),
    ("kuwait", "KW"), ("algeria", "DZ"), ("bahrain", "BH"), ("iraq", "IQ"),
    ("yemen", "YE"), ("nepal", "NP"), ("turkey|turkish", "TR"),
]
def infer_country(ctx):
    t = (ctx or "").lower()
    for pat, cc in COUNTRY_KW:
        if re.search(pat, t):
            return cc
    return "International"

candidates = json.load(open(BASE + "team08-candidates.json"))
new_leads = json.load(open(BASE + "team08-newleads.json"))

# recover completed from log
verified = []
pending = []
done = set()
live_re = re.compile(r"LIVE '(.*)' cat=(.+) cc=(\S+) code=([A-Za-z0-9]{22})")
for line in open(BASE + "team08-harvest-log.txt", encoding="utf-8", errors="ignore"):
    m = live_re.search(line)
    if m:
        name, cat, cc, code = m.groups()
        done.add(code)
        verified.append({"name": name, "category": cat, "country": cc,
                         "description": f"Join {name}, a WhatsApp group listed under {cat}. Connect with members, share updates and stay in touch with the community.",
                         "invite": f"https://chat.whatsapp.com/{code}", "image": ""})
        continue
    m2 = re.search(r"code=([A-Za-z0-9]{22})", line)
    if m2 and ("DEAD" in line or "DROP" in line):
        done.add(m2.group(1))
    elif m2 and "PENDING" in line:
        code = m2.group(1)
        done.add(code)
        ctx = candidates.get(code, {}).get("ctx", "")
        cat = infer_category(ctx); cc = infer_country(ctx)
        pending.append({"name": "Pending group", "category": cat, "country": cc,
                        "description": "Join this WhatsApp group listed under " + cat + ".",
                        "invite": f"https://chat.whatsapp.com/{code}", "image": "", "reason": "transport"})
log(f"RESUME recovered verified={len(verified)} pending={len(pending)} done={len(done)} of {len(candidates)}")

remaining = [c for c in candidates if c not in done]
log(f"REMAINING {len(remaining)}")

def check_code(code):
    time.sleep(0.5)
    title = ""; status = None; err = None
    for attempt in range(2):
        try:
            ws = requests.Session(); ws.headers.update(WUA)
            r = ws.get(f"https://chat.whatsapp.com/{code}", timeout=12, allow_redirects=True)
            status = r.status_code
            if status == 200:
                m = OGTITLE_RE.search(r.text) or OGTITLE_RE2.search(r.text)
                title = html.unescape(m.group(1)).strip() if m else ""
                if title:
                    break
                time.sleep(1.5)
            else:
                break
        except Exception as e:
            err = str(e)[:120]
            time.sleep(1.5)
    return code, title, status, err

lock = threading.Lock()
count = [0]
def worker(code):
    c, title, status, err = check_code(code)
    with lock:
        count[0] += 1; n = count[0]
    total = len(remaining)
    if err and not title and status is None:
        ctx = candidates[c]["ctx"]
        cat = infer_category(ctx); cc = infer_country(ctx)
        pending.append({"name": "Pending group", "category": cat, "country": cc,
                        "description": "Join this WhatsApp group listed under " + cat + ".",
                        "invite": f"https://chat.whatsapp.com/{c}", "image": "", "reason": "transport"})
        log(f"[R{n}/{total}] PENDING transport {c} err={err}")
        return
    if status != 200 or not title:
        log(f"[R{n}/{total}] DEAD status={status} title_empty code={c}")
        return
    if title in ("WhatsApp Group", "Join this group on WhatsApp", "WhatsApp", "Join group on WhatsApp"):
        log(f"[R{n}/{total}] DEAD generic title={title!r} code={c}")
        return
    if "channel" in title.lower():
        log(f"[R{n}/{total}] DROP channel title={title!r} code={c}")
        return
    if blocked(title):
        log(f"[R{n}/{total}] DROP blocked title={title!r} code={c}")
        return
    name = title.strip()
    if len(name) < 2 or len(name) > 120:
        log(f"[R{n}/{total}] DROP bad name len title={title!r} code={c}")
        return
    cat = infer_category(candidates[c]["ctx"] + " " + name)
    cc = infer_country(candidates[c]["ctx"] + " " + name)
    verified.append({"name": name, "category": cat, "country": cc,
                     "description": f"Join {name}, a WhatsApp group listed under {cat}. Connect with members, share updates and stay in touch with the community.",
                     "invite": f"https://chat.whatsapp.com/{c}", "image": ""})
    log(f"[R{n}/{total}] LIVE {name!r} cat={cat} cc={cc} code={c}")

with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(worker, remaining))

verified_sorted = sorted(verified, key=lambda x: x["invite"])
write_json_retry(BASE + "team08-leads-harvest-h.json", verified_sorted)
write_json_retry(BASE + "team08-leads-harvest-h-pending.json", pending)
write_json_retry(BASE + "team08-leads-harvest-h-leads.json",
                 [{"url": u, "source": lbl} for u, lbl in new_leads[:300]])
log(f"PHASE2 DONE verified={len(verified_sorted)} pending={len(pending)} new_leads_file={min(300, len(new_leads))} of {len(new_leads)} raw")
