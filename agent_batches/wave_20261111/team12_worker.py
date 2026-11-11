#!/usr/bin/env python3
"""TEAM 12 — linkado sitemap sweep, indices 0-1499 (wave 20261111).
Phase A: fetch detail pages, extract chat.whatsapp.com code + H1 + category.
Phase B: slow-verify codes (curl, browser UA, 200 + non-empty og:title = LIVE).
Writes partial outputs + checkpoint as it goes. Resume-safe.
"""
import json, re, html, time, os, subprocess, threading
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
SITEMAP = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/linkado_sitemap.xml"
EXISTING = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

VERIFIED_F = os.path.join(WAVE, "team12-linkado-0-1499.json")
PENDING_F  = os.path.join(WAVE, "team12-linkado-0-1499-pending.json")
LEADS_F    = os.path.join(WAVE, "team12-linkado-0-1499-leads.json")
SUMMARY_F  = os.path.join(WAVE, "team12-linkado-0-1499-summary.json")
CAND_F     = os.path.join(WAVE, "team12-candidates.json")
VSTATE_F   = os.path.join(WAVE, "team12-verify-state.json")
CKPT_F     = os.path.join(WAVE, "team12-checkpoint.json")

CATMAP = {
    "amizade": "Friendship", "namoro": "Friendship",
    "educacao": "Education", "esportes": "Sports", "fitness": "Health",
    "games": "Gaming", "tecnologia": "Technology", "trabalho": "Jobs",
    "comprar-e-venda": "Buy Sell", "carros": "Community & Social",
    "cidades": "Community & Social", "lgbt": "Community & Social",
    "links": "Community & Social", "moda-e-beleza": "Community & Social",
    "religiao": "Community & Social", "politica": "News",
    "figurinhas": "Entertainment", "musica": "Entertainment",
    "series": "Entertainment", "status": "Entertainment",
    "dinheiro": "Online Earning",  # refined per-name below
}
SCAM_PATTERNS = [
    r"b[\s\-]?love", r"forsage", r"s?heyi", r"holiverse",
    r"meta[\s\-]?whale", r"airdrop\s*(vip|premium|garantido)",
    r"aposta\s*garantida", r"lucro\s*certo.*aposta", r"sinais\s*vip.*aposta",
    r"fixed\s*match", r"jogo\s*viciado",
]
PORN_PATTERNS = [
    r"porn", r"xxx", r"xvideos", r"pornhub", r"redtube", r"putaria",
    r"nudes?", r"pelad[oa]s?", r"onlyfans", r"vazad[oa]s?",
    r"sexo\s*expl[ií]cito", r"v[ií]deos?\s+de\s+sexo", r"fotos?\s+de\s+sexo",
    r"sexo\s*(🔥|😈|🍆|🍑)",
    r"xereca", r"suruba", r"troca\s+de\s+casal", r"casal\s+liberal",
    r"m[ée]nage", r"sigilo.*🔞|🔞.*sigilo", r"sexo.*🔞|🔞.*sexo",
    r"gostosas?.*🔞|🔞.*gostosas?",
]
ILLEGAL_PATTERNS = [
    r"vendas?\s+de\s+documentos", r"documentos?\s+falsos?",
    r"\brg\s+falso", r"\bcpf\s+falso", r"\bcnh\s+falsa",
    r"cart[ãa]o(es)?\s+clonados?", r"clonad[oa]s?.*cart[ãa]o",
    r"cartel.*cart[õo]es",
]
NEG_RE = re.compile(r"[^.!?\n]*(proibid[oa]|sem\s+porn|n[aã]o\s+.*porn|no\s+porn|proibido\s+sexo)[^.!?\n]*", re.I)

def strip_negations(text):
    return NEG_RE.sub(" ", text or "")

def screen(text):
    """Return exclusion reason or None. Screens scam + hard porn + illegal sales."""
    t = strip_negations(text or "")
    low = t.lower()
    for p in SCAM_PATTERNS:
        if re.search(p, low):
            return "scam-brand: " + p
    for p in PORN_PATTERNS:
        if re.search(p, low):
            return "hard-porn/xxx: " + p
    for p in ILLEGAL_PATTERNS:
        if re.search(p, low):
            return "illegal-sale: " + p
    return None

def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)

def get_grupo_urls():
    xml = open(SITEMAP, encoding="utf-8").read()
    locs = re.findall(r"<loc>([^<]+)</loc>", xml)
    mods = re.findall(r"<lastmod>([^<]+)</lastmod>", xml)
    return [(l, m) for l, m in zip(locs, mods) if "/grupo/" in l]

def fetch_detail(url):
    """curl-based: linkado closes connections early and urllib raises
    IncompleteRead on nearly every page; curl tolerates it."""
    for attempt in (1, 2):
        try:
            p = subprocess.run(
                ["curl", "-s", "-L", "--compressed", "--max-time", "60",
                 "-A", UA, url],
                capture_output=True, text=True, timeout=70)
            body = p.stdout or ""
            if p.returncode == 0 and len(body) > 1000:
                return 200, body
            if attempt == 1:
                time.sleep(5)
        except Exception:
            if attempt == 1:
                time.sleep(5)
    raise RuntimeError("curl fetch failed after retry")

