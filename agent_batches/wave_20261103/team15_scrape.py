#!/usr/bin/env python3
"""Team15 — wave 20261103: igrupos.com MEXICO, new city slugs + deeper mining.
Adapted from team30-scrape.py/team30-finalize.py (wave_20261102).
Cities: all MX. Verification via PYTHON requests (fresh connection per request).
"""
import json, re, os, sys, time, html as ihtml, unicodedata as _u
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261103")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9"}

CITIES = ["queretaro", "merida", "oaxaca", "toluca", "hermosillo", "acapulco",
          "durango", "chihuahua", "leon", "cancun", "puebla", "tijuana",
          "monterrey", "guadalajara"]
MAX_PAGES = 12
DETAIL_PER_CITY = 250
TIME_BUDGET_S = 55 * 60  # bank and stop

START = time.time()

def fetch(url, timeout=35):
    last = None
    for _ in range(2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last = e
            time.sleep(1.5)
    raise last

PORN_RE = re.compile(
    r'\b(porn|pornhub|xxx|nude|nudist|sex\s?video|escort|call\s?girl|'
    r'fuck|dick|pussy|boobs?|tits|anal|horny|porno|'
    r'sexo\s?(gratis|duro|expl[ií]cito)|chicas\s?(calientes|sexys))\b', re.I)
EMOJI_RE = re.compile('[\U0001F975\U0001F346\U0001F351\U0001F51E\U0001F4A6\U0001F445\U0001F444\U0001F48B]')

def map_category(tag):
    t = (tag or "").lower()
    m = {
        "rap": "Music", "musica": "Music", "música": "Music", "rock": "Music",
        "k-pop": "Music", "regueton": "Music", "reggaeton": "Music",
        "amistad": "Friendship", "conocer": "Friendship", "ligar": "Girls",
        "amor": "Girls", "citas": "Girls", "chicas": "Girls",
        "deportes": "Sports", "futbol": "Sports", "fútbol": "Sports",
        "apuestas": "Sports", "gaming": "Gaming", "juegos": "Gaming",
        "videojuegos": "Gaming", "free-fire": "Gaming", "clash": "Gaming",
        "minecraft": "Gaming", "gta": "Gaming", "trabajo": "Jobs",
        "empleo": "Jobs", "empleos": "Jobs", "estudio": "Education",
        "educacion": "Education", "educación": "Education", "tareas": "Education",
        "universidad": "Education", "ingles": "Education",
        "noticias": "News", "news": "News", "negocios": "Business",
        "emprendimiento": "Business", "marketing": "Business",
        "cripto": "Crypto", "criptomonedas": "Crypto", "bitcoin": "Crypto",
        "trading": "Finance", "inversiones": "Finance", "dinero": "Finance",
        "forex": "Finance", "compras": "Buy-Sell", "ventas": "Buy-Sell",
        "compra": "Buy-Sell", "venta": "Buy-Sell", "tecnologia": "Technology",
        "tecnología": "Technology", "programacion": "Technology",
        "salud": "Health", "fitness": "Health", "viajes": "Travel",
        "turismo": "Travel", "peliculas": "Movies", "películas": "Movies",
        "cine": "Movies", "series": "Movies", "anime": "Entertainment",
        "comida": "Food", "recetas": "Food", "cocina": "Food",
        "gastronomia": "Food", "mascotas": "Pets", "perros": "Pets",
        "gatos": "Pets", "humor": "Funny", "memes": "Funny",
        "chistes": "Funny", "stickers": "Entertainment",
        "entretenimiento": "Entertainment", "ciudad": "Regional",
        "mexico": "Regional",
    }
    for key, cat in m.items():
        if key in t:
            return cat
    return "Other"

def text_of(h):
    h = re.sub(r'<script.*?</script>', ' ', h, flags=re.S | re.I)
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S | re.I)
    h = re.sub(r'<[^>]+>', ' ', h)
    return re.sub(r'\s+', ' ', ihtml.unescape(h)).strip()

