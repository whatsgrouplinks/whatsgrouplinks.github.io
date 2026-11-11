#!/usr/bin/env python3
"""TEAM 11 wave 20261111 — linkado sitemap grupo indices 2700-3099."""
import json, re, time, html, subprocess, os
from concurrent.futures import ThreadPoolExecutor

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
SITE = "/home/hatch/workspace/whatsapp-groups-site"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

CATMAP = {
    "amizade": "Friendship", "amizades": "Friendship",
    "namoro": "Friendship", "relacionamento": "Friendship",
    "entretenimento": "Entertainment", "diversão": "Entertainment", "diversao": "Entertainment",
    "figurinhas": "Entertainment", "música": "Entertainment", "musica": "Entertainment",
    "filmes": "Entertainment", "séries": "Entertainment", "series": "Entertainment",
    "animes": "Entertainment", "humor": "Funny", "memes": "Funny",
    "empregos": "Jobs", "emprego": "Jobs", "vagas": "Jobs", "trabalho": "Jobs",
    "educação": "Education", "educacao": "Education", "estudos": "Education",
    "livros": "Education", "leitura": "Education", "idiomas": "Education",
    "inglês": "Education", "ingles": "Education", "cursos": "Education",
    "bolsas": "Scholarship", "bolsa": "Scholarship",
    "islâmico": "Islamic", "islamico": "Islamic", "islã": "Islamic", "alcorão": "Islamic",
    "esportes": "Sports", "esporte": "Sports", "futebol": "Sports",
    "finanças": "Finance", "financas": "Finance", "investimentos": "Finance",
    "investimento": "Finance", "dinheiro": "Finance", "renda": "Finance",
    "compra e venda": "Buy Sell", "compras": "Buy Sell", "vendas": "Buy Sell",
    "comprar e venda": "Buy Sell", "classificados": "Buy Sell",
    "saúde": "Health", "saude": "Health", "beleza": "Health", "fitness": "Health",
    "notícias": "News", "noticias": "News", "política": "News", "politica": "News",
    "jogos": "Gaming", "games": "Gaming", "jogo": "Gaming",
    "tecnologia": "Technology", "tech": "Technology",
    "negócios": "Business", "negocios": "Business", "empreendedorismo": "Business",
    "culinária": "Cooking", "culinaria": "Cooking", "receitas": "Cooking",
    "viagens": "Travel", "viagem": "Travel", "turismo": "Travel",
    "carros": "Community & Social", "motos": "Community & Social",
    "família": "Community & Social", "familia": "Community & Social",
    "religião": "Community & Social", "religiao": "Community & Social",
    "cristão": "Community & Social", "cristao": "Community & Social",
    "evangélico": "Community & Social", "católico": "Community & Social",
    "grupos": "Community & Social", "geral": "Community & Social",
    "animais": "Community & Social", "pets": "Community & Social",
    "moda": "Community & Social", "poesia": "Poetry",
    "cripto": "Crypto", "criptomoedas": "Crypto", "bitcoin": "Crypto",
    "ganhar dinheiro": "Online Earning", "renda extra": "Online Earning",
    "freelance": "Freelance", "freela": "Freelance",
    "imóveis": "Real Estate", "imoveis": "Real Estate",
    "apostas": "Finance", "cassino": "Entertainment",
}

SCAM = ["b-love", "blove", "b love", "forsage", "shey", "holiverse", "meta-whale",
        "meta whale", "airdrop", "paypal loader", "bitfinex",
        "counterfeit currency", "crypto-doubling", "carding",
        "dinheiro fácil", "dinheiro facil", "dobrar seu dinheiro",
        "lucro garantido", "investimento garantido", "ganhe dinheiro rápido",
        "ganhe dinheiro rapido", "multiplicar bitcoin", "multiplicar seu dinheiro",
        "falsificar", "clonar cartão", "clonar cartao", "roubar", "hackear whatsapp",
        "sinais vip", "banca garantida", "aposta garantida", "ganhar na loteria"]
ADULT = ["🔞", "🥵", "porn", "xxx", "sexo explícito", "sexo explicito",
         "putaria", "conteúdo adulto", "conteudo adulto", "nudes", "novinhas",
         "gostosas", "safada", "tesão", "tesao", "erótico", "erotico",
         "onlyfans", "pack de", "vazados", "vazadas", "amadores quentes",
         "sex chat", "acompanhantes", "garotas de programa", "sexo grátis",
         "sexo gratis", "xereca", "boquete", "siririca"]
