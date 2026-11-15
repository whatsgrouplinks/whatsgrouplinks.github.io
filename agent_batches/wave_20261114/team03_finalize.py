#!/usr/bin/env python3
"""team03 finalize: screen live titles, categorize, build outputs."""
import json, re, unicodedata, html

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
W13 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
W10 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"

def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

PORN_RES = [r"\bporn", r"\bxxx\b", r"onlyfans", r"\bnovinh", r"putaria", r"vazament", r"vazad", r"\bnudes?\b",
            r"gostosa", r"safad", r"\bsexo\b", r"erotic", r"hentai", r"pelad", r"\bpack\b.*(vazad|nua|pelad|novinh|xxx|porn)",
            r"call\s*gratis", r"video\s*call.*18"]
BET_RES = [r"tigrinho", r"fortune", r"cassino", r"casino", r"slot", r"apost[ae](?!ila)", r"palpites?",
           r"\bsinais\b", r"\bsinal\b", r"\bbets?\b", r"bet365", r"betano", r"wjbet", r"aviator", r"\bmines\b", r"roleta",
           r"(win|wiin|pix|super|mega|sport)?bet\b", r"\btips\b", r"\bblaze\b", r"slo+ts",
           r"horario.*pagando|pagando.*horario",
           r"cambista", r"\bbancas?\b", r"plataformas?\s+pagantes?", r"pagantes?",
           r"recarga.*b[oô]nus", r"b[oô]nus.*recarga", r"jogo\s+do\s+bicho"]
MONEY_EMOJI = ["💵", "💸", "💰", "🤑", "🧧", "💲"]
SCAM_RES = [r"airdrop", r"bin[aá]ri", r"lucro\s+garantido", r"dinheiro\s+f[aá]cil",
            r"renda\s+extra.*(invest|cripto|trade|sinais)", r"dobrar.*dinheiro", r"multiplicar.*dinheiro"]
TIGER_CTX = ["fortune", "slot", "cassino", "casino", "bet", "sinais", "dinheiro", "ganhar", "plataforma", "aposta"]
SLOT_EMOJI = "\U0001F3B0"  # slot machine

LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"})

def _despace(n):
    """Collapse runs of single letters separated by spaces: 'G H O S T B E T' -> 'ghostbet'."""
    toks = n.split()
    out = []
    i = 0
    while i < len(toks):
        if len(toks[i]) == 1:
            j = i
            while j < len(toks) and len(toks[j]) == 1:
                j += 1
            if j - i >= 3:
                out.append("".join(toks[i:j]))
                i = j
                continue
        out.append(toks[i])
        i += 1
    return " ".join(out)

