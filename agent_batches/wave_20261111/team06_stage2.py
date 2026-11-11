#!/usr/bin/env python3
"""TEAM 06 — Stage 2: dedupe vs existing codes, slow-verify via chat.whatsapp.com,
classify category, screen scams/adult, bank verified/pending/dead.
Checkpoints every 200 verifications to team06-stage2-checkpoint.json.
"""
import json, re, os, sys, time, threading, unicodedata, html
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG_RE2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:title"', re.I)

# ---------- category mapping (PT -> canonical) ----------
PT_CAT = {
    "amizade": "Friendship", "amigos": "Friendship", "namoro": "Friendship",
    "educação": "Education", "educacao": "Education", "estudos": "Education",
    "empregos": "Jobs", "emprego": "Jobs", "trabalho": "Jobs",
    "entretenimento": "Entertainment", "música": "Entertainment", "musica": "Entertainment",
    "filmes": "Entertainment", "séries": "Entertainment", "series": "Entertainment",
    "islâmico": "Islamic", "islamico": "Islamic", "islão": "Islamic", "islao": "Islamic",
    "religião": "Community & Social", "religiao": "Community & Social",
    "notícias": "News", "noticias": "News",
    "esportes": "Sports", "esporte": "Sports", "futebol": "Sports",
    "tecnologia": "Technology",
    "saúde": "Health", "saude": "Health",
    "negócios": "Business", "negocios": "Business",
    "jogos": "Gaming", "games": "Gaming",
    "comunidade": "Community & Social", "geral": "Community & Social",
    "outros": "Community & Social", "variedades": "Community & Social",
    "ganhar dinheiro": "Online Earning", "renda extra": "Online Earning",
    "criptomoedas": "Crypto", "cripto": "Crypto",
    "culinária": "Cooking", "culinaria": "Cooking", "receitas": "Cooking",
    "poesia": "Poetry",
    "viagem": "Travel", "turismo": "Travel",
    "bolsas de estudo": "Scholarship", "bolsa de estudos": "Scholarship",
    "freelance": "Freelance", "freelancer": "Freelance",
    "imóveis": "Real Estate", "imoveis": "Real Estate",
    "comprar e venda": "Buy Sell", "compras": "Buy Sell", "vendas": "Buy Sell",
    "dinheiro": "Online Earning",
    "links": "Community & Social", "lgbt": "Community & Social",
    "figurinhas": "Entertainment",
    "moda e beleza": "Community & Social", "carros": "Community & Social",
    "status": "Community & Social", "cidades": "Community & Social",
    "politica": "News", "fitness": "Health",
    "finanças": "Finance", "financas": "Finance",
    "humor": "Funny", "engraçado": "Funny", "memes": "Funny",
}

KW_CAT = [
    (r"\b(amizade|amigos|friendship|namoro|conhecer pessoas|bate-papo|chat)\b", "Friendship"),
    (r"\b(educa|estudo|escola|faculdade|curso|aprender|ingles|inglês|matemática|vestibular|enem)\b", "Education"),
    (r"\b(emprego|vaga|trabalho|contrata|oportunidade de trabalho)\b", "Jobs"),
    (r"\b(filme|serie|série|música|musica|entretenimento|novela|anime|doramas?)\b", "Entertainment"),
    (r"\b(islam|islâm|muçulman|alcorão|quran|mesquita|allah)\b", "Islamic"),
    (r"\b(notícia|noticia|jornal|news|urgente)\b", "News"),
    (r"\b(futebol|esporte|sport|flamengo|corinthians|palmeiras|futebol)\b", "Sports"),
    (r"\b(tecnologia|programa|python|javascript|informática|informatica|celular|android|iphone)\b", "Technology"),
    (r"\b(saúde|saude|emagrec|dieta|fitness|treino|academia|nutri)\b", "Health"),
    (r"\b(negócio|negocio|empreendedor|empresa|marketing|vendas?)\b", "Business"),
    (r"\b(jogo|games?|gamer|free fire|fortnite|minecraft|roblox)\b", "Gaming"),
    (r"\b(ganhar dinheiro|renda extra|dinheiro online|trabalhar em casa)\b", "Online Earning"),
    (r"\b(cripto|bitcoin|ethereum|binance|trading)\b", "Crypto"),
    (r"\b(receita|culinária|culinaria|cozinha|bolo|doces?)\b", "Cooking"),
    (r"\b(poesia|poema|poeta)\b", "Poetry"),
    (r"\b(viagem|turismo|passagem|praia|mochil)\b", "Travel"),
    (r"\b(bolsa de estudo|bolsas? de estudo|scholarship)\b", "Scholarship"),
    (r"\b(freelance|freelancer)\b", "Freelance"),
    (r"\b(imóvel|imovel|aluguel|casa à venda|apartamento)\b", "Real Estate"),
    (r"\b(compra e venda|compra|venda|desapega|classificados)\b", "Buy Sell"),
    (r"\b(finanças|financas|investimento|bolsa de valores|juros)\b", "Finance"),
    (r"\b(humor|meme|engraçado|piada|risada)\b", "Funny"),
]

