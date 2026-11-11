#!/usr/bin/env python3
"""TEAM 10 wave 20261111 — linkado sitemap indices 2300-2699 (400 grupo detail pages).
Phase 1: fetch detail pages, extract invite code + name + category + description.
Phase 2: dedupe vs union (.existing_codes.json + groups.json invites).
Phase 3: slow-verify fresh codes (curl chat.whatsapp.com, HTTP 200 + non-empty og:title = live).
Writes checkpoints + final outputs into the wave dir. No merge, no generate.py, no deploy.
"""
import json, os, re, subprocess, time, html as htmlmod
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/home/hatch/workspace/whatsapp-groups-site"
WAVE = os.path.join(BASE, "agent_batches/wave_20261111")
RAW = os.path.join(WAVE, "team10_raw")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
SITEMAP = os.path.join(BASE, "agent_batches/wave_20261110/linkado_sitemap.xml")

CODE_RE = re.compile(r"chat\.whatsapp\.com(?:\\/|/)(?:invite/)?([A-Za-z0-9_-]{8,22})")
ANCHOR_RE = re.compile(r'<a[^>]+href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{8,22})"')
OGTITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"')

CATMAP = [
    ("amizade", "Friendship"), ("namoro", "Friendship"), ("relacionamento", "Friendship"),
    ("amizades", "Friendship"),
    ("jogos", "Gaming"), ("games", "Gaming"), ("game", "Gaming"), ("free fire", "Gaming"),
    ("filmes", "Entertainment"), ("música", "Entertainment"), ("musica", "Entertainment"),
    ("séries", "Entertainment"), ("series", "Entertainment"), ("entretenimento", "Entertainment"),
    ("meme", "Funny"), ("humor", "Funny"), ("engraçado", "Funny"), ("engracado", "Funny"),
    ("esportes", "Sports"), ("futebol", "Sports"), ("esporte", "Sports"),
    ("notícias", "News"), ("noticias", "News"), ("notícia", "News"),
    ("educação", "Education"), ("educacao", "Education"), ("estudos", "Education"),
    ("estudo", "Education"), ("cursos", "Education"), ("escola", "Education"),
    ("empregos", "Jobs"), ("vagas", "Jobs"), ("emprego", "Jobs"), ("trabalho", "Jobs"),
    ("tecnologia", "Technology"), ("tech", "Technology"),
    ("saúde", "Health"), ("saude", "Health"), ("fitness", "Health"), ("emagrecimento", "Health"),
    ("negócios", "Business"), ("negocios", "Business"), ("empreendedor", "Business"),
    ("vendas", "Buy Sell"), ("compras", "Buy Sell"), ("ofertas", "Buy Sell"),
    ("promoções", "Buy Sell"), ("promocoes", "Buy Sell"), ("achadinhos", "Buy Sell"),
    ("descontos", "Buy Sell"), ("classificados", "Buy Sell"),
    ("islâmico", "Islamic"), ("islamico", "Islamic"), ("muçulmano", "Islamic"),
    ("culinária", "Cooking"), ("culinaria", "Cooking"), ("receitas", "Cooking"),
    ("viagem", "Travel"), ("viagens", "Travel"), ("turismo", "Travel"),
    ("poesia", "Poetry"), ("poemas", "Poetry"),
    ("ganhar dinheiro", "Online Earning"), ("renda extra", "Online Earning"),
    ("renda", "Online Earning"), ("ganhar", "Online Earning"),
    ("criptomoedas", "Crypto"), ("cripto", "Crypto"), ("bitcoin", "Crypto"),
    ("dinheiro", "Finance"), ("finanças", "Finance"), ("financas", "Finance"),
    ("investimentos", "Finance"), ("investimento", "Finance"),
    ("bolsas", "Scholarship"), ("bolsa", "Scholarship"),
    ("freelancer", "Freelance"), ("freelance", "Freelance"),
    ("imóveis", "Real Estate"), ("imoveis", "Real Estate"),
    ("comunidade", "Community & Social"), ("geral", "Community & Social"),
    ("outros", "Community & Social"), ("religião", "Community & Social"),
    ("religiao", "Community & Social"), ("evangélico", "Community & Social"),
    ("evangelico", "Community & Social"), ("católico", "Community & Social"),
    ("catolico", "Community & Social"), ("cristão", "Community & Social"),
    ("cristao", "Community & Social"), ("bíblia", "Community & Social"),
    ("biblia", "Community & Social"), ("oração", "Community & Social"),
    ("oracao", "Community & Social"),
]

def map_category(raw):
    r = (raw or "").strip().lower()
    if not r:
        return "Community & Social"
    for key, cat in CATMAP:
        if key in r:
            return cat
    return "Community & Social"

def clean_text(s):
    s = htmlmod.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def curl_fetch(url, outpath):
    """Returns (http_code, size) or (0, 0) on transport failure."""
    try:
        r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "90",
                            "-o", outpath, "-w", "%{http_code} %{size_download}", url],
                           capture_output=True, text=True, timeout=100)
        parts = r.stdout.strip().split()
        if len(parts) == 2 and parts[0].isdigit():
            return int(parts[0]), int(parts[1])
        return 0, 0
    except Exception:
        return 0, 0

