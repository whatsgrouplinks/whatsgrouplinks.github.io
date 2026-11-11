#!/usr/bin/env python3
"""TEAM 05 — build output files from checkpoints (idempotent, safe to re-run).
Reads team05-mine-checkpoint.jsonl + team05-verify-checkpoint.jsonl (+ existing codes),
applies content screening + PT->canonical category mapping, writes:
  team05-leads-slice5.json (verified), team05-leads-slice5-pending.json,
  team05-leads-slice5-leads.json, team05-leads-slice5-summary.json
"""
import json, re, os, html
from collections import Counter

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
LEADS = os.path.join(WAVE, "leads_slice5.json")
EXISTING = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
MINE_CKPT = os.path.join(WAVE, "team05-mine-checkpoint.jsonl")
VERIFY_CKPT = os.path.join(WAVE, "team05-verify-checkpoint.jsonl")

CAT_MAP = {
    "amizade": "Friendship", "amigos": "Friendship", "encontros": "Friendship",
    "namoro": "Friendship", "relacionamento": "Friendship",
    "esportes": "Sports", "futebol": "Sports", "esporte": "Sports",
    "games": "Gaming", "jogos": "Gaming", "game": "Gaming",
    "entretenimento": "Entertainment", "filmes": "Entertainment",
    "música": "Entertainment", "musica": "Entertainment", "séries": "Entertainment",
    "series": "Entertainment", "animes": "Entertainment", "desenhos": "Entertainment",
    "educação": "Education", "educacao": "Education", "estudos": "Education",
    "estudo": "Education", "escola": "Education", "cursos": "Education",
    "emprego": "Jobs", "empregos": "Jobs", "trabalho": "Jobs", "vagas": "Jobs",
    "notícias": "News", "noticias": "News", "jornalismo": "News",
    "tecnologia": "Technology", "tech": "Technology",
    "saúde": "Health", "saude": "Health", "fitness": "Health", "beleza": "Health",
    "negócios": "Business", "negocios": "Business", "empreendedorismo": "Business",
    "culinária": "Cooking", "culinaria": "Cooking", "receitas": "Cooking",
    "poesia": "Poetry", "frases": "Poetry", "poemas": "Poetry", "literatura": "Poetry",
    "viagem": "Travel", "viagens": "Travel", "turismo": "Travel",
    "bolsa de estudos": "Scholarship", "bolsas": "Scholarship",
    "bolsa": "Scholarship", "scholarship": "Scholarship",
    "freelance": "Freelance", "freelancer": "Freelance",
    "imóveis": "Real Estate", "imoveis": "Real Estate",
    "compra e venda": "Buy Sell", "comprar e venda": "Buy Sell", "vendas": "Buy Sell", "venda": "Buy Sell",
    "finanças": "Finance", "financas": "Finance", "investimentos": "Finance",
    "humor": "Funny", "memes": "Funny", "engraçado": "Funny",
    "islã": "Islamic", "islamico": "Islamic", "islâmico": "Islamic", "islam": "Islamic",
    "ganhar dinheiro": "Online Earning", "dinheiro": "Online Earning",
    "renda extra": "Online Earning", "renda": "Online Earning",
    "criptomoedas": "Crypto", "cripto": "Crypto", "bitcoin": "Crypto",
    "links": "Community & Social", "comunidade": "Community & Social",
    "geral": "Community & Social", "outros": "Community & Social",
    "família": "Community & Social", "familia": "Community & Social",
    "animais": "Community & Social", "carros": "Community & Social",
    "religião": "Community & Social", "religiao": "Community & Social",
    "política": "Community & Social", "politica": "Community & Social",
    "moda": "Community & Social", "motos": "Community & Social",
    "música e filmes": "Entertainment", "cinema": "Entertainment",
}

def map_category(cat_pt):
    if not cat_pt:
        return "Community & Social", True
    key = cat_pt.strip().lower()
    if key in CAT_MAP:
        return CAT_MAP[key], False
    # try contains-match for compound PT labels
    for k, v in CAT_MAP.items():
        if k in key:
            return v, False
    return "Community & Social", True

