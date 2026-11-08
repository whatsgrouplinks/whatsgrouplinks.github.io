#!/usr/bin/env python3
"""Team 32 — Arabic residual retry: re-verify Nov-3 team38b pending candidates (scribd doc 695394718, Egypt/Arabic)."""
import json, re, html, os, threading, time
from concurrent.futures import ThreadPoolExecutor

WD = os.path.dirname(os.path.abspath(__file__))
SRC = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/team38b-unverified-pending.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})")
OG_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I | re.S)
OG_RE2 = re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', re.I | re.S)

PORN_PAT = re.compile(r"(porn|pornhub|xxx|nude|sex\s*video|escort|call\s*girl|fuck|dick|pussy|boobs|anal|bokep|سكس|سكسي|جنس|افلام جنس|🥵|🍆|🍑|🔞|💦|👅|👄|💋|مزا\s*دینے|مزہ\s*دینے)", re.I)

CATS = [
    ("Islamic", ["دين","ديني","اسلام","إسلام","قرآن","قران","صلاة","صلي","مسجد","ذكر","دعاء","سنة","حديث","رمضان","توحيد","فقه","سيرة","quran","islam","islamic"]),
    ("Jobs", ["وظيف","وظائف","شغل","توظيف","job","jobs","وظيفة","فرص عمل"]),
    ("Buy-Sell", ["بيع","شراء","سوق","عقار","سيارات","متجر","تسويق","بيع وشراء"]),
    ("Sports", ["رياضة","رياضي","رياضية","كرة","كوره","رياضه","sport","كرة القدم"]),
    ("News", ["اخبار","أخبار","خبر","news"]),
    ("Education", ["مدرسة","مدارس","تعليم","دراسة","جامعة","طلاب","دروس","مذاكرة","education"]),
    ("Girls", ["بنات","فتيات","بنوت","girl"]),
    ("Friendship", ["احباب","تعارف","صداقة","اصدقاء","أصدقاء","شباب","صحبة","صداقات","friend"]),
    ("Business", ["تجارة","أعمال","مشروع","استثمار","ربح","business","تجاره"]),
    ("Health", ["صحة","صحي","طب","دواء","دكتور","صحه","health"]),
    ("Movies", ["افلام","أفلام","مسلسلات","فيلم","movie"]),
    ("Music", ["موسيقى","اغاني","أغاني","غناء","music"]),
    ("Food", ["اكل","أكل","طبخ","مطبخ","وصفات","food"]),
    ("Funny", ["ضحك","نكت","فكاهة","مضحك","funny"]),
    ("Technology", ["تقنية","تكنولوجيا","هاتف","جوال","كمبيوتر","برمجة","tech"]),
    ("Crypto", ["عملات","بيتكوين","تداول","فوركس","crypto","forex"]),
    ("Travel", ["سفر","سياحة","رحلات","travel"]),
    ("Pets", ["حيوانات","قطط","كلاب","pets"]),
    ("Finance", ["مال","تمويل","finance"]),
]
COUNTRIES = [
    ("EG", ["مصر","مصري","مصرية","egypt"]),
    ("SA", ["السعودية","السعوديه","سعودي","سعودية","saudi"]),
    ("MA", ["المغرب","المغربية","المغربيه","مغربي","morocco"]),
    ("DZ", ["الجزائر","جزائري","algeria"]),
    ("TN", ["تونس","تونسي","tunisia"]),
    ("AE", ["الإمارات","الامارات","دبي","اماراتي","uae","dubai"]),
    ("YE", ["اليمن","يمني","yemen"]),
    ("PS", ["فلسطين","فلسطيني","palestine"]),
    ("JO", ["الأردن","الاردن","أردني","jordan"]),
    ("SY", ["سوريا","سوري","syria"]),
    ("IQ", ["العراق","عراقي","iraq"]),
    ("KW", ["الكويت","كويتي","kuwait"]),
    ("QA", ["قطر","قطري","qatar"]),
    ("BH", ["البحرين","bahrain"]),
    ("OM", ["عمان","oman"]),
    ("LB", ["لبنان","لبناني","lebanon"]),
    ("LY", ["ليبيا","libya"]),
    ("SD", ["السودان","سوداني","sudan"]),
    ("MR", ["موريتانيا","mauritania"]),
]
CN_WORD = {"EG":"Egypt","SA":"Saudi Arabia","MA":"Morocco","DZ":"Algeria","TN":"Tunisia",
           "AE":"the UAE","YE":"Yemen","PS":"Palestine","JO":"Jordan","SY":"Syria","IQ":"Iraq",
           "KW":"Kuwait","QA":"Qatar","BH":"Bahrain","OM":"Oman","LB":"Lebanon","LY":"Libya",
           "SD":"Sudan","MR":"Mauritania","International":"Arabic-speaking"}