def parse_detail(page_html):
    wa = re.findall(r"https?://chat\.whatsapp\.com/([A-Za-z0-9]+)", page_html)
    code = wa[0] if wa else None
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", page_html, re.S)
    h1 = html.unescape(re.sub(r"<[^>]+>", "", h1s[0])).strip() if h1s else ""
    cats = re.findall(r'href="/categoria/([^"]+)"', page_html)
    cat_slug = cats[0] if cats else ""
    md = re.search(r'<meta name="description" content="([^"]*)"', page_html)
    meta_desc = html.unescape(md.group(1)) if md else ""
    tg = "t.me/" in page_html or "telegram" in page_html.lower()
    return code, h1, cat_slug, meta_desc, tg

def clean_name(h1):
    name = h1
    name = re.sub(r"^Grupo de WhatsApp\s+", "", name, flags=re.I).strip()
    name = re.sub(r"\s*-\s*[A-Za-zÀ-ÿ ]+$", "", name).strip() if " - " in name else name
    return name.strip()

def category_for(cat_slug, name):
    cat = CATMAP.get(cat_slug, "Community & Social")
    low = (name or "").lower()
    if cat_slug == "dinheiro":
        if re.search(r"invest|bolsa|trading|trade|cripto|bitcoin|forex", low):
            cat = "Finance"
        else:
            cat = "Online Earning"
    elif cat_slug == "religiao":
        if re.search(r"isl[ãa]|muçulman|allah|cor[ãa]o|mesquita", low):
            cat = "Islamic"
    elif cat_slug == "carros":
        if re.search(r"vend|compr|negoci|oferta|pre[çc]o", low):
            cat = "Buy Sell"
    return cat

def verify_code(code):
    """curl check. Returns (status, og_title): status in live/dead/transport."""
    for attempt in (1, 2):
        try:
            p = subprocess.run(
                ["curl", "-s", "-L", "--max-time", "30",
                 "-A", UA, f"https://chat.whatsapp.com/{code}"],
                capture_output=True, text=True, timeout=40)
            body = p.stdout or ""
            m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
            og = html.unescape(m.group(1)).strip() if m else ""
            if og and og.lower() != "whatsapp":
                return "live", og
            # empty og:title: retry once after pause (deterministic dead only after retry)
            if attempt == 1:
                time.sleep(6)
                continue
            return "dead", og
        except Exception as e:
            if attempt == 1:
                time.sleep(6)
                continue
            return "transport", str(e)
    return "dead", ""

