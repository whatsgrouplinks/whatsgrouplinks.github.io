#!/usr/bin/env python3
"""team06 verify: curl-verify extracted invite codes via og:title rule, dedupe, screen."""
import json, re, sys, os, subprocess, html
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
SITE = "/home/hatch/workspace/whatsapp-groups-site"

def load_existing():
    with open(os.path.join(SITE, ".existing_codes.json")) as f:
        data = json.load(f)
    if isinstance(data, dict):
        return set(data.keys())
    return set(data)

def og_title(code):
    """Return (title_or_None, status) status in live/dead/transport."""
    url = f"https://chat.whatsapp.com/{code}"
    try:
        p = subprocess.run(["curl", "-s", "-L", "--max-time", "90", "-A", UA, url],
                           capture_output=True, timeout=100)
        if p.returncode != 0 or not p.stdout:
            return None, "transport"
        s = p.stdout.decode("utf-8", "ignore")
        m = re.search(r'<meta property="og:title" content="([^"]*)"', s)
        if not m:
            return None, "transport"  # no og tag at all = page didn't render / transport
        t = html.unescape(m.group(1)).strip()
        if not t:
            return None, "dead"
        if t.lower() in ("whatsapp group invite", "whatsapp group", "invite"):
            return None, "dead"
        return t, "live"
    except Exception:
        return None, "transport"

# --- screening ---
PORN = re.compile(r"(porn|xxx|sexo|sex |sexo |putaria|putaria|nudes|nude|onlyfans|er[oó]tic|18\+|\+18|adulto|hentai|pussy|dick|boobs|anal|orgasm|masturb|escort|prostitut|gostosa|gostoso|pelad|transa|fetiche|bdsm|cu ?\b|pau |rola|buceta|caralho|pornô|porno)", re.I)
CASINO = re.compile(r"(tigrinho|fortune tiger|plataforma[s]? pagante[s]?|sinais|wjb ?et|\bbet\b|bet ?365|aviator|crash|slots|caça-n[ií]quel|cassino|casino|aposta|apostas|palpite|betano|blaze|f12|pixbet|betfair|sportingbet|banca|milion[aá]rio|ganhar dinheiro f[aá]cil|airdrop|investimento.*(lucro|retorno|garantido)|cripto.*(lucro|dobrar|invest))", re.I)

def screen(name, title):
    text = f"{name} {title}"
    if PORN.search(text):
        return "porn/sexual content"
    if CASINO.search(text):
        return "casino/betting/casino-signal"
    return None

# category mapping from linkado title suffix / keywords
CATMAP = [
    ("Education", ["educa", "estudo", "escola", "curso", "aprender", "aula", "professor", "faculdade", "universidade", "concurso", "vestibular", "enem", "ingl", "matem", "redação"]),
    ("Jobs", ["emprego", "vaga", "trabalho", "renda", "freela", "contrata", "currículo", "oportunidade"]),
    ("Sports", ["futebol", "esporte", "sport", "palmeiras", "flamengo", "corinthians", "são paulo", "vasco", "copa", "nfl", "basquete", "volei", "f1", "formula"]),
    ("Funny", ["humor", "meme", "engraçado", "risada", "piada", "figurinha", "sticker"]),
    ("Islamic", ["islam", "muçulman", "allah", "alcorão", "mesquita"]),
    ("Health", ["saúde", "emagrec", "fitness", "academia", "dieta", "medicina", "nutri"]),
    ("News", ["notícia", "noticia", "jornal", "news", "urgente", "plantão"]),
    ("Finance", ["finança", "dinheiro", "invest", "bolsa", "pix", "renda extra", "ganhar dinheiro"]),
    ("Buy Sell", ["comprar", "venda", "oferta", "promoção", "desconto", "loja", "marketplace", "brechó"]),
    ("Technology", ["tecnologia", "programa", "dev", "python", "php", "javascript", "android", "iphone", "tech", "informática"]),
    ("Music", ["música", "musica", "cantor", "sertanejo", "funk", "rock", "mpb", "playlist"]),
    ("Movies", ["filme", "série", "cinema", "netflix", "doramas", "anime", "desenho"]),
    ("Cricket", ["cricket"]),
    ("Gaming", ["game", "gamer", "free fire", "fortnite", "minecraft", "roblox", "jogos", "ps5", "xbox", "gta"]),
    ("Girls", ["meninas", "garotas", "mulheres", "girls"]),
    ("Boys", ["meninos", "garotos", "rapazes", "boys"]),
    ("Motivation", ["motivação", "motivacao", "superação", "reflexão", "frases"]),
    ("Business", ["negócio", "empreendedor", "marketing", "vendas", "empresa"]),
    ("Poetry", ["poesia", "poema", "poeta"]),
    ("Cooking", ["receita", "culinária", "cozinha", "bolo", "doces"]),
    ("Crypto", ["cripto", "bitcoin", "crypto", "blockchain"]),
    ("Online Earning", ["ganhar dinheiro", "renda extra", "trabalhar em casa", "home office"]),
    ("Friendship", ["amizade", "amigos", "conhecer pessoas", "amizades"]),
    ("Community & Social", ["comunidade", "grupo de", "bate-papo", "conversa", "social"]),
]

def guess_category(text):
    t = text.lower()
    for cat, kws in CATMAP:
        if any(k in t for k in kws):
            return cat
    return "Community & Social"