def screen(title, dircat=None):
    """Returns (decision, reason): decision in keep/drop/flag."""
    n = norm(title)
    nl = n.translate(LEET)  # leetspeak-normalized copy (S0RTEI0S -> sorteios)
    nd = _despace(n)  # spaced-letter copy (G H O S T B E T -> ghostbet)
    # personal info: phone number in title
    if len(re.sub(r"\D", "", title or "")) >= 10:
        return ("drop", "personal info: phone number in title")
    # restore: negated prohibition
    if re.search(r"(proibido|proibida|sem|nao|não)\b.{0,25}(porn|sexo|xxx|vazad|nudes?)", n):
        return ("keep", "negated-prohibition restore")
    # restore: sexta-feira (word-boundary regexes already avoid it, but be explicit)
    # restore: 18+ age gate alone is not porn
    # porn
    for pat in PORN_RES:
        if re.search(pat, n) or re.search(pat, nl) or re.search(pat, nd):
            return ("drop", f"porn/adult: {pat}")
    # casino/betting
    for pat in BET_RES:
        if re.search(pat, n) or re.search(pat, nl) or re.search(pat, nd):
            return ("drop", f"casino/betting: {pat}")
    # gol premiado = goal-betting promo
    if "gol" in n and "premiad" in n:
        return ("drop", "casino: gol premiado (goal betting)")
    if SLOT_EMOJI in (title or ""):
        return ("drop", "casino: slot-machine emoji")
    # tiger emoji + money emoji = Fortune Tiger promo
    if "🐯" in (title or "") and any(e in (title or "") for e in MONEY_EMOJI):
        return ("drop", "casino: tiger emoji + money emoji")
    # betting team/troop + money/tiger emoji
    if re.search(r"\b(tropa|equipe)\b", n) and ("🐯" in (title or "") or any(e in (title or "") for e in MONEY_EMOJI)):
        return ("drop", "casino: betting team + money/tiger emoji")
    # referral money scheme
    if re.search(r"ganh[ea]\s+dinheiro", n) and re.search(r"indicac|referral|indicando", n):
        return ("drop", "scam: earn-money-by-referral scheme")
    # fature (earn big) + money emoji
    if re.search(r"\bfature\b", n) and any(e in (title or "") for e in MONEY_EMOJI):
        return ("drop", "scam: fature money claim")
    # fenix metodos = betting methods
    if "fenix" in n and re.search(r"met[ao]d[ao]s?\b", n):
        return ("drop", "casino: fenix metodos (betting methods)")
    # 888 casino number + gambling context
    if "888" in n and re.search(r"jogo|slot|bet|cassino|tigre|plataforma|manga", n):
        return ("drop", "casino: 888 + gambling context")
    # 18+ marker on sticker/pack groups = adult stickers risk
    if "🔞" in (title or "") and re.search(r"figurinha|sticker|\bpack\b", n):
        return ("drop", "porn/adult: 18+ sticker/pack group")
    # plataforma + explicit betting context (pagando/ganhar/lucro/bonus/sinal/sorteio/divulgacao/horarios/money emoji)
    if "plataforma" in n:
        if any(w in n for w in ["pagando", "paga", "ganhar", "lucro", "bonus", "sinal", "sorteio", "divulgacao", "horario"]) \
           or any(w in nl for w in ["sorteio", "sinal"]) \
           or any(e in (title or "") for e in MONEY_EMOJI):
            return ("drop", "casino: plataforma + betting context")
    if re.search(r"\btigr[ee]s?\b", n):
        if any(w in n for w in TIGER_CTX):
            return ("drop", "casino: tiger + betting context")
        return ("flag", "tiger without betting context — review")
    for pat in SCAM_RES:
        if re.search(pat, n):
            return ("drop", f"scam: {pat}")
    if re.search(r"\bsinais\b", n):
        return ("drop", "betting-signal: sinais")
    if re.search(r"ganhar\s+dinheiro", n):
        return ("flag", "money-making claim — review")
    if n.strip() in ("jogos", "grupo jogos", "grupo de jogos", "grupo de jogo"):
        return ("flag", "jogos — ambiguous, possible gambling")
    if sum((title or "").count(e) for e in MONEY_EMOJI) >= 2:
        return ("flag", "heavy money emojis — review")
    if re.search(r"\bhack", n):
        return ("flag", "hacked-content — review")
    if "dinheiro" in norm(dircat or "") and "play" in n:
        return ("flag", "play group in Dinheiro category — possible casino platform")
    if re.search(r"plataforma", n):
        return ("flag", "plataforma — possible casino-platform promo, review")
    if re.search(r"premium", n) and re.search(r"economia|dinheiro|trade|investimento|lucro", n):
        return ("flag", "premium money group — review")
    if re.search(r"\b18\s*\+|\+18\b|maiores?\s+de\s+18", n):
        return ("keep", "18+ age gate only, non-porn")
    return ("keep", "")