NEG = ["proibido", "proibida", "proibidos", "proibidas", "sem ", "não ", "nao ",
       "nunca", "zero ", "nenhum", "nenhuma"]

def strip_negated(text):
    # Remove sentences that prohibit the adult content (e.g. 'Proibido pornografia')
    parts = re.split(r'(?<=[.!;])\s+', text)
    kept = []
    for p in parts:
        pl = p.lower()
        if any(n in pl for n in NEG) and any(a in pl for a in ADULT):
            continue
        kept.append(p)
    return " ".join(kept)

def has_adult(text):
    return any(a in strip_negated(text).lower() for a in ADULT)

def has_scam(text):
    return any(s in text.lower() for s in SCAM)

def fetch(url, timeout=60):
    try:
        r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", str(timeout),
                            "-w", "\n%{http_code}", url],
                           capture_output=True, text=True, timeout=timeout + 10)
        body, _, code = r.stdout.rpartition("\n")
        st = int(code) if code.strip().isdigit() else None
        if st is None or st == 0:
            return None, ""
        return st, body
    except Exception:
        return None, ""

def parse_page(h):
    m = re.search(r'<title>(.*?)</title>', h, re.S)
    title = html.unescape(m.group(1)).strip() if m else ""
    m2 = re.search(r'property="og:description"\s+content="([^"]*)"', h)
    desc = html.unescape(m2.group(1)).strip() if m2 else ""
    codes = re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})', h)
    seen = set(); uniq = []
    for c in codes:
        if c not in seen:
            seen.add(c); uniq.append(c)
    tele = bool(re.search(r't\.me/|telegram\.me/', h))
    return title, desc, uniq, tele

def clean_name(title):
    name = re.sub(r'^Grupo de WhatsApp\s*', '', title, flags=re.I).strip()
    name = re.sub(r'\s*-\s*[^-]{1,40}$', '', name).strip()
    name = re.sub(r'\s+', ' ', name)
    return name[:120]

def cat_from_title(title):
    m = re.search(r'-\s*([^-]{1,40})\s*$', title)
    if m:
        raw = m.group(1).strip().lower()
        if raw in CATMAP:
            return CATMAP[raw], raw
        for k, v in CATMAP.items():
            if k in raw:
                return v, raw
        return None, raw
    return None, ""

def clean_desc(d, name):
    d = re.sub(r'^Grupo de WhatsApp [^,]+, na categoria [^\.]+\.\s*', '', d, flags=re.I)
    d = re.sub(r'linkado\.app|Linkado', '', d, flags=re.I)
    d = re.sub(r'https?://\S+|www\.\S+', '', d)
    d = re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+', '', d)  # emails
    d = re.sub(r'\+?\d[\d\s().-]{7,}\d', '', d)  # phone-like
    d = re.sub(r'\s+', ' ', d).strip()
    return d