def map_cat(name):
    nl = name.lower()
    for cat, kws in CATS:
        for kw in kws:
            if kw in nl:
                return cat
    return "Community"

def map_country(name):
    nl = name.lower()
    for cc, kws in COUNTRIES:
        for kw in kws:
            if kw in nl:
                return cc
    return "International"

class RateLimited(Exception): pass

_tls = threading.local()
_stop = threading.Event()
_lock = threading.Lock()
stats = {"verified":0,"dead":0,"porn":0,"transport":0,"skipped_union":0}

def get_session():
    s = getattr(_tls, "sess", None)
    if s is None:
        import requests
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        _tls.sess = s
    return s

def rebuild_session():
    import requests
    try:
        _tls.sess.close()
    except Exception:
        pass
    _tls.sess = None

def og_title(page):
    m = OG_RE.search(page) or OG_RE2.search(page)
    if not m:
        return ""
    return html.unescape(m.group(1)).strip()

def make_item(code, title):
    cat = map_cat(title)
    cc = map_country(title)
    cw = CN_WORD[cc]
    desc = (f"Join this active {cw} WhatsApp {cat.lower()} group for daily chat, updates and new friends. "
            f"A friendly {cw} {cat.lower()} community to share posts and connect with members.")
    return {"name": title, "category": cat, "country": cc, "description": desc,
            "invite": f"https://chat.whatsapp.com/{code}", "image": ""}

def verify_one(cand):
    if _stop.is_set():
        return ("stopped", cand)
    invite = cand["invite"]
    if "/invite/" in invite:
        return ("dead", cand)  # channel format — excluded
    m = CODE_RE.search(invite)
    if not m:
        return ("dead", cand)
    code = m.group(1)
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = get_session().get(url, timeout=60, allow_redirects=True)
    except Exception:
        rebuild_session()
        return ("transport", cand)
    if r.status_code == 429:
        _stop.set()
        return ("stopped", cand)
    title = og_title(r.text)
    if not title:
        return ("dead", cand)
    if PORN_PAT.search(title):
        return ("porn", cand)
    name = cand.get("name") or ""
    if re.fullmatch(r"[A-Za-z0-9]{20,24}", name):
        name = title  # placeholder name was the code; use og:title
    item = make_item(code, name)
    return ("verified", item)

def main():
    union = set(json.load(open(os.path.join(WD, "dedupe_union.json"))))
    cands = json.load(open(SRC))
    print(f"union={len(union)} candidates={len(cands)}", flush=True)

    todo, seen = [], set()
    for c in cands:
        m = CODE_RE.search(c["invite"])
        code = m.group(1) if m else None
        if not code or code in union or code in seen:
            stats["skipped_union"] += 1
            continue
        seen.add(code)
        todo.append(c)
    print(f"after dedupe: {len(todo)} to verify, {stats['skipped_union']} skipped", flush=True)

    verified, pending = [], []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=20) as ex:
        for i, res in enumerate(ex.map(verify_one, todo), 1):
            kind, payload = res
            if kind == "verified":
                verified.append(payload); stats["verified"] += 1
            elif kind == "dead":
                stats["dead"] += 1
            elif kind == "porn":
                stats["porn"] += 1
            elif kind == "transport":
                pending.append({**payload, "note": "transport failure"}); stats["transport"] += 1
            elif kind == "stopped":
                pending.append({**payload, "note": "rate-limited — resume here next wave"})
            if i % 200 == 0:
                print(f"  {i}/{len(todo)} elapsed={time.time()-t0:.0f}s stats={stats} rate_limited={_stop.is_set()}", flush=True)

    print(f"DONE elapsed={time.time()-t0:.0f}s stats={stats} rate_limited={_stop.is_set()}", flush=True)
    json.dump(verified, open(os.path.join(WD, "team32-arabic-residual.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WD, "team32-unverified-pending.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(WD, "team32-stats.json"), "w") as f:
        json.dump({"candidates": len(cands), "to_verify": len(todo), **stats,
                   "rate_limited": _stop.is_set()}, f, indent=1)
    print(f"verified={len(verified)} pending={len(pending)}", flush=True)

if __name__ == "__main__":
    main()