# --- content screening ---
PORN_TERMS = ["xxx", "porn", "putaria", "vazad", "nude", "onlyfans", "xvideos",
              "redtube", "s3x0", "sexo"]
BET_TERMS = [r"slot", r"cassino", r"casino", r"aposta",
             r"\bbet\b", r"bet365", r"tigrinho", r"fortune tiger", r"jogo do tigre",
             r"aviator", r"roleta", r"🎰"]
CRYPTO_SCAM = ["b-love", "blove", "forsage", "sheyi", "holiverse",
               "meta-whale", "metawhale", "airdrop"]
MONEY_WORDS = ["pagand", "ganhe", "ganhar", "dinheiro", "saque", "lucro",
               "bônus", "bonus", "depósito", "deposito", "multiplicar"]

def strip_negated_prohibition(text):
    """Remove sentences that prohibit porn (a group saying 'no porn' is not porn)."""
    sents = re.split(r"(?<=[.!?\n])\s+", text)
    kept = []
    for s in sents:
        low = s.lower()
        if "proibid" in low:
            continue
        if re.search(r"\b(não|nao|no|sem)\b", low) and any(t in low for t in PORN_TERMS):
            continue
        kept.append(s)
    return " ".join(kept)

def screen(text, og_title=""):
    """Returns exclusion reason or None."""
    blob = f"{text} {og_title}".lower()
    for t in CRYPTO_SCAM:
        if t in blob:
            return f"crypto-airdrop scam term: {t}"
    for pat in BET_TERMS:
        if re.search(pat, blob):
            return f"betting term: {pat}"
    if "plataforma" in blob and any(w in blob for w in MONEY_WORDS):
        return "betting: plataforma + money words"
    if "🎰" in blob:
        return "betting: slot-machine emoji"
    clean = strip_negated_prohibition(blob)
    for t in PORN_TERMS:
        if t in clean:
            return f"hard porn/xxx term: {t}"
    return None

PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://\S+|www\.\S+")

def clean_text(t):
    t = html.unescape(t or "")
    t = URL_RE.sub("", t)
    t = EMAIL_RE.sub("", t)
    t = PHONE_RE.sub("", t)
    t = re.sub(r"\s+", " ", t).strip(" .-,;:|")
    return t.strip()

