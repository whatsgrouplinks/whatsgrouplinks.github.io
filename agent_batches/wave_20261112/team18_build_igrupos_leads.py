#!/usr/bin/env python3
"""TEAM18 build igrupos leads from mined detail pages + screen + categorize."""
import json, re

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
recs = [json.loads(l) for l in open(f"{WAVE}/team18-igrupos-mined.jsonl")]
live = [r for r in recs if r.get("status") == 200]

DROP = [
    (re.compile(r"(?i)\b(porn|xxx|sexo|call.?girl|escort|hentai|brazzers|hookup|onlyfans|desi bhabhi|sexual home)\b"), "porn/sexual content"),
    (re.compile(r"(?i)\blemon\b"), "lemon = erotic roleplay content"),
    (re.compile(r"(?i)(airdrop|binary.?option|opciones binarias|venda de xit|apuestas deportivas|betting|sinais|trading.*(lucro|profit|ganancias)|ganhe dinheiro|dinheiro f[aá]cil)"), "scam/betting/trading-promo name"),
]
NEG = re.compile(r"(?i)(proibido|prohibido|sem|não pode|no porn|porn not allowed|prohibida)")

def screen(title, desc):
    text = f"{title} {desc}"
    for pat, reason in DROP:
        if pat.search(text) and not NEG.search(text):
            return reason
    return None

def category(title, desc, tags):
    t = f"{title} {desc} {' '.join(tags)}".lower()
    if any(k in t for k in ["cripto", "crypto", "bitcoin"]): return "Crypto"
    if any(k in t for k in ["amistad", "amigos", "conocer gente", "quedada", "quedadas", "salidas"]): return "Friendship"
    if any(k in t for k in ["futbol", "fútbol", "fórmula", "formula 1", "deporte", "moto", "motero", "salsa", "bachata", "cine"]): return "Sports" if any(k in t for k in ["futbol","fútbol","deporte","moto","motero"]) else "Entertainment"
    if any(k in t for k in ["gay", "lesbiana", "bisex", "lgbt", "trans"]): return "Community & Social"
    if any(k in t for k in ["rol", "roleplay", "dungeon", "anime", "fandom", "juego", "juegos", "gaming", "misterio", "terror"]): return "Gaming" if any(k in t for k in ["rol","roleplay","dungeon","juego","juegos","gaming"]) else "Entertainment"
    if any(k in t for k in ["negocio", "emprendimiento", "dinero", "inversion", "bolsa"]): return "Business"
    if any(k in t for k in ["estudio", "estudiantes", "clase", "universidad", "idioma"]): return "Education"
    if any(k in t for k in ["musica", "música", "cine", "pelicula", "series"]): return "Entertainment"
    if any(k in t for k in ["cristiano", "catolico", "iglesia", "biblia", "oracion"]): return "Community & Social"
    if any(k in t for k in ["cocina", "receta", "comida"]): return "Cooking"
    if any(k in t for k in ["salud", "fitness", "gym"]): return "Health"
    return "Community & Social"

leads, excluded = [], []
for r in sorted(live, key=lambda x: x["gid"]):
    title, desc = r.get("title", ""), r.get("description", "")
    drop = screen(title, desc)
    if drop:
        excluded.append({"gid": r["gid"], "url": r["url"], "title": title, "reason": drop})
        continue
    leads.append({
        "url": r["url"], "source": "igrupos.com", "kind": "detail",
        "gid": r["gid"], "name": title, "description": desc,
        "country": r.get("country", ""), "country_flag_unverified": True,
        "tags": r.get("tags", []), "category_guess": category(title, desc, r.get("tags", [])),
        "note": "Invite code NOT in static HTML (join button is JS/login-gated); browser leg must open the detail page and click through to capture chat.whatsapp.com code, then verify.",
    })

json.dump(leads, open(f"{WAVE}/team18-igrupos-leads-raw.json", "w"), ensure_ascii=False, indent=1)
json.dump(excluded, open(f"{WAVE}/team18-igrupos-excluded.json", "w"), ensure_ascii=False, indent=1)
print(f"leads={len(leads)} excluded={len(excluded)}")
for e in excluded:
    print("DROP", e["gid"], e["title"][:70], "|", e["reason"])
# overlap check vs yesterday team32 igrupos gids
old = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/team32-igrupos-geogated-leads.json"))
old_gids = {int(re.search(r"/grupo/(\d+)", l["url"]).group(1)) for l in old if "/grupo/" in l["url"] and l["source"] == "igrupos.com"}
new_gids = {l["gid"] for l in leads}
print("overlap with team32 igrupos gids:", sorted(new_gids & old_gids))
print("gid range new:", min(new_gids), max(new_gids), "| in-slice 526723-526885:", sum(1 for g in new_gids if 526723 <= g <= 526885), "| above 527086:", sum(1 for g in new_gids if g > 527086))