DIRCAT_MAP = {
    "series": "Entertainment", "filmes": "Entertainment", "musica": "Entertainment",
    "música": "Entertainment", "anime": "Entertainment", "doramas": "Entertainment",
    "desenhos": "Entertainment", "tv": "Entertainment", "entretenimento": "Entertainment",
    "esportes": "Sports", "futebol": "Sports", "esporte": "Sports",
    "humor": "Funny", "memes": "Funny", "comedia": "Funny",
    "amizade": "Community & Social", "namoro": "Community & Social",
    "relacionamento": "Community & Social", "encontros": "Community & Social",
    "dinheiro": "Finance", "financas": "Finance", "finanças": "Finance",
    "investimentos": "Finance", "vendas": "Buy Sell", "compras": "Buy Sell",
    "compra": "Buy Sell", "classificados": "Buy Sell", "ofertas": "Buy Sell",
    "religiao": "Community & Social", "religião": "Community & Social",
    "islamico": "Islamic", "islâmico": "Islamic", "cristao": "Community & Social",
    "saude": "Health", "saúde": "Health", "fitness": "Health",
    "noticias": "News", "notícias": "News", "jornalismo": "News",
    "empregos": "Jobs", "vagas": "Jobs", "trabalho": "Jobs",
    "tecnologia": "Technology", "programacao": "Technology", "programação": "Technology",
    "jogos": "Gaming", "games": "Gaming", "free-fire": "Gaming", "pubg": "Gaming",
    "negocios": "Business", "negócios": "Business", "empreendedorismo": "Business",
    "culinaria": "Cooking", "culinária": "Cooking", "receitas": "Cooking",
    "criptomoedas": "Crypto", "cripto": "Crypto", "bitcoin": "Crypto",
    "poesia": "Poetry", "literatura": "Poetry", "livros": "Education",
    "imoveis": "Real Estate", "imóveis": "Real Estate",
    "viagem": "Travel", "turismo": "Travel",
    "estudos": "Education", "educacao": "Education", "educação": "Education",
    "cursos": "Education", "escola": "Education", "universidade": "Education",
    "bolsas": "Scholarship", "bolsa": "Scholarship",
    "freelance": "Freelance", "freelancer": "Freelance",
    "ganhar-dinheiro": "Earning", "renda": "Earning",
    "comunicacao": "Community & Social", "comunidade": "Community & Social",
    "geral": "Community & Social", "diversos": "Community & Social",
    "moda": "Community & Social", "beleza": "Health", "carros": "Community & Social",
    "motos": "Community & Social", "politica": "News", "política": "News",
}

def categorize(title, dircat):
    dc = norm(dircat or "").strip()
    t = norm(title)
    # strong title signals beat the directory category
    if re.search(r"\bloja\b", t):
        return "Buy Sell"
    if re.search(r"\bvendas?\b", t):
        return "Buy Sell"
    if re.search(r"contas\w*(flix|netflix|prime|disney|hbo|spotify)", t):
        return "Buy Sell"
    if dc in DIRCAT_MAP:
        return DIRCAT_MAP[dc]
    # keyword fallback from title
    t = norm(title)
    if re.search(r"vaga|emprego|trabalho", t):
        return "Jobs"
    if re.search(r"cripto|bitcoin|binance", t):
        return "Crypto"
    if re.search(r"futebol|esporte|palmeiras|flamengo|corinthians", t):
        return "Sports"
    if re.search(r"receita|culinaria|cozinha", t):
        return "Cooking"
    if re.search(r"venda|vende|comprar|bazar|brecho|loja", t):
        return "Buy Sell"
    if re.search(r"curso|estudo|faculdade|escola|ingles|inglês", t):
        return "Education"
    if re.search(r"musica|música|sertanejo|funk", t):
        return "Entertainment"
    if re.search(r"noticia|notícia", t):
        return "News"
    if re.search(r"islam|muçulman|allah|alcor", t):
        return "Islamic"
    if re.search(r"jogo|game|free fire|pubg", t):
        return "Gaming"
    if re.search(r"amizade|amigos|conversar|bate-papo", t):
        return "Community & Social"
    return "Community & Social"