def extract_candidate(html, url):
    """Extract main WA code + listing name/category/description from a linkado detail page."""
    u = html.replace('\\"', '"').replace('\\/', '/')
    codes = set(CODE_RE.findall(u))
    anchor = ANCHOR_RE.findall(u)
    code = None
    if anchor:
        code = anchor[0]
    elif len(codes) == 1:
        code = next(iter(codes))
    elif len(codes) > 1:
        code = sorted(codes)[0]  # fallback; flagged in notes
    # name from H1, fallback og:title
    name = ""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", u, re.S)
    if m:
        name = clean_text(m.group(1))
        name = re.sub(r"^grupo de whatsapp\s+", "", name, flags=re.I)
    ogd = ""
    m = re.search(r'og:description"\s+content="([^"]*)"', u)
    if m:
        ogd = clean_text(m.group(1))
    cat_raw = ""
    m = re.search(r"/categoria/([a-z0-9-]+)", u)
    if m:
        cat_raw = m.group(1)
    desc = ""
    if ogd:
        # strip "Grupo de WhatsApp X, na categoria Y. " prefix
        d2 = re.sub(r"^grupo de whatsapp [^,]+, na categoria [^.]*\.\s*", "", ogd, flags=re.I)
        desc = d2.strip()
    if not cat_raw:
        m = re.search(r"na categoria ([^.]+)\.", ogd, re.I)
        if m:
            cat_raw = m.group(1).strip()
    if not name:
        m = re.search(r'og:title"\s+content="([^"]*)"', u)
        if m:
            t = clean_text(m.group(1))
            t = re.sub(r"^grupo de whatsapp\s+", "", t, flags=re.I)
            t = re.sub(r"\s+-\s+[^-]+$", "", t)
            name = t
    has_telegram = bool(re.search(r"https://t\.me/(?!share/)[A-Za-z0-9_+]{4,}", u))
    has_channel = "whatsapp.com/channel" in u
    removed = False  # set by size+emptiness check in build; the not-found string is inlined on every page
    return {"code": code, "name": name, "category_raw": cat_raw,
            "description_raw": desc, "has_telegram": has_telegram,
            "has_channel": has_channel, "removed": removed, "n_codes": len(codes),
            "all_codes": sorted(codes)}

def get_slice():
    xml = open(SITEMAP, encoding="utf-8").read()
    urls = re.findall(r"<url>\s*<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", xml)
    grupo = [(l, m) for l, m in urls if "/grupo/" in l]
    return grupo[2300:2700]

# ---------------- Phase 1: fetch ----------------
def fetch_one(item):
    idx, (url, lastmod) = item
    fn = os.path.join(RAW, f"p{idx:04d}.html")
    status = ""
    if os.path.exists(fn) and os.path.getsize(fn) > 50000:
        status = "cached"
    else:
        code, size = curl_fetch(url, fn)
        status = f"{code} {size}"
        time.sleep(0.5)
        if code != 200 or size < 50000:
            time.sleep(2)
            code2, size2 = curl_fetch(url, fn)
            status = f"retry {code2} {size2}"
            time.sleep(0.5)
    try:
        html = open(fn, encoding="utf-8", errors="ignore").read()
    except Exception:
        html = ""
    rec = {"index": idx, "url": url, "lastmod": lastmod, "fetch": status}
    if len(html) > 50000:
        rec.update(extract_candidate(html, url))
    else:
        rec.update({"code": None, "name": "", "category_raw": "", "description_raw": "",
                    "has_telegram": False, "has_channel": False, "removed": False, "n_codes": 0, "all_codes": []})
    return rec

