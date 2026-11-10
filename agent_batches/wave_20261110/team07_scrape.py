#!/usr/bin/env python3
"""TEAM 07 — WhatsGroupLinks wave_20261110, leads slice 7.
Fetches 184 listing pages, extracts WhatsApp invite codes, dedupes against
the 108,365-code union, verifies each fresh code via chat.whatsapp.com,
writes the 4 output files. Writes ONLY inside the wave_20261110 dir.
"""
import html as htmlmod
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

WORK = Path("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110")
SCRATCH = WORK / "_team07_scratch"
SCRATCH.mkdir(parents=True, exist_ok=True)
SLICE = Path("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_07.json")
EXISTING = Path("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")
GROUPS = Path("/home/hatch/workspace/whatsapp-groups-site/groups.json")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
GROUPDA_LEADS = []
ALLOWED_CATS = {"Entertainment","Jobs","Education","Islamic","Sports","Community & Social",
                "Finance","Funny","Buy Sell","Health","News","Gaming","Technology","Business"}

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})")
CHAN_RE = re.compile(r"whatsapp\.com/channel/")
OG_TITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)

# ---- content screens ----
ADULT_RES = [
    r"🔞", r"🥵", r"\bsexy\b", r"\bhookup\b", r"\bescort\b", r"\bporn\b", r"\bxxx\b",
    r"sex\s*chat", r"\bsexting\b", r"\bhorny\b", r"\bnaughty\b", r"\bmasturbat",
    r"friends?\s+with\s+benefits", r"\bfwb\b", r"sex\s*vc\b", r"\bvc\s*sex\b",
    r"18\+\s*(sex|porn|hot|adult|nude|xxx)", r"(sex|porn|hot|adult|nude)\s*18\+",
    r"\bnude\b", r"\bcall\s*girl", r"\bdesi\s*bhabhi\b",
]
SCAM_RES = [
    r"b-?love", r"\bforsage\b", r"\bsheyi\b", r"airdrop", r"paypal\s+loader",
    r"\bbitfinex\b", r"counterfeit\s+curren", r"crypto[ -]?doubling",
    r"\bcarding\b", r"double\s+(your\s+)?(money|crypto|bitcoin|investment)",
    r"double\s+your\s+profit", r"investment\s*doubl", r"money\s*mule",
    r"earn\s+\$?\d+\s*(daily|per day)\s*(guaranteed|without investment)",
]
ADULT_PATS = [re.compile(p, re.I) for p in ADULT_RES]
SCAM_PATS = [re.compile(p, re.I) for p in SCAM_RES]
PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{9,}\d")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SOURCE_WORDS = re.compile(r"\b(groupjoin|groupda|ongrupos|igrupos|grupbul|groupsinvite|groupizo|appgrouplink|groupssor)\b", re.I)

def screen(text):
    """Return 'adult' / 'scam' / 'personal' / None."""
    t = text or ""
    for p in ADULT_PATS:
        if p.search(t):
            return "adult"
    for p in SCAM_PATS:
        if p.search(t):
            return "scam"
    if PHONE_RE.search(t) or EMAIL_RE.search(t):
        return "personal"
    return None

def clean_text(s):
    if not s:
        return ""
    s = htmlmod.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"https?://\S+", " ", s)
    s = SOURCE_WORDS.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip(" -–—•·|")
    return s

def clean_name(s, maxlen=100):
    s = clean_text(s)
    s = s.replace("WhatsApp Group Link", "").replace("whatsapp group link", "").strip(" -–—•·|")
    s = re.sub(r"\s+", " ", s).strip()
    return s[:maxlen].strip() or "WhatsApp Group"

