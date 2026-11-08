#!/usr/bin/env python3
"""Team 02 — wave 20261108 slice 02 harvest.
Fetches listing pages, extracts chat.whatsapp.com codes + names,
verifies each code live (og:title), dedupes vs union, writes 3 outputs.
"""
import json, re, time, html, os, sys, subprocess
import requests

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261108")
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
S = requests.Session(); S.headers.update(UA)

def load_json(p):
    with open(p, encoding='utf-8') as f: return json.load(f)

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

union = set(load_json(os.path.join(WAVE, "dedupe_union.json")))
print("union size:", len(union), flush=True)
slice_entries = load_json(os.path.join(WAVE, "leads_slice_02.json"))
slice_urls = set(e["url"] for e in slice_entries)
print("slice urls:", len(slice_entries), flush=True)

ADULT_EMOJI = set("🥵🍆🍑🔞💦👅👄💋")
BLOCK_WORDS = ["xxx", "porn", "sex video", "sex videos", "call girl", "call girls",
               "escort", "bitfinex", "paypal loader", "counterfeit", "fake currency",
               "fake money", "money mule", "adult video", "18+ video", "nude", "sexy video"]
GENERIC_TITLES = {"whatsapp group", "join this group on whatsapp", "whatsapp", "join group on whatsapp"}

CATEGORIES = ["Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health",
  "Business","Gaming","Friendship","Community & Social","Online Earning","Crypto","Cooking",
  "Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell","Finance","Funny"]

COUNTRY_MAP = {"united states":"US","india":"IN","pakistan":"PK","united kingdom":"GB",
  "bangladesh":"BD","nigeria":"NG","sri lanka":"LK","nepal":"NP","kenya":"KE","ghana":"GH",
  "south africa":"ZA","australia":"AU","canada":"CA","indonesia":"ID","malaysia":"MY",
  "philippines":"PH","brazil":"BR","spain":"ES","portugal":"PT","turkey":"TR","uae":"AE",
  "saudi arabia":"SA","egypt":"EG","morocco":"MA","iran":"IR","afghanistan":"AF"}

def clean_text(t):
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t or ''))
    t = re.sub(r'\s+', ' ', t).strip(' -–—|•·\u200b')
    return t.strip()

def blocked(name, desc=""):
    hay = (name + " " + desc).lower()
    if any(e in name for e in ADULT_EMOJI):
        return "adult-emoji"
    for w in BLOCK_WORDS:
        if w in hay:
            return "blocked-word:" + w
    return None

def map_category(chip, name):
    h = (chip + " " + name).lower()
    if any(k in h for k in ["pubg", "free fire", "gaming", "game", "esport", "fantasy"]): return "Gaming"
    if any(k in h for k in ["cricket", "football", "sports", "psl", "ipl"]): return "Sports"
    if any(k in h for k in ["job", "naukri", "sarkari", "employment", "hiring"]): return "Jobs"
    if any(k in h for k in ["quran", "islam", "muslim", "madrasa", "namaz"]): return "Islamic"
    if any(k in h for k in ["binance", "crypto", "bitcoin", "trading"]): return "Crypto"
    if any(k in h for k in ["earn", "earning", "make money"]): return "Online Earning"
    if any(k in h for k in ["movie", "drama", "music", "entertain", "funny", "meme", "comedy", "shitpost"]):
        return "Funny" if any(k in h for k in ["funny", "meme", "shitpost"]) else "Entertainment"
    if any(k in h for k in ["news"]): return "News"
    if any(k in h for k in ["study", "educat", "student", "exam", "physics", "class 12", "board"]): return "Education"
    if any(k in h for k in ["scholarship"]): return "Scholarship"
    if any(k in h for k in ["health", "fitness", "medical"]): return "Health"
    if any(k in h for k in ["business"]): return "Business"
    if any(k in h for k in ["technology", "developer", "tech", "webtech"]): return "Technology"
    if any(k in h for k in ["cook", "food", "recipe"]): return "Cooking"
    if any(k in h for k in ["poetry", "shayari"]): return "Poetry"
    if any(k in h for k in ["travel", "tour"]): return "Travel"
    if any(k in h for k in ["freelance"]): return "Freelance"
    if any(k in h for k in ["real estate", "property"]): return "Real Estate"
    if any(k in h for k in ["buy", "sell", "shopping"]): return "Buy & Sell"
    if any(k in h for k in ["finance", "solar"]): return "Finance"
    if any(k in h for k in ["friend", "chat", "chill", "single"]): return "Friendship"
    return "Community & Social"

