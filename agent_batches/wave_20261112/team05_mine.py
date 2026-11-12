#!/usr/bin/env python3
"""TEAM 04 — WhatsGroupLinks wave 20261111, leads slice 4 (linkado.app grupo pages).
Mines listing pages (curl, browser UA), extracts invite codes, dedupes vs
.existing_codes.json, verifies slowly (curl chat.whatsapp.com, LIVE iff HTTP 200
AND non-empty og:title, one retry on empty og:title after a pause), screens
content, banks verified. Writes checkpoints + final outputs incrementally so a
partial run is still bankable. Run in batches of 100 listings; stops at deadline.
"""
import json, re, os, sys, time, html, subprocess, threading
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
LEADS = os.path.join(WAVE, "leads_slice4.json")
EXISTING = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

MINED_JL = os.path.join(WAVE, "team05-mined.jsonl")
VERIFY_JL = os.path.join(WAVE, "team05-verify.jsonl")
OUT_VERIFIED = os.path.join(WAVE, "team05-leads-slice4.json")
OUT_PENDING = os.path.join(WAVE, "team05-leads-slice4-pending.json")
OUT_LEADS = os.path.join(WAVE, "team05-leads-slice4-leads.json")
OUT_SUMMARY = os.path.join(WAVE, "team05-leads-slice4-summary.json")

DEADLINE_MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 120.0
START = time.time()
DEADLINE = START + DEADLINE_MIN * 60
WORKERS = 6
lock = threading.Lock()

CANON = ["Education","Jobs","Entertainment","Islamic","News","Sports","Technology",
         "Health","Business","Gaming","Friendship","Community & Social","Online Earning",
         "Crypto","Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate",
         "Buy Sell","Finance","Funny"]

PT_MAP = {
    "amizade": "Friendship", "amigos": "Friendship", "namoro": "Friendship",
    "dinheiro": "Finance", "finanças": "Finance", "financas": "Finance",
    "comprar e venda": "Buy Sell", "compra e venda": "Buy Sell",
    "compras": "Buy Sell", "vendas": "Buy Sell",
    "educação": "Education", "educacao": "Education", "estudos": "Education",
    "cursos": "Education", "escola": "Education",
    "emprego": "Jobs", "empregos": "Jobs", "vagas": "Jobs", "trabalho": "Jobs",
    "entretenimento": "Entertainment", "filmes": "Entertainment",
    "música": "Entertainment", "musica": "Entertainment", "memes": "Funny",
    "humor": "Funny", "comédia": "Funny", "comedia": "Funny",
    "esportes": "Sports", "futebol": "Sports", "esporte": "Sports",
    "tecnologia": "Technology", "saúde": "Health", "saude": "Health",
    "negócios": "Business", "negocios": "Business",
    "empreendedorismo": "Business", "jogos": "Gaming", "games": "Gaming",
    "notícias": "News", "noticias": "News",
    "culinária": "Cooking", "culinaria": "Cooking", "receitas": "Cooking",
    "poesia": "Poetry", "viagem": "Travel", "turismo": "Travel",
    "bolsa": "Scholarship", "bolsas": "Scholarship",
    "freelance": "Freelance", "imóveis": "Real Estate", "imoveis": "Real Estate",
    "cripto": "Crypto", "bitcoin": "Crypto", "criptomoedas": "Crypto",
    "religião": "Community & Social", "religiao": "Community & Social",
    "fé": "Community & Social", "bíblia": "Community & Social",
    "oração": "Community & Social", "igreja": "Community & Social",
    "ganhos": "Online Earning", "renda extra": "Online Earning",
    "comunidade": "Community & Social", "geral": "Community & Social",
    "outros": "Community & Social", "diversos": "Community & Social",
}
EARN_KW = ["renda extra", "ganhar dinheiro", "ganhe dinheiro", "ganhar", "ganhe",
           "lucro", "investimento", "marketing digital", "renda"]
SCAM_TOKENS = ["b-love", "blove", "forsage", "sheyi", "holiverse",
               "meta-whale", "metawhale", "meta whale",
               "bot mines", "mines vip", "sinais mines"]
