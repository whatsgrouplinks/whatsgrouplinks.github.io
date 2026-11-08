#!/usr/bin/env python3
"""Team 07 wave 20261108 harvester: slice 07 (115 URLs)."""
import json, re, time, html, sys
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108"
UA_D = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
UA_M = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"}

leads = json.load(open(f"{BASE}/leads_slice_07.json"))
union = set(json.load(open(f"{BASE}/dedupe_union.json")))
print(f"leads={len(leads)} union={len(union)}", flush=True)

ADULT_EMOJI = set("🥵🍆🍑🔞💦👅👄💋")
BLOCK_WORDS = ["porn", "xxx", "sex video", "call girl", "call-girl", "escort",
               "bitfinex", "paypal loader", "counterfeit", "fake currency",
               "fake money", "money mule", "18+ video", "adult video", "desi bhabhi sex"]
GENERIC_TITLES = {"whatsapp group", "join this group on whatsapp", "whatsapp group invite", ""}

CATMAP = {
    "romantic": ("Friendship", "International"), "love": ("Friendship", "International"),
    "thailand": ("Community & Social", "TH"), "philippines": ("Community & Social", "PH"),
    "china": ("Community & Social", "CN"), "joker": ("Funny", "International"),
    "newspaper": ("News", "International"), "status": ("Entertainment", "International"),
    "coin-master": ("Gaming", "International"), "japanese": ("Education", "JP"),
    "makeup-artist": ("Community & Social", "International"), "dubai": ("Community & Social", "AE"),
    "tv-shows": ("Entertainment", "International"), "cooking": ("Cooking", "International"),
    "gym": ("Health", "International"), "fashion": ("Community & Social", "International"),
    "yoga": ("Health", "International"), "dj": ("Entertainment", "International"),
    "wallpapers": ("Entertainment", "International"), "import-export": ("Business", "International"),
    "startup": ("Business", "International"), "graphic-design": ("Technology", "International"),
    "upsc": ("Education", "IN"), "gk": ("Education", "IN"), "entrepreneur": ("Business", "International"),
    "meditation": ("Health", "International"), "edm": ("Entertainment", "International"),
    "teachers": ("Education", "International"), "iit": ("Education", "IN"), "jee": ("Education", "IN"),
    "russian": ("Education", "RU"), "english-learning": ("Education", "International"),
    "canada": ("Community & Social", "CA"), "mexico": ("Community & Social", "MX"),
    "abu-dhabi": ("Community & Social", "AE"), "christian": ("Community & Social", "International"),
    "arabic": ("Education", "International"), "bts-army": ("Entertainment", "International"),
    "tvk-family": ("Entertainment", "International"), "binance": ("Crypto", "International"),
    "business": ("Business", "International"), "earning": ("Online Earning", "International"),
    "entertainment": ("Entertainment", "International"), "fans": ("Entertainment", "International"),
    "games": ("Gaming", "International"), "game": ("Gaming", "International"),
    "health": ("Health", "International"), "indian": ("Community & Social", "IN"),
    "international": ("Community & Social", "International"), "jobs": ("Jobs", "International"),
    "latest": ("Community & Social", "International"), "learning": ("Education", "International"),
    "news": ("News", "International"), "religious": ("Islamic", "International"),
    "sales-marketing": ("Business", "International"), "share-market": ("Finance", "International"),
    "sports": ("Sports", "International"), "study": ("Education", "International"),
    "tech": ("Technology", "International"), "animal": ("Community & Social", "International"),
    "blog": ("Community & Social", "International"), "country": ("Community & Social", "International"),
    "education": ("Education", "International"), "youtube": ("Entertainment", "International"),
    "instagram": ("Entertainment", "International"), "movies": ("Entertainment", "International"),
    "shopping": ("Buy & Sell", "International"), "girls": ("Friendship", "International"),
    "hot": ("Entertainment", "International"),
}

def cat_for(url):
    slug = url.rstrip("/").split("/")[-1].lower()
    for k, v in CATMAP.items():
        if k in slug:
            return v
    return ("Community & Social", "International")

def clean_text(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t or ""))
    return re.sub(r"\s+", " ", t).strip(" -|·•\n\t")

def blocked(name, title):
    s = f"{name} {title}".lower()
    if any(e in s for e in ADULT_EMOJI):
        return True
    return any(w in s for w in BLOCK_WORDS)

# ---------- fetch listing pages ----------
candidates = {}   # code -> {name, url(listing), invite_url, cat, country}
new_leads = {}
attempted = 0
skipped_retired = []
fetch_fail = []