def fetch(url, timeout=30, session=None):
    sess = session or S
    r = sess.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text

def curl_fetch(url, timeout=40):
    try:
        out = subprocess.run(["curl", "-sS", "-L", "--max-time", str(timeout),
            "-A", UA['User-Agent'], url], capture_output=True, text=True, timeout=timeout+10)
        if out.returncode == 0 and out.stdout:
            return out.stdout
    except Exception as e:
        print("curl err", url, e, flush=True)
    return None

# ---------------- candidate collection ----------------
# candidates: dict code -> {name, category, country, source_url, invite_form}
candidates = {}
new_leads = {}   # url -> source label

def add_candidate(code, name, category, country, source_url, invite_form="plain"):
    if len(code) != 22 or code in union or code in candidates:
        return False
    candidates[code] = {"name": clean_text(name)[:120], "category": category,
                        "country": country, "source": source_url, "form": invite_form}
    return True

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})(?![A-Za-z0-9])')

def extract_listicle(url, category, country, name_from="context"):
    """Extract (code, name) pairs from a listicle page (tables / <li> items)."""
    try:
        t = fetch(url)
    except Exception as e:
        print("FETCH FAIL", url, e, flush=True)
        t = curl_fetch(url)
        if not t:
            print("CURL FAIL too", url, flush=True)
            return 0
    n = 0
    # table rows first
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S | re.I):
        m = CODE_RE.search(row)
        if not m: continue
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)
        name = clean_text(tds[0]) if tds else ""
        form = "invite" if "/invite/" in row[m.start():m.start()+40] else "plain"
        if add_candidate(m.group(1), name, category, country, url, form): n += 1
    # list items
    for li in re.findall(r'<li[^>]*>(.*?)</li>', t, re.S | re.I):
        m = CODE_RE.search(li)
        if not m: continue
        before = li[:m.start()]
        name = clean_text(before)
        # strip trailing separators / "Join" words
        name = re.sub(r'(join|click here|join group|join now)\s*$', '', name, flags=re.I).strip(' -–—')
        form = "invite" if "/invite/" in li[m.start():m.start()+40] else "plain"
        if add_candidate(m.group(1), name, category, country, url, form): n += 1
    # fallback: any remaining code with context text
    for m in CODE_RE.finditer(t):
        if m.group(1) in candidates or m.group(1) in union: continue
        ctx = clean_text(t[max(0, m.start()-400):m.start()])
        name = ctx.split('|')[-1].strip()[-100:] if ctx else ""
        name = re.sub(r'(join|click here|join group)\s*$', '', name, flags=re.I).strip(' -–—')
        if len(name) > 2 and add_candidate(m.group(1), name, category, country, url,
                                           "invite" if "/invite/" in t[m.start():m.start()+40] else "plain"):
            n += 1
    print(f"LISTICLE {url} -> +{n} fresh candidates (total {len(candidates)})", flush=True)
    return n

# ---- 1. groupsinvite.link detail pages (24) ----
gi_slugs = []
for e in slice_entries:
    m = re.match(r'https://groupsinvite\.link/group/link/([a-z0-9]+)/', e["url"])
    if m: gi_slugs.append(m.group(1))
