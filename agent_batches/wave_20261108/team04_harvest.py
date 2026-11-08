#!/usr/bin/env python3
"""Team 04 — wave 20261108 slice 04 harvest.
Fetches groupjoin.link API tag pages + groupchatconnect channel pages,
dedupes against the wave dedupe union, verifies invite codes live via
chat.whatsapp.com, writes verified / pending / leads JSON into the wave dir.
"""
import json, re, subprocess, sys, time, threading, os
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261108")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
GENERIC_TITLES = {"whatsapp group", "join this group on whatsapp", "whatsapp", "join group", ""}

union = set(json.load(open(os.path.join(WAVE, "dedupe_union.json"))))
leads = json.load(open(os.path.join(WAVE, "leads_slice_04.json")))
print(f"union={len(union)} slice={len(leads)}", flush=True)

# ---- tag skip list: porn / adult-service / money-mule tags (rule 3) ----
PORN_TAGS = {
    "cuckold", "village xxx", "bokep sange", "pron video", "sax video",
    "xnxx videos only", "#adult", "bokep viral", "bugil", "grup bokep",
    "saling berbagi bokep", "naekd girls", "hot girl", "hot video",
    "shemale", "ndue video call service", "full open video call",
    "hot fac voice ke sath", "desi videos", "bokep bugil", "naked", "ndue",
    "mlm", "e money", "emoney",
}
ADULT_EMOJI = set("🥵🍆🍑🔞💦👅👄💋")
BAD_WORDS = re.compile(
    r"(bokep|pron\b|porn|xxx|xnxx|naked|nude|bugil|\bsex\b|sange|cuckold|shemale|"
    r"call[\s\-]?girl|escort|desi[\s\-]?video|video[\s\-]?call[\s\-]?service|"
    r"full[\s\-]?open|hot[\s\-]?girl|hot[\s\-]?video|paypal[\s\-]?loader|"
    r"bitfinex|counterfeit|fake[\s\-]?currency|fake[\s\-]?note|money[\s\-]?mule|"
    r"double your money|guaranteed[\s\-]?profit|adult[\s\-]?video)",
    re.I)
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{8,}\d")

CATEGORIES = {"Education","Jobs","Entertainment","Islamic","News","Sports","Technology",
    "Health","Business","Gaming","Friendship","Community & Social","Online Earning",
    "Crypto","Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate",
    "Buy & Sell","Finance","Funny"}

def canon_category(cat_name, tags, title):
    s = " ".join([cat_name or ""] + list(tags or []) + [title or ""]).lower()
    rules = [
        (r"scholarship", "Scholarship"),
        (r"crypto|bitcoin|forex|trading|finance|invest", "Finance"),
        (r"islam|quran|muslim|religious|naat|hamd", "Islamic"),
        (r"education|study|exam|school|college|university|learn|student|ielts|css|pcs", "Education"),
        (r"job|career|hiring|vacancy|employment|work from home", "Jobs"),
        (r"online earn|earn money|earning|refer and earn|without investment|earnmoney", "Online Earning"),
        (r"news|breaking|headline", "News"),
        (r"sport|football|cricket|hockey|fifa", "Sports"),
        (r"game|gaming|minecraft|free fire|ff\b|pubg|mabar", "Gaming"),
        (r"movie|music|netflix|drama|song|entertainment|fun|meme|joke|comedy|funny|shorts|viral video|youtube", "Entertainment"),
        (r"health|fitness|medical|doctor|hospital|diet", "Health"),
        (r"business|entrepreneur|startup|shop|store|sale|deals|buy|sell|market", "Buy & Sell"),
        (r"cook|recipe|food", "Cooking"),
        (r"poetry|poem|shayari|ghazal|urdu adab", "Poetry"),
        (r"travel|tour|tourism|trip|ticket|visa", "Travel"),
        (r"freelance|fiverr|upwork|design|writing", "Freelance"),
        (r"real estate|property|plot|house for sale", "Real Estate"),
        (r"pet|animal|nature|wildlife", "Community & Social"),
        (r"friend|friendship|chat|girls|boys|bhabi|gf\b|dating|social", "Friendship"),
        (r"tech|software|program|computer|ai\b|mobile", "Technology"),
    ]
    for pat, cat in rules:
        if re.search(pat, s):
            return cat
    return "Community & Social"

def clean_text(t):
    return re.sub(r"\s+", " ", (t or "")).strip()

