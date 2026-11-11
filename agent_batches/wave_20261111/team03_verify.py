#!/usr/bin/env python3
"""TEAM 03 wave 20261111 slice 3: verify extracted codes (SLOW: 6 workers, 0.5s delay),
dedupe vs existing, screen content, categorize, bank verified/pending/leads/summary.
Reads team03-raw-extract.json. Resume-safe: skips codes already in checkpoint.
"""
import json, re, time, threading
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
RAW = f"{WAVE}/team03-raw-extract.json"
EXISTING = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
VCHK = f"{WAVE}/team03-verify-checkpoint.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG_RE2 = re.compile(r'og:title"\s+content="([^"]*)"')

CATMAP = {
    "amizade": "Friendship", "namoro": "Friendship", "amizade e namoro": "Friendship",
    "dinheiro": "Online Earning", "ganhar dinheiro": "Online Earning", "renda extra": "Online Earning",
    "games": "Gaming", "jogos": "Gaming",
    "trabalho": "Jobs", "empregos": "Jobs", "emprego": "Jobs",
    "comprar e venda": "Buy Sell", "vendas": "Buy Sell", "compra e venda": "Buy Sell",
    "links": "Community & Social", "status": "Community & Social", "geral": "Community & Social",
    "outros": "Community & Social", "diversos": "Community & Social", "grupos": "Community & Social",
    "esportes": "Sports", "futebol": "Sports", "esporte": "Sports",
    "series": "Entertainment", "filmes": "Entertainment", "musica": "Entertainment",
    "música": "Entertainment", "figurinhas": "Entertainment", "filmes e series": "Entertainment",
    "entretenimento": "Entertainment", "memes": "Funny", "humor": "Funny",
    "tecnologia": "Technology", "moda e beleza": "Community & Social",
    "religião": "Community & Social", "religiao": "Community & Social", "igreja": "Community & Social",
    "evangelho": "Community & Social", "bíblia": "Community & Social",
    "educação": "Education", "educacao": "Education", "estudos": "Education", "escola": "Education",
    "notícias": "News", "noticias": "News",
    "saúde": "Health", "saude": "Health",
    "negócios": "Business", "negocios": "Business",
    "culinária": "Cooking", "culinaria": "Cooking", "receitas": "Cooking",
    "poesia": "Poetry", "viagem": "Travel", "turismo": "Travel",
    "bolsa de estudos": "Scholarship", "bolsas": "Scholarship",
    "criptomoedas": "Crypto", "finanças": "Finance", "financas": "Finance",
    "engraçado": "Funny", "engracado": "Funny",
}
CANONICAL = {"Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health",
             "Business","Gaming","Friendship","Community & Social","Online Earning","Crypto",
             "Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate","Buy Sell",
             "Finance","Funny"}

import threading as _th
_TLS = _th.local()