print("groupsinvite slugs:", len(gi_slugs), flush=True)
for slug in gi_slugs:
    detail = f"https://groupsinvite.link/group/link/{slug}/"
    try:
        t = fetch(detail)
    except Exception as e:
        print("GI FETCH FAIL", detail, e, flush=True)
        continue
    name_m = re.search(r'<div class="invite-hero-name">(.*?)</div>', t, re.S)
    name = clean_text(name_m.group(1)) if name_m else ""
    cat_m = re.search(r'class="category-chip"[^>]*>(.*?)</a>', t, re.S)
    chip = clean_text(cat_m.group(1)) if cat_m else ""
    ctry_m = re.search(r'group/country/[^"]*"[^>]*>(.*?)</a>', t, re.S)
    ctry_raw = clean_text(ctry_m.group(1)) if ctry_m else ""
    country = COUNTRY_MAP.get(ctry_raw.lower(), "International")
    desc_m = re.search(r'data-full-description="([^"]*)"', t)
    desc = html.unescape(desc_m.group(1)) if desc_m else ""
    # rules page reveals the real code
    rules = f"https://groupsinvite.link/group/rules/{slug}/"
    try:
        rt = fetch(rules)
        cm = CODE_RE.search(rt)
        if cm:
            cat = map_category(chip, name)
            if add_candidate(cm.group(1), name, cat, country, detail):
                candidates[cm.group(1)]["desc_hint"] = desc
        else:
            print("GI NO CODE on rules page", slug, flush=True)
    except Exception as e:
        print("GI RULES FAIL", slug, e, flush=True)
    # harvest related detail URLs as leads
    for rel in set(re.findall(r'https://groupsinvite\.link/group/link/[a-z0-9]+/', t)):
        if rel not in slice_urls and rel != detail:
            new_leads[rel] = "groupsinvite.link related group"
    time.sleep(0.5)
print("after groupsinvite: candidates =", len(candidates), flush=True)

# ---- 2. code-bearing listicles ----
extract_listicle("https://appgrouplink.com/government-jobs-whatsapp-group-links/", "Jobs", "IN")
extract_listicle("https://wagroupshub.com/sports-whatsapp-group-links/", "Sports", "IN")
extract_listicle("https://whtsgrouplink.com/movies-whatsapp-group-links/", "Entertainment", "IN")
extract_listicle("https://whatzgrouplink.com/movies-and-drama-whatsapp-group-link/", "Entertainment", "PK")
extract_listicle("https://whtspgrouplink.com/south-indian-whatsapp-group-links/", "Entertainment", "IN")
# slow hosts via curl
for url, cat, ctry in [
    ("https://www.sociallykeeda.com/pakistani-whatsapp-group/", "Community & Social", "PK"),
    ("https://joinwagroup.link/lahore-whatsapp-group-link/", "Community & Social", "PK"),
]:
    t = curl_fetch(url)
    if t:
        # reuse extraction by monkey-patching fetch result: write temp parse inline
        n0 = len(candidates)
        for row in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S | re.I):
            m = CODE_RE.search(row)
            if not m: continue
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)
            add_candidate(m.group(1), clean_text(tds[0]) if tds else "", cat, ctry, url)
        for li in re.findall(r'<li[^>]*>(.*?)</li>', t, re.S | re.I):
            m = CODE_RE.search(li)
            if not m: continue
            nm = clean_text(li[:m.start()])
            add_candidate(m.group(1), nm, cat, ctry, url)
        print(f"CURL LISTICLE {url} -> +{len(candidates)-n0}", flush=True)
    else:
        print("CURL FAIL", url, flush=True)

# ---- 3. sarkarijobs: check for codes / internal group links ----
try:
    t = fetch("https://www.sarkarijobs.com/join-whatsapp-groups-links-for-sarkari-jobs-sarkari-result/")
    print("sarkarijobs codes:", len(set(CODE_RE.findall(t))),
          "wa.me:", len(re.findall(r'wa\.me/', t)), flush=True)