def main():
    grupo = get_grupo_urls()
    slice_urls = grupo[0:1500]
    existing = set(load_json(EXISTING, []))
    print(f"slice size: {len(slice_urls)} | existing codes: {len(existing)}", flush=True)

    candidates = load_json(CAND_F, [])  # list of dicts keyed by idx
    cand_by_idx = {c["idx"]: c for c in candidates}
    vstate = load_json(VSTATE_F, {})    # code -> {status, og_title}
    lock = threading.Lock()

    # ---------- Phase A: fetch detail pages ----------
    # todo = missing indices + previously failed fetches (retry pass)
    todo = [i for i in range(len(slice_urls))
            if i not in cand_by_idx or cand_by_idx[i].get("fetch_status") != "http200"]
    print(f"Phase A: {len(todo)} detail pages to fetch", flush=True)
    fetch_counter = {"n": 0}

    def fetch_one(i):
        url, lastmod = slice_urls[i]
        rec = {"idx": i, "url": url, "lastmod": lastmod, "code": None,
               "h1": "", "cat_slug": "", "meta_desc": "", "fetch_status": ""}
        try:
            status, page_html = fetch_detail(url)
            rec["fetch_status"] = f"http{status}"
            if status == 200:
                code, h1, cat_slug, meta_desc, tg = parse_detail(page_html)
                rec.update(code=code, h1=h1, cat_slug=cat_slug,
                           meta_desc=meta_desc, telegram_hint=tg)
            else:
                rec["fetch_status"] = f"http{status}"
        except Exception as e:
            rec["fetch_status"] = f"error:{type(e).__name__}:{str(e)[:80]}"
        with lock:
            cand_by_idx[i] = rec
            fetch_counter["n"] += 1
            n = fetch_counter["n"]
            if n % 25 == 0 or n == len(todo):
                save_json(CAND_F, [cand_by_idx[k] for k in sorted(cand_by_idx)])
                save_json(CKPT_F, {"phase": "A", "last_fetched_idx": max(cand_by_idx),
                                   "fetched": len(cand_by_idx), "total": 1500,
                                   "http200": sum(1 for r in cand_by_idx.values()
                                                  if r.get("fetch_status") == "http200"),
                                   "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        time.sleep(0.6)
        return i

    if todo:
        with ThreadPoolExecutor(max_workers=10) as ex:
            list(ex.map(fetch_one, todo))
        save_json(CAND_F, [cand_by_idx[k] for k in sorted(cand_by_idx)])
    print("Phase A done", flush=True)

    # ---------- Phase B: verify ----------
    # dedupe within slice + against existing
    seen = set()
    verify_list = []  # (idx, code)
    dup_in_slice = 0
    already_existing = 0
    no_link = 0
    fetch_fail = 0
    for i in range(len(slice_urls)):
        rec = cand_by_idx.get(i)
        if not rec:
            continue
        if rec["fetch_status"] != "http200":
            fetch_fail += 1
            continue
        code = rec.get("code")
        if not code:
            no_link += 1
            continue
        if code in existing:
            already_existing += 1
            continue
        if code in seen:
            dup_in_slice += 1
            continue
        seen.add(code)
        verify_list.append((i, code))
    print(f"Phase B: {len(verify_list)} codes to verify | existing-skip={already_existing} "
          f"dup-in-slice={dup_in_slice} no-link={no_link} fetch-fail={fetch_fail}", flush=True)

    verified, pending, exclusions = [], [], []
    dead = 0
    counter = {"n": 0}

    def verify_one(item):
        nonlocal dead
        i, code = item
        if code in vstate and vstate[code]["status"] in ("live", "dead"):
            status, og = vstate[code]["status"], vstate[code].get("og_title", "")
        else:
            status, og = verify_code(code)
            with lock:
                vstate[code] = {"status": status, "og_title": og}
            time.sleep(1.0)
        rec = cand_by_idx[i]
        with lock:
            counter["n"] += 1
            n = counter["n"]
            if status == "live":
                name = re.sub(r"\s+", " ", og.strip() or clean_name(rec["h1"])).strip()
                reason = screen(name) or screen(rec["h1"]) or screen(rec["meta_desc"])
                if reason:
                    exclusions.append({"code": code, "reason": reason, "name": name})
                else:
                    cat = category_for(rec["cat_slug"], name)
                    desc = (f"WhatsApp group '{name}' — {cat} community in Brazil."
                            if len(name) <= 120 else
                            f"WhatsApp group in the {cat} category — Brazilian community.")
                    verified.append({"name": name, "category": cat, "country": "BR",
                                     "description": desc,
                                     "invite": f"https://chat.whatsapp.com/{code}"})
            elif status == "dead":
                dead += 1
            else:  # transport
                cat = category_for(rec["cat_slug"], clean_name(rec["h1"]))
                pending.append({"name": clean_name(rec["h1"]) or code, "category": cat,
                                "country": "BR",
                                "description": f"WhatsApp group in the {cat} category — Brazilian community.",
                                "invite": f"https://chat.whatsapp.com/{code}",
                                "reason": f"transport failure verifying invite: {og}"})
            if n % 50 == 0 or n == len(verify_list):
                save_json(VERIFIED_F, verified)
                save_json(PENDING_F, pending)
                save_json(VSTATE_F, vstate)
                save_json(CKPT_F, {"phase": "B", "verified_so_far": n,
                                   "total_to_verify": len(verify_list),
                                   "verified": len(verified), "pending": len(pending),
                                   "dead": dead, "last_fetched_idx": 1499,
                                   "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return status

    if verify_list:
        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(verify_one, verify_list))

    # dedupe verified by invite (safety)
    seen_inv = set()
    verified_u = []
    for v in verified:
        if v["invite"] not in seen_inv:
            seen_inv.add(v["invite"])
            verified_u.append(v)
    verified = verified_u

    save_json(VERIFIED_F, verified)
    save_json(PENDING_F, pending)
    save_json(VSTATE_F, vstate)
    leads = sorted({f"https://linkado.app/categoria/{s}" for s in CATMAP})
    save_json(LEADS_F, leads)
    summary = {
        "team": 12,
        "slice": "linkado sitemap indices 0-1499",
        "sources": ["https://linkado.app/grupo/<slug> (sitemap order, lastmod desc)",
                    "https://chat.whatsapp.com/<code> live check"],
        "verified": len(verified),
        "pending": len(pending),
        "leads": len(leads),
        "dead": dead,
        "exclusions": exclusions,
        "resume": "complete" if len(cand_by_idx) == 1500 else f"next index {max(cand_by_idx)+1}",
        "notes": {
            "indices_covered": len(cand_by_idx),
            "no_whatsapp_link_pages": no_link,
            "codes_already_in_union": already_existing,
            "dup_codes_within_slice": dup_in_slice,
            "detail_fetch_failures": fetch_fail,
            "last_mined_url": slice_urls[len(cand_by_idx)-1][0] if cand_by_idx else None,
            "last_mined_lastmod": slice_urls[len(cand_by_idx)-1][1] if cand_by_idx else None,
            "next_index": len(cand_by_idx) if len(cand_by_idx) < 1500 else None,
            "country": "BR for all (Brazilian site, pt_BR)",
        },
    }
    save_json(SUMMARY_F, summary)
    save_json(CKPT_F, {"phase": "done", "last_fetched_idx": 1499,
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    print("DONE", json.dumps(summary, ensure_ascii=False, indent=1), flush=True)

if __name__ == "__main__":
    main()