def main():
    raw = json.load(open(f"{BASE}/team03-raw.json"))
    ver = {v["code"]: v for v in json.load(open(f"{BASE}/team03-verify.json"))}
    raw_by_code = {}
    for r in raw:
        if r.get("code"):
            raw_by_code.setdefault(r["code"], r)
    candidates, excluded, pending, flagged = [], [], [], []
    counts = {"raw": len(raw), "no_invite": 0, "dupes": 0, "live": 0, "dead": 0}
    union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
    seen = set()
    for r in raw:
        c = r.get("code")
        if not c:
            counts["no_invite"] += 1
            continue
        if c in union or c in seen:
            counts["dupes"] += 1
            continue
        seen.add(c)
        v = ver.get(c)
        if not v:
            pending.append({"code": c, "reason": "not yet verified"})
            continue
        if v["status"] == "pending":
            pending.append({"code": c, "reason": v.get("err") or "pending"})
            continue
        if v["status"] != "live":
            counts["dead"] += 1
            continue
        counts["live"] += 1
        title = (v.get("title") or "").strip() or (r.get("name") or "").strip()
        if not title:
            excluded.append({"code": c, "reason": "live but empty title"})
            continue
        if not re.sub(r"[^\w\u00C0-\u024F]+", "", title, flags=re.UNICODE):
            excluded.append({"code": c, "reason": "junk name (no alphanumeric characters)", "title": title})
            continue
        dec, reason = screen(title, r.get("dircat"))
        if dec == "drop":
            excluded.append({"code": c, "reason": reason, "title": title})
            continue
        cat = categorize(title, r.get("dircat"))
        item = {"name": title, "category": cat, "country": "BR",
                "description": f"Join {title}, an active WhatsApp group for {cat.lower()}.",
                "invite": f"https://chat.whatsapp.com/{c}"}
        if dec == "flag":
            flagged.append({**item, "flag": reason})
        candidates.append(item)
    json.dump(candidates, open(f"{BASE}/team03-candidates.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(f"{BASE}/team03-pending.json", "w"), ensure_ascii=False, indent=1)
    # leads: sitemap indices 11000+ (unmined) + any main-slice URLs never fetched
    sitemap = open(f"{W10}/linkado_sitemap.xml").read().splitlines()
    grupo = [re.search(r"https://linkado\.app/grupo/[0-9a-f]+", l).group(0)
             for l in sitemap if "/grupo/" in l and "https://linkado.app/grupo/" in l]
    fetched = {r["url"] for r in raw}
    leads = [{"kind": "url", "value": u,
              "note": "unmined linkado listing (sitemap index %d); banked as lead" % i}
             for i, u in enumerate(grupo) if i >= 11000 and u not in fetched]
    json.dump(leads, open(f"{BASE}/team03-leads.json", "w"), ensure_ascii=False, indent=1)
    summary = {
        "team": "team03",
        "slice": "linkado grupo sitemap indices 9000-10999 (2000 URLs) + 41 retry leads from team34 (8500-8999 no-invite/fetch-fail)",
        "sources": ["linkado.app grupo pages (sitemap copy wave_20261110/linkado_sitemap.xml)",
                    "team34 leads file wave_20261113/team34-leads.json"],
        "controls": {
            "live": "KrDwdK8EIkB6vgauHg5M7N -> og:title 'JAY - PHP & Python Full Stack Developer' (LIVE, as expected)",
            "fabricated": "ZzZzZzZzZzZzZzZzZzZzZz -> empty og:title (dead, as expected)"},
        "raw": counts["raw"],
        "verified": counts["live"],
        "dupes": counts["dupes"],
        "dead": counts["dead"],
        "no_invite": counts["no_invite"],
        "excluded_count": len(excluded),
        "excluded": excluded,
        "flagged_count": len(flagged),
        "flagged": flagged,
        "pending": len(pending),
        "leads": len(leads),
        "candidates": len(candidates),
        "resume_point": "sitemap index 11000 (next unmined); team03-verify.json holds all verification results",
        "note": "Screening on LIVE WhatsApp og:title with NFKD normalization + PT betting vocabulary + slot emoji; negated-prohibition restores kept; 18+ age gates on non-porn groups kept.",
    }
    json.dump(summary, open(f"{BASE}/team03-summary.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: summary[k] for k in
                      ("raw", "verified", "dupes", "dead", "no_invite", "excluded_count",
                       "flagged_count", "pending", "leads", "candidates")}, indent=1))

if __name__ == "__main__":
    main()