except Exception as e:
    print("sarkarijobs fetch fail", e, flush=True)

# ---- 4. whtsagrouplinks categories (403-prone, curl) ----
for url, cat, ctry in [
    ("https://www.whtsagrouplinks.com/pakistani-whatsapp-group-link/", "Community & Social", "PK"),
    ("https://www.whtsagrouplinks.com/indian-whatsapp-group-link/", "Community & Social", "IN"),
    ("https://www.whtsagrouplinks.com/international-whatsapp-groups-links/", "Community & Social", "International"),
    ("https://www.whtsagrouplinks.com/movies-whatsapp-group-link/", "Entertainment", "International"),
]:
    t = curl_fetch(url)
    if not t:
        print("WHTSA FAIL", url, flush=True); continue
    n0 = len(candidates)
    for m in CODE_RE.finditer(t):
        if m.group(1) in candidates or m.group(1) in union: continue
        ctx = clean_text(t[max(0, m.start()-300):m.start()])
        nm = ctx.split('|')[-1].strip()[-100:]
        add_candidate(m.group(1), nm, cat, ctry, url,
                      "invite" if "/invite/" in t[m.start():m.start()+40] else "plain")
    print(f"WHTSA {url} -> +{len(candidates)-n0}", flush=True)

# ---- 5. ongrupos: collect group detail links as leads ----
for cat_url in ["https://ongrupos.com/categoria/amizades","https://ongrupos.com/categoria/tecnologia",
                "https://ongrupos.com/categoria/religiao","https://ongrupos.com/categoria/videos",
                "https://ongrupos.com/categoria/carros-e-motos","https://ongrupos.com/categoria/animes-e-desenhos"]:
    try:
        t = fetch(cat_url)
        for g in set(re.findall(r'https://ongrupos\.com/grupo/[^\s"\'<>]+', t)):
            if g not in slice_urls:
                new_leads[g] = "ongrupos group detail"
    except Exception as e:
        print("ongrupos fail", cat_url, e, flush=True)

# ---- 6. YouTube descriptions (full codes may be in description JSON) ----
YT = [
 ("https://www.youtube.com/watch?v=JKRIwOlro0w", "Education", "IN"),
 ("https://www.youtube.com/shorts/qLyQIXTSUPY", "Education", "IN"),
 ("https://www.youtube.com/watch?v=rt33HvswB4M", "Entertainment", "IN"),
 ("https://www.youtube.com/watch?v=s5a9B-XaIrU", "Entertainment", "IN"),
 ("https://www.youtube.com/watch?v=B0JNw6ZkKfo", "Community & Social", "International"),
 ("https://www.youtube.com/watch?v=qkKqgJEn3P4", "News", "PK"),
 ("https://www.youtube.com/watch?v=jJAXKJMp_F0", "Jobs", "PK"),
 ("https://www.youtube.com/watch?v=dzfjxUcCAAE", "News", "PK"),
 ("https://www.youtube.com/watch?v=WAzy6gcU8JA", "Entertainment", "International"),
 ("https://www.youtube.com/watch?v=PcPcHDSjFHc", "News", "International"),
 ("https://www.youtube.com/watch?v=eaArhRLk754", "News", "LK"),
]
for url, cat, ctry in YT:
    try:
        t = fetch(url, timeout=30)
        dm = re.search(r'"shortDescription":"((?:[^"\\]|\\.)*)"', t)
        title_m = re.search(r'"title":"((?:[^"\\]|\\.)*)"', t)
        desc = bytes(dm.group(1), 'utf-8').decode('unicode_escape') if dm else ""
        title = bytes(title_m.group(1), 'utf-8').decode('unicode_escape') if title_m else ""
        found = set(CODE_RE.findall(desc))
        print(f"YT {url} title={title[:60]!r} codes_in_desc={len(found)}", flush=True)
        for code in found:
            add_candidate(code, title, cat, ctry, url)
    except Exception as e:
        print("YT FAIL", url, e, flush=True)
    time.sleep(1)

