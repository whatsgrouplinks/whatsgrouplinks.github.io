#!/usr/bin/env python3
"""Team 14: parallel verification of deduped codes with checkpointing."""
import json, re, time, html, os, sys, threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261103")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
WORKERS = 6

CAT_MAP = {
    "jobs": "Jobs", "adult": "Other", "money": "Finance", "business": "Business",
    "entertainment": "Entertainment", "comedy": "Funny", "music": "Music",
    "education": "Education", "news-and-politics": "News", "online-shopping": "Buy-Sell",
    "health": "Health", "sports-and-fitness": "Sports", "friendship": "Friendship",
    "travel-and-tourism": "Travel", "gaming": "Gaming", "beauty-and-fashion": "Other",
    "quotes": "Other", "flirting": "Friendship", "love-and-relationship": "Friendship",
    "photography": "Other", "pets-and-animals": "Pets", "food-and-recipes": "Food",
    "science-and-technology": "Technology", "earn-money-online": "Finance",
    "spiritual": "Islamic", "autos-and-vehicles": "Other", "fan-club": "Entertainment",
    "other": "Other", "advertising": "Business", "art-and-design": "Other",
    "investment": "Finance", "comics": "Entertainment", "mus": "Music", "mu": "Music",
    "deals-and-offers": "Buy-Sell", "online-shoppi": "Buy-Sell", "pets-and-anim": "Pets",
}
ADULT_PAT = re.compile(r'porn|pornhub|xxx|nude|sex\s*video|escort|call\s*girl|fuck|dick|pussy|boobs|anal|🥵|🍆|🍑|🔞|💦|👅|👄|💋', re.I)

SURROGATE_PAIR = re.compile(r'[\ud800-\udbff][\udc00-\udfff]')
BOILER = re.compile(r'^welcome to my whatsapp group\s*\.?\s*.*?\.?\s*please join my whatsapp group\s*\.?\s*', re.I | re.S)

def repair_text(s):
    """Fix latin-1-mojibake from the parser's unicode_escape round-trip,
    then merge UTF-16 surrogate pairs into real characters."""
    if not s:
        return s
    out, buf = [], []
    def flush():
        if buf:
            cand = ''.join(buf)
            try:
                out.append(cand.encode('latin-1').decode('utf-8'))
            except Exception:
                out.append(cand)
            buf.clear()
    for ch in s:
        o = ord(ch)
        if o > 0xFF or 0xD800 <= o <= 0xDFFF:
            flush(); out.append(ch)
        elif 0x80 <= o <= 0xFF:
            buf.append(ch)
        else:
            flush(); out.append(ch)
    flush()
    s = ''.join(out)
    def merge(m):
        hi, lo = ord(m.group(0)[0]), ord(m.group(0)[1])
        return chr(0x10000 + ((hi - 0xD800) << 10) + (lo - 0xDC00))
    return SURROGATE_PAIR.sub(merge, s)

def clean_desc(d):
    d = repair_text(d).strip()
    d = BOILER.sub('', d).strip()
    d = re.sub(r'groupjoin\.link', '', d, flags=re.I).strip()
    return d

rate_limited = threading.Event()
lock = threading.Lock()
verified, pending, stats = [], [], {"dead": 0, "transport": 0, "porn": 0, "done": 0}
ckpt_path = os.path.join(WAVE, "team14_verify_ckpt.jsonl")
seen_codes = set()

def load_ckpt():
    if os.path.exists(ckpt_path):
        for line in open(ckpt_path):
            try:
                e = json.loads(line)
                seen_codes.add(e["code"])
                if e["status"] == "verified":
                    verified.append(e["item"])
                elif e["status"] == "pending":
                    pending.append(e["item"])
                else:
                    stats[e["status"]] += 1
            except Exception:
                pass

def write_ckpt(code, status, item=None):
    with lock:
        with open(ckpt_path, "a") as f:
            f.write(json.dumps({"code": code, "status": status, "item": item}, ensure_ascii=False) + "\n")

def make_desc(name, cat, country, rec):
    topic = rec.get("cat_name") or rec.get("tag") or cat
    cword = {"PK":"Pakistan","IN":"India","NG":"Nigeria","US":"the US","BR":"Brazil",
             "MX":"Mexico","ID":"Indonesia","GB":"the UK"}.get(country, "around the world" if country=="International" else country)
    desc = (rec.get("desc") or "").strip()
    base = desc[:180].rstrip() if (desc and len(desc) > 20) else f"A {cat.lower()} community group about {topic.lower()}."
    return (f"{base} Join {name} to connect with people interested in {topic.lower()} "
            f"{cat.lower()} in {cword}.").strip()