def make_desc(name, raw_desc, cat):
    d = clean_text(raw_desc or "")
    # keep at most 2 sentences, drop trailing junk
    if d:
        parts = re.split(r"(?<=[.!?])\s+", d)
        d = " ".join(parts[:2]).strip()
        if len(d) > 220:
            d = d[:217].rsplit(" ", 1)[0] + "."
        if d and not d.endswith((".", "!", "?")):
            d += "."
        if len(d) >= 25:
            return d
    topic = {"Entertainment": "entertainment and fun discussions",
             "Jobs": "job openings and career updates",
             "Education": "study material and learning discussions",
             "Islamic": "Islamic reminders and discussions",
             "Sports": "sports news and discussions",
             "Finance": "finance and money discussions",
             "Funny": "funny posts and memes",
             "Buy Sell": "buying and selling",
             "Health": "health tips and discussions",
             "News": "news and current updates",
             "Gaming": "gaming discussions and updates",
             "Technology": "technology discussions and updates",
             "Business": "business ideas and discussions"}.get(cat, "community discussions")
    return f"Join {name}, a WhatsApp group for {topic} with other members."

# ---- category maps ----
GJ_CAT = {"sports & fitness": "Sports", "sports and fitness": "Sports", "earn money online": "Finance",
          "entertainment": "Entertainment", "jobs": "Jobs", "education": "Education",
          "islamic": "Islamic", "news": "News", "gaming": "Gaming", "technology": "Technology",
          "business": "Business", "health": "Health", "funny": "Funny", "buy & sell": "Buy Sell",
          "buy and sell": "Buy Sell", "community": "Community & Social", "friendship": "Community & Social",
          "crypto": "Finance", "finance": "Finance", "music": "Entertainment", "movies": "Entertainment",
          "adult": "ADULT", "dating": "Community & Social"}
GI_CAT = {"ai-machine-learning-data-science": "Technology", "astrology-horoscope-spirituality": "Community & Social",
          "beauty-fashion-lifestyle": "Community & Social", "business-startup-earn-money": "Business",
          "buy-sell-marketplace": "Buy Sell", "career-jobs-freelancing": "Jobs",
          "community-friendship-social": "Community & Social", "crypto-blockchain-web3": "Finance",
          "dating-matrimony-relationships": "Community & Social", "education-study-learning": "Education",
          "entertainment-comedy-fun": "Entertainment", "finance-stocks-investing": "Finance",
          "fitness-gym-bodybuilding": "Health", "local-city-country": "Community & Social",
          "marketing-advertising-affiliate": "Business", "music-songs-bands": "Entertainment",
          "news-politics-information": "News", "photography-video-editing": "Entertainment",
          "programming-coding-software": "Technology", "religion-devotional-faith": "Community & Social",
          "science-engineering-technology": "Technology"}
ONG_CAT = {"amor-e-romance": "Community & Social", "links": "Community & Social", "gays": "Community & Social",
           "namoro": "Community & Social", "cidades": "Community & Social", "jogos": "Gaming",
           "compras-e-vendas": "Buy Sell", "vagas-de-emprego": "Jobs", "negocios": "Business",
           "esportes": "Sports", "filmes-e-series": "Entertainment", "futebol": "Sports",
           "status": "Funny", "memes": "Funny", "musicas": "Entertainment", "geeks": "Entertainment",
           "novelas": "Entertainment", "frases-e-mensagens": "Community & Social",
           "moda-e-beleza": "Community & Social", "profissoes": "Jobs",
           "figurinhas-e-stickers": "Funny", "empreendedorismo": "Business", "receitas": "Community & Social",
           "fas": "Entertainment", "emagrecimento": "Health", "educativo": "Education",
           "estudos": "Education", "ciencias": "Education", "fisica": "Health", "cultivo": "Community & Social",
           "ganhar-seguidores": "Community & Social", "redes-sociais": "Community & Social",
           "lgbt": "Community & Social", "bbb": "Entertainment", "free-fire": "Gaming"}
GS_CAT = {"entertainment": "Entertainment", "dating": "Community & Social", "news": "News",
          "business": "Business", "gaming": "Gaming", "crypto": "Finance", "education": "Education",
          "shopping": "Buy Sell", "sports": "Sports", "jobs": "Jobs", "health": "Health",
          "technology": "Technology", "religion": "Community & Social", "travel": "Community & Social",
          "music": "Entertainment", "friendship, games, entertainment": "Community & Social",
          "friendship, fun, games": "Community & Social", "friends": "Community & Social"}
