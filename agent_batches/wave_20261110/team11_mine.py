#!/usr/bin/env python3
"""TEAM 11 — linkado.app sitemap indices 0-499 (newest grupo pages)."""
import json, re, time, html, subprocess
from concurrent.futures import ThreadPoolExecutor

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
SITE = "/home/hatch/workspace/whatsapp-groups-site"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

CATMAP = {
    "amizade": "Community & Social", "amizades": "Community & Social",
    "entretenimento": "Entertainment", "diversão": "Entertainment",
    "empregos": "Jobs", "emprego": "Jobs", "vagas": "Jobs",
    "educação": "Education", "educacao": "Education", "estudos": "Education",
    "religião": "Community & Social", "religiao": "Community & Social",
    "islâmico": "Islamic", "islamico": "Islamic", "islã": "Islamic",
    "esportes": "Sports", "esporte": "Sports", "futebol": "Sports",
    "finanças": "Finance", "financas": "Finance", "investimentos": "Finance",
    "humor": "Funny", "memes": "Funny",
    "compra e venda": "Buy Sell", "compras": "Buy Sell", "vendas": "Buy Sell",
    "saúde": "Health", "saude": "Health",
    "notícias": "News", "noticias": "News",
    "jogos": "Gaming", "games": "Gaming", "jogo": "Gaming",
    "tecnologia": "Technology",
    "negócios": "Business", "negocios": "Business",
    "namoro": "Community & Social", "relacionamento": "Community & Social",
    "música": "Entertainment", "musica": "Entertainment", "filmes": "Entertainment",
    "séries": "Entertainment", "animes": "Entertainment",
    "família": "Community & Social", "familia": "Community & Social",
    "grupos": "Community & Social", "geral": "Community & Social",
    "cristão": "Community & Social", "cristao": "Community & Social",
    "evangélico": "Community & Social", "católico": "Community & Social",
    "política": "News", "politica": "News",
    "culinária": "Community & Social", "culinaria": "Community & Social",
    "viagens": "Community & Social", "viagem": "Community & Social",
    "carros": "Community & Social", "motos": "Community & Social",
    "apostas": "Finance", "cassino": "Entertainment",
    "livros": "Education", "leitura": "Education",
    "idiomas": "Education", "inglês": "Education",
    "moda": "Community & Social", "beleza": "Health",
    "animais": "Community & Social", "pets": "Community & Social",
    "ganhar dinheiro": "Finance", "renda extra": "Finance",
    "cristãos": "Community & Social",
}

SCAM = ["b-love", "blove", "forsage", "shey", "airdrop", "paypal loader",
        "bitfinex", "counterfeit currency", "crypto-doubling", "carding",
        "dinheiro fácil", "dinheiro facil", "dobrar", "lucro garantido",
        "investimento garantido", "ganhe dinheiro rápido", "ganhe dinheiro rapido",
        "multiplicar bitcoin", "multiplicar seu dinheiro", "falsificar",
        "clonar cartão", "clonar cartao", "roubar", "hackear whatsapp"]
ADULT = ["🔞", "🥵", "sexy", "hookup", "escort", "porn", "xxx", "18+",
         "putaria", "sexo explícito", "sexo explicito", "conteúdo adulto",
         "conteudo adulto", "nudes", "novinhas", "gostosas", "safada",
         "tesão", "tesao", "erótico", "erotico", "onlyfans", "pack de",
         "vazados", "vazadas", "amadores quentes", "sex chat", "sexo grátis",
         "sexo gratis", "acompanhantes", "garotas de programa"]

def fetch(url, timeout=60):
    # curl subprocess: urllib hung/timeouts on this host under concurrency; curl is reliable here
    try:
        r = subprocess.run(["curl", "-s", "-L", "-A", UA["User-Agent"],
                            "--max-time", str(timeout), "-w", "\n%{http_code}", url],
                           capture_output=True, text=True, timeout=timeout + 10)
        body, _, code = r.stdout.rpartition("\n")
        st = int(code) if code.strip().isdigit() else None
        if st is None or st == 0:
            return None, ""
        return st, body
    except Exception:
        return None, ""

def parse_page(html_text):
    m = re.search(r'<title>(.*?)</title>', html_text, re.S)
    title = html.unescape(m.group(1)).strip() if m else ""
    m2 = re.search(r'property="og:description"\s+content="([^"]*)"', html_text)
    desc = html.unescape(m2.group(1)).strip() if m2 else ""
    codes = re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})', html_text)
    # dedupe codes preserving order
    seen = set(); uniq = []
    for c in codes:
        if c not in seen:
            seen.add(c); uniq.append(c)
    return title, desc, uniq