def fetch_url(url, timeout=30):
    """curl fetch; returns (status, body) or (0, '') on transport failure."""
    try:
        p = subprocess.run(["curl", "-sS", "-m", str(timeout), "-A", UA, "-L", url],
                           capture_output=True, text=True, timeout=timeout + 10)
        body = p.stdout or ""
        m = re.search(r"HTTP/\S+ (\d+)", body)  # not present; curl -sS doesn't print status
        return (200 if body else 0, body)
    except Exception:
        return (0, "")

def fetch_api(url):
    """Fetch groupjoin API with 429 backoff. Returns parsed JSON or None + reason."""
    for attempt in range(3):
        try:
            p = subprocess.run(
                ["curl", "-sS", "-m", "40", "-A", UA,
                 "-w", "\n%{http_code}", url],
                capture_output=True, text=True, timeout=55)
            out = p.stdout or ""
            if "\n" in out:
                body, code = out.rsplit("\n", 1)
                code = int(code.strip()) if code.strip().isdigit() else 0
            else:
                body, code = out, 0
            if code == 200:
                return json.loads(body)
            if code == 429:
                print(f"  429 on {url[:80]} — sleeping 90s (attempt {attempt+1})", flush=True)
                time.sleep(90)
                continue
            print(f"  HTTP {code} on {url[:80]}", flush=True)
            return None
        except Exception as e:
            print(f"  fetch error {e} on {url[:80]}", flush=True)
            time.sleep(10)
    return None

def extract_code(link):
    if not link:
        return None
    m = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})", link)
    return m.group(1) if m else None

candidates = {}   # code -> record (pre-verification)
seen_codes = set()
new_leads = []
failed_tags = []
attempted = 0

def tag_of(url):
    m = re.search(r"[?&]tag=([^&]+)", url)
    import urllib.parse
    return urllib.parse.unquote_plus(m.group(1)).lower().strip() if m else ""

api_urls = [e["url"] for e in leads if "api.groupjoin.link" in e["url"]]
chan_urls = [e["url"] for e in leads if "groupchatconnect.info/channel" in e["url"]]
other_urls = [e["url"] for e in leads if "api.groupjoin.link" not in e["url"] and "groupchatconnect.info/channel" not in e["url"]]
print(f"api={len(api_urls)} channels={len(chan_urls)} other={len(other_urls)}", flush=True)

# ---- 1. groupchatconnect channel pages: confirm no group invite ----
for u in chan_urls:
    attempted += 1
    st, body = fetch_url(u)
    if st != 200:
        print(f"  channel {u} fetch fail", flush=True)
        continue
    codes = set(re.findall(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})", body))
    # channel pages carry a channel invite, not group codes; only harvest real group codes
    if codes:
        print(f"  channel {u} HAS codes: {codes}", flush=True)
        for c in codes:
            if c not in union and c not in seen_codes:
                seen_codes.add(c)
                candidates[c] = {"name": "GroupChatConnect group", "category": "Community & Social",
                                 "country": "International",
                                 "description": "Join this WhatsApp group.",
                                 "invite": f"https://chat.whatsapp.com/{c}", "image": ""}
    time.sleep(1)

# ---- 2. groupjoin API tag pages ----
for u in api_urls:
    tag = tag_of(u)
    attempted += 1
    if tag in PORN_TAGS:
        print(f"  SKIP porn/scam tag: {tag}", flush=True)
        continue
    data = fetch_api(u)
    if not data:
        failed_tags.append(u)
        continue
    items = data.get("data") or []
    print(f"  tag '{tag}': {len(items)} items", flush=True)
    if len(items) >= 20:
        # pagination exists; bank page 2 as a lead
        import urllib.parse
        q = urllib.parse.urlencode({"tag": tag, "page": 2, "limit": 20, "safeSearch": "blur"})
        new_leads.append({"url": f"https://api.groupjoin.link/groups?{q}", "source": "team04-page2"})
    for it in items:
        code = extract_code(it.get("link") or "")
        if not code or code in union or code in seen_codes:
            continue
        title = clean_text(it.get("group_title"))
        desc = clean_text(it.get("group_desc"))
        tags = [clean_text(t) for t in (it.get("tags") or [])]
        blob = f"{title} {desc} {' '.join(tags)}"
        if not title:
            continue
        if any(e in blob for e in ADULT_EMOJI):
            continue
        if BAD_WORDS.search(blob):
            continue
        if PHONE_RE.search(title):
            continue
        if (it.get("nsfw") == 1) and BAD_WORDS.search(" ".join(tags)):
            continue
        cat = canon_category((it.get("category") or {}).get("category_name"), tags, title)
        country = ((it.get("country") or {}).get("iso2") or "International").upper()
        if len(country) != 2:
            country = "International"
        if len(desc) < 25 or desc.lower().startswith("welcome to my whatsapp group"):
            description = (f"Join {title}, a WhatsApp group listed under {cat}. "
                           f"Connect with members, share updates and stay in touch with the community.")
        else:
            description = desc[:300]
        seen_codes.add(code)
        candidates[code] = {"name": title[:120], "category": cat, "country": country,
                            "description": description,
                            "invite": f"https://chat.whatsapp.com/{code}", "image": ""}