COUNTRY_SLUG = {"pakistan": "PK", "india": "IN", "bangladesh": "BD", "usa": "US", "uk": "GB",
                "united-kingdom": "GB", "nigeria": "NG", "kenya": "KE", "ghana": "GH",
                "south-africa": "ZA", "canada": "CA", "australia": "AU", "nepal": "NP",
                "sri-lanka": "LK", "philippines": "PH", "indonesia": "ID", "malaysia": "MY",
                "turkey": "TR", "uae": "AE", "saudi-arabia": "SA", "egypt": "EG", "brazil": "BR",
                "mexico": "MX", "spain": "ES", "germany": "DE", "france": "FR", "italy": "IT",
                "netherlands": "NL", "russia": "RU", "ukraine": "UA", "iran": "IR", "iraq": "IQ",
                "afghanistan": "AF", "myanmar": "MM", "thailand": "TH", "vietnam": "VN", "china": "CN",
                "japan": "JP", "korea": "KR", "tanzania": "TZ", "uganda": "UG", "zambia": "ZM",
                "zimbabwe": "ZW", "ethiopia": "ET", "morocco": "MA", "algeria": "DZ", "sudan": "SD",
                "colombia": "CO", "argentina": "AR", "peru": "PE", "chile": "CL", "venezuela": "VE"}

def fetch(url, timeout=15):
    try:
        r = requests.get(url, headers=UA, timeout=timeout)
        return r.status_code, r.text
    except Exception as e:
        return None, f"ERR:{type(e).__name__}: {e}"