def main():
    existing = set(json.load(open(EXISTING)))
    all_leads = json.load(open(LEADS))
    mined, verify = {}, {}
    mined_urls, failed_urls, no_invite_urls = set(), [], []
    unknown_cats = Counter()
    if os.path.exists(MINE_CKPT):
        for line in open(MINE_CKPT):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            mined_urls.add(rec["url"])
            if rec.get("status") == "ok":
                for c in rec.get("codes", []):
                    if c not in mined:
                        mined[c] = rec
                if not rec.get("codes"):
                    no_invite_urls.append(rec["url"])
            elif rec.get("status") == "fetch-failed":
                failed_urls.append(rec["url"])
    if os.path.exists(VERIFY_CKPT):
        for line in open(VERIFY_CKPT):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            verify[rec["code"]] = rec

    unmined_urls = [u for u in all_leads if u not in mined_urls]
    leads_out = sorted(set(failed_urls) | set(unmined_urls))

    verified, pending, exclusions = [], [], []
    dead = 0
    dupes_existing = 0
    for code, rec in mined.items():
        if code in existing:
            dupes_existing += 1
            continue
        v = verify.get(code)
        name = clean_text(rec.get("name", ""))
        # Re-split title at the LAST " - ": group names may contain " - "
        # (early checkpoint rows were parsed at the first " - "). Recombining
        # name + " - " + cat_pt reproduces the title suffix; rsplit is idempotent
        # for rows that were already parsed correctly.
        cat_pt_raw = (rec.get("cat_pt") or "").strip()
        if cat_pt_raw and " - " in (name + " - " + cat_pt_raw):
            full = name + " - " + cat_pt_raw
            name, cat_pt_raw = full.rsplit(" - ", 1)
            name, cat_pt_raw = name.strip(), cat_pt_raw.strip()
        desc = clean_text(rec.get("desc", ""))
        cat, unknown = map_category(cat_pt_raw)
        if unknown and cat_pt_raw:
            unknown_cats[cat_pt_raw] += 1
        if not name:
            name = f"WhatsApp Group {code[:8]}"
        if not desc or len(desc) < 5:
            # listing desc was just its own invite link / a fragment
            desc = f"WhatsApp group {name} ({cat})."
        if len(desc) > 300:
            desc = desc[:297].rstrip() + "..."
        country = "BR" if re.search(r"brasil|brazil|brasileir|\U0001F1E7\U0001F1F7",
                                    f"{name} {desc}", re.I) else ""
        og = v.get("og_title", "") if v else ""
        reason = screen(f"{name} {desc}", og)
        if reason:
            exclusions.append({"code": code, "reason": reason})
            continue
        if v is None:
            pending.append({"name": name, "category": cat, "country": country,
                            "description": desc,
                            "invite": f"https://chat.whatsapp.com/{code}",
                            "reason": "not yet verified"})
        elif v["status"] == "live":
            verified.append({"name": name, "category": cat, "country": country,
                             "description": desc,
                             "invite": f"https://chat.whatsapp.com/{code}"})
        elif v["status"] == "pending":
            pending.append({"name": name, "category": cat, "country": country,
                            "description": desc,
                            "invite": f"https://chat.whatsapp.com/{code}",
                            "reason": v.get("reason", "transport failure")})
        else:
            dead += 1

    verified.sort(key=lambda x: x["invite"])
    pending.sort(key=lambda x: x["invite"])
    summary = {
        "team": "team05",
        "slice": "leads_slice5",
        "sources": ["linkado.app listing pages (all 3603 URLs in leads_slice5.json)"],
        "verified": len(verified),
        "pending": len(pending),
        "leads": len(leads_out),
        "dead": dead,
        "exclusions": exclusions,
        "resume": {
            "mined_urls": len(mined_urls),
            "unmined_urls": len(unmined_urls),
            "mine_checkpoint": "team05-mine-checkpoint.jsonl",
            "verify_checkpoint": "team05-verify-checkpoint.jsonl",
            "candidate_codes_mined": len(mined),
            "dupes_vs_existing_codes": dupes_existing,
            "no_invite_listings": len(no_invite_urls),
            "fetch_failed_listings": len(failed_urls),
            "next_step": ("Re-run team05_pipeline.py (it resumes from checkpoints: "
                          "mine then verify), then team05_build.py to rebuild outputs."),
        },
        "notes": [
            f"Slice total: {len(all_leads)} linkado.app listing URLs.",
            f"Unknown PT categories mapped to Community & Social: {dict(unknown_cats)}",
            "Live rule applied: HTTP 200 + non-empty og:title after 1 spaced retry; empty og:title = dead.",
            "404/410 listings counted as dead, not re-led; transport/5xx/429 failures + unmined URLs are in the leads file for the next wave.",
            "Country 'BR' set only when name/desc mentions Brasil/Brazil/Brasileiro or the Brazil flag; otherwise ''.",
            "Girls/friendship groups kept; only hard porn/xxx, named crypto-airdrop scams and betting/slot groups excluded. Negated-prohibition sentences ('proibido pornografia') stripped before the porn screen.",
            "Some linkado titles are truncated mid-word with '...' by linkado itself (stored as shown); descriptions were URL-stripped and refilled from name/category when shorter than 5 chars.",
            "Verify transport failures (18 codes) are in the pending file with reason 'transport failure after retries' — retry them next wave; do not treat as dead.",
        ],
    }
    with open(os.path.join(WAVE, "team05-leads-slice5.json"), "w") as f:
        json.dump(verified, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WAVE, "team05-leads-slice5-pending.json"), "w") as f:
        json.dump(pending, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WAVE, "team05-leads-slice5-leads.json"), "w") as f:
        json.dump(leads_out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WAVE, "team05-leads-slice5-summary.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: summary[k] for k in ("verified", "pending", "leads", "dead")}, indent=1))
    print("exclusions:", len(exclusions), "dupes_existing:", dupes_existing,
          "mined_urls:", len(mined_urls), "unmined:", len(unmined_urls))

if __name__ == "__main__":
    main()
