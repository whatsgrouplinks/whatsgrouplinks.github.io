#!/usr/bin/env python3
"""TEAM 13 wave_20261104: harvest NEW groupjoin.link tags (beyond Nov-3 set).
API: https://api.groupjoin.link/groups?tag=<NAME>&page=N&limit=20&safeSearch=blur
NOTE: og:title verification is IMPOSSIBLE this wave (chat.whatsapp.com unreachable
from this VM - curl timeouts; browser.open 403). All candidates -> pending with
note 'transport failure' per brief.
Policy change: adult-slug records are DROPPED ON SIGHT (never written).
"""
import json, re, time, html, os, sys, random
from urllib.parse import quote
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})(?![A-Za-z0-9])")

# (tag name, pages to scrape: list of page numbers)
TAGS = [
    ("sri lanka", list(range(1, 11))),
    ("urdu", list(range(1, 9))),
    ("bangladesh", list(range(1, 6))),
    ("kerala", list(range(1, 6))),
    ("bangla", list(range(1, 8))),
    ("telugu", list(range(1, 8))),
    ("kannada", list(range(1, 7))),
    ("arabic", list(range(1, 9))),
    ("japanese", list(range(1, 5))),
    ("japan", list(range(1, 4))),
    ("morocco", list(range(1, 4))),
    ("egypt", list(range(1, 4))),
    ("lahore", list(range(1, 4))),
    ("punjabi", list(range(1, 4))),
    ("afrikaans", list(range(1, 4))),
    ("marathi", list(range(1, 4))),
    ("cricket", list(range(1, 4))),
    ("islamic", list(range(1, 5))),
    ("school", list(range(1, 7))),
    ("career", list(range(1, 6))),
    ("fashion", list(range(1, 5))),
    ("art", list(range(1, 6))),
    ("softwareengineer", list(range(1, 6))),
    ("photography", list(range(1, 6))),
    ("design", list(range(1, 6))),
    ("trading", list(range(1, 6))),
    ("technology", list(range(1, 6))),
    ("science", list(range(1, 6))),
    ("spiritual", list(range(1, 5))),
    ("amanah", list(range(1, 5))),
    ("devotional", list(range(1, 5))),
    ("web series", list(range(1, 5))),
    ("work from home", list(range(1, 5))),
    ("youtube", list(range(1, 5))),
    ("friendship", list(range(1, 5))),
    ("clothing", list(range(1, 5))),
]

PORN_WORDS = ["porn", "pornhub", "xxx", "nude", "sex video", "escort",
              "call girl", "fuck", "dick", "pussy", "boobs", "anal", "bokep",
              "xnxx", "xvideos", "milf", "hentai", "incest", "bhabhi", "aunty",
              "chudai", "saxy", "sax chat", "ndue", "nudes", "mms video",
              "desi mms", "vcs", "video call service", "open video call",
              "18+", "🔞", "🥵", "🍆", "🍑", "💦", "👅", "👄", "💋", "🍌"]
ADULT_TAG_MARKERS = ["adult", "18", "18+", "xxx", "porn", "sex", "sexy",
                     "hot", "bhabhi", "aunty", "nude", "ndue", "vcs",
                     "bokep", "call", "girl"]
MINORS_MARKERS = ["school girl", "school boy", "schoolgirl", "schoolboy",
                  "child", "teen girl", "teen boy", "minor", "smp", "sma",
                  "sd ", " under 18", "u18"]
MULE_PATTERNS = ["paypal receiver", "paypal loader", "cashapp flip",
                 "money mule", "ssd chemical", "counterfeit currency",
                 "double your money", "hyip", "forex doubler",
                 "loading paypal", "receiver and loader"]

