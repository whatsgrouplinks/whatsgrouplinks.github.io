#!/usr/bin/env python3
"""Team30 v2 — Mexico/Central America scrape of igrupos.com city pages.
Faster: requests Session keep-alive, tighter page caps, per-city detail cap,
resume-friendly checkpoints.
"""
import json, re, os, time, html as ihtml, threading, sys
import requests

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261102")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

CITIES = {
    "ciudad-de-mexico": "MX", "guadalajara": "MX", "monterrey": "MX",
    "cancun": "MX", "puebla": "MX", "tijuana": "MX",
    "guatemala": "GT", "quetzaltenango": "GT",
    "san-jose": "CR",
    "san-salvador": "SV",
    "tegucigalpa": "HN", "san-pedro-sula": "HN",
    "managua": "NI", "leon": "NI",
    "panama": "PA", "david": "PA",
}
MAX_PAGES = 6        # per city
DETAIL_PER_CITY = 100

HEADERS = {"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9"}

def fetch(url, timeout=35):
    # NOTE: the egress proxy breaks keep-alive reuse; use a fresh connection
    # per request with one retry.
    last = None
    for attempt in range(2):
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
    r'sexo\s?(gratis|duro|expl[ií]cito)|chicas\s?(calientes|sexys))\b',
    re.I)
EMOJI_RE = re.compile('[\U0001F975\U0001F346\U0001F351\U0001F51E\U0001F4A6\U0001F445\U0001F444\U0001F48B]')

TAG2CAT = {
    "rap": "Music", "musica": "Music", "música": "Music", "rock": "Music",
    "k-pop": "Music", "regueton": "Music", "reggaeton": "Music",
    "amistad": "Friendship", "conocer": "Friendship", "ligar": "Girls",
    "amor": "Girls", "citas": "Girls", "chicas": "Girls",
    "deportes": "Sports", "futbol": "Sports", "fútbol": "Sports", "apuestas": "Sports",
    "gaming": "Gaming", "juegos": "Gaming", "videojuegos": "Gaming",
    "free-fire": "Gaming", "clash": "Gaming", "minecraft": "Gaming", "gta": "Gaming",
    "trabajo": "Jobs", "empleo": "Jobs", "empleos": "Jobs",
    "estudio": "Education", "educacion": "Education", "educación": "Education",
    "tareas": "Education", "universidad": "Education", "ingles": "Education",
    "noticias": "News", "news": "News",
    "negocios": "Business", "emprendimiento": "Business", "marketing": "Business",
    "cripto": "Crypto", "criptomonedas": "Crypto", "bitcoin": "Crypto", "trading": "Finance",
    "inversiones": "Finance", "dinero": "Finance", "forex": "Finance",
    "compras": "Buy-Sell", "ventas": "Buy-Sell", "compra": "Buy-Sell", "venta": "Buy-Sell",
    "tecnologia": "Technology", "tecnología": "Technology", "programacion": "Technology",
    "salud": "Health", "fitness": "Health",
    "viajes": "Travel", "turismo": "Travel",
    "peliculas": "Movies", "películas": "Movies", "cine": "Movies", "series": "Movies", "anime": "Entertainment",
    "comida": "Food", "recetas": "Food", "cocina": "Food", "gastronomia": "Food",
    "mascotas": "Pets", "perros": "Pets", "gatos": "Pets",
    "humor": "Funny", "memes": "Funny", "chistes": "Funny",
    "stickers": "Entertainment", "entretenimiento": "Entertainment",
    "ciudad": "Regional", "mexico": "Regional", "guatemala": "Regional",
}

