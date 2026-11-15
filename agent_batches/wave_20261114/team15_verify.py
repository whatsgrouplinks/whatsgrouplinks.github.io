#!/usr/bin/env python3
"""team15 wave_20261114: verify raw codes from team15-raw.jsonl, dedupe, screen, emit candidates."""
import json, re, time, html, os
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
prev = set(c["invite"].rsplit("/", 1)[-1] for c in
         json.load(open(os.path.join(PREV, "team15-candidates.json"))))

CATMAP = [
    (r"estudio|universidad|educaci|idioma|ingles|clases|aprender", "Education"),
    (r"trabajo|empleo|ofertas.*trabajo", "Jobs"),
    (r"deporte|futbol|fútbol|baloncesto|gimnasio|fitness|correr", "Sports"),
    (r"humor|memes|risas|chistes", "Funny"),
    (r"salud|bienestar|nutrici|yoga|pilates|meditaci", "Health"),
    (r"cocina|recetas|comida", "Cooking"),
    (r"tecnolog|programaci|desarrollo|informatic|ia\b|inteligencia", "Technology"),
    (r"juego|gaming|videojuegos|free fire|roblox", "Gaming"),
    (r"negocio|emprend|empresa|startup|marketing", "Business"),
    (r"noticia|actualidad", "News"),
    (r"cripto|bitcoin|trading", "Crypto"),
    (r"compra|venta|vendo|compro|mercado", "Buy Sell"),
    (r"viaje|turismo|senderismo|aventura", "Travel"),
    (r"islam|musulman|coran|mezquita", "Islamic"),
    (r"poes|poema|literatura|libros|lectura", "Poetry"),
    (r"becas|scholarship", "Scholarship"),
    (r"freelance|autonomo|autónomo", "Freelance"),
    (r"dinero|ganar|ingresos|finanzas|inversi", "Earning"),
    (r"amistad|planes|social|conocer|quedadas|erasmus|fiesta|música|musica|cine|series|anime", "Community & Social"),
]
DROP = re.compile(r"(?i)\b(porn|xxx|porno|sexo\s+expl|onlyfans|escort|putas|tigrinho|fortune\s*tiger|sinais|plataformas\s+pagantes|wjbet|cassino|casino|slots|apostas|apuestas|jogo\s+do\s+bicho|rifa|bolao|bolão|airdrop|binary|op[cç][oõ]es\s+bin|dinheiro\s+gr[aá]tis|free\s+money|ganhar\s+dinheiro\s+f[aá]cil)\b")
CLOSED = re.compile(r"(?i)closed group|moved to new group|grupo cerrado|grupo fechado")

def category_for(name, cats):
    hay = " ".join(cats or []) + " " + (name or "")
    for pat, cat in CATMAP:
        if re.search(pat, hay, re.I):
            return cat
    return "Community & Social"

def verify(session, code):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(3):
        try:
            r = session.get(url, timeout=60)
            if r.status_code == 429:
                return "pending", f"HTTP 429 attempt {attempt+1}"
            t = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', r.text)
            if not t:
                t = re.search(r'<meta[^>]*content="([^"]*)"[^>]*property="og:title"', r.text)
            title = html.unescape(t.group(1)).strip() if t else ""
            if title:
                return "live", title
            if attempt < 2:
                time.sleep(20)
        except requests.RequestException as e:
            if attempt < 2:
                time.sleep(20)
            else:
                return "pending", f"transport: {type(e).__name__}"
    return "dead", "empty og:title after 3 spaced attempts"

def main():
    raw = {}
    for line in open(os.path.join(WAVE, "team15-raw.jsonl")):
        r = json.loads(line)
        raw.setdefault(r["code"], r)
    print(f"raw unique codes: {len(raw)}", flush=True)
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"})
    # controls
    st, title = verify(s, "KrDwdK8EIkB6vgauHg5M7N")
    print(f"CONTROL live: {st} {title!r}", flush=True)
    assert st == "live" and title == "JAY - PHP & Python Full Stack Developer", "live control failed"
    st, title = verify(s, "ZzZzZzZzZzZzZzZzZzZzZzZz")
    print(f"CONTROL fabricated: {st} {title!r}", flush=True)
    assert st == "dead", "fabricated control failed"

    candidates, pending, excluded = [], [], []
    counts = {"dupes": 0, "dead": 0}
    for code, rec in raw.items():
        if code in union or code in prev:
            counts["dupes"] += 1
            continue
        st, info = verify(s, code)
        if st == "pending":
            pending.append({"code": code, "reason": info, "name": rec.get("name", "")})
            continue
        if st == "dead":
            counts["dead"] += 1
            continue
        title = info
        if CLOSED.search(title):
            excluded.append({"code": code, "reason": f"live og:title {title!r} - group closed/moved"})
            continue
        if DROP.search(title) or DROP.search(rec.get("name", "")):
            excluded.append({"code": code, "reason": f"live og:title {title!r} - banned content (porn/casino/betting/scam pattern)"})
            continue
        name = title
        cat = category_for(name, rec.get("cats", []))
        cat_low = cat.lower()
        desc = (f"Join {name}, an active WhatsApp group for {cat_low}. "
                f"Connect with members, share updates and chat in this {cat_low} group on WhatsApp.")
        candidates.append({"name": name, "category": cat, "country": "ES",
                           "description": desc,
                           "invite": f"https://chat.whatsapp.com/{code}"})
        print(f"OK {code} {name!r} [{cat}]", flush=True)
        time.sleep(2)
    json.dump(candidates, open(os.path.join(WAVE, "team15-candidates.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WAVE, "team15-pending.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(excluded, open(os.path.join(WAVE, "team15-excluded.json"), "w"), ensure_ascii=False, indent=1)
    print(f"RESULT raw={len(raw)} dupes={counts['dupes']} dead={counts['dead']} "
          f"candidates={len(candidates)} pending={len(pending)} excluded={len(excluded)}", flush=True)

if __name__ == "__main__":
    main()