CAT_MAP = {
    "education": "Education", "business": "Business", "entertainment": "Entertainment",
    "gaming": "Gaming", "money": "Finance", "finance": "Finance", "earning": "Finance",
    "online-shopping": "Buy-Sell", "health": "Health", "technology": "Technology",
    "crypto": "Crypto", "cryptocurrency": "Crypto", "travel": "Travel",
    "music": "Music", "movies": "Movies", "film": "Movies", "food": "Food",
    "pets": "Pets", "funny": "Funny", "comedy": "Funny", "islamic": "Islamic",
    "news": "News", "sports": "Sports", "sports-and-fitness": "Sports",
    "jobs": "Jobs", "career": "Jobs", "friendship": "Friendship", "friends": "Friendship",
    "family": "Friendship", "fashion": "Other", "clothing": "Buy-Sell",
    "art": "Entertainment", "design": "Technology", "photography": "Entertainment",
    "spiritual": "Islamic", "devotional": "Other", "youtube": "Entertainment",
    "fan-club": "Entertainment", "cricket": "Sports", "science": "Education",
    "school": "Education", "animation": "Entertainment", "trading": "Finance",
    "forex": "Finance", "marketing": "Business", "advertising": "Business",
    "community": "Community", "social": "Community", "chat": "Friendship",
    "love": "Friendship", "girls": "Girls", "dating": "Friendship",
}

COUNTRY_ADJ = {"PK": "Pakistani", "IN": "Indian", "BD": "Bangladeshi",
               "LK": "Sri Lankan", "JP": "Japanese", "MA": "Moroccan",
               "EG": "Egyptian", "ZA": "South African", "NG": "Nigerian",
               "ID": "Indonesian", "MY": "Malaysian"}
COUNTRY_NAME = {"PK": "Pakistan", "IN": "India", "BD": "Bangladesh",
                "LK": "Sri Lanka", "JP": "Japan", "MA": "Morocco",
                "EG": "Egypt", "ZA": "South Africa", "NG": "Nigeria",
                "ID": "Indonesia", "MY": "Malaysia"}

def clean(s):
    if not s: return ""
    s = html.unescape(str(s))
    s = re.sub(r"\s+", " ", s).strip()
    return s

def is_porn(rec):
    blob = (rec.get("group_title", "") + " " + rec.get("group_desc", "")).lower()
    tags = [str(t).lower() for t in rec.get("tags", [])]
    cslug = str(rec.get("category", {}).get("category_slug", "")).lower()
    if cslug == "adult":
        return True
    for t in tags:
        tl = t.strip().lower()
        if tl in ADULT_TAG_MARKERS or "18+" in tl or tl in ("18", "adult", "porn", "xxx"):
            return True
    for w in PORN_WORDS:
        if w in blob:
            return True
    return False

def is_minors(rec):
    blob = (rec.get("group_title", "") + " " + rec.get("group_desc", "") + " " +
            " ".join(rec.get("tags", []))).lower()
    return any(m in blob for m in MINORS_MARKERS)

def mule_flag(rec):
    blob = (rec.get("group_title", "") + " " + rec.get("group_desc", "")).lower()
    return [p for p in MULE_PATTERNS if p in blob]

def has_personal_info(title):
    if re.search(r"\+?\d[\d\s\-]{7,}\d", title): return True
    if re.search(r"[\w.]+@[\w.]+\.\w+", title): return True
    return False

def fetch_page(tag, page):
    url = "https://api.groupjoin.link/groups"
    params = {"tag": tag, "page": page, "limit": 20, "safeSearch": "blur"}
    last = None
    for attempt in range(5):
        try:
            r = requests.get(url, params=params,
                             headers={"User-Agent": UA}, timeout=90)
            if r.status_code == 429:
                wait = 90 + attempt * 60
                print(f"429 on {tag} p{page}: sleeping {wait}s (attempt {attempt+1})",
                      flush=True)
                time.sleep(wait)
                last = "http 429"
                continue
            if r.status_code == 200:
                return ("ok", tag, page, r.json())
            last = f"http {r.status_code}"
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:80]}"
        time.sleep(5 + attempt * 5)
    return ("fail", tag, page, last)