print(f"candidates pre-verify: {len(candidates)}", flush=True)
json.dump({"candidates": candidates, "new_leads": new_leads, "failed_tags": failed_tags,
           "attempted": attempted},
          open(os.path.join(WAVE, "team04-progress.json"), "w"), ensure_ascii=False)

# ---- 3. verify codes live (max 3 parallel, >=0.5s between checks) ----
import requests
from requests.adapters import HTTPAdapter

VERIFIED, PENDING = [], []
lock = threading.Lock()
last_check = [0.0]

def check_code(code):
    rec = candidates[code]
    with lock:
        gap = 0.6 - (time.time() - last_check[0])
        if gap > 0:
            time.sleep(gap)
        last_check[0] = time.time()
    sess = requests.Session()
    sess.mount("https://", HTTPAdapter(max_retries=0))
    for attempt in range(2):
        try:
            r = sess.get(f"https://chat.whatsapp.com/{code}", headers={"User-Agent": UA},
                         timeout=25, allow_redirects=True)
            if r.status_code != 200:
                if r.status_code in (429, 500, 502, 503):
                    if attempt == 0:
                        time.sleep(5)
                        continue
                    return ("pending", code)
                return ("dead", code)
            m = re.search(r'property="og:title"\s+content="([^"]*)"', r.text) or \
                re.search(r'content="([^"]*)"\s+property="og:title"', r.text)
            title = (m.group(1).strip() if m else "")
            if title and title.lower() not in GENERIC_TITLES:
                # channel check: whatsapp channels show og:title too; require group-ish page
                if "channel" in r.text.lower()[:2000] and "group" not in r.text.lower()[:2000]:
                    return ("dead", code)
                return ("live", code, title)
            if attempt == 0:
                time.sleep(8)  # ambiguous 200-empty: retry once after pause, fresh session
                sess = requests.Session()
                continue
            return ("dead", code)
        except requests.exceptions.RequestException:
            if attempt == 0:
                time.sleep(5)
                continue
            return ("pending", code)
    return ("dead", code)

results = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(check_code, c): c for c in candidates}
    done = 0
    for f in futs:
        res = f.result()
        results[futs[f]] = res
        done += 1
        if done % 50 == 0:
            print(f"  verified {done}/{len(candidates)}", flush=True)
            # checkpoint
            _v = [candidates[c] for c, r in results.items() if r and r[0] == "live"]
            _p = [dict(candidates[c], reason="transport") for c, r in results.items() if r and r[0] == "pending"]
            json.dump(_v, open(os.path.join(WAVE, "team04-leads-harvest-d.json"), "w"), ensure_ascii=False)
            json.dump(_p, open(os.path.join(WAVE, "team04-leads-harvest-d-pending.json"), "w"), ensure_ascii=False)

VERIFIED = [candidates[c] for c, r in results.items() if r and r[0] == "live"]
PENDING = [dict(candidates[c], reason="transport") for c, r in results.items() if r and r[0] == "pending"]
DEAD = sum(1 for r in results.values() if r and r[0] == "dead")
# dedupe leads
seen_l = set(); leads_out = []
for l in new_leads:
    if l["url"] not in seen_l:
        seen_l.add(l["url"]); leads_out.append(l)

def w(name, data):
    for i in range(5):
        try:
            with open(os.path.join(WAVE, name), "w") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=1)
            return True
        except OSError as e:
            print(f"  write {name} failed ({e}), retry {i+1}", flush=True)
            time.sleep(2)
    return False

w("team04-leads-harvest-d.json", VERIFIED)
w("team04-leads-harvest-d-pending.json", PENDING)
w("team04-leads-harvest-d-leads.json", leads_out)
print(f"DONE attempted={attempted} candidates={len(candidates)} verified={len(VERIFIED)} "
      f"pending={len(PENDING)} dead={DEAD} leads={len(leads_out)} failed_tags={len(failed_tags)}", flush=True)
print("FAILED TAGS:", json.dumps(failed_tags, indent=0), flush=True)