def main():
    t0 = time.time()
    log = []
    def say(m):
        print(f"[{time.time()-t0:7.1f}s] {m}", flush=True)
        log.append(m)

    # ---------- dedupe union ----------
    existing = set(json.load(open(EXISTING)))
    say(f"existing_codes: {len(existing)}")
    groups = json.load(open(GROUPS))
    gcodes = set()
    for g in groups:
        m = CODE_RE.search(g.get("invite", "") or "")
        if m:
            gcodes.add(m.group(1))
    union = existing | gcodes
    say(f"groups.json codes: {len(gcodes)}; union: {len(union)}")

    items = json.load(open(SLICE))
    say(f"slice entries: {len(items)}")

    # skip groupjoin adult/sexual tag pages entirely (never fetch/verify/bank)
    ADULT_TAGS = {"adult", "sexchat", "sexting", "sex-vc", "naughty", "horny",
                  "masturbation", "friends-with-benefits"}
    skipped_adult_pages = []
    todo = []
    for it in items:
        u = htmlmod.unescape(it["url"])
        low = u.lower()
        if "groupjoin.link/tag/" in low:
            tag = low.split("/tag/")[1].split("?")[0].strip().lower()
            if tag in ADULT_TAGS:
                skipped_adult_pages.append(u)
                continue
        # groupda.com is Cloudflare-403 via curl and Wayback-429: never fetch, bank as leads
        if "groupda.com" in urlparse(u).netloc.lower():
            continue
        todo.append({"url": u, "source": it.get("source", "")})
    say(f"skipped adult groupjoin tag pages: {len(skipped_adult_pages)}; to fetch: {len(todo)}")
    # leads dict is built later in main(); pre-seed groupda URLs here via a module-level holder
    GROUPDA_LEADS.extend([
        (htmlmod.unescape(it["url"]), "groupda.com WP listing post (unfetched: Cloudflare 403 via curl; Wayback 429)")
        for it in items if "groupda.com" in urlparse(htmlmod.unescape(it["url"])).netloc.lower()
        and "sitemap" not in htmlmod.unescape(it["url"]).lower()
    ])

    candidates = {}   # code -> dict(name, category, country, description, source_page)
    leads = {}        # url -> source label
    input_urls = {htmlmod.unescape(i["url"]) for i in items}
    for u, s in GROUPDA_LEADS:
        if u not in input_urls:
            leads.setdefault(u, s)

    def add_candidate(code, name, cat, country, desc, src_page):
        if not code or len(code) < 10 or code.startswith("XXXX"):
            return
        if code in candidates:
            return
        candidates[code] = {"name": clean_name(name), "category": cat if cat in ALLOWED_CATS else "Community & Social",
                            "country": country if re.fullmatch(r"[A-Z]{2}", country or "") else "International",
                            "description": "", "_raw_desc": desc or "", "_src": src_page}

    def add_lead(url, source):
        u = htmlmod.unescape(url).strip()
        if u and u not in input_urls:
            leads.setdefault(u, source)

    # ---------- fetch listing pages ----------
    def fetch_listing(it):
        return it, fetch(it["url"])

    listings = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_listing, it): it for it in todo}
        for f in as_completed(futs):
            it, (st, txt) = f.result()
            listings[it["url"]] = (st, txt)
    ok = sum(1 for st, _ in listings.values() if st == 200)
    say(f"listings fetched: {ok}/ {len(todo)} HTTP200")

    # ---------- parse per domain ----------
    gi_details = []   # (slug, name, cat, country, page_url)
    ag_posts = []     # appgrouplink post urls from its sitemap (already in todo as 1 url)
    for it in todo:
        url, src = it["url"], it["source"]
        st, txt = listings.get(url, (None, ""))
        host = urlparse(url).netloc.lower()
        if st != 200:
            # unfetchable listing -> keep as lead for a future (browser) wave
            if "groupda.com" in host and url.endswith(".xml") is False and "sitemap" not in url:
                add_lead(url, "groupda.com WP listing post (unfetched: Cloudflare 403 via curl)")
            elif "groupda.com" in host:
                pass
            else:
                add_lead(url, f"{src} (unfetched HTTP {st})")
            continue
        if CHAN_RE.search(txt) and "groupssor" not in host:
            pass  # channels handled per-item below where relevant

        if "groupjoin.link" in host:
            # Next.js embeds groups as an escaped JSON string: \"group_title\" etc.
            txt = txt.replace('\\"', '"').replace("\\u0026", "&")
            # positional pairing: titles, descs, links, categories in document order
            titles = re.findall(r'"group_title":"((?:[^"\\]|\\.)*)"', txt)
            descs = re.findall(r'"group_desc":"((?:[^"\\]|\\.)*)"', txt)
            links = re.findall(r'"link":"https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', txt)
            cats = re.findall(r'"category":\{"id":\d+,"category_name":"([^"]+)"', txt)
            countries = re.findall(r'"country":\s*"([A-Za-z]{2})"', txt)
            n = min(len(titles), len(links))
            for i in range(n):
                cat_raw = (cats[i] if i < len(cats) else "").strip().lower()
                if cat_raw == "adult":
                    continue
                cat = GJ_CAT.get(cat_raw, "Community & Social")
                ctry = countries[i].upper() if i < len(countries) else "International"
                add_candidate(links[i], titles[i], cat, ctry,
                              descs[i] if i < len(descs) else "", url)
            say(f"GJ {url.split('?')[0][-40:]}: titles={len(titles)} links={len(links)} cats={len(cats)}")
        elif "groupsinvite.link" in host:
            cat_slug = url.rstrip("/").split("/")[-1]
            cat = GI_CAT.get(cat_slug, "Community & Social")
            blocks = txt.split('group-name-link')
            for b in blocks[1:]:
                m = re.search(r'href="https://groupsinvite\.link/group/link/([a-z0-9]+)/"[^>]*>(.*?)</a>', b, re.S)
                if not m:
                    continue
                slug, nm = m.group(1), clean_text(m.group(2))
                cm = re.search(r'/group/country/([a-z\-]+)/', b)
                ctry = COUNTRY_SLUG.get(cm.group(1), "International") if cm else "International"
                gi_details.append((slug, nm, cat, ctry, url))
        elif "ongrupos.com" in host:
            cat_slug = url.rstrip("/").split("/")[-1]
            cat = ONG_CAT.get(cat_slug, "Community & Social")
            ids = re.findall(r'href="https://ongrupos\.com/grupo/([A-Za-z0-9_-]{10,})"', txt)
            # titles: card text segments between grupo links
            segs = re.split(r'https://ongrupos\.com/grupo/[A-Za-z0-9_-]+', txt)
            for j, gid in enumerate(dict.fromkeys(ids)):
                seg = segs[j + 1] if j + 1 < len(segs) else ""
                text = clean_text(seg)
                nm = text.split(".")[0][:100] if text else gid
                # name is usually the first short chunk before description; take first 60 chars chunk
                nm = nm.strip()
                add_candidate(gid, nm, cat, "BR", text, url)
        elif "grupbul.com" in host:
            for gid in dict.fromkeys(re.findall(r'href="https://grupbul\.com/group/(\d+)"', txt)):
                add_lead(f"https://grupbul.com/group/{gid}", "grupbul.com group detail (JS-gated invite)")
        elif "igrupos.com" in host:
            for gid, title in re.findall(r'id="grupo-(\d+)"[\s\S]{0,3000}?<h3 class="group-title"[^>]*>(.*?)</h3>', txt):
                add_lead(f"https://www.igrupos.com/grupo/{gid}", f"igrupos.com group detail: {clean_text(title)[:60]}")
        elif "groupizo.com" in host and url.endswith(".xml"):
            for loc in re.findall(r"<loc>(.*?)</loc>", txt):
                add_lead(htmlmod.unescape(loc), "groupizo.com group detail")
        elif "appgrouplink.com" in host and url.endswith(".xml"):
            for loc in re.findall(r"<loc>(.*?)</loc>", txt):
                ag_posts.append(htmlmod.unescape(loc))
        elif "groupssor-api" in host:
            try:
                data = json.loads(txt)
            except Exception as e:
                say(f"groupssor JSON parse fail: {e}")
                data = []
            for d in data:
                if str(d.get("platform", "")).lower() != "whatsapp":
                    continue
                link = d.get("inviteLink", "") or ""
                if CHAN_RE.search(link):
                    continue
                m = CODE_RE.search(link)
                if not m:
                    continue
                cat = GS_CAT.get(str(d.get("category", "")).lower(), "Community & Social")
                ctry = str(d.get("country", "") or "").upper()
                if not re.fullmatch(r"[A-Z]{2}", ctry):
                    ctry = "International"
                add_candidate(m.group(1), d.get("name", ""), cat, ctry, d.get("description", ""), url)
            say(f"groupssor items: {len(data)}")
        elif "groupda.com" in host:
            # Cloudflare-blocked normally; if it ever returns 200, parse WP table rows
            rows = re.findall(r"<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)", txt, re.S)
            for nm, code in rows:
                add_candidate(code, nm, "Community & Social", "International", "", url)
        else:
            # generic fallback: any codes on the page
            for code in dict.fromkeys(CODE_RE.findall(txt)):
                add_candidate(code, urlparse(url).path.strip("/").replace("-", " ")[:60],
                              "Community & Social", "International", "", url)

    say(f"candidates extracted (all sources): {len(candidates)}; GI detail pages queued: {len(set(s for s, *_ in gi_details))}; AG posts: {len(ag_posts)}")

    # ---------- groupsinvite detail pages (exact-case codes) ----------
    # Detail pages take ~14s each on this slow host: fetch at most 6 slugs per
    # category now; bank the rest as leads for a dedicated resolver wave.
    gi_by_slug = {}
    per_cat = {}
    for slug, nm, cat, ctry, page in gi_details:
        gi_by_slug.setdefault(slug, (nm, cat, ctry, page))
    say(f"unique GI slugs: {len(gi_by_slug)}")
    gi_fetch_slugs = []
    for slug, (nm, cat, ctry, page) in gi_by_slug.items():
        if per_cat.get(cat, 0) < 6:
            per_cat[cat] = per_cat.get(cat, 0) + 1
            gi_fetch_slugs.append(slug)
        else:
            add_lead(f"https://groupsinvite.link/group/link/{slug}/",
                     f"groupsinvite.link group detail ({cat}; slug is lowercase code)")
    say(f"GI detail pages to fetch (6/category cap): {len(gi_fetch_slugs)}; rest banked as leads")

    def fetch_gi(item):
        slug, (nm, cat, ctry, page) = item
        st, txt = fetch(f"https://groupsinvite.link/group/link/{slug}/", timeout=25)
        code = None
        ogd = ""
        if st == 200:
            m = CODE_RE.search(txt)
            if m:
                code = m.group(1)
            om = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', txt, re.I)
            if om:
                ogd = htmlmod.unescape(om.group(1))
        return slug, code, ogd, st
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(fetch_gi, (slug, gi_by_slug[slug])): slug for slug in gi_fetch_slugs}
        for f in as_completed(futs):
            slug, code, ogd, st = f.result()
            if code:
                nm, cat, ctry, page = gi_by_slug[slug]
                add_candidate(code, nm, cat, ctry, ogd, page)
            else:
                add_lead(f"https://groupsinvite.link/group/link/{slug}/",
                         "groupsinvite.link group detail (detail fetch failed)")
    say(f"candidates after GI details: {len(candidates)}")

    # ---------- appgrouplink post pages ----------
    def fetch_ag(u):
        st, txt = fetch(u)
        out = []
        if st == 200:
            rows = re.findall(r"<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?chat\.whatsapp\.com/invite/([A-Za-z0-9_-]+)", txt, re.S)
            for nm, code in rows:
                out.append((nm, code))
            if not rows:
                for code in dict.fromkeys(CODE_RE.findall(txt)):
                    out.append((u, code))
        return u, st, out
    ag_done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_ag, u): u for u in ag_posts}
        for f in as_completed(futs):
            u, st, rows = f.result()
            if st == 200:
                ag_done += 1
                slug = urlparse(u).path.strip("/").replace("-whatsapp-group-links", "").replace("-", " ")
                for nm, code in rows:
                    add_candidate(code, nm, "Community & Social", "International", "", u)
            else:
                add_lead(u, "appgrouplink.com post (unfetched)")
    say(f"AG posts fetched OK: {ag_done}/{len(ag_posts)}; candidates: {len(candidates)}")
    json.dump({k: v for k, v in candidates.items()},
              open(SCRATCH / "candidates_raw.json", "w"), ensure_ascii=False, indent=1)

    # ---------- dedupe + screen ----------
    fresh = {}
    dup = 0
    for code, c in candidates.items():
        if code in union:
            dup += 1
            continue
        fresh[code] = c
    say(f"dupes vs union: {dup}; fresh pre-screen: {len(fresh)}")

    exclusions = []
    screened = {}
    for code, c in fresh.items():
        blob = f"{c['name']} {c['_raw_desc']}"
        r = screen(blob)
        if r:
            exclusions.append({"code": code, "reason": f"{r}: name/desc screen ({blob[:80]})"})
            continue
        screened[code] = c
    say(f"screened out pre-verify: {len(exclusions)}; to verify: {len(screened)}")

    # ---------- verify (max 3 parallel, >=0.5s between starts, 15s timeout) ----------
    lock = threading.Lock()
    last_start = [0.0]

    def verify_one(code):
        url = f"https://chat.whatsapp.com/{code}"
        attempts = 0
        last_err = ""
        last_status = None
        while attempts < 3:
            attempts += 1
            with lock:
                wait = 0.5 - (time.time() - last_start[0])
                if wait > 0:
                    time.sleep(wait)
                last_start[0] = time.time()
            try:
                r = requests.get(url, headers=UA, timeout=15)
                last_status = r.status_code
                if r.status_code in (429, 403, 500, 502, 503, 504):
                    return code, "pending", "", f"HTTP {r.status_code}"
                m = OG_TITLE_RE.search(r.text or "")
                title = htmlmod.unescape(m.group(1)).strip() if m else ""
                if title:
                    return code, "live", title, ""
                # 200 but empty title -> retry (spaced); after 3 attempts dead
                last_err = "empty og:title"
                time.sleep(1.0)
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                return code, "pending", "", last_err
        return code, "dead", "", last_err or "empty og:title"

    verified, pending, dead = [], [], []
    dead_n = 0
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(verify_one, code): code for code in screened}
        done = 0
        for f in as_completed(futs):
            code, status, title, err = f.result()
            done += 1
            if done % 100 == 0:
                say(f"verify progress: {done}/{len(screened)} live={len(verified)} pending={len(pending)} dead={dead_n}")
            c = screened[code]
            if status == "live":
                r = screen(title) or screen(f"{c['name']} {c['_raw_desc']}")
                if r:
                    exclusions.append({"code": code, "reason": f"{r}: og:title screen ({title[:80]})"})
                    continue
                desc = make_desc(c["name"], c["_raw_desc"], c["category"])
                if screen(desc):
                    exclusions.append({"code": code, "reason": "scam/adult: generated description screen"})
                    continue
                verified.append({"name": c["name"], "category": c["category"], "country": c["country"],
                                 "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})
            elif status == "pending":
                pending.append({"name": c["name"], "category": c["category"], "country": c["country"],
                                "description": make_desc(c["name"], c["_raw_desc"], c["category"]),
                                "invite": f"https://chat.whatsapp.com/{code}",
                                "reason": err or "transport failure"})
            else:
                dead_n += 1
    say(f"verify done: live={len(verified)} pending={len(pending)} dead={dead_n} excluded={len(exclusions)}")

    # ---------- outputs ----------
    leads_list = [{"url": u, "source": s} for u, s in sorted(leads.items())]
    # also carry the unfetched groupda listing posts as leads (they were input, but re-bank for browser leg)
    json.dump(verified, open(WORK / "team07-leads-slice7.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(WORK / "team07-leads-slice7-pending.json", "w"), ensure_ascii=False, indent=1)
    json.dump(leads_list, open(WORK / "team07-leads-slice7-leads.json", "w"), ensure_ascii=False, indent=1)
    sources = sorted({urlparse(i["url"]).netloc for i in items})
    summary = {
        "team": 7,
        "slice": "leads slice 7",
        "sources": sources,
        "verified": len(verified),
        "pending": len(pending),
        "leads": len(leads_list),
        "dead": dead_n,
        "exclusions": exclusions,
        "resume": "Slice 7 of wave_20261109 fully processed: all 184 listing URLs attempted. "
                  "groupjoin Adult/sexual tag pages skipped unfetched (Adult, Sexchat, Sexting, Sex-vc, Naughty, Horny, Masturbation, Friends-with-benefits). "
                  "groupda.com pages Cloudflare-403 via curl and Wayback 429 — carried as leads for a browser leg. "
                  "grupbul/igrupos invites are JS/POST-gated — their group detail URLs banked as leads. "
                  "groupizo sitemap URLs banked as leads (detail pages hide invites). "
                  "groupsinvite: detail pages take ~14s each, so only 6 groups per category were resolved this run; "
                  "all other groupsinvite detail URLs banked as leads (slug = lowercase invite code; exact case needs the detail page). "
                  "Pending items are transport/HTTP-429/403/5xx only and need re-verification next wave.",
        "notes": f"candidates extracted={len(candidates)}; dupes vs 108365-code union={dup}; "
                 f"fresh pre-screen={len(fresh)}; screened pre-verify={len([e for e in exclusions])}; "
                 f"listings HTTP200={ok}/{len(todo)}; skipped adult groupjoin pages={len(skipped_adult_pages)}; "
                 f"GI detail pages={len(gi_by_slug)}; AG posts fetched={ag_done}/{len(ag_posts)}; "
                 f"verify: max 3 parallel, >=0.5s spacing, 15s timeout, up to 3 attempts on empty og:title; "
                 f"HTTP 429/403/5xx treated as PENDING (not dead). Elapsed {time.time()-t0:.0f}s.",
    }
    json.dump(summary, open(WORK / "team07-leads-slice7-summary.json", "w"), ensure_ascii=False, indent=1)
    say(f"DONE verified={len(verified)} pending={len(pending)} leads={len(leads_list)} dead={dead_n} exclusions={len(exclusions)}")
    json.dump(log, open(SCRATCH / "run_log.json", "w"), indent=1)

if __name__ == "__main__":
    main()