def clean_name(title):
    name = re.sub(r'^Grupo de WhatsApp\s*', '', title, flags=re.I).strip()
    name = re.sub(r'\s*-\s*[^-]{1,40}$', '', name).strip()  # trailing " - Category"
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

def main():
    # --- dedupe union ---
    existing = set(json.load(open(f"{SITE}/.existing_codes.json")))
    groups = json.load(open(f"{SITE}/groups.json"))
    gcodes = set()
    for g in groups:
        inv = g.get("invite", "")
        mm = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', inv)
        if mm:
            gcodes.add(mm.group(1))
    union = existing | gcodes
    print(f"union codes: {len(union)} (existing {len(existing)} + groups {len(gcodes)})", flush=True)

    entries = []
    for line in open(f"{WD}/grupo_0_499.txt"):
        idx, url, lastmod = line.rstrip("\n").split("\t")
        entries.append((int(idx), url, lastmod))
    done = set()
    try:
        for line in open(f"{WD}/team11_mined.ckpt.jsonl"):
            done.add(json.loads(line)["idx"])
    except FileNotFoundError:
        pass
    all_entries = list(entries)
    if done:
        print(f"resuming: {len(done)} already mined", flush=True)
        entries = [e for e in entries if e[0] not in done]

    def mine(entry):
        idx, url, lastmod = entry
        time.sleep(0.1)
        st, h = fetch(url)
        if st is None or not h:
            time.sleep(5)
            st, h = fetch(url)
        if st is None or not h:
            return {"idx": idx, "url": url, "lastmod": lastmod, "error": "fetch-fail"}
        title, desc, codes = parse_page(h)
        return {"idx": idx, "url": url, "lastmod": lastmod, "title": title,
                "desc": desc, "codes": codes, "status": st}

    raw = []
    try:
        for line in open(f"{WD}/team11_mined.ckpt.jsonl"):
            raw.append(json.loads(line))
    except FileNotFoundError:
        pass
    ck = open(f"{WD}/team11_mined.ckpt.jsonl", "a")
    with ThreadPoolExecutor(max_workers=5) as ex:
        for r in ex.map(mine, entries):
            raw.append(r)
            ck.write(json.dumps(r, ensure_ascii=False) + "\n"); ck.flush()
            if len(raw) % 50 == 0:
                print(f"mined {len(raw)}/500", flush=True)
    json.dump(raw, open(f"{WD}/team11_raw_mined.json", "w"), ensure_ascii=False, indent=1)
    print(f"mined done: {len(raw)} pages", flush=True)

    fetch_fail = [r for r in raw if "error" in r]
    print(f"fetch failures: {len(fetch_fail)}", flush=True)

    # --- candidates: fresh codes only ---
    cands = []  # dicts
    seen_codes = set()
    exclusions = []
    for r in raw:
        if "error" in r:
            continue
        title, desc = r["title"], r["desc"]
        if not r["codes"]:
            continue
        name = clean_name(title)
        low = (title + " " + desc + " " + name).lower()
        for code in r["codes"]:
            if code in seen_codes:
                continue
            seen_codes.add(code)
            if code in union:
                continue
            if any(s in low for s in SCAM):
                exclusions.append({"code": code, "reason": "scam signals: " + title[:80]}); continue
            if any(s in low for s in ADULT):
                exclusions.append({"code": code, "reason": "adult-sexual signals: " + title[:80]}); continue
            cat, rawcat = cat_from_title(title)
            if cat is None:
                cat = "Community & Social"
            cands.append({"code": code, "name": name, "title": title, "desc": desc,
                          "category": cat, "rawcat": rawcat, "url": r["url"],
                          "idx": r["idx"], "lastmod": r["lastmod"]})
    print(f"fresh candidates (post-dedupe+screen): {len(cands)}", flush=True)
    json.dump({"cands": cands, "exclusions": exclusions, "fetch_fail": fetch_fail},
              open(f"{WD}/team11_candidates.json", "w"), ensure_ascii=False, indent=1)

    # --- verify each candidate ---
    def verify(c):
        time.sleep(0.55)
        url = f"https://chat.whatsapp.com/{c['code']}"
        for attempt in range(2):
            st, h = fetch(url, timeout=15)
            if st is None:
                if attempt == 0:
                    time.sleep(2)
                    continue
                return (c, "pending", "transport failure (no HTTP status)")
            if st == 200:
                m = re.search(r'property="og:title"\s+content="([^"]*)"', h or "")
                og = html.unescape(m.group(1)).strip() if m else ""
                if og:
                    return (c, "live", og)
                if attempt == 0:
                    time.sleep(2)
                    continue
                return (c, "dead", "HTTP 200 but empty og:title after 2 tries")
            return (c, "dead", f"HTTP {st}")
        return (c, "dead", "no og:title")

    results = []
    vck = open(f"{WD}/team11_verify.ckpt.jsonl", "w")
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(verify, cands):
            results.append(res)
            vck.write(json.dumps({"code": res[0]["code"], "status": res[1], "info": res[2]}, ensure_ascii=False) + "\n"); vck.flush()
            if len(results) % 25 == 0:
                print(f"verified {len(results)}/{len(cands)}", flush=True)
    json.dump([{"code": c["code"], "status": s, "info": i} for c, s, i in results],
              open(f"{WD}/team11_verify_results.json", "w"), ensure_ascii=False, indent=1)

    verified, pending, dead = [], [], []
    for c, s, info in results:
        if s == "live":
            low = (c["title"] + " " + info).lower()
            if any(a in low for a in ADULT):
                exclusions.append({"code": c["code"], "reason": "adult signals in WhatsApp og:title: " + info[:80]})
                dead.append((c, "adult og:title"))
                continue
            if any(a in low for a in SCAM):
                exclusions.append({"code": c["code"], "reason": "scam signals in WhatsApp og:title: " + info[:80]})
                dead.append((c, "scam og:title"))
                continue
            d = c["desc"]
            # clean description: strip "Grupo de WhatsApp X, na categoria Y." boilerplate
            d = re.sub(r'^Grupo de WhatsApp [^,]+, na categoria [^\.]+\.\s*', '', d, flags=re.I)
            d = re.sub(r'linkado\.app|Linkado', '', d, flags=re.I).strip()
            d = re.sub(r'\s+', ' ', d)
            if not d or len(d) < 15:
                d = f"A WhatsApp group for {c['name']}. Join to chat, share updates and connect with members."
            if len(d) > 240:
                d = d[:237].rsplit(" ", 1)[0] + "..."
            verified.append({"name": c["name"] or "WhatsApp Group",
                             "category": c["category"],
                             "country": "BR",
                             "description": d,
                             "invite": f"https://chat.whatsapp.com/{c['code']}"})
        elif s == "pending":
            pending.append({"name": c["name"], "category": c["category"], "country": "BR",
                            "description": c["desc"][:200],
                            "invite": f"https://chat.whatsapp.com/{c['code']}",
                            "reason": info})
        else:
            dead.append((c, info))

    leads = sorted(set(r["url"] for r in raw if "error" not in r))
    raw_sorted = sorted(raw, key=lambda r: r["idx"])
    last = raw_sorted[-1] if raw_sorted else {"idx": -1, "url": "", "lastmod": ""}
    summary = {
        "team": 11,
        "slice": "linkado sitemap 0-499",
        "sources": ["https://linkado.app/sitemap.xml"],
        "verified": len(verified),
        "pending": len(pending),
        "leads": 0,
        "dead": len(dead),
        "exclusions": exclusions,
        "resume": f"next index 500 / {all_entries[499][1]} / lastmod {all_entries[499][2]} (mined through index {last['idx']}, {last['url']}, {last['lastmod']})",
        "notes": (f"Mined 500 newest grupo pages from linkado sitemap (19,731 grupo URLs total; "
                  f"fetch failures: {len(fetch_fail)}). Fresh candidates after dedupe vs 108,365-code union: {len(cands)}. "
                  f"Live rate among fresh candidates: {len(verified)}/{len(cands)}.")
    }
    json.dump(verified, open(f"{WD}/team11-linkado-0-499.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(f"{WD}/team11-linkado-0-499-pending.json", "w"), ensure_ascii=False, indent=1)
    json.dump([], open(f"{WD}/team11-linkado-0-499-leads.json", "w"), ensure_ascii=False, indent=1)
    json.dump(summary, open(f"{WD}/team11-linkado-0-499-summary.json", "w"), ensure_ascii=False, indent=1)
    print("VERIFIED:", len(verified), "PENDING:", len(pending), "DEAD:", len(dead),
          "EXCL:", len(exclusions), flush=True)

if __name__ == "__main__":
    main()