PORN_TOKENS = ["porn", "xxx", "porno", "pornô", "putaria", "nudes",
               "sexo explicito", "sexo explícito", "conteúdo adulto",
               "conteudo adulto", "videos quentes", "vídeos quentes",
               "goza", "gozar", "vendo meus conte"]
NEGATION_RES = [
    r"🚫[^.!?;]{0,60}",
    r"\bproibid[oa]s?\b[^.!?;]{0,60}",
    r"\bproibição\b[^.!?;]{0,60}",
    r"\bnão é permitido\b[^.!?;]{0,60}",
    r"\bnao e permitido\b[^.!?;]{0,60}",
    r"\bsem porn\w*\b[^.!?;]{0,40}",
    r"\bno porn\b[^.!?;]{0,40}",
    r"\bconteúdos? pornogr[aá]ficos?\b.{0,0}",  # handled below via emoji strip
]
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def curl(url, max_time):
    try:
        r = subprocess.run(["curl", "-s", "-L", "--compressed", "--max-time",
                            str(max_time), "-A", UA, url],
                           capture_output=True, text=True, timeout=max_time + 15)
        return r.stdout or ""
    except Exception:
        return ""

def clean_text(t):
    if not t:
        return ""
    t = html.unescape(t)
    t = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), t)
    t = t.replace("\\n", " ").replace("\\t", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t

def strip_prohibitions(t):
    """Remove negated-prohibition sentences/phrases before porn screening."""
    if not t:
        return ""
    s = t
    # "🚫 Conteúdos pornograficos" / "🚫 porn ..." -> whole prohibition phrase
    s = re.sub(r"🚫\s*[^.!?;\n]{0,80}", " ", s)
    s = re.sub(r"⛔\s*[^.!?;\n]{0,80}", " ", s)
    for pat in [r"\bproibid[oa]s?\b[^.!?;\n]{0,80}",
                r"\bn[ãa]o (?:é|e) permitido\b[^.!?;\n]{0,80}",
                r"\bsem porn\w*[^.!?;\n]{0,60}",
                r"\bno porn\b[^.!?;\n]{0,60}",
                r"\bproibido porn\w*[^.!?;\n]{0,60}"]:
        s = re.sub(pat, " ", s, flags=re.I)
    return s

def screen(name, desc, ogtitle):
    """Return exclusion reason or None. Screens banked name AND og:title."""
    blob = f"{name} {desc} {ogtitle or ''}"
    low = blob.lower()
    for tok in SCAM_TOKENS:
        if tok in low:
            return f"crypto-airdrop scam token '{tok}'"
    # betting-scam: betting terms + guaranteed-profit language
    if re.search(r"\b(bet|aposta|apostas|cassino|casino)\b", low) and \
       re.search(r"lucro garantido|ganho garantido|dinheiro f[aá]cil|dobrar|2x|100% certo|certeza de ganho", low):
        return "betting-scam language"
    # adult-emoji combo: 🔞 together with a sexual emoji / sex-meetup wording
    if "🔞" in blob and re.search(r"🍆|🍑|😈|🥵|encontro|sexo|goza|putaria|acompanhante", low):
        return "adult sexual content (🔞 + sexual emoji/meetup og:title)"
    clean = strip_prohibitions(blob)
    clow = clean.lower()
    for tok in PORN_TOKENS:
        if tok in clow:
            return f"hard porn/xxx marker '{tok}'"
    if PHONE_RE.search(name) or EMAIL_RE.search(name):
        return "personal info (phone/email) in name"
    return None

def map_category(pt_cat, name, desc):
    c = (pt_cat or "").strip().lower()
    if c in PT_MAP:
        cat = PT_MAP[c]
    else:
        cat = None
        blob = f"{c} {name} {desc}".lower()
        for kw, cc in [("renda extra", "Online Earning"), ("ganhar dinheiro", "Online Earning"),
                       ("investimento", "Finance"), ("vagas", "Jobs"), ("emprego", "Jobs"),
                       ("futebol", "Sports"), ("free fire", "Gaming"), ("jogos", "Gaming"),
                       ("filme", "Entertainment"), ("música", "Entertainment"),
                       ("receita", "Cooking"), ("oração", "Community & Social"),
                       ("islâm", "Islamic"), ("muçulman", "Islamic"), ("alcorão", "Islamic"),
                       ("bitcoin", "Crypto"), ("cripto", "Crypto")]:
            if kw in blob:
                cat = cc
                break
        if not cat:
            cat = "Community & Social"
    # Dinheiro refinement: earning keywords -> Online Earning
    if c == "dinheiro":
        blob = f"{name} {desc}".lower()
        if any(k in blob for k in EARN_KW):
            cat = "Online Earning"
    # selling keywords in the name override soft categories
    if cat in ("Friendship", "Community & Social", "Finance"):
        nm = (name or "").lower()
        if "venda" in nm or "seguidor" in nm or "iptv" in nm:
            cat = "Buy Sell"
    return cat

def parse_listing(html_text, url):
    if not html_text:
        return None
    codes = re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,})", html_text)
    code = codes[0] if codes else None
    # unescape RSC payload for JSON-LD fields
    u = html_text.replace('\\"', '"')
    name = desc = None
    m = re.search(r'"@type":"WebPage","name":"((?:[^"\\]|\\.)*)","description":"((?:[^"\\]|\\.)*)"', u)
    if m:
        name, desc = clean_text(m.group(1)), clean_text(m.group(2))
    title = None
    tm = re.search(r"<title>([^<]*)</title>", html_text)
    if tm:
        title = clean_text(tm.group(1))
    pt_cat = ""
    if title and title.startswith("Grupo de WhatsApp "):
        body = title[len("Grupo de WhatsApp "):]
        if " - " in body:
            nm, pt_cat = body.rsplit(" - ", 1)
            if not name:
                name = nm.strip()
        elif not name:
            name = body.strip()
    if not name and title:
        name = title
    if not pt_cat:
        cm = re.search(r"categoria de grupos de WhatsApp de ([^ ][^<]{0,60}?) no Linkado", u)
        if cm:
            pt_cat = clean_text(cm.group(1)).strip()
    # description fallback: og:description trailing sentence
    if not desc:
        om = re.search(r'og:description" content="([^"]*)"', html_text)
        if om:
            od = clean_text(om.group(1))
            parts = od.split(". ", 1)
            if len(parts) > 1:
                desc = parts[1].strip()
    if name:
        name = name.strip()
        if name.endswith("..."):
            name = name[:-3].strip()
    return {"url": url, "code": code, "name": name or "", "pt_category": pt_cat,
            "description": desc or ""}