def main():
    slice_urls = get_slice()
    assert len(slice_urls) == 400, len(slice_urls)
    print("slice size:", len(slice_urls), "first:", slice_urls[0], "last:", slice_urls[-1], flush=True)
    cand_path = os.path.join(WAVE, "team10_candidates.json")
    candidates = []
    if os.path.exists(cand_path):
        candidates = json.load(open(cand_path))
        print("resuming from checkpoint:", len(candidates), "candidates", flush=True)
    if len(candidates) < 400:
        have_idx = {c["index"] for c in candidates}
        todo = [(2300 + i, slice_urls[i]) for i in range(400) if (2300 + i) not in have_idx]
        # re-fetch only missing; keep order by index
        with ThreadPoolExecutor(max_workers=6) as ex:
            futs = {ex.submit(fetch_one, it): it[0] for it in todo}
            done = 0
            for fut in as_completed(futs):
                rec = fut.result()
                candidates.append(rec)
                done += 1
                if done % 50 == 0:
                    candidates.sort(key=lambda r: r["index"])
                    json.dump(candidates, open(cand_path, "w"), ensure_ascii=False, indent=1)
                    print(f"fetched {len(candidates)}/400", flush=True)
        candidates.sort(key=lambda r: r["index"])
        json.dump(candidates, open(cand_path, "w"), ensure_ascii=False, indent=1)
    print("phase1 done:", len(candidates), flush=True)
    n_code = sum(1 for c in candidates if c.get("code"))
    n_tg = sum(1 for c in candidates if not c.get("code") and c.get("has_telegram"))
    n_chan = sum(1 for c in candidates if not c.get("code") and c.get("has_channel"))
    n_nocode = sum(1 for c in candidates if not c.get("code") and not c.get("has_telegram") and not c.get("has_channel"))
    n_fail = sum(1 for c in candidates if not c.get("code") and not c.get("name"))
    print(f"with WA code: {n_code}, telegram-only: {n_tg}, channel-only: {n_chan}, no join link: {n_nocode}, fetch-failed: {n_fail}", flush=True)

    # ---------------- Phase 2: dedupe ----------------
    existing = set(json.load(open(os.path.join(BASE, ".existing_codes.json"))))
    try:
        groups = json.load(open(os.path.join(BASE, "groups.json")))
        for it in groups:
            m = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)", it.get("invite", ""))
            if m:
                existing.add(m.group(1))
    except Exception as e:
        print("groups.json union add failed:", e, flush=True)
    print("union codes:", len(existing), flush=True)
    fresh = []
    dup = 0
    for c in candidates:
        code = c.get("code")
        if not code:
            continue
        if code in existing:
            dup += 1
        else:
            fresh.append(c)
    print(f"fresh candidates: {len(fresh)}, already in union: {dup}", flush=True)
    json.dump(fresh, open(os.path.join(WAVE, "team10_fresh.json"), "w"), ensure_ascii=False, indent=1)

    # ---------------- Phase 3: verify ----------------
    prog_path = os.path.join(WAVE, "team10_verify_progress.json")
    results = {}
    if os.path.exists(prog_path):
        results = json.load(open(prog_path))
        print("resuming verification:", len(results), "done", flush=True)

    def verify_one(c):
        code = c["code"]
        if code in results:
            return code, results[code]
        tmp = os.path.join(RAW, f"wa_{code}.html")
        # attempt 1
        time.sleep(0.8)
        hc, size = curl_fetch(f"https://chat.whatsapp.com/{code}", tmp)
        og = ""
        if hc == 200 and size > 0:
            try:
                h = open(tmp, encoding="utf-8", errors="ignore").read()
                m = OGTITLE_RE.search(h)
                if m:
                    og = clean_text(m.group(1))
            except Exception:
                pass
        if hc != 200:
            # transport failure -> retry once after pause
            time.sleep(3)
            hc, size = curl_fetch(f"https://chat.whatsapp.com/{code}", tmp)
            if hc == 200 and size > 0:
                try:
                    h = open(tmp, encoding="utf-8", errors="ignore").read()
                    m = OGTITLE_RE.search(h)
                    if m:
                        og = clean_text(m.group(1))
                except Exception:
                    pass
        if hc != 200:
            res = {"status": "pending", "reason": f"transport failure (HTTP {hc})", "og": ""}
        elif og:
            res = {"status": "live", "og": og, "reason": ""}
        else:
            # retry once after pause (empty-og retry rule)
            time.sleep(3)
            hc2, size2 = curl_fetch(f"https://chat.whatsapp.com/{code}", tmp)
            og2 = ""
            if hc2 == 200 and size2 > 0:
                try:
                    h = open(tmp, encoding="utf-8", errors="ignore").read()
                    m = OGTITLE_RE.search(h)
                    if m:
                        og2 = clean_text(m.group(1))
                except Exception:
                    pass
            if hc2 != 200:
                res = {"status": "pending", "reason": f"transport failure on retry (HTTP {hc2})", "og": ""}
            elif og2:
                res = {"status": "live", "og": og2, "reason": ""}
            else:
                res = {"status": "dead", "og": "", "reason": "HTTP 200 + empty og:title after spaced retry"}
        results[code] = res
        return code, res

    todo = [c for c in fresh if c["code"] not in results]
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(verify_one, c): c["code"] for c in todo}
        done = 0
        for fut in as_completed(futs):
            fut.result()
            done += 1
            if done % 25 == 0:
                json.dump(results, open(prog_path, "w"), ensure_ascii=False, indent=1)
                lv = sum(1 for r in results.values() if r["status"] == "live")
                dd = sum(1 for r in results.values() if r["status"] == "dead")
                pd = sum(1 for r in results.values() if r["status"] == "pending")
                print(f"verified {len(results)}/{len(fresh)} live={lv} dead={dd} pending={pd}", flush=True)
    json.dump(results, open(prog_path, "w"), ensure_ascii=False, indent=1)
    lv = sum(1 for r in results.values() if r["status"] == "live")
    dd = sum(1 for r in results.values() if r["status"] == "dead")
    pd = sum(1 for r in results.values() if r["status"] == "pending")
    print(f"VERIFY DONE: live={lv} dead={dd} pending={pd}", flush=True)

if __name__ == "__main__":
    main()