def clean_name(title):
    # linkado titles look like "Grupo de WhatsApp NAME - Category - Links"
    name = title
    name = re.sub(r"^Grupo de WhatsApp\s+", "", name, flags=re.I)
    name = re.sub(r"\s*-\s*Links?\s*$", "", name, flags=re.I)
    # strip trailing " - <category>" suffix if present
    parts = name.rsplit(" - ", 1)
    if len(parts) == 2 and len(parts[1]) <= 30:
        name = parts[0]
    name = re.sub(r"\s+", " ", name).strip()
    return name[:120]

def main(page_files):
    existing = load_existing()
    print(f"existing codes: {len(existing)}", flush=True)
    # gather codes with metadata
    items = {}  # code -> {name, category, country, source_url, title}
    for pf in page_files:
        try:
            pages = json.load(open(pf))
        except Exception as e:
            print(f"skip {pf}: {e}", flush=True); continue
        for p in pages:
            for code in p.get("codes", []):
                if code in items:
                    continue
                name = clean_name(p.get("title", ""))
                items[code] = {"name": name, "title": p.get("title", ""),
                               "source_url": p.get("url", ""), "desc": p.get("desc", "")}
    print(f"unique codes extracted: {len(items)}", flush=True)
    fresh = {c: v for c, v in items.items() if c not in existing}
    dupes = len(items) - len(fresh)
    print(f"dupes vs existing: {dupes}; fresh to verify: {len(fresh)}", flush=True)

    codes = list(fresh.keys())
    results = {}
    t0 = __import__("time").time()
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, (code, (title, status)) in enumerate(zip(codes, ex.map(lambda c: og_title(c), codes))):
            results[code] = (title, status)
            if (i + 1) % 25 == 0:
                print(f"{i+1}/{len(codes)} verified, {sum(1 for v in results.values() if v[1]=='live')} live, {__import__('time').time()-t0:.0f}s", flush=True)
    live = {c: v for c, v in results.items() if v[1] == "live"}
    dead = sum(1 for v in results.values() if v[1] == "dead")
    transport = [c for c, v in results.items() if v[1] == "transport"]
    print(f"live={len(live)} dead={dead} transport={len(transport)}", flush=True)

    # retry transport once after a pause
    if transport:
        print("retrying transport failures after 45s...", flush=True)
        __import__("time").sleep(45)
        with ThreadPoolExecutor(max_workers=6) as ex:
            for code, (title, status) in zip(transport, ex.map(lambda c: og_title(c), transport)):
                results[code] = (title, status)
        live = {c: v for c, v in results.items() if v[1] == "live"}
        dead = sum(1 for v in results.values() if v[1] == "dead")
        transport = [c for c, v in results.items() if v[1] == "transport"]
        print(f"after retry: live={len(live)} dead={dead} transport={len(transport)}", flush=True)

    candidates, excluded, pending = [], [], []
    seen = set()
    for f in ("team06-candidates.json", "team06-pending.json"):
        p = os.path.join(WAVE, f)
        if os.path.exists(p):
            try:
                prev = json.load(open(p))
                if f.startswith("team06-candidates"):
                    candidates.extend(prev)
                    seen.update(c["invite"].split("/")[-1] for c in prev)
                else:
                    pending.extend(prev)
            except Exception:
                pass
    for code, (title, status) in results.items():
        if status != "live":
            if status == "transport":
                meta = fresh[code]
                pending.append({"name": clean_name(meta["title"]) or title or "WhatsApp Group",
                                "category": guess_category(meta["title"]),
                                "country": "", "description": "",
                                "invite": f"https://chat.whatsapp.com/{code}",
                                "reason": "transport failure after retry"})
            continue
        meta = fresh[code]
        raw_name = clean_name(meta["title"])
        # linkado truncates long titles with "..."; prefer live WhatsApp og:title then
        if (not raw_name) or raw_name.endswith("...") or raw_name.endswith("…"):
            name = re.sub(r"\s+", " ", title).strip()[:120]
        else:
            name = raw_name
        reason = screen(name, title)
        if reason:
            excluded.append({"code": code, "reason": reason})
            continue
        cat = guess_category(meta["title"] + " " + title)
        desc = f"Join {name}, an active WhatsApp group for {cat}. Connect with members, share updates and chat about {cat.lower()} topics."
        if code in seen:
            continue
        seen.add(code)
        candidates.append({"name": name, "category": cat, "country": "",
                           "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})
    json.dump(candidates, open(os.path.join(WAVE, "team06-candidates.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WAVE, "team06-pending.json"), "w"), ensure_ascii=False, indent=1)
    stats = {"raw": len(items), "verified": len(candidates), "dupes": dupes,
             "dead": dead, "excluded": excluded, "pending": len(pending), "leads": 0}
    json.dump(stats, open(os.path.join(WAVE, "team06-verify-stats.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(WAVE, "team06-runs.jsonl"), "a") as f:
        f.write(json.dumps(stats) + "\n")
    # accumulate exclusions persistently
    ex_path = os.path.join(WAVE, "team06-excluded.json")
    prev_ex = json.load(open(ex_path)) if os.path.exists(ex_path) else []
    prev_ex.extend(excluded)
    json.dump(prev_ex, open(ex_path, "w"), ensure_ascii=False, indent=1)
    print(f"CANDIDATES={len(candidates)} EXCLUDED={len(excluded)} PENDING={len(pending)}", flush=True)
    for e in excluded[:20]:
        print("excluded:", e, flush=True)

if __name__ == "__main__":
    main(sys.argv[1:])
