#!/usr/bin/env python3
"""Team 02 rescue verification pass v2 — 3 parallel workers (rule max), >=0.6s
between check starts, fresh session + rotated UA per check, one retry on empty title.
Re-decides all 80 candidates from team02-candidates.json.
"""
import json, re, time, html, os, random, threading
import requests
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261108")
UAS = [
 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
]
ADULT_EMOJI = set("🥵🍆🍑🔞💦👅👄💋")
BLOCK_WORDS = ["xxx", "porn", "sex video", "sex videos", "call girl", "call girls",
               "escort", "bitfinex", "paypal loader", "counterfeit", "fake currency",
               "fake money", "money mule", "adult video", "18+ video", "nude", "sexy video"]
GENERIC_TITLES = {"whatsapp group", "join this group on whatsapp", "whatsapp", "join group on whatsapp"}

RATE_LOCK = threading.Lock()
LAST_START = [0.0]

def rate_wait():
    with RATE_LOCK:
        now = time.time()
        wait = 0.7 - (now - LAST_START[0])
        if wait > 0:
            time.sleep(wait)
        LAST_START[0] = time.time()

def write_json_retry(path, data, tries=6):
    for i in range(tries):
        try:
            tmp = path + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            os.replace(tmp, path)
            return True
        except Exception as e:
            print("WRITE FAIL", path, e, "retry", i+1, flush=True)
            time.sleep(2)
    return False

def blocked(name):
    if any(e in name for e in ADULT_EMOJI):
        return "adult-emoji"
    hay = name.lower()
    for w in BLOCK_WORDS:
        if w in hay:
            return "blocked-word:" + w
    return None

def refine_category(cat, name):
    h = name.lower()
    if cat != "Community & Social":
        return cat
    if any(k in h for k in ["clothing", "clothes", "store", "shop", "buy", "sell", "shopping"]): return "Buy & Sell"
    if any(k in h for k in ["pubg", "free fire", "gaming", "game", "esport"]): return "Gaming"
    if any(k in h for k in ["cricket", "football", "sports"]): return "Sports"
    if any(k in h for k in ["job", "naukri", "sarkari", "hiring"]): return "Jobs"
    if any(k in h for k in ["quran", "islam", "madrasa", "namaz", "allah"]): return "Islamic"
    if any(k in h for k in ["movie", "drama", "music", "song", "dj "]): return "Entertainment"
    if any(k in h for k in ["news"]): return "News"
    if any(k in h for k in ["study", "exam", "class", "board", "physics", "student"]): return "Education"
    if any(k in h for k in ["crypto", "binance", "bitcoin"]): return "Crypto"
    if any(k in h for k in ["earn", "earning"]): return "Online Earning"
    if any(k in h for k in ["subscriber", "youtube"]): return "Entertainment"
    return cat

def check(code, form):
    """Returns (status, title): 'live' | 'dead' | 'transport'."""
    url = f"https://chat.whatsapp.com/invite/{code}" if form == "invite" else f"https://chat.whatsapp.com/{code}"
    for attempt in range(2):
        rate_wait()
        ua = random.choice(UAS)
        s = requests.Session()
        s.headers.update({'User-Agent': ua, 'Accept-Language': 'en-US,en;q=0.9',
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
        try:
            r = s.get(url, timeout=25)
        except Exception:
            if attempt == 0:
                time.sleep(10)
                continue
            return 'transport', ''
        if r.status_code != 200:
            return 'dead', ''
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
        if not m:
            m = re.search(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:title\"", r.text)
        title = html.unescape(m.group(1)).strip() if m else ""
        if title:
            return 'live', title
        if attempt == 0:
            time.sleep(10)
            continue
        return 'dead', ''
    return 'dead', ''

def verify_one(args):
    i, c = args
    code = c["code"]
    status, title = check(code, c.get("form", "plain"))
    print(f"[{i+1}] {status.upper()} {code} {title!r}", flush=True)
    return i, c, status, title

def main():
    cands = json.load(open(os.path.join(WAVE, "team02-candidates.json")))
    print(f"rescue v2: {len(cands)} candidates, 3 workers", flush=True)
    results = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        for i, c, status, title in ex.map(verify_one, list(enumerate(cands))):
            results[i] = (c, status, title)
    verified, pending, dead = [], [], []
    for i in range(len(cands)):
        c, status, title = results[i]
        code = c["code"]
        if status == 'live':
            if title.lower() in GENERIC_TITLES or "whatsapp channel" in title.lower():
                dead.append(code); continue
            b = blocked(title)
            if b:
                print(f"BLOCKED {code} {b} {title!r}", flush=True); dead.append(code); continue
            cat = refine_category(c["category"], title)
            desc = f"Join {title}, a WhatsApp group listed under {cat}. Connect with members, share updates and stay active in this {cat.lower()} community."
            invite = f"https://chat.whatsapp.com/invite/{code}" if c.get("form") == "invite" else f"https://chat.whatsapp.com/{code}"
            verified.append({"name": title, "category": cat, "country": c["country"],
                             "description": desc, "invite": invite, "image": ""})
        elif status == 'transport':
            nm = c["name"] or "WhatsApp Group"
            invite = f"https://chat.whatsapp.com/invite/{code}" if c.get("form") == "invite" else f"https://chat.whatsapp.com/{code}"
            pending.append({"name": nm, "category": c["category"], "country": c["country"],
                            "description": f"Join {nm}, a WhatsApp group listed under {c['category']}.",
                            "invite": invite, "image": "", "reason": "transport"})
        else:
            dead.append(code)
    # leads: re-collect groupsinvite related detail URLs + ongrupos group links
    slice_urls = set(e["url"] for e in json.load(open(os.path.join(WAVE, "leads_slice_02.json"))))
    leads = {}
    S = requests.Session(); S.headers.update({'User-Agent': UAS[0]})
    for e in json.load(open(os.path.join(WAVE, "leads_slice_02.json"))):
        m = re.match(r'https://groupsinvite\.link/group/link/([a-z0-9]+)/', e["url"])
        if not m: continue
        try:
            t = S.get(e["url"], timeout=25).text
            for rel in set(re.findall(r'https://groupsinvite\.link/group/link/[a-z0-9]+/', t)):
                if rel not in slice_urls:
                    leads[rel] = "groupsinvite.link related group"
        except Exception:
            pass
        time.sleep(0.4)
    for cat_url in ["https://ongrupos.com/categoria/amizades","https://ongrupos.com/categoria/religiao",
                    "https://ongrupos.com/categoria/carros-e-motos"]:
        try:
            t = S.get(cat_url, timeout=25).text
            for g in set(re.findall(r'https://ongrupos\.com/grupo/[^\s"\'<>]+', t)):
                if g not in slice_urls:
                    leads[g] = "ongrupos group detail"
        except Exception:
            pass
        time.sleep(0.5)
    leads_out = [{"url": u, "source": s} for u, s in sorted(leads.items())]
    print(f"RESCUE DONE verified={len(verified)} pending={len(pending)} dead={len(dead)} leads={len(leads_out)}", flush=True)
    write_json_retry(os.path.join(WAVE, "team02-leads-harvest-b.json"), verified)
    write_json_retry(os.path.join(WAVE, "team02-leads-harvest-b-pending.json"), pending)
    write_json_retry(os.path.join(WAVE, "team02-leads-harvest-b-leads.json"), leads_out)
    json.dump(dead, open(os.path.join(WAVE, "team02-dead.json"), "w"))
    print("FILES WRITTEN", flush=True)

if __name__ == "__main__":
    main()