def parse_cards(page_html):
    cards = []
    for m in re.finditer(r'href="grupo/(\d+)".*?</p>\s*</a>', page_html, re.S):
        gid = m.group(1)
        block = m.group(0)
        title = re.search(r'<h3 class="group-title">(.*?)</h3>', block, re.S)
        desc = re.search(r'<p class="group-description">(.*?)</p>', block, re.S)
        flag = re.search(r'images/banderas24/([A-Z]{2})\.png', block)
        city = re.search(r'href="whatsapp/[a-z0-9\-]+/([a-z0-9\-]+)"[^>]*>\s*#([^<]+)</a>', block)
        t = text_of(title.group(1)) if title else ""
        d = text_of(desc.group(1)) if desc else ""
        cards.append({
            "gid": gid,
            "title": t,
            "desc": d,
            "flag": flag.group(1) if flag else "",
            "tag": (city.group(2).strip() if city else ""),
            "cityname": "",
        })
    return cards

def detail_code(gid):
    h = fetch(f"https://www.igrupos.com/grupo/{gid}")
    if re.search(r'chat\.whatsapp\.com/invite/', h):
        return "", "", ""
    codes = re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', h)
    code = codes[0] if codes else ""
    title = re.search(r'<title>(.*?)</title>', h, re.S)
    title = text_of(title.group(1)).split('|')[0].strip() if title else ""
    tagm = re.search(r'Grupos de Whatsapp\s*&\w+;\s*([^<]{2,40})', h)
    tag = tagm.group(1).strip() if tagm else ""
    return code, title, tag

def og_title(code):
    """og:title str | '' dead | None transport failure | 'RATELIMIT'."""
    try:
        r = requests.get(f"https://chat.whatsapp.com/{code}", headers=HEADERS,
                         timeout=25)
    except Exception:
        return None
    if r.status_code == 429:
        return "RATELIMIT"
    body = r.text or ""
    if not body:
        return None
    m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', body)
    if not m:
        return None
    return ihtml.unescape(m.group(1)).strip()