# ---------- screening ----------
SCAM_PATTERNS = [
    r"b[\s\-]?love", r"forsage", r"shey[iy]", r"holiverse", r"meta[\s\-]?whale",
    r"airdrop", r"ganhe (dinheiro|r\$|reais) (grátis|gratis|rápido|rapido)",
    r"aposta[s]?", r"bet365", r"cassino", r"casino", r"jogos de azar",
    r"pix (grátis|gratis|dobro)", r"dobrar (seu )?dinheiro", r"lucro (garantido|diário|diario)",
    r"investimento (garantido|seguro) (100|mil|%)", r"r\$ ?\d+ ?por dia",
]
PORN_PATTERNS = [
    r"\b(xxx|porn[oô]|sexo explícito|sexo explicito|putaria|videos? (de )?sexo|sexo (grátis|gratis|ao vivo))\b",
    r"\b(nudes?|onlyfans|pack de (fotos|videos?)|vazados?|novinhas (peladas?|nua))\b",
    r"\b(🔞|🍆|🍑|💦)\b",
]
NEGATION_STRIP = re.compile(
    r"[^.!?\n]*(proibido|não (permitido|vale|pode)|sem (porn|sexo|putaria)|no porn|no sex|sem nude)[^.!?\n]*",
    re.I)

def norm(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()

def is_scam_or_porn(text):
    t = norm(text)
    t_clean = NEGATION_STRIP.sub(" ", t)
    for p in SCAM_PATTERNS:
        if re.search(p, t):
            return "scam: " + p
    for p in PORN_PATTERNS:
        if re.search(p, t_clean):
            return "adult/porn: " + p
    return None

def clean_name(title):
    # "Grupo de WhatsApp <Name> - <Category>" -> <Name>
    t = (title or "").strip()
    t = re.sub(r"^grupo de whatsapp\s+", "", t, flags=re.I)
    t = re.sub(r"\s*[-–—|]\s*[^-–—|]{2,40}$", "", t).strip()
    return t[:120]

def classify(cat_pt, name):
    c = (cat_pt or "").strip().lower()
    if c in PT_CAT:
        return PT_CAT[c]
    for k, v in PT_CAT.items():
        if k in c:
            return v
    n = norm(name)
    for pat, v in KW_CAT:
        if re.search(pat, n):
            return v
    return "Community & Social"

def verify(code, session):
    """Returns (status, og_title). status: live|dead|transport.
    WhatsApp serves valid invites from this env in ~29s; timeout must exceed that."""
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(2):
        try:
            r = session.get(url, timeout=45)
            if r.status_code != 200:
                if attempt == 0:
                    time.sleep(5.0)
                    continue
                return ("dead", "")
            m = OG_RE.search(r.text) or OG_RE2.search(r.text)
            title = (m.group(1).strip() if m else "")
            if title:
                return ("live", title)
            # empty og:title -> retry once after pause
            if attempt == 0:
                time.sleep(5.0)
                continue
            return ("dead", "")
        except Exception:
            if attempt == 0:
                time.sleep(5.0)
                continue
            return ("transport", "")
    return ("dead", "")

def write_outputs(results, by_code, existing, partial=False):
    verified, pending, dead, exclusions = [], [], [], []
    for code, rec in by_code.items():
        if code in existing:
            continue
        r = results.get(code)
        if r is None:
            continue  # not yet verified; stays out of all files (resume point covers it)
        st = r["status"]
        name = html.unescape(clean_name(rec["title"])) or (html.unescape(r["og"]) or "WhatsApp Group")
        desc = html.unescape((rec["desc"] or "").strip())
        cat = classify(rec["cat_pt"], name)
        if st == "live":
            reason = is_scam_or_porn(name + " " + r["og"] + " " + desc)
            if reason:
                exclusions.append({"code": code, "reason": reason})
                continue
            if not desc:
                desc = f"Grupo de WhatsApp {name} ({cat}). Entre e participe da comunidade."
            verified.append({"name": name, "category": cat, "country": "",
                             "description": desc[:300], "invite": f"https://chat.whatsapp.com/{code}"})
        elif st == "transport":
            pending.append({"name": name, "category": cat, "country": "",
                            "description": desc[:300], "invite": f"https://chat.whatsapp.com/{code}",
                            "reason": "transport failure during verification"})
        else:
            dead.append(code)
    json.dump(verified, open(os.path.join(WAVE, "team06-leads-slice6.json"), "w"), ensure_ascii=False)
    json.dump(pending, open(os.path.join(WAVE, "team06-leads-slice6-pending.json"), "w"), ensure_ascii=False)
    failed_pages = json.load(open(os.path.join(WAVE, "team06-stage1-failed.json")))
    ckpt1 = json.load(open(os.path.join(WAVE, "team06-stage1-checkpoint.json")))
    no_code_pages = sorted(u for u, v in ckpt1.items() if not v.get("codes"))
    leads = sorted(set(failed_pages) | set(no_code_pages))
    json.dump(leads, open(os.path.join(WAVE, "team06-leads-slice6-leads.json"), "w"), ensure_ascii=False)
    done_n = len(results)
    total_new = len([c for c in by_code if c not in existing])
    remaining = [c for c in by_code if c not in existing and c not in results]
    summary = {
        "team": "team06", "slice": "leads_slice6",
        "sources": ["linkado.app listing pages (3603)"],
        "verified": len(verified), "pending": len(pending),
        "leads": len(leads), "dead": len(dead),
        "exclusions": exclusions,
        "resume": ("PARTIAL: %d/%d new codes verified; %d unverified codes remain in "
                   "team06-stage2-checkpoint.json (rerun team06_stage2.py to resume). "
                   "Stage1 checkpoint team06-stage1-checkpoint.json; failed/no-code listing pages in "
                   "team06-leads-slice6-leads.json" % (done_n, total_new, len(remaining)))
                  if partial else
                  "complete: all new codes verified; stage1 checkpoint team06-stage1-checkpoint.json; "
                  "stage2 checkpoint team06-stage2-checkpoint.json; failed/no-code listing pages in "
                  "team06-leads-slice6-leads.json",
        "notes": (f"unique codes mined {len(by_code)}; dup vs existing {len([c for c in by_code if c in existing])}; "
                  f"dead codes {len(dead)} not banked; leads = {len(failed_pages)} fetch-failed + "
                  f"{len(no_code_pages)} no-code pages (invite hidden/removed, retry next wave). "
                  f"ENV NOTE: live codes return non-empty og:title (WhatsApp lookup ~30s); dead/revoked codes "
                  f"return HTTP 200 with empty og:title (fast after first lookup). Empty-og codes were retried once "
                  f"after a 5s pause before being marked dead, per the wave rule."),
    }
    json.dump(summary, open(os.path.join(WAVE, "team06-leads-slice6-summary.json"), "w"), ensure_ascii=False, indent=2)
    print(f"OUTPUTS written partial={partial} VERIFIED={len(verified)} PENDING={len(pending)} "
          f"LEADS={len(leads)} DEAD={len(dead)} EXCLUSIONS={len(exclusions)}", flush=True)
    return summary

def main():
    cands = json.load(open(os.path.join(WAVE, "team06-stage1-candidates.json")))
    existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
    by_code = {}
    for c in cands:
        by_code.setdefault(c["code"], c)
    if len(sys.argv) > 1 and sys.argv[1] == "finalize":
        results = json.load(open(os.path.join(WAVE, "team06-stage2-checkpoint.json")))
        complete = len(results) >= len([c for c in by_code if c not in existing])
        write_outputs(results, by_code, existing, partial=not complete)
        return
    print(f"unique codes mined: {len(by_code)}", flush=True)
    new_codes = [c for c in by_code if c not in existing]
    print(f"new (not in existing): {len(new_codes)}; dup vs existing: {len(by_code)-len(new_codes)}", flush=True)

    ckpt_path = os.path.join(WAVE, "team06-stage2-checkpoint.json")
    results = {}
    if os.path.exists(ckpt_path):
        results = json.load(open(ckpt_path))
        print(f"resuming: {len(results)} verifications done", flush=True)
    session = requests.Session()
    session.headers.update(UA)
    lock = threading.Lock()
    counter = [0]
    total = len(new_codes)

    def work(code):
        if code in results:
            return
        status, og = verify(code, session)
        time.sleep(0.55)
        with lock:
            results[code] = {"status": status, "og": og}
            counter[0] += 1
            n = counter[0]
        if n % 200 == 0:
            with lock:
                json.dump(results, open(ckpt_path, "w"), ensure_ascii=False)
                write_outputs(results, by_code, existing, partial=True)
            print(f"{n}/{total} verified", flush=True)

    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(work, new_codes))
    json.dump(results, open(ckpt_path, "w"), ensure_ascii=False)
    write_outputs(results, by_code, existing, partial=False)

if __name__ == "__main__":
    main()
