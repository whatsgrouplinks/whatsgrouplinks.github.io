#!/usr/bin/env python3
"""TEAM 10 wave 20261111 — build final outputs from candidates + verification progress.
Screening: crypto-airdrop scams, betting scams, hard porn/xxx (negated-prohibition
sentences stripped first), document/identity-fraud facilitation. Girls/friendship ALLOWED.
Writes team10-linkado-2300.json / -pending.json / -leads.json / -summary.json
"""
import json, os, re, html as htmlmod

BASE = "/home/hatch/workspace/whatsapp-groups-site"
WAVE = os.path.join(BASE, "agent_batches/wave_20261111")

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
    ("comprar", "Buy Sell"), ("venda", "Buy Sell"), ("vendo", "Buy Sell"),
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

# --- screening ---
# Remove negated-prohibition sentences first (a group saying "no porn" is not porn).
NEG_SENT = re.compile(
    r"[^.!?\n]*\b(proibido|proibida|proibidos|proibidas|sem|não|nao|never|not allowed|"
    r"prohibited|proibidas|banido|não permitido|nao permitido)\b[^.!?\n]*"
    r"\b(porn\w*|xxx|sexo|nudes?|putaria|conteúdo adulto|conteudo adulto|"
    r"vazados?|onlyfans)[^.!?\n]*[.!?\n]?", re.I)

SCAM_PATTERNS = [
    (re.compile(r"b[\s\-]?love", re.I), "crypto-airdrop scam (B-Love)"),
    (re.compile(r"forsage", re.I), "crypto-airdrop/pyramid scam (Forsage)"),
    (re.compile(r"sheyi", re.I), "crypto-airdrop scam (SHEYI)"),
    (re.compile(r"holiverse", re.I), "crypto-airdrop scam (HOLIVERSE)"),
    (re.compile(r"meta[\s\-]?whale", re.I), "crypto-airdrop scam (Meta Whale)"),
    (re.compile(r"tigrinho|fortune[\s\-]?tiger|jogo do tigre", re.I), "betting scam (Tigrinho/Fortune Tiger)"),
    (re.compile(r"aviator", re.I), "betting scam (Aviator)"),
    (re.compile(r"sinais?\s+de\s+aposta", re.I), "betting-tip scam"),
    (re.compile(r"aposta(s)?\s+garantida", re.I), "betting scam (guaranteed bet)"),
    (re.compile(r"lucro\s+garantido", re.I), "betting/earning scam (guaranteed profit)"),
    (re.compile(r"ganhe\s+dinheiro\s+apostando", re.I), "betting scam"),
    (re.compile(r"cnh\b.{0,40}(sem\s+exame|comprar|sem\s+prova)", re.I), "document fraud (selling CNH without exam)"),
    (re.compile(r"(comprar|vendo|venda).{0,40}carteira\s+de\s+(motorista|habilita)", re.I), "document fraud (selling driver licence)"),
    (re.compile(r"(conta\s+uber|conta\s+99).{0,60}(vendo|venda|verifica[cç][aã]o\s+facial)", re.I), "identity-fraud facilitation (selling Uber/99 accounts)"),
    (re.compile(r"certificado\s+m[ée]dico.{0,40}(vendo|venda|comprar)", re.I), "document fraud (selling medical certificates)"),
    (re.compile(r"\bcc\b.{0,40}(fake|falso|clonad)", re.I), "financial fraud (fake credit cards/banks)"),
    (re.compile(r"banc[oa]s?\s*fake", re.I), "financial fraud (fake banks)"),
    (re.compile(r"cart[ãa]o\s*(clonado|fake|falso)", re.I), "financial fraud (cloned/fake cards)"),
    (re.compile(r"\b(carding|fullz)\b", re.I), "financial fraud (carding)"),
    (re.compile(r"plataformas?\s+(pagantes?|pagando)", re.I), "betting scam (paying gambling platform)"),
    (re.compile(r"links?\s+pagantes?", re.I), "betting scam (paying links)"),
    (re.compile(r"melhor plataforma", re.I), "betting scam (gambling platform promo)"),
    (re.compile(r"\bcoopera[cç]", re.I), "betting scam (betting cooperation)"),
    (re.compile(r"\bmontante\b", re.I), "betting scam (stake/montante)"),
    (re.compile(r"deposit(ar|e|a)\s+\d", re.I), "betting scam (deposit-to-play platform)"),
    (re.compile(r"\b(cassino|apostas?)\b", re.I), "betting scam (casino/betting)"),
    (re.compile(r"[🎰]", re.I), "betting scam (slot-machine emoji)"),
]
# "bancas" (betting banks) only counts when paired with platforms/raffles/dynamics
BANCA_COMBO = re.compile(r"\bbancas?\b", re.I)
BANCA_CTX = re.compile(r"(plataforma|sorteio|din[âa]mica)", re.I)
PORN_PATTERNS = [
    (re.compile(r"\bxxx\b", re.I), "hard porn (xxx)"),
    (re.compile(r"porn[ôoó]?", re.I), "hard porn"),
    (re.compile(r"sexo\s+expl[íi]cito", re.I), "explicit sexual content"),
    (re.compile(r"conte[úu]do\s+adulto", re.I), "adult content"),
    (re.compile(r"\bputaria\b", re.I), "explicit sexual content"),
    (re.compile(r"\bnudes?\b", re.I), "nude content"),
    (re.compile(r"vazad[oa]s?\b.{0,20}(onlyfans|nudes|fotos)", re.I), "leaked nude content"),
    (re.compile(r"(onlyfans|privacy)\s+vazad", re.I), "leaked adult content"),
    (re.compile(r"\bsex\s+videos?\b|\bporn\s+videos?\b", re.I), "porn videos"),
]