RETIRED_HOSTS = {"whatsgroulink.com", "www.imagesplatform.com", "www.instagram.com"}
for entry in leads:
    url = entry["url"]
    host = url.split("/")[2]
    if host in RETIRED_HOSTS:
        skipped_retired.append(url)
        continue
    attempted += 1
    cat, country = cat_for(url)
    try:
        r = requests.get(url, headers=UA_D, timeout=15)
        if r.status_code != 200:
            fetch_fail.append((url, r.status_code))
            continue
        h = r.text
    except Exception as e:
        fetch_fail.append((url, f"ERR {type(e).__name__}"))
        continue
    # new listing leads: internal links on same host
    for m in re.finditer(r'href="(https?://' + re.escape(host) + r'[^"]+)"', h):
        lu = m.group(1).split("#")[0].rstrip("/")
        if lu == url.rstrip("/") or lu in [l["url"].rstrip("/") for l in leads]:
            continue
        if re.search(r"(category|whatsapp-group|whatsapp-groups|group-links)", lu):
            new_leads[lu] = host
    # appgrouplink table rows
    found = 0
    for m in re.finditer(r"<tr><td>(.*?)</td>.*?<a [^>]*href=https?://chat\.whatsapp\.com/invite/([A-Za-z0-9]+)", h, re.S):
        name, code = clean_text(m.group(1)), m.group(2)
        if code not in candidates:
            candidates[code] = {"name": name, "listing": url, "invite": f"https://chat.whatsapp.com/invite/{code}", "cat": cat, "country": country}
        found += 1
    # generic anchors
    for m in re.finditer(r'<a [^>]*href="https?://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{10,})[^"]*"[^>]*>(.*?)</a>', h, re.S):
        code = m.group(1)
        if code in candidates:
            continue
        anchor = clean_text(m.group(2))
        # look backwards for a <td> or heading text
        pre = h[max(0, m.start()-500):m.start()]
        tds = re.findall(r"<td[^>]*>(.*?)</td>", pre, re.S)
        name = clean_text(tds[-1]) if tds else anchor
        if not name or name.lower() in ("join group", "join", "join now", "click here"):
            name = anchor or "WhatsApp Group"
        candidates[code] = {"name": name, "listing": url, "invite": f"https://chat.whatsapp.com/{code}", "cat": cat, "country": country}
        found += 1
    print(f"[{attempted}] {url} -> {found} candidates (total {len(candidates)})", flush=True)
    time.sleep(0.3)

print(f"FETCH DONE attempted={attempted} candidates={len(candidates)} retired_skipped={len(skipped_retired)} fetch_fail={len(fetch_fail)}", flush=True)
for u, e in fetch_fail:
    print("  FAIL", u, e, flush=True)

# dedupe against union + within run
todo = []
seen = set()
for code, c in candidates.items():
    if code in union or code in seen:
        continue
    seen.add(code)
    todo.append((code, c))
print(f"TO VERIFY: {len(todo)} (after union dedupe)", flush=True)
json.dump([{"code": k, "invite": v["invite"], "name": v["name"], "cat": v["cat"], "country": v["country"], "listing": v["listing"]} for k, v in candidates.items()],
          open(f"{BASE}/team07-candidates-raw.json", "w"), ensure_ascii=False)

# ---------- verify ----------
def og_title(text):
    m = re.search(r'property="og:title" content="([^"]*)"', text)
    return html.unescape(m.group(1)).strip() if m else ""

def check(item):
    code, c = item
    url = c["invite"]
    for attempt in range(2):
        try:
            s = requests.Session()
            r = s.get(url, headers=UA_D if attempt == 0 else UA_M, timeout=20)
            if r.status_code != 200:
                if attempt == 0:
                    time.sleep(2)
                    continue
                return (code, c, "dead", "")
            title = og_title(r.text)
            if title and title.lower() not in GENERIC_TITLES:
                return (code, c, "live", title)
            # empty/ambiguous: retry once after pause
            if attempt == 0:
                time.sleep(3)
                continue
            return (code, c, "dead", title)
        except Exception:
            if attempt == 0:
                time.sleep(2)
                continue
            return (code, c, "transport", "")
    return (code, c, "dead", "")

verified, pending = [], []
# stagger: submit in small waves of 3 with 0.5s gaps via executor
def worker(item):
    time.sleep(0.5)
    return check(item)

with ThreadPoolExecutor(max_workers=3) as ex:
    for i, res in enumerate(ex.map(worker, todo)):
        code, c, status, title = res
        if status == "live":
            if blocked(c["name"], title):
                print(f"  BLOCKED {code} {title!r}", flush=True)
                continue
            name = title
            cat, country = c["cat"], c["country"]
            desc = f"Join {name}, a WhatsApp group listed under {cat}. Connect with members, share updates and stay active in the group."
            verified.append({"name": name, "category": cat, "country": country,
                             "description": desc, "invite": c["invite"], "image": ""})
        elif status == "transport":
            pending.append({"name": c["name"], "category": c["cat"], "country": c["country"],
                            "description": f"Join {c['name']}, a WhatsApp group listed under {c['cat']}.",
                            "invite": c["invite"], "image": "", "reason": "transport"})
        if (i + 1) % 25 == 0:
            print(f"  verified {i+1}/{len(todo)} live={len(verified)} pending={len(pending)}", flush=True)
            json.dump(verified, open(f"{BASE}/team07-leads-harvest-g.json", "w"), ensure_ascii=False, indent=1)
            json.dump(pending, open(f"{BASE}/team07-leads-harvest-g-pending.json", "w"), ensure_ascii=False, indent=1)

leads_out = [{"url": u, "source": h} for u, h in sorted(new_leads.items())]
json.dump(verified, open(f"{BASE}/team07-leads-harvest-g.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{BASE}/team07-leads-harvest-g-pending.json", "w"), ensure_ascii=False, indent=1)
json.dump(leads_out, open(f"{BASE}/team07-leads-harvest-g-leads.json", "w"), ensure_ascii=False, indent=1)
summary = {"attempted": attempted, "candidates": len(candidates), "to_verify": len(todo),
           "verified": len(verified), "pending": len(pending), "new_leads": len(leads_out),
           "retired_skipped": skipped_retired, "fetch_fail": fetch_fail}
json.dump(summary, open(f"{BASE}/team07-summary.json", "w"), ensure_ascii=False, indent=1)
print("SUMMARY", json.dumps(summary, indent=1), flush=True)
