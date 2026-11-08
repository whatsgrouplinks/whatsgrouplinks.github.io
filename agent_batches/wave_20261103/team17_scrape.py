#!/usr/bin/env python3
"""TEAM17 — igrupos.com LatAm-2 scrape (VE/BO/PY/UY/DO/GT/CR/PA/HN/SV/NI).
City + country pages, adapted from team30's proven pipeline (wave_20261102).
team30 did: guatemala, quetzaltenango, san-salvador, tegucigalpa,
san-pedro-sula, managua, leon, panama, david (+MX cities) — those are SKIPPED.
CR's san-jose was San Jose CA in team30's run (only 4 CR items), so CR is fresh.
"""
import json, re, os, time, html as ihtml, sys
import requests

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261103")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9"}

# slug -> ISO. team30-owned slugs (guatemala, quetzaltenango, san-salvador,
# tegucigalpa, san-pedro-sula, managua, leon, panama, david) are excluded.
PAGES = {
    # VENEZUELA
    "caracas": "VE", "maracaibo": "VE", "valencia-carabobo": "VE",
    "barquisimeto": "VE", "maracay": "VE", "merida-merida": "VE",
    "ciudad-guayana": "VE", "maturin": "VE",
    # BOLIVIA
    "la-paz": "BO", "santa-cruz-de-la-sierra": "BO", "cochabamba": "BO",
    "el-alto": "BO", "oruro": "BO", "sucre": "BO", "tarija": "BO",
    # PARAGUAY
    "asuncion": "PY", "ciudad-del-este": "PY", "encarnacion": "PY",
    "pedro-juan-caballero": "PY",
    # URUGUAY
    "montevideo": "UY", "salto-salto": "UY", "paysandu": "UY", "maldonado": "UY",
    # DOMINICAN REPUBLIC
    "santo-domingo": "DO", "santiago-de-los-caballeros": "DO", "la-romana": "DO",
    "puerto-plata": "DO", "bavaro": "DO", "moca-espaillat": "DO",
    # GUATEMALA (new city slugs only)
    "mixco": "GT", "escuintla-escuintla": "GT", "antigua-guatemala": "GT",
    "puerto-barrios": "GT", "huehuetenango": "GT", "coban": "GT",
    # COSTA RICA (country page + cities)
    "costa-rica": "CR", "cartago": "CR", "alajuela": "CR", "heredia": "CR",
    "puntarenas": "CR", "liberia": "CR",
    # PANAMA (new cities; team30 did panama+david)
    "colon-colon": "PA", "la-chorrera": "PA", "san-miguelito": "PA",
    "david-chiriqui": "PA", "santiago-de-veraguas": "PA",
    # HONDURAS (new cities; team30 did tegucigalpa+san-pedro-sula)
    "la-ceiba": "HN", "choloma": "HN", "el-progreso": "HN",
    "comayagua": "HN", "danli": "HN",
    # EL SALVADOR (new cities; team30 did san-salvador)
    "santa-ana-santa-ana": "SV", "san-miguel-san-miguel": "SV",
    "sonsonate": "SV", "usulutan": "SV",
    # NICARAGUA (new cities; team30 did managua+leon)
    "granada-granada": "NI", "esteli": "NI", "matagalpa": "NI",
    "chinandega": "NI", "masaya": "NI",
}
MAX_PAGES = 3          # per page (4 for costa-rica country page)
DETAIL_PER_PAGE = 50

def fetch(url, timeout=35):
    # fresh connection per request (egress proxy breaks keep-alive), one retry
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
    try:
        r = requests.get(f"https://chat.whatsapp.com/{code}",
                         headers={"User-Agent": UA}, timeout=25)
    except Exception:
        return None
    if r.status_code == 429:
        return "RATELIMIT"
    try:
        m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"',
                      r.text)
    except Exception:
        return None
    if not m:
        return None
    return ihtml.unescape(m.group(1)).strip()

def main():
    union = set(json.load(open(os.path.join(BASE, "dedupe_union.json"))))
    print("union:", len(union), flush=True)

    cards = []
    seen_gid = set()
    for slug, iso in PAGES.items():
        max_pages = 4 if slug == "costa-rica" else MAX_PAGES
        city_cards = []
        for page in range(1, max_pages + 1):
            url = (f"https://www.igrupos.com/whatsapp/{slug}" if page == 1
                   else f"https://www.igrupos.com/whatsapp/{slug}/{page}")
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

    trimmed = []
    per_page = {}
    for c in cards:
        n = per_page.get(c["slug"], 0)
        if n < DETAIL_PER_PAGE:
            trimmed.append(c); per_page[c["slug"]] = n + 1
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
    with ThreadPoolExecutor(max_workers=4) as ex:
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
              open(os.path.join(BASE, "team17-candidates.json"), "w"), ensure_ascii=False)

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
                "name": name, "country": r["iso"],
                "invite": f"https://chat.whatsapp.com/{r['code']}",
                "_meta": {"title": r["title"], "tag": r["tag"],
                          "cityname": r["cityname"], "desc": r["raw_desc"]},
            })
        time.sleep(0.6)
        if (i + 1) % 25 == 0 or i == len(results) - 1:
            print(f"verify {i+1}/{len(results)} verified={len(verified)} pending={len(pending)}", flush=True)
            json.dump({"verified": verified, "pending": pending, "porn_drops": porn_drops},
                      open(os.path.join(BASE, "team17-progress.json"), "w"), ensure_ascii=False)

    print(f"DONE verified={len(verified)} pending={len(pending)} porn_drops={porn_drops}", flush=True)

if __name__ == "__main__":
    main()