print("TOTAL fresh candidates before verify:", len(candidates), flush=True)
write_json_retry(os.path.join(WAVE, "team02-candidates.json"),
                 [{"code": k, **v} for k, v in candidates.items()])

# ---------------- verification ----------------
def record_base(c, code):
    invite = f"https://chat.whatsapp.com/invite/{code}" if c["form"] == "invite" else f"https://chat.whatsapp.com/{code}"
    nm = c["name"] or "WhatsApp Group"
    return {"name": nm, "category": c["category"], "country": c["country"],
            "description": f"Join {nm}, a WhatsApp group listed under {c['category']}.",
            "invite": invite, "image": ""}

def og_title(code, form):
    url = f"https://chat.whatsapp.com/invite/{code}" if form == "invite" else f"https://chat.whatsapp.com/{code}"
    r = S.get(url, timeout=20)
    if r.status_code != 200:
        return None, r.status_code, None
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
    if not m:
        m = re.search(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:title\"", r.text)
    return (html.unescape(m.group(1)).strip() if m else ""), r.status_code, url

verified, pending = [], []
for code, c in candidates.items():
    try:
        title, status, url = og_title(code, c["form"])
    except Exception as e:
        print("TRANSPORT ERR", code, type(e).__name__, flush=True)
        pending.append({**record_base(c, code), "reason": "transport"})
        time.sleep(0.6); continue
    if title == "" and status == 200:
        # ambiguous: retry once after pause with fresh session
        time.sleep(6)
        try:
            S2 = requests.Session(); S2.headers.update(UA)
            r = S2.get(url, timeout=20)
            m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
            title = html.unescape(m.group(1)).strip() if m else ""
            status = r.status_code
        except Exception as e:
            print("TRANSPORT ERR retry", code, type(e).__name__, flush=True)
            pending.append({**record_base(c, code), "reason": "transport"})
            time.sleep(0.6); continue
    if status != 200 or not title or title.lower() in GENERIC_TITLES:
        print(f"DEAD {code} status={status} title={title!r}", flush=True)
        time.sleep(0.6); continue
    if "whatsapp channel" in title.lower():
        print(f"CHANNEL DROP {code} title={title!r}", flush=True)
        time.sleep(0.6); continue
    name = title
    if blocked(name):
        print(f"BLOCKED {code} {blocked(name)} name={name!r}", flush=True)
        time.sleep(0.6); continue
    cat = c["category"]
    # refine category from og:title if page category was generic
    if cat == "Community & Social":
        cat = map_category("", name)
        if cat == "Community & Social":
            cat = c["category"]
    country = c["country"]
    desc = f"Join {name}, a WhatsApp group listed under {cat}. Connect with members, share updates and stay active in this {cat.lower()} community."
    invite = f"https://chat.whatsapp.com/invite/{code}" if c["form"] == "invite" else f"https://chat.whatsapp.com/{code}"
    verified.append({"name": name, "category": cat, "country": country,
                     "description": desc, "invite": invite, "image": ""})
    print(f"OK {code} :: {name!r} [{cat}/{country}]", flush=True)
    time.sleep(0.6)

print("verified:", len(verified), "pending:", len(pending), flush=True)

leads_out = [{"url": u, "source": s} for u, s in sorted(new_leads.items()) if u not in slice_urls]
print("new leads:", len(leads_out), flush=True)

write_json_retry(os.path.join(WAVE, "team02-leads-harvest-b.json"), verified)
write_json_retry(os.path.join(WAVE, "team02-leads-harvest-b-pending.json"), pending)
write_json_retry(os.path.join(WAVE, "team02-leads-harvest-b-leads.json"), leads_out)
print("DONE verified=%d pending=%d leads=%d" % (len(verified), len(pending), len(leads_out)), flush=True)