def _leet(s):
    # light leetspeak normalization for fraud screening ("banc0s" -> "bancos")
    return (s or "").replace("0", "o").replace("1", "i")

def screen(name, og_title, desc=""):
    """Return exclusion reason or None. Screens banked name, live og:title AND description."""
    for text, label in ((name, "name"), (og_title, "og:title"), (desc, "description")):
        t = text or ""
        stripped = NEG_SENT.sub(" ", t)
        norm = _leet(stripped)
        for pat, reason in SCAM_PATTERNS:
            if pat.search(stripped) or pat.search(norm):
                return f"{reason} — in {label}"
        for pat, reason in PORN_PATTERNS:
            if pat.search(stripped):
                return f"{reason} — in {label}"
        if BANCA_COMBO.search(stripped) and BANCA_CTX.search(stripped):
            return f"betting scam (bancas + platforms/raffles) — in {label}"
    return None

DEALS_RE = re.compile(r"(oferta|achadinho|promo[cç][aã]o|cupom|desconto|shopee|mercado\s+livre|shein|compra\s+e\s+venda|vendo|loja|pre[cç]o|barato|garimpo|achados?)", re.I)
EARN_RE = re.compile(r"(renda\s+extra|ganhar\s+dinheiro|fazer\s+dinheiro|ganhar\s+grana|dinheiro\s+em\s+casa|make\s+money)", re.I)

def content_category(name, desc, base):
    """Content override: deals groups -> Buy Sell, earning pitches -> Online Earning."""
    t = f"{name or ''} {desc or ''}"
    if DEALS_RE.search(t):
        return "Buy Sell"
    if EARN_RE.search(t):
        return "Online Earning"
    return base

PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://\S+|www\.\S+")

def clean_desc(d, name, category):
    d = (d or "").strip()
    d = URL_RE.sub("", d)
    if PHONE_RE.search(d) or EMAIL_RE.search(d):
        d = ""
    # strip "Grupo de WhatsApp <anything incl. commas>, na categoria <cat>. " prefix
    d = re.sub(r"^grupo de whatsapp .{0,200}?na categoria [^.]{0,60}\.\s*", "", d, flags=re.I)
    d = re.sub(r"\s+", " ", d).strip(" .")
    if len(d) < 15:
        d = ""
    if d:
        # cap ~280 chars at a word boundary
        if len(d) > 280:
            d = d[:280].rsplit(" ", 1)[0]
        return d
    cat_l = category.lower()
    return f"A WhatsApp group for {cat_l} in Brazil. Members of '{name}' share updates, tips and discussion about {cat_l}."