def main():
    existing = set(json.load(open(f"{SITE}/.existing_codes.json")))
    groups = json.load(open(f"{SITE}/groups.json"))
    gcodes = set()
    for g in groups:
        mm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', g.get("invite", ""))
        if mm:
            gcodes.add(mm.group(1))
    union = existing | gcodes
    print(f"union codes: {len(union)} (existing {len(existing)} + groups {len(gcodes)})", flush=True)

    entries = []
    for line in open(f"{WD}/team11_slice2700.txt"):
        idx, url, lastmod = line.rstrip("\n").split("\t")
        entries.append((int(idx), url, lastmod))

    ckpt_path = f"{WD}/team11_mined2700.ckpt.jsonl"
    done = {}
    try:
        for line in open(ckpt_path):
            r = json.loads(line)
            done[r["idx"]] = r
    except FileNotFoundError:
        pass
    todo = [e for e in entries if e[0] not in done]
    print(f"resuming: {len(done)} mined, {len(todo)} to fetch", flush=True)

    def mine(entry):
        idx, url, lastmod = entry
        st, h = fetch(url)
        if st is None or not h:
            time.sleep(5)
            st, h = fetch(url)
        if st is None or not h:
            return {"idx": idx, "url": url, "lastmod": lastmod, "error": "fetch-fail"}
        title, desc, codes, tele = parse_page(h)
        return {"idx": idx, "url": url, "lastmod": lastmod, "title": title,
                "desc": desc, "codes": codes, "telegram_only": tele and not codes, "status": st}

    ck = open(ckpt_path, "a")
    raw = list(done.values())
    with ThreadPoolExecutor(max_workers=5) as ex:
        for r in ex.map(mine, todo):
            raw.append(r)
            ck.write(json.dumps(r, ensure_ascii=False) + "\n"); ck.flush()
            if len(raw) % 50 == 0:
                print(f"mined {len(raw)}/400", flush=True)
    ck.close()
    raw.sort(key=lambda r: r["idx"])
    json.dump(raw, open(f"{WD}/team11_raw2700.json", "w"), ensure_ascii=False, indent=1)
    fetch_fail = [r for r in raw if "error" in r]
    print(f"mined done: {len(raw)} pages, fetch failures: {len(fetch_fail)}", flush=True)

    cands, exclusions = [], []
    seen_codes = set()
    n_tele = n_nojoin = n_dup = 0
    for r in raw:
        if "error" in r:
            continue
        if not r["codes"]:
            n_nojoin += 1
            continue
        title, desc = r["title"], r["desc"]
        name = clean_name(title)
        low = (title + " " + desc + " " + name).lower()
        for code in r["codes"]:
            if code in seen_codes:
                continue
            seen_codes.add(code)
            if code in union:
                n_dup += 1
                continue
            if has_scam(low):
                exclusions.append({"code": code, "reason": "scam signals: " + title[:100]}); continue
            if has_adult(low):
                exclusions.append({"code": code, "reason": "adult-sexual signals: " + title[:100]}); continue
            cat, rawcat = cat_from_title(title)
            if cat is None:
                cat = "Community & Social"
            cands.append({"code": code, "name": name, "title": title, "desc": desc,
                          "category": cat, "rawcat": rawcat, "url": r["url"],
                          "idx": r["idx"], "lastmod": r["lastmod"]})
    print(f"fresh candidates (post-dedupe+screen): {len(cands)}; dup-in-union: {n_dup}; no-join pages: {n_nojoin}; exclusions pre-verify: {len(exclusions)}", flush=True)
    json.dump({"cands": cands, "exclusions": exclusions, "fetch_fail": fetch_fail},
              open(f"{WD}/team11_candidates2700.json", "w"), ensure_ascii=False, indent=1)

    def verify(c):
        time.sleep(0.6)
        url = f"https://chat.whatsapp.com/{c['code']}"
        last_err = None
        for attempt in range(2):
            st, h = fetch(url, timeout=20)
            if st is None:
                last_err = "transport failure (no HTTP status)"
                if attempt == 0:
                    time.sleep(3)
                    continue
                return (c, "pending", last_err)
            if st == 200:
                m = re.search(r'property="og:title"\s+content="([^"]*)"', h or "")
                og = html.unescape(m.group(1)).strip() if m else ""
                if og:
                    return (c, "live", og)
                if attempt == 0:
                    time.sleep(3)
                    continue
                return (c, "dead", "HTTP 200 but empty og:title after 2 spaced tries")
            return (c, "dead", f"HTTP {st}")
        return (c, "pending", last_err or "transport failure")

    vckpt_path = f"{WD}/team11_verify2700.ckpt.jsonl"
    vdone = {}
    try:
        for line in open(vckpt_path):
            r = json.loads(line)
            vdone[r["code"]] = r
    except FileNotFoundError:
        pass
    vcands = [c for c in cands if c["code"] not in vdone]
    print(f"verify resume: {len(vdone)} done, {len(vcands)} to verify", flush=True)
    results = [(next(c for c in cands if c["code"] == code), v["status"], v["info"])
               for code, v in vdone.items()]
    vck = open(vckpt_path, "a")
    with ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(verify, vcands):
            results.append(res)
            vck.write(json.dumps({"code": res[0]["code"], "status": res[1], "info": res[2]}, ensure_ascii=False) + "\n"); vck.flush()
            if len(results) % 25 == 0:
                print(f"verified {len(results)}/{len(cands)}", flush=True)
    vck.close()

    verified, pending, dead = [], [], []
    for c, s, info in results:
        if s == "live":
            low = (c["title"] + " " + info).lower()
            if has_adult(low):
                exclusions.append({"code": c["code"], "reason": "adult signals in WhatsApp og:title: " + info[:100]})
                dead.append((c, "adult og:title")); continue
            if has_scam(low):
                exclusions.append({"code": c["code"], "reason": "scam signals in WhatsApp og:title: " + info[:100]})
                dead.append((c, "scam og:title")); continue
            # Bank live name from og:title; H1/directory name when og:title truncated
            og = info.strip()
            if og.endswith("...") or og.endswith("…") or "�" in og or len(og) < 3:
                name = c["name"]
            else:
                name = re.sub(r'\s+', ' ', og).strip()[:120]
            d = clean_desc(c["desc"], name)
            if not d or len(d) < 15:
                d = f"A WhatsApp group for {name}. Join to chat, share updates and connect with members."
            if len(d) > 240:
                d = d[:237].rsplit(" ", 1)[0] + "..."
            verified.append({"name": name or "WhatsApp Group",
                             "category": c["category"],
                             "country": "BR",
                             "description": d,
                             "invite": f"https://chat.whatsapp.com/{c['code']}"})
        elif s == "pending":
            pending.append({"name": c["name"], "category": c["category"], "country": "BR",
                            "description": clean_desc(c["desc"], c["name"])[:200],
                            "invite": f"https://chat.whatsapp.com/{c['code']}",
                            "reason": info})
        else:
            dead.append((c, info))

    last = raw[-1] if raw else {"idx": -1, "url": "", "lastmod": ""}
    nxt = entries[-1][1]  # index 3100 url from sitemap (recomputed below)
    summary = {
        "team": 11,
        "slice": "linkado sitemap 2700-3099",
        "sources": ["https://linkado.app/sitemap.xml (wave_20261110 copy; 19,731 grupo URLs, sitemap order = lastmod desc)"],
        "verified": len(verified),
        "pending": len(pending),
        "leads": 0,
        "dead": len(dead),
        "exclusions": exclusions,
        "resume": f"next index 3100, {nxt} (last mined: index {last['idx']}, {last['url']}, lastmod {last['lastmod']})",
        "notes": (f"Mined 400/400 grupo detail pages (indices 2700-3099). Fetch failures: {len(fetch_fail)}. "
                  f"Pages with no chat.whatsapp.com join link (Telegram-only/channel/removed): {n_nojoin}. "
                  f"Fresh candidates after dedupe vs {len(union)}-code union: {len(cands)}. "
                  f"Verified live via curl browser UA (HTTP 200 + non-empty og:title; empty og:title after 2 spaced retries = dead; transport failure = pending). "
                  f"All verified are Brazilian (country BR). No merge into groups.json, no generate.py, no deploy.")
    }
    # fix resume next URL: read index 3100 from sitemap
    import xml.etree.ElementTree as ET
    import re as _re
    txt = open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/linkado_sitemap.xml").read()
    locs = _re.findall(r"<loc>(.*?)</loc>", txt)
    mods = _re.findall(r"<lastmod>(.*?)</lastmod>", txt)
    grupo = [(l, m) for l, m in zip(locs, mods) if "/grupo/" in l]
    summary["resume"] = (f"next index 3100, {grupo[3100][0]}, lastmod {grupo[3100][1]} "
                         f"(last mined: index {last['idx']}, {last['url']}, lastmod {last['lastmod']})")
    json.dump(verified, open(f"{WD}/team11-linkado-2700.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(f"{WD}/team11-linkado-2700-pending.json", "w"), ensure_ascii=False, indent=1)
    json.dump([], open(f"{WD}/team11-linkado-2700-leads.json", "w"), ensure_ascii=False, indent=1)
    json.dump(summary, open(f"{WD}/team11-linkado-2700-summary.json", "w"), ensure_ascii=False, indent=1)
    print("VERIFIED:", len(verified), "PENDING:", len(pending), "DEAD:", len(dead),
          "EXCL:", len(exclusions), "NOJOIN:", n_nojoin, "FETCHFAIL:", len(fetch_fail), flush=True)

if __name__ == "__main__":
    main()
