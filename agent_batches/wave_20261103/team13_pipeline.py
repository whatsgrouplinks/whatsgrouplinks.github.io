#!/usr/bin/env python3
"""TEAM 13: harvest current true tail pages (money 100-104, education 30-32,
business 83-85), dedupe vs union, verify codes, write outputs."""
import json, re, time, html, os, sys
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})")
PORN_WORDS = ["porn", "pornhub", "xxx", "nude", "sex video", "escort",
              "call girl", "fuck", "dick", "pussy", "boobs", "anal"]
PORN_EMOJI = ["\U0001F975", "\U0001F346", "\U0001F351", "\U0001F51E",
              "\U0001F4A6", "\U0001F445", "\U0001F444", "\U0001F48B"]
MULE_WORDS = ["passcode", "paypal loader", "counterfeit currency",
              "fake currency", "money flip", "double your money"]

CAT_MAP = {"money": "Finance", "education": "Education", "business": "Business",
           "sports": "Sports", "gaming": "Gaming", "jobs": "Jobs",
           "entertainment": "Entertainment", "friendship": "Friendship",
           "news": "News", "islamic": "Islamic", "buy-sell": "Buy-Sell",
           "health": "Health", "community": "Community", "technology": "Technology",
           "crypto": "Crypto", "travel": "Travel", "music": "Music",
           "movies": "Movies", "food": "Food", "pets": "Pets", "funny": "Funny",
           "girls": "Girls", "adult": "Other"}

def api_page(tag, page, attempts=4, timeout=45):
    last = None
    for i in range(attempts):
        try:
            r = requests.get("https://api.groupjoin.link/groups",
                params={"tag": tag, "page": page, "limit": 20, "safeSearch": "blur"},
                headers={"User-Agent": UA, "Accept": "application/json"}, timeout=timeout)
            return r.json()
        except Exception as e:
            last = e
            time.sleep(2 + i * 3)
    print(f"  API FAIL tag={tag} p{page}: {last}", flush=True)
    return None

def looks_porn(text):
    t = text.lower()
    return any(w in t for w in PORN_WORDS) or any(e in text for e in PORN_EMOJI)

def looks_mule(text):
    t = text.lower()
    return any(w in t for w in MULE_WORDS)

def clean_desc(desc, title, cat_label, country_name):
    d = re.sub(r"https?://\S+", "", desc or "")
    d = html.unescape(d).strip()
    d = re.sub(r"\s+", " ", d)
    if not d or len(d) < 15:
        d = f"A {cat_label} WhatsApp group for {country_name} members: {title.strip()}."
    # cap at 2 sentences / 300 chars
    sents = re.split(r"(?<=[.!?])\s+", d)
    d = " ".join(sents[:2]).strip()[:300]
    return d

union = set(json.load(open(f"{WAVE}/dedupe_union.json")))
print(f"union: {len(union)} codes", flush=True)

TAIL_PAGES = {"money": range(100, 105), "education": range(30, 33), "business": range(83, 86)}

cands, seen, porn_drops, mule_flags = [], set(), 0, []
for tag, pages in TAIL_PAGES.items():
    for p in pages:
        d = api_page(tag, p)
        if not d or not d.get("data"):
            print(f"  {tag} p{p}: no data", flush=True)
            time.sleep(1)
            continue
        print(f"  {tag} p{p}: {len(d['data'])} records", flush=True)
        for rec in d["data"]:
            link = rec.get("link", "") or ""
            m = CODE_RE.search(link)
            if not m:
                continue
            code = m.group(1)
            if code in union or code in seen:
                continue
            title = (rec.get("group_title") or "").strip()
            desc = rec.get("group_desc") or ""
            blob = f"{title} {desc}"
            if looks_porn(blob):
                porn_drops += 1
                continue
            if looks_mule(blob):
                mule_flags.append({"code": code, "title": title})
                continue
            ctry = rec.get("country") or {}
            iso2 = (ctry.get("iso2") or "").upper()
            cname = ctry.get("name") or "International"
            cat = rec.get("category") or {}
            slug = (cat.get("category_slug") or "").lower()
            cat_label = CAT_MAP.get(slug, "Other")
            if slug == "adult":
                porn_drops += 1
                continue
            seen.add(code)
            cands.append({
                "code": code, "name": title or f"{cat_label} group",
                "category": cat_label, "country": iso2 if len(iso2) == 2 else "International",
                "description": clean_desc(desc, title, cat_label, cname),
                "invite": f"https://chat.whatsapp.com/{code}", "image": "",
            })
        time.sleep(1)
print(f"candidates after dedupe/filters: {len(cands)}; porn_drops={porn_drops}; mule_flags={len(mule_flags)}", flush=True)
json.dump(cands, open(f"{WAVE}/team13-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump(mule_flags, open(f"{WAVE}/team13-mule-flags.json", "w"), ensure_ascii=False, indent=1)

# ---- verification ----
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
verified, pending = [], []
stop429 = False
for i, c in enumerate(cands):
    code = c["code"]
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=25)
        if r.status_code == 429:
            print("  HTTP 429 -> STOP verifying", flush=True)
            stop429 = True
            pending.append({**c, "note": "rate-limited"})
            pending.extend({**x, "note": "rate-limited"} for x in cands[i+1:])
            break
        m = OG_RE.search(r.text)
        og = html.unescape(m.group(1)).strip() if m else ""
        if og:
            item = dict(c)
            item["name"] = c["name"] if c["name"] else og
            verified.append(item)
            print(f"  OK {code} :: {og[:60]}", flush=True)
        else:
            print(f"  DEAD {code} (empty og:title)", flush=True)
    except Exception as e:
        print(f"  TRANSPORT FAIL {code}: {type(e).__name__}", flush=True)
        pending.append({**c, "note": "transport failure"})
    time.sleep(0.7)

json.dump(verified, open(f"{WAVE}/team13-gjl-tails.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{WAVE}/team13-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
print(f"DONE: verified={len(verified)} pending={len(pending)} porn_drops={porn_drops} mule_flags={len(mule_flags)} stop429={stop429}", flush=True)