def main():
    candidates = json.load(open(os.path.join(WAVE, "team10_candidates.json")))
    results = json.load(open(os.path.join(WAVE, "team10_verify_progress.json")))
    fresh = json.load(open(os.path.join(WAVE, "team10_fresh.json")))
    cand_by_code = {c["code"]: c for c in candidates if c.get("code")}

    verified, pending, exclusions = [], [], []
    dead = 0
    for c in fresh:
        code = c["code"]
        res = results.get(code)
        if res is None:
            pending.append({**base_rec(c), "reason": "not verified (run incomplete)"})
            continue
        if res["status"] == "pending":
            r = base_rec(c)
            r["reason"] = res.get("reason", "transport failure")
            pending.append(r)
        elif res["status"] == "dead":
            dead += 1
        elif res["status"] == "live":
            og = res.get("og", "")
            linkado_name = c.get("name") or og
            # H1/linkado name when og:title is truncated (strict prefix of listing name)
            name = og
            if linkado_name and og and linkado_name.lower().startswith(og.lower()) and len(linkado_name) > len(og):
                name = linkado_name
            if not name:
                name = linkado_name
            name = (name or "").strip()
            category = map_category(c.get("category_raw") or "")
            desc = clean_desc(c.get("description_raw") or "", name, category)
            reason = screen(name, og, desc)
            if reason:
                exclusions.append({"code": code, "reason": reason})
                continue
            category = content_category(name, desc, category)
            desc = clean_desc(c.get("description_raw") or "", name, category)
            verified.append({"name": name, "category": category, "country": "BR",
                             "description": desc,
                             "invite": f"https://chat.whatsapp.com/{code}"})
    # leads: detail pages never mined (fetch failed / truncated). Removed listings
    # (linkado "nao existe ou pode ter sido removido") are mined-and-gone, NOT leads.
    leads = []
    for c in candidates:
        if not c.get("name") and not c.get("code") and not c.get("removed"):
            leads.append(c["url"])
    # dedupe verified by code (paranoia) preserving order
    seen = set()
    v2 = []
    for v in verified:
        code = v["invite"].rsplit("/", 1)[-1]
        if code not in seen:
            seen.add(code)
            v2.append(v)
    verified = v2

    json.dump(verified, open(os.path.join(WAVE, "team10-linkado-2300.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WAVE, "team10-linkado-2300-pending.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(leads, open(os.path.join(WAVE, "team10-linkado-2300-leads.json"), "w"), ensure_ascii=False, indent=1)

    n_tg = sum(1 for c in candidates if not c.get("code") and c.get("has_telegram") and not c.get("has_channel"))
    n_chan = sum(1 for c in candidates if not c.get("code") and c.get("has_channel") and not c.get("has_telegram"))
    n_both = sum(1 for c in candidates if not c.get("code") and c.get("has_telegram") and c.get("has_channel"))
    n_nolink = sum(1 for c in candidates if not c.get("code") and not c.get("has_telegram") and not c.get("has_channel") and c.get("name"))
    n_removed = sum(1 for c in candidates if c.get("removed"))
    n_fail = sum(1 for c in candidates if not c.get("name") and not c.get("code") and not c.get("removed"))
    dup = sum(1 for c in candidates if c.get("code") and c["code"] not in {f["code"] for f in fresh})
    from collections import Counter
    cats = Counter(v["category"] for v in verified)
    last = candidates[-1]
    summary = {
        "team": 10,
        "slice": "linkado sitemap 2300-2699",
        "sources": ["https://linkado.app/sitemap.xml (agent_batches/wave_20261110/linkado_sitemap.xml; 19,731 grupo URLs, sitemap order = lastmod desc)"],
        "verified": len(verified),
        "pending": len(pending),
        "leads": len(leads),
        "dead": dead,
        "exclusions": exclusions,
        "resume": f"next index 2700, https://linkado.app/grupo/69baf82349dbc7627d73499f, lastmod 2026-03-19T00:04:44.051Z (last mined: index 2699, {last['url']}, lastmod {last['lastmod']})",
        "notes": (
            f"Mined 400/400 grupo detail pages (indices 2300-2699). Join links: "
            f"{sum(1 for c in candidates if c.get('code'))} chat.whatsapp.com, {n_tg} Telegram-only (no WhatsApp invite, not bankable), "
            f"{n_chan} whatsapp.com/channel (dropped, channel not group), {n_both} page with both Telegram + channel links (not bankable), "
            f"{n_nolink} pages with no join link, {n_removed} removed listings on linkado ('Grupo nao encontrado'), {n_fail} fetch failures. "
            f"Of WA codes, {dup} already in the union, leaving {len(fresh)} fresh records covering {len(results)} unique codes "
            f"(1 code, Kgsoce2gPPr12VfUtiPncp, listed on 2 detail pages). "
            f"Verification via curl with browser UA (HTTP 200 + non-empty og:title = live; empty og:title after spaced retry = dead; transport failure = pending): "
            f"{len(verified)} live banked, {dead} dead, {len(pending)} pending, {len(exclusions)} live exclusions. "
            f"Calibration re-confirmed this run: 3 known-live codes from wave 20261110 team10 (ENWcV0vArH0KdOd7vDaNTJ, CKT3322HYJWKoypMEIQyzz, KDZZjnv03ZuCCNAn1fe7Sh) "
            f"returned non-empty og:title with the live group name; a fabricated code returned empty og:title. "
            f"Names banked are the live WhatsApp group names from og:title (linkado H1 name used when og:title was a truncated prefix). "
            f"All verified are Brazilian (country BR); categories: {dict(cats)}. "
            f"No merge into groups.json, no generate.py, no deploy (per brief)."
        ),
    }
    json.dump(summary, open(os.path.join(WAVE, "team10-linkado-2300-summary.json"), "w"), ensure_ascii=False, indent=1)
    print(f"verified={len(verified)} pending={len(pending)} leads={len(leads)} dead={dead} exclusions={len(exclusions)}")
    print("categories:", dict(cats))

def base_rec(c):
    category = map_category(c.get("category_raw") or "")
    name = (c.get("name") or "").strip() or "WhatsApp group"
    return {"name": name, "category": category, "country": "BR",
            "description": clean_desc(c.get("description_raw") or "", name, category),
            "invite": f"https://chat.whatsapp.com/{c['code']}"}

if __name__ == "__main__":
    main()