def main():
    union = set(json.load(open(os.path.join(WAVE, "dedupe_union.json"))))
    print(f"union loaded: {len(union)}", flush=True)

    # resume: keep pages already fetched
    raw_path = os.path.join(WAVE, "team13_raw_pages.json")
    results = {}
    if os.path.exists(raw_path):
        try:
            for k, v in json.load(open(raw_path)).items():
                t, p = k.rsplit("::", 1)
                results[(t, int(p))] = v
        except Exception as e:
            print(f"resume read failed: {e}", flush=True)
    print(f"resumed {len(results)} pages", flush=True)

    jobs = [(t, p) for (t, pages) in TAGS for p in pages
            if (t, p) not in results]
    print(f"{len(jobs)} page fetches queued (sequential, polite)", flush=True)
    rate_limited = False
    done = 0
    for (t, p) in jobs:
        st, tag, page, payload = fetch_page(t, p)
        if st == "ok":
            results[(tag, page)] = payload
            done += 1
            if done % 10 == 0:
                print(f"progress: {done}/{len(jobs)} ok", flush=True)
                json.dump({f"{tt}::{pp}": v for (tt, pp), v in results.items()},
                          open(raw_path, "w"), ensure_ascii=False)
        elif payload == "http 429":
            rate_limited = True
            print(f"GAVE UP (persistent 429) on {tag} p{page} - banking progress",
                  flush=True)
        else:
            print(f"FAIL {tag} p{page}: {payload}", flush=True)
        time.sleep(4 + random.random() * 3)
    json.dump({f"{t}::{p}": v for (t, p), v in results.items()},
              open(raw_path, "w"), ensure_ascii=False)
    print(f"pages ok: {len(results)}, rate_limited={rate_limited}", flush=True)

    seen = set()
    candidates, porn_drops, minor_drops, mule_flags = [], 0, 0, []
    for (tag, page), data in sorted(results.items()):
        for rec in data.get("data", []):
            link = rec.get("link", "")
            if "/invite/" in link:
                continue  # channels
            m = CODE_RE.search(link)
            if not m:
                continue
            code = m.group(1)
            if not re.fullmatch(r"[A-Za-z0-9]{20,24}", code):
                continue
            if is_porn(rec):
                porn_drops += 1
                continue
            if is_minors(rec):
                minor_drops += 1
                continue
            flags = mule_flag(rec)
            if flags:
                mule_flags.append({"code": code, "title": clean(rec.get("group_title")),
                                   "patterns": flags, "tag": tag})
                continue
            title = clean(rec.get("group_title", ""))
            if not title or has_personal_info(title) or title.lower().startswith("http"):
                continue
            if code in union or code in seen:
                continue
            seen.add(code)
            candidates.append({"code": code, "title": title,
                               "desc": clean(rec.get("group_desc", "")),
                               "cat_slug": str(rec.get("category", {}).get("category_slug", "")).lower(),
                               "cat_name": str(rec.get("category", {}).get("category_name", "")),
                               "country": str(rec.get("country", {}).get("iso2", "") or "International"),
                               "tags": [str(t) for t in rec.get("tags", [])][:8],
                               "src_tag": tag,
                               "img": str(rec.get("group_img", "") or "")})
    print(f"candidates={len(candidates)} porn_drops={porn_drops} "
          f"minor_drops={minor_drops} mule={len(mule_flags)}", flush=True)
    json.dump(candidates, open(os.path.join(WAVE, "team13_candidates.json"), "w"),
              ensure_ascii=False, indent=1)
    json.dump(mule_flags, open(os.path.join(WAVE, "team13_mule_flags.json"), "w"),
              ensure_ascii=False, indent=1)
    json.dump({"porn_drops": porn_drops, "minor_drops": minor_drops,
               "rate_limited": rate_limited,
               "pages_ok": len(results), "pages_queued": len(jobs)},
              open(os.path.join(WAVE, "team13_harvest_stats.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