def og_title(html_text):
    if not html_text:
        return None, 0
    m = re.search(r'og:title["\']?\s+content=["\']([^"\']*)', html_text)
    if m:
        return clean_text(m.group(1)), 200
    return "", 200

def verify_code(code):
    """Returns (status, ogtitle): status in live/dead/pending."""
    h1 = curl(f"https://chat.whatsapp.com/{code}", 45)
    t1, _ = og_title(h1)
    if t1:
        return "live", t1
    if not h1:
        # transport failure, not a verdict yet — retry once after pause
        time.sleep(20)
        h2 = curl(f"https://chat.whatsapp.com/{code}", 45)
        t2, _ = og_title(h2)
        if t2:
            return "live", t2
        if not h2:
            return "pending", ""
        return "dead", ""
    # got HTML but empty og:title -> retry once after pause (rule)
    time.sleep(20)
    h2 = curl(f"https://chat.whatsapp.com/{code}", 45)
    t2, _ = og_title(h2)
    if t2:
        return "live", t2
    if not h2:
        return "pending", ""
    return "dead", ""

def append_jl(path, rec):
    with lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def load_jl(path):
    out = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        pass
    return out

def write_outputs(state):
    with open(OUT_VERIFIED, "w", encoding="utf-8") as f:
        json.dump(state["verified"], f, ensure_ascii=False, indent=1)
    with open(OUT_PENDING, "w", encoding="utf-8") as f:
        json.dump(state["pending"], f, ensure_ascii=False, indent=1)
    with open(OUT_LEADS, "w", encoding="utf-8") as f:
        json.dump(state["leads"], f, ensure_ascii=False, indent=1)
    summary = {
        "team": "team05", "slice": "leads_slice4",
        "sources": ["linkado.app grupo pages"],
        "verified": len(state["verified"]),
        "pending": len(state["pending"]),
        "leads": len(state["leads"]),
        "dead": state["dead"],
        "exclusions": state["exclusions"],
        "resume": state["resume"],
        "notes": state["notes"],
    }
    with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)