def main():
    union = set(json.load(open(os.path.join(WAVE, "dedupe_union.json"))))
    print("union:", len(union), flush=True)

    # ---- stage 1: listing pages ----
    cards, seen_gid = [], set()
    stop_reason = None
    porn_drops = 0
    resume_file = os.path.join(WAVE, "team15-candidates.json")
    if os.path.exists(resume_file) and os.path.getsize(resume_file) > 100:
        print("RESUME: loading candidates from file, skipping listing stage", flush=True)
        d0 = json.load(open(resume_file))
        results = d0["candidates"]
        porn_drops = d0.get("porn_drops", 0)
        results, batch_codes = [], set()
        for r in d0["candidates"]:
            code = r["code"]
            if code in union or code in batch_codes:
                continue
            batch_codes.add(code)
            results.append(r)
        print(f"resumed candidates: {len(results)}", flush=True)
    else:
        # parallel listing fetch (proxy is slow: ~20s/page), then sequential
        # per-city assembly with "no new" early-stop
        def fetch_page(job):
            slug, page = job
            url = (f"https://www.igrupos.com/whatsapp/{slug}" if page == 1
                   else f"https://www.igrupos.com/whatsapp/{slug}/{page}")
            try:
                return (slug, page, fetch(url), None)
            except Exception as e:
                return (slug, page, None, type(e).__name__)
        jobs = [(s, p) for s in CITIES for p in range(1, MAX_PAGES + 1)]
        pages = {}
        def pwork(j):
            return fetch_page(j)
        with ThreadPoolExecutor(max_workers=10) as ex:
            done = 0
            for slug, page, html, err in ex.map(pwork, jobs):
                done += 1
                if err:
                    print(f"  {slug} p{page}: fetch error {err}", flush=True)
                else:
                    pages[(slug, page)] = html
                if done % 25 == 0:
                    print(f"listing {done}/{len(jobs)}", flush=True)
        for slug in CITIES:
            if time.time() - START > TIME_BUDGET_S:
                stop_reason = "time budget hit during listing"
                break
            city_cards = []
            for page in range(1, MAX_PAGES + 1):
                html = pages.get((slug, page))
                if html is None:
                    break
                pc = parse_cards(html)
                new = [c for c in pc if c["gid"] not in seen_gid]
                if not new:
                    print(f"  {slug} p{page}: no new, stop", flush=True)
                    break
                for c in new:
                    c["slug"] = slug
                    seen_gid.add(c["gid"])
                city_cards += new
                print(f"  {slug} p{page}: +{len(new)}", flush=True)
                if len(new) < 10:
                    break
            cards += city_cards
        print("total cards:", len(cards), "stop:", stop_reason, flush=True)

        trimmed, per_city = [], {}
        for c in cards:
            n = per_city.get(c["slug"], 0)
            if n < DETAIL_PER_CITY:
                trimmed.append(c); per_city[c["slug"]] = n + 1
        print("details to fetch:", len(trimmed), flush=True)

        results, batch_codes = [], set()
        done = 0
        def work(c):
            try:
                return (c, detail_code(c["gid"]))
            except Exception:
                return (c, None)
        with ThreadPoolExecutor(max_workers=8) as ex:
            for c, det in ex.map(work, trimmed):
                done += 1
                if done % 100 == 0:
                    print(f"details {done}/{len(trimmed)}", flush=True)
                if not det:
                    continue
                code, dtitle, dtag = det
                if not code or code in union or code in batch_codes:
                    continue
                title = dtitle or c["title"]
                text = (title + " " + c["desc"]).strip()
                if PORN_RE.search(text) or EMOJI_RE.search(text):
                    porn_drops += 1
                    continue
                batch_codes.add(code)
                results.append({"code": code, "title": title, "tag": c.get("tag", "") or dtag,
                                "cityname": c["cityname"], "flag": c["flag"],
                                "slug": c["slug"], "raw_desc": c["desc"][:400]})
        print(f"candidates: {len(results)} porn_drops: {porn_drops}", flush=True)
        json.dump({"candidates": results, "porn_drops": porn_drops},
                  open(os.path.join(WAVE, "team15-candidates.json"), "w"),
                  ensure_ascii=False)

    # ---- stage 2: verify ----
    verified, pending = [], []
    ratelimited = False
    for i, r in enumerate(results):
        if ratelimited:
            r["note"] = "rate-limited"; pending.append(r); continue
        og = og_title(r["code"])
        if og == "RATELIMIT":
            print("RATE LIMITED at", i, "- banking rest as pending", flush=True)
            r["note"] = "rate-limited"; pending.append(r)
            ratelimited = True
            continue
        if og is None:
            r["note"] = "transport failure"; pending.append(r)
        elif og == "":
            pass
        else:
            name = og if og else r["title"]
            if re.search(r'^\+?\d[\d\s\-]{7,}$', name):
                continue
            if PORN_RE.search(name) or EMOJI_RE.search(name):
                porn_drops += 1
                continue
            verified.append({
                "name": name, "tag": r["tag"], "invite":
                f"https://chat.whatsapp.com/{r['code']}",
                "_meta": {"title": r["title"], "tag": r["tag"],
                          "cityname": r["cityname"], "desc": r["raw_desc"],
                          "slug": r["slug"]},
            })
        time.sleep(0.8)
        if (i + 1) % 25 == 0 or i == len(results) - 1:
            print(f"verify {i+1}/{len(results)} verified={len(verified)}", flush=True)
            json.dump({"verified": verified, "pending": pending,
                       "porn_drops": porn_drops},
                      open(os.path.join(WAVE, "team15-progress.json"), "w"),
                      ensure_ascii=False)
    print(f"DONE verify verified={len(verified)} pending={len(pending)} porn={porn_drops}", flush=True)
    json.dump({"verified": verified, "pending": pending, "porn_drops": porn_drops,
               "resume": stop_reason or "listing completed"},
              open(os.path.join(WAVE, "team15-progress.json"), "w"), ensure_ascii=False)

if __name__ == "__main__":
    main()
