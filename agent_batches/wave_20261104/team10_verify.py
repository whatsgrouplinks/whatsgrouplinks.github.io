#!/usr/bin/env python3
"""Team 10: verify candidate codes via chat.whatsapp.com og:title (keep-alive sessions).
Dedupe vs union, apply content filters, write verified array in exact schema."""
import json, re, html, threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104"

PORN = ["porn", "pornhub", "xxx", "nude", "sex video", "escort", "call girl", "fuck",
        "dick", "pussy", "boobs", "anal", "bokep"]
SCAM = ["satta", "fix game", "fix jodi", "kalyan matka", "hyip", "paypal receiver",
        "loader", "money mule", "double your money", "double paisa"]
MINOR = ["menor", "menores", "novinha", "novinhas", "<18", "menor de idade"]

EMOJI_BAD = ["\U0001F975", "\U0001F346", "\U0001F351", "\U0001F51E", "\U0001F4A6",
             "\U0001F445", "\U0001F444", "\U0001F48B"]

def bad(txt):
    t = (txt or "").lower()
    if any(k in t for k in PORN):
        return True
    if any(e in (txt or "") for e in EMOJI_BAD):
        return True
    return False

def scammy(txt):
    t = (txt or "").lower()
    return any(k in t for k in SCAM)

def minor_dating(txt):
    t = (txt or "").lower()
    return any(k in t for k in MINOR)

_thread = threading.local()
def get_session():
    if not hasattr(_thread, "s"):
        s = requests.Session()
        s.headers.update({"User-Agent": UA})
        _thread.s = s
    return _thread.s

def og_title(code):
    s = get_session()
    try:
        r = s.get("https://chat.whatsapp.com/" + code, timeout=60)
        if r.status_code == 429:
            return ("http429", None)
        if r.status_code != 200:
            return ("http" + str(r.status_code), None)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        if not m:
            return ("no-og", None)
        t = html.unescape(m.group(1)).strip()
        return ("ok", t if t else None)
    except Exception:
        return ("transport", None)

def clean_title(t, code_title):
    name = (t or code_title or "").strip()
    name = re.sub(r'^\s*Grupo de WhatsApp\s+', '', name, flags=re.I)
    name = re.sub(r'\s*-\s*Amizade\s*$', '', name, flags=re.I)
    name = name.strip()
    if not name or len(name) < 3:
        name = (code_title or t or "").strip()
    return name

def describe(name):
    tl = name.lower()
    bits = []
    if "amizade" in tl or "amigos" in tl:
        bits.append("make new friends and chat")
    if "namoro" in tl or "relacionamento" in tl:
        bits.append("meet new people")
    if "figurinha" in tl or "sticker" in tl:
        bits.append("share stickers and memes")
    if "futebol" in tl:
        bits.append("talk football")
    if not bits:
        bits.append("chat and make friends")
    return ("A Brazilian WhatsApp friendship group where members " + ", ".join(bits) +
            ". Join to connect, chat daily and grow your circle.")

def main():
    union = set(json.load(open(WAVE + "/dedupe_union.json")))
    cands = json.load(open(WAVE + "/team10-candidates.json"))
    print("Union: %d, candidates: %d" % (len(union), len(cands)), flush=True)

    seen = set()
    work = []
    for c in cands:
        code = c["code"]
        if not re.fullmatch(r'[A-Za-z0-9]{20,24}', code):
            continue
        if code in union or code in seen:
            continue
        seen.add(code)
        work.append(c)
    print("After dedupe: %d" % len(work), flush=True)

    verified, pending, leads = [], [], []
    porn_drops = scam_drops = dead = transport = 0
    rate_limited = False

    with ThreadPoolExecutor(max_workers=30) as ex:
        futs = {ex.submit(og_title, c["code"]): c for c in work}
        n = 0
        for f in as_completed(futs):
            c = futs[f]
            n += 1
            status, title = f.result()
            if status == "http429":
                rate_limited = True
                pending.append({"name": c.get("title") or "", "category": "Friendship",
                                "country": "BR", "description": "", "image": "",
                                "invite": "https://chat.whatsapp.com/" + c["code"],
                                "note": "rate-limited"})
                continue
            if status == "transport":
                transport += 1
                pending.append({"name": c.get("title") or "", "category": "Friendship",
                                "country": "BR", "description": "", "image": "",
                                "invite": "https://chat.whatsapp.com/" + c["code"],
                                "note": "transport failure"})
                continue
            if not title:
                dead += 1
                continue
            name = clean_title(title, c.get("title"))
            blob = "%s %s %s" % (name, title, c.get("desc", ""))
            if bad(blob):
                porn_drops += 1
                continue
            if scammy(blob):
                scam_drops += 1
                continue
            if minor_dating(blob):
                leads.append({"domain": "linkado.app",
                              "url": "https://linkado.app/grupo/" + c["gid"],
                              "why": "minors-targeted group excluded: " + name[:60]})
                continue
            verified.append({
                "name": name[:120],
                "category": "Friendship",
                "country": "BR",
                "description": describe(name),
                "invite": "https://chat.whatsapp.com/" + c["code"],
                "image": ""
            })
            if n % 500 == 0:
                print("  verified %d/%d -> %d ok" % (n, len(work), len(verified)), flush=True)

    json.dump(verified, open(WAVE + "/team10-linkado-amizade.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(WAVE + "/team10-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
    json.dump(leads, open(WAVE + "/team10-leads.json", "w"), ensure_ascii=False, indent=1)
    print("VERIFIED=%d PENDING=%d LEADS=%d PORN_DROPS=%d SCAM_DROPS=%d DEAD=%d TRANSPORT=%d RATE_LIMITED=%s"
          % (len(verified), len(pending), len(leads), porn_drops, scam_drops, dead, transport, rate_limited), flush=True)

if __name__ == "__main__":
    main()