def check_one(code, rec):
    title = repair_text(rec.get("title", ""))
    desc = clean_desc(rec.get("desc", ""))
    rec["title"], rec["desc"] = title, desc
    if ADULT_PAT.search(title) or ADULT_PAT.search(desc):
        stats["porn"] += 1
        write_ckpt(code, "porn")
        return
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = requests.get(url, headers=UA, timeout=25, allow_redirects=True)
        if r.status_code == 429:
            rate_limited.set()
            write_ckpt(code, "pending", {"code": code, "record": rec, "note": "rate-limited"})
            return
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text, re.I)
        if not m:
            m = re.search(r"<meta\s+property='og:title'\s+content='([^']*)'", r.text, re.I)
        t = html.unescape(m.group(1)).strip() if m else ""
    except Exception:
        stats["transport"] += 1
        write_ckpt(code, "transport", None)
        pending.append({"code": code, "record": rec, "note": "transport failure"})
        return
    if not t:
        stats["dead"] += 1
        write_ckpt(code, "dead", None)
        return
    if ADULT_PAT.search(t):
        stats["porn"] += 1
        write_ckpt(code, "porn")
        return
    name = rec["title"] if rec["title"] else t
    cat = CAT_MAP.get((rec.get("cat_slug") or "").lower(), "Other")
    country = (rec.get("country") or "").upper() or "International"
    if len(country) != 2:
        country = "International"
    item = {"name": name, "category": cat, "country": country,
            "description": make_desc(name, cat, country, rec),
            "invite": url, "image": rec.get("img") or ""}
    verified.append(item)
    write_ckpt(code, "verified", item)

def build_merged():
    raw = json.load(open(os.path.join(WAVE, "team14_raw.json")))
    union = set(json.load(open(os.path.join(WAVE, "dedupe_union.json"))))
    merged = {}
    du, ds = 0, 0
    for tag, blob in raw.items():
        for r in blob["records"]:
            code = r["code"]
            if code in union:
                du += 1
                continue
            if code in merged:
                ds += 1
                continue
            merged[code] = r
    json.dump(merged, open(os.path.join(WAVE, "team14_merged.json"), "w"), ensure_ascii=False)
    print(f"union={len(union)} new_unique={len(merged)} union_dups={du} self_dups={ds}", flush=True)
    return merged

def main():
    load_ckpt()
    merged_path = os.path.join(WAVE, "team14_merged.json")
    merged = json.load(open(merged_path)) if os.path.exists(merged_path) else build_merged()
    work = [(c, r) for c, r in merged.items() if c not in seen_codes]
    print(f"total={len(merged)} resume-from-ckpt={len(seen_codes)} to-verify={len(work)}", flush=True)
    n = len(work)
    idx = {"i": 0}
    def worker(chunk):
        for code, rec in chunk:
            if rate_limited.is_set():
                write_ckpt(code, "pending", {"code": code, "record": rec, "note": "rate-limited"})
                pending.append({"code": code, "record": rec, "note": "rate-limited"})
                continue
            check_one(code, rec)
            with lock:
                idx["i"] += 1
                stats["done"] += 1
                if idx["i"] % 100 == 0:
                    print(f"  progress {idx['i']}/{n} verified={len(verified)} dead={stats['dead']} transport={stats['transport']} porn={stats['porn']} pending={len(pending)} 429={rate_limited.is_set()}", flush=True)
            time.sleep(0.5)
    chunks = [work[i::WORKERS] for i in range(WORKERS)]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(worker, chunks))
    json.dump(verified, open(os.path.join(WAVE, "team14-gjl-newtags.json"), "w"), ensure_ascii=False, indent=1)
    if pending:
        json.dump(pending, open(os.path.join(WAVE, "team14-unverified-pending.json"), "w"), ensure_ascii=False, indent=1)
    print(f"FINAL verified={len(verified)} pending={len(pending)} dead={stats['dead']} transport={stats['transport']} porn_drops={stats['porn']} rate_limited={rate_limited.is_set()}", flush=True)

if __name__ == "__main__":
    main()