def _session():
    s = getattr(_TLS, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        _TLS.s = s
    return s

SCAM_RES = [
    r"b[\s\-]?love", r"forsage", r"shey[iy]", r"holiverse", r"meta[\s\-]?whale",
    r"\bairdrop\b", r"free\s*(usdt|btc|eth|bnb|trx)\b",
]
PORN_RES = [
    r"\bxxx\b", r"\bporn[oô]?\b", r"putaria", r"\bsexo\b", r"\bnudes?\b",
    r"v[ií]deos?\s*(porn|sexo|\+?18|adulto)", r"grupo\s*(porn|sexo)",
    r"\bgozar\b", r"del[ií]cias?\s*\+?18",
]
NEG_RE = re.compile(r"[^.!?;]*(proibido|prohibited|sem|no|não|nao|não é permitido|é proibido)[^.!?;]*(porn|sexo|nudes?|xxx|putaria)[^.!?;]*[.!?;]?", re.I)

def strip_negated(text):
    return NEG_RE.sub(" ", text)

def screen(name, ogtitle):
    t = strip_negated(f"{name} {ogtitle}")
    low = t.lower()
    for pat in SCAM_RES:
        if re.search(pat, low):
            return f"blocked scam: {pat}"
    for pat in PORN_RES:
        if re.search(pat, low):
            return f"blocked porn: {pat}"
    return None

def clean_desc(desc_pt, name, cat):
    import html as _html
    d = _html.unescape(desc_pt or "")
    d = re.sub(r"Grupo de WhatsApp [^,]+, na categoria [^.]*\.?\s*", "", d)
    d = re.sub(r"https?://\S+|www\.\S+", "", d)
    d = re.sub(r"\S+@\S+\.\S+", "", d)
    d = re.sub(r"\+?\d[\d\s().-]{6,}\d", "", d)  # phone-like runs
    d = re.sub(r"\b\d{6,}\b", "", d)  # bare long IDs (Kwai/TikTok/phone fragments)
    d = re.sub(r"\s+", " ", d).strip(" .-,;:")
    if len(d) < 12 or "@" in d:
        d = f"WhatsApp group '{name}' — {cat} group. Join to chat and share with members."
    if len(d) > 200:
        d = d[:197].rsplit(" ", 1)[0] + "..."
    return d

def og_title(html):
    import html as _html
    m = OG_RE.search(html) or OG_RE2.search(html)
    return _html.unescape(m.group(1).strip()) if m else ""

def check_code(code):
    url = f"https://chat.whatsapp.com/{code}"
    title = ""
    last_err = ""
    for attempt in range(2):
        try:
            r = _session().get(url, timeout=90)
            time.sleep(0.5)
            if r.status_code == 200:
                title = og_title(r.text)
                if title:
                    return ("live", title, "")
                last_err = "HTTP 200 empty og:title"
            elif 400 <= r.status_code < 500:
                return ("dead", "", f"HTTP {r.status_code}")
            else:
                last_err = f"HTTP {r.status_code}"
        except Exception as e:
            last_err = f"transport: {e}"
            try:
                _TLS.s = None
            except Exception:
                pass
        time.sleep(3)
    if "transport" in last_err or last_err.startswith("HTTP 5"):
        return ("pending", "", last_err)
    return ("dead", "", last_err)

def main():
    import sys
    raw_path = sys.argv[1] if len(sys.argv) > 1 else RAW
    raw = json.load(open(raw_path))
    existing = set(json.load(open(EXISTING)))
    # unique codes, first listing wins
    by_code = {}
    for rec in raw:
        for c in rec.get("codes", []):
            if c not in by_code:
                by_code[c] = rec
    print(f"listings={len(raw)} unique_codes={len(by_code)}", flush=True)
    ckpt = {}
    try:
        ckpt = {r["code"]: r for r in json.load(open(VCHK))}
    except Exception:
        pass
    todo = [c for c in by_code if c not in ckpt or ckpt[c].get("status") == "pending"]
    print(f"already_checked={len(ckpt)} to_check={len(todo)}", flush=True)
    lock = threading.Lock()
    results = dict(ckpt)
    counter = {"n": 0}

    def work(code):
        if code in existing:
            res = {"code": code, "status": "existing", "ogtitle": "", "reason": "already in groups.json"}
        else:
            st, title, reason = check_code(code)
            res = {"code": code, "status": st, "ogtitle": title, "reason": reason}
        with lock:
            results[code] = res
            counter["n"] += 1
            if counter["n"] % 50 == 0:
                json.dump(list(results.values()), open(VCHK, "w"), ensure_ascii=False)
                print(f"checked {len(results)}/{len(by_code)}", flush=True)

    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(work, todo))
    json.dump(list(results.values()), open(VCHK, "w"), ensure_ascii=False)

    verified, pending, exclusions = [], [], []
    dead = 0
    for code, res in results.items():
        rec = by_code[code]
        if res["status"] == "live":
            block = screen(rec.get("name", ""), res["ogtitle"])
            if block:
                exclusions.append({"code": code, "reason": block})
                continue
            cat_pt = (rec.get("category_pt") or "").strip().lower()
            cat = CATMAP.get(cat_pt, "Community & Social")
            name = (rec.get("name") or "").strip() or res["ogtitle"]
            verified.append({
                "name": name[:120],
                "category": cat,
                "country": "BR",
                "description": clean_desc(rec.get("desc_pt", ""), name, cat),
                "invite": f"https://chat.whatsapp.com/{code}",
            })
        elif res["status"] == "pending":
            cat_pt = (rec.get("category_pt") or "").strip().lower()
            cat = CATMAP.get(cat_pt, "Community & Social")
            name = (rec.get("name") or "").strip()
            pending.append({
                "name": name[:120] or code,
                "category": cat,
                "country": "BR",
                "description": clean_desc(rec.get("desc_pt", ""), name or code, cat),
                "invite": f"https://chat.whatsapp.com/{code}",
                "reason": res.get("reason", "transport failure"),
            })
        elif res["status"] == "existing":
            exclusions.append({"code": code, "reason": "already in groups.json (existing code)"})
        else:
            dead += 1
    # leads: listing pages that failed to fetch + un-fetched listings
    try:
        failed = json.load(open(f"{WAVE}/team03-fetch-failed.json"))
        leads = [f["url"] for f in failed]
    except Exception:
        leads = []
    fetched_urls = {r["url"] for r in raw}
    all_urls = json.load(open(f"{WAVE}/leads_slice3.json"))
    leads += [u for u in all_urls if u not in fetched_urls]
    # fetched but JS-gated (no invite code in static HTML) — needs a browser click to reveal
    leads += [r["url"] for r in raw if not r.get("codes")]
    leads = sorted(set(leads))

    json.dump(verified, open(f"{WAVE}/team03-leads-slice3.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(f"{WAVE}/team03-leads-slice3-pending.json", "w"), ensure_ascii=False, indent=1)
    json.dump(leads, open(f"{WAVE}/team03-leads-slice3-leads.json", "w"), ensure_ascii=False, indent=1)
    summary = {
        "team": "team03", "slice": "leads slice 3",
        "sources": ["linkado.app grupo pages (3,603 listing URLs)"],
        "verified": len(verified), "pending": len(pending), "leads": len(leads),
        "dead": dead, "exclusions": exclusions,
        "resume": ("fetch+verify complete" if not leads else
                   f"retry {len(leads)} listing URLs in team03-leads-slice3-leads.json"),
        "notes": ("All listing pages are linkado.app (pt-BR). Country BR set from site locale/content. "
                  "Descriptions sanitized: emails/URLs/phone-like digit runs removed. "
                  "Live = HTTP 200 + non-empty og:title on chat.whatsapp.com, retried once."),
    }
    json.dump(summary, open(f"{WAVE}/team03-leads-slice3-summary.json", "w"), ensure_ascii=False, indent=1)
    print(f"VERIFIED={len(verified)} PENDING={len(pending)} LEADS={len(leads)} DEAD={dead} EXCL={len(exclusions)}", flush=True)

if __name__ == "__main__":
    main()