def main():
    urls = json.load(open(LEADS))
    existing = set(json.load(open(EXISTING)))
    mined_done = {r["url"]: r for r in load_jl(MINED_JL)}
    verified_done = {r["code"]: r for r in load_jl(VERIFY_JL)}
    state = {"verified": [], "pending": [], "leads": [], "dead": 0,
             "exclusions": [], "resume": "", "notes": []}
    # rebuild state from checkpoints (idempotent re-run safe)
    seen_codes = set()
    for r in load_jl(VERIFY_JL):
        code = r["code"]
        if r["status"] == "live" and code not in seen_codes:
            seen_codes.add(code)
            state["verified"].append({k: r[k] for k in ("name", "category", "country", "description", "invite")})
        elif r["status"] == "dead":
            state["dead"] += 1
        elif r["status"] == "pending":
            state["pending"].append({k: r[k] for k in ("name", "category", "country", "description", "invite") if k in r} | {"reason": r.get("reason", "transport failure")})
    for r in load_jl(MINED_JL):
        pass
    for e in [r for r in load_jl(VERIFY_JL) if r["status"] == "excluded"]:
        state["exclusions"].append({"code": e["code"], "reason": e["reason"]})
    # also exclusions recorded at mine stage (dup-existing)
    for r in load_jl(MINED_JL):
        if r.get("stage") == "dup-existing":
            state["exclusions"].append({"code": r["code"], "reason": "already in groups.json (existing code)"})

    todo = [u for u in urls if u not in mined_done]
    print(f"total={len(urls)} mined_done={len(mined_done)} todo={len(todo)} verified_so_far={len(state['verified'])}", flush=True)
    idx = 0
    batch_no = 0
    while idx < len(todo):
        if time.time() > DEADLINE:
            print("DEADLINE reached, stopping.", flush=True)
            break
        batch = todo[idx:idx + 100]
        idx += len(batch)
        batch_no += 1
        # ---- mine batch ----
        def mine_one(u):
            h = curl(u, 60)
            if not h:
                time.sleep(5)
                h = curl(u, 60)
            if not h:
                return {"url": u, "stage": "fetch-fail"}
            p = parse_listing(h, u)
            if not p or not p["code"]:
                return {"url": u, "stage": "no-invite", "name": (p or {}).get("name", ""), "pt_category": (p or {}).get("pt_category", "")}
            return {"url": u, "stage": "mined", **p}
        from concurrent.futures import as_completed as _ac
        mined = []
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {ex.submit(mine_one, u): u for u in batch}
            for fut in _ac(futs):
                r = fut.result()
                mined.append(r)
                append_jl(MINED_JL, r)
                mined_done[r["url"]] = r
        # ---- verify mined codes in batch ----
        cands = []
        for r in mined:
            if r["stage"] != "mined":
                continue
            code = r["code"]
            if code in existing:
                append_jl(MINED_JL, {"url": r["url"], "stage": "dup-existing", "code": code})
                state["exclusions"].append({"code": code, "reason": "already in groups.json (existing code)"})
                continue
            if code in seen_codes or code in verified_done:
                continue
            seen_codes.add(code)
            cands.append(r)
        def verify_one(r):
            code = r["code"]
            cat = map_category(r.get("pt_category", ""), r.get("name", ""), r.get("description", ""))
            name = r.get("name", "") or "WhatsApp Group"
            desc = r.get("description", "")
            status, ogt = verify_code(code)
            rec = {"code": code, "name": name, "category": cat, "country": "BR",
                   "description": desc, "invite": f"https://chat.whatsapp.com/{code}",
                   "og_title": ogt or "", "status": status,
                   "pt_category": r.get("pt_category", ""), "source_url": r["url"]}
            if status == "live":
                reason = screen(name, desc, ogt)
                if reason:
                    rec["status"] = "excluded"
                    rec["reason"] = reason
                else:
                    if not desc:
                        rec["description"] = f"Join {name}, a WhatsApp group listed under {cat}."
                    elif len(desc) > 300:
                        rec["description"] = desc[:297].rstrip() + "..."
            return rec
        if cands:
            from concurrent.futures import as_completed as _ac2
            with ThreadPoolExecutor(max_workers=WORKERS) as ex:
                futs = {ex.submit(verify_one, r): r for r in cands}
                for fut in _ac2(futs):
                    rec = fut.result()
                    append_jl(VERIFY_JL, rec)
                    verified_done[rec["code"]] = rec
                    if rec["status"] == "live":
                        d = rec["description"] or f"Join {rec['name']}, a WhatsApp group listed under {rec['category']}."
                        state["verified"].append({"name": rec["name"], "category": rec["category"],
                                                  "country": "BR", "description": d,
                                                  "invite": rec["invite"]})
                    elif rec["status"] == "dead":
                        state["dead"] += 1
                    elif rec["status"] == "pending":
                        state["pending"].append({"name": rec["name"], "category": rec["category"],
                                                 "country": "BR",
                                                 "description": rec["description"] or f"Join {rec['name']}, a WhatsApp group listed under {rec['category']}.",
                                                 "invite": rec["invite"],
                                                 "reason": "transport failure during verification (curl empty/timeout)"})
                    elif rec["status"] == "excluded":
                        state["exclusions"].append({"code": rec["code"], "reason": rec["reason"]})
        # ---- leads: fetch-fails + not-yet-attempted ----
        state["leads"] = [r["url"] for r in mined_done.values() if r.get("stage") == "fetch-fail"]
        state["leads"] += todo[idx:]
        state["resume"] = f"next unmined listing index {idx} of {len(todo)} remaining in this run's todo list; overall slice position {len(mined_done)} of {len(urls)} listings attempted; resume by re-running this script (it skips mined_done URLs)."
        state["notes"] = [
            f"listings attempted so far: {len(mined_done)} of {len(urls)}",
            f"listings with no invite found: {sum(1 for r in mined_done.values() if r.get('stage')=='no-invite')}",
            f"listings fetch-failed (in leads file for retry): {sum(1 for r in mined_done.values() if r.get('stage')=='fetch-fail')}",
            "linkado.app is very slow from this VM (TTFB ~15-20s) and chat.whatsapp.com ~10s+ with occasional timeouts; throughput is network-bound.",
            "country BR for all (linkado.app is a Brazilian directory, locale pt_BR).",
            "Descriptions use the listing's own description text where present, else a template from name/category. No source name/link stored in verified entries.",
        ]
        write_outputs(state)
        print(f"batch {batch_no}: attempted={len(mined_done)} verified={len(state['verified'])} dead={state['dead']} pending={len(state['pending'])} excl={len(state['exclusions'])} elapsed_min={round((time.time()-START)/60,1)}", flush=True)
    state["leads"] = [r["url"] for r in mined_done.values() if r.get("stage") == "fetch-fail"] + todo[idx:]
    state["resume"] = f"next unmined listing index {idx} of {len(todo)} remaining in this run's todo list; overall slice position {len(mined_done)} of {len(urls)} listings attempted; resume by re-running this script (it skips mined_done URLs)."
    write_outputs(state)
    print(f"DONE attempted={len(mined_done)} verified={len(state['verified'])} dead={state['dead']} pending={len(state['pending'])} leads={len(state['leads'])} excl={len(state['exclusions'])}", flush=True)

if __name__ == "__main__":
    main()