def map_category(tag):
    t = tag.lower()
    for key, cat in TAG2CAT.items():
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
    for m in re.finditer(r'href="grupo/(\d+)".*?</a>', page_html, re.S):
        gid = m.group(1)
        block = m.group(0)
        title = re.search(r'<h3 class="group-title">(.*?)</h3>', block, re.S)
        desc = re.search(r'<p class="group-description">(.*?)</p>', block, re.S)
        flag = re.search(r'images/banderas24/([A-Z]{2})\.png', block)
        city = re.search(r'href="whatsapp/([a-z0-9\-]+)"[^>]*>([^<]+)</a>', block)
        cards.append({
            "gid": gid,
            "title": text_of(title.group(1)) if title else "",
            "desc": text_of(desc.group(1)) if desc else "",
            "flag": flag.group(1) if flag else "",
            "cityname": city.group(2).strip() if city else "",
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
    """Returns og:title str, '' for dead, None for transport failure,
    or the sentinel 'RATELIMIT' on HTTP 429."""
    import subprocess
    try:
        p = subprocess.run(
            ["curl", "-sL", "--max-time", "25", "-o", "/tmp/og.html", "-w",
             "%{http_code}", "-A", UA, f"https://chat.whatsapp.com/{code}"],
            capture_output=True, text=True, timeout=35)
    except Exception:
        return None
    httpcode = (p.stdout or "").strip()[-3:]
    if httpcode == "429":
        return "RATELIMIT"
    try:
        body = open("/tmp/og.html", encoding="utf-8", errors="ignore").read()
    except Exception:
        return None
    if not body:
        return None
    m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', body)
    if not m:
        return None
    return ihtml.unescape(m.group(1)).strip()

def main():
    union = set(json.load(open(os.path.join(BASE, "dedupe_union.json"))))
    print("union:", len(union), flush=True)

    cards = []
    seen_gid = set()
    for slug, iso in CITIES.items():
        city_cards = []
        for page in range(1, MAX_PAGES + 1):
            url = f"https://www.igrupos.com/whatsapp/{slug}" if page == 1 else f"https://www.igrupos.com/whatsapp/{slug}/{page}"
            try:
                h = fetch(url)
            except Exception as e:
                print(f"  {slug} p{page}: fetch error {type(e).__name__}", flush=True)
                break
            pc = parse_cards(h)
            new = [c for c in pc if c["gid"] not in seen_gid]
            if not new:
                print(f"  {slug} p{page}: no new, stop", flush=True)
                break
            for c in new:
                c["iso"] = iso; c["slug"] = slug
                seen_gid.add(c["gid"])
            city_cards += new
            print(f"  {slug} p{page}: +{len(new)}", flush=True)
            if len(new) < 10:
                break
            time.sleep(0.3)
        cards += city_cards
    print("total cards:", len(cards), flush=True)

    # trim to DETAIL_PER_CITY per city, preserving order
    trimmed = []
    per_city = {}
    for c in cards:
        n = per_city.get(c["slug"], 0)
        if n < DETAIL_PER_CITY:
            trimmed.append(c); per_city[c["slug"]] = n + 1
    print("details to fetch:", len(trimmed), flush=True)

    from concurrent.futures import ThreadPoolExecutor
    results, batch_codes = [], set()
    porn_drops = 0
    done = 0
    def work(c):
        try:
            return (c, detail_code(c["gid"]))
        except Exception:
            return (c, None)
    with ThreadPoolExecutor(max_workers=5) as ex:
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
            results.append({"code": code, "title": title, "tag": dtag,
                            "cityname": c["cityname"], "iso": c["iso"],
                            "flag": c["flag"], "raw_desc": c["desc"][:400]})
    print(f"candidates: {len(results)} porn_drops: {porn_drops}", flush=True)
    json.dump({"candidates": results, "porn_drops": porn_drops},
              open(os.path.join(BASE, "team30-candidates.json"), "w"), ensure_ascii=False)

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
                "name": name, "category": map_category(r["tag"]),
                "country": r["iso"], "description": "",
                "invite": f"https://chat.whatsapp.com/{r['code']}", "image": "",
                "_meta": {"title": r["title"], "tag": r["tag"],
                          "cityname": r["cityname"], "desc": r["raw_desc"]},
            })
        time.sleep(0.7)
        if (i + 1) % 25 == 0 or i == len(results) - 1:
            print(f"verify {i+1}/{len(results)} verified={len(verified)}", flush=True)
            json.dump({"verified": verified, "pending": pending, "porn_drops": porn_drops},
                      open(os.path.join(BASE, "team30-progress.json"), "w"), ensure_ascii=False)

    print(f"DONE verified={len(verified)} pending={len(pending)} porn_drops={porn_drops}", flush=True)

if __name__ == "__main__":
    main()
