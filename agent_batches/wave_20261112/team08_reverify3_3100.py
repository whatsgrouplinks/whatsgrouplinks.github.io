#!/usr/bin/env python3
"""TEAM 08 wave 20261112 — VERIFY PASS 3 (flakiness repair).
Spot-checks after pass 2 showed chat.whatsapp.com serves og:title
intermittently: 3 codes dead in pass 2 showed real og:titles minutes later,
and one request hit a 90s ReadTimeout. Pass 3 re-checks all 255 pass-2 dead
codes with the corrected og:title-only rule (2 spaced tries each) and
re-confirms the 21 kept codes. Any code live in pass 3 is banked."""
import json, re, time, html, threading
from concurrent.futures import ThreadPoolExecutor
import requests

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

data = json.load(open(f"{WD}/team08_candidates3100.json"))
cands = {c["code"]: c for c in data["cands"]}
exclusions, leads = data["exclusions"], data["leads"]
v2 = {json.loads(l)["code"]: json.loads(l) for l in open(f"{WD}/team08_verify3100_v2.ckpt.jsonl")}
dead_codes = [code for code, v in v2.items() if v["status"] == "dead"]
kept_codes = [code for code, v in v2.items() if v["status"] == "live"]
print(f"pass3: re-check {len(dead_codes)} dead + reconfirm {len(kept_codes)} kept", flush=True)

tls = threading.local()
def get_session():
    if not hasattr(tls, "s"):
        s = requests.Session(); s.headers.update({"User-Agent": UA}); tls.s = s
    return tls.s

def verify(code):
    url = f"https://chat.whatsapp.com/{code}"
    last_err = None
    for attempt in range(2):
        try:
            r = get_session().get(url, timeout=90)
        except Exception as e:
            last_err = f"transport failure ({type(e).__name__})"
            if attempt == 0:
                time.sleep(3); continue
            return (code, "pending", last_err)
        if r.status_code == 200:
            m = re.search(r'property="og:title"\s+content="([^"]*)"', r.text or "")
            og = html.unescape(m.group(1)).strip() if m else ""
            if og and og.lower() != "whatsapp group invite":
                return (code, "live", og)
            if attempt == 0:
                time.sleep(3); continue
            return (code, "dead", "HTTP 200 but empty/generic og:title after 2 spaced tries")
        return (code, "dead", f"HTTP {r.status_code}")
    return (code, "pending", last_err or "transport failure")

ckpt_path = f"{WD}/team08_verify3100_v3.ckpt.jsonl"
done = {}
try:
    for line in open(ckpt_path):
        r = json.loads(line); done[r["code"]] = r
except FileNotFoundError:
    pass
todo = [c for c in dead_codes + kept_codes if c not in done]
print(f"resume: {len(done)} done, {len(todo)} to check", flush=True)
results = [(code, done[code]["status"], done[code]["info"]) for code in done]
ck = open(ckpt_path, "a")
with ThreadPoolExecutor(max_workers=4) as ex:
    for res in ex.map(verify, todo):
        results.append(res)
        ck.write(json.dumps({"code": res[0], "status": res[1], "info": res[2]}, ensure_ascii=False) + "\n"); ck.flush()
        if len(results) % 25 == 0:
            print(f"checked {len(results)}/{len(dead_codes)+len(kept_codes)}", flush=True)
ck.close()

# Merge: live if live in v2-kept reconfirm OR live in pass 3
v3 = {code: (s, i) for code, s, i in results}
final_live, final_pending, final_dead = {}, [], []
for code, c in cands.items():
    s3, i3 = v3.get(code, ("missing", ""))
    if code in kept_codes:
        if s3 == "live":
            final_live[code] = i3
        elif s3 == "pending":
            final_pending.append((c, i3))
        else:
            # kept in v2 but dead in pass 3 reconfirm: flaky — keep as pending, do not bank, do not call dead
            final_pending.append((c, "live in pass 2, dead in pass 3 reconfirm (flaky og:title) — needs later recheck"))
    else:
        if s3 == "live":
            final_live[code] = i3
        elif s3 == "pending":
            final_pending.append((c, i3))
        else:
            final_dead.append((c, i3))

SCAM = ["b-love", "blove", "forsage", "shey", "holiverse", "meta-whale",
        "meta whale", "airdrop", "paypal loader", "bitfinex",
        "counterfeit currency", "crypto-doubling", "carding",
        "dinheiro fácil", "dinheiro facil", "dobrar seu dinheiro",
        "lucro garantido", "investimento garantido", "ganhe dinheiro rápido",
        "ganhe dinheiro rapido", "multiplicar bitcoin", "multiplicar seu dinheiro",
        "falsificar", "clonar cartão", "clonar cartao", "roubar", "hackear whatsapp",
        "sinais vip", "banca garantida", "aposta garantida", "ganhar na loteria",
        "opções binárias", "opcoes binarias", "opção binária", "binary option",
        "venda de xit", "venda de hack", "hack pago", "lucro diário garantido",
        "lucro diario garantido", "ganhos diários garantidos", "robô de apostas",
        "robo de apostas", "apostas esportivas vip", "grupo de apostas",
        "ai trading", "trading com ia", "lucros diários", "lucros diarios"]
ADULT = ["porn", "xxx", "hentai", "brazzers", "desi bhabhi", "sexual home",
         "sexo explícito", "sexo explicito", "putaria", "conteúdo adulto",
         "conteudo adulto", "nudes", "novinhas", "gostosas", "safada", "tesão",
         "tesao", "erótico", "erotico", "onlyfans", "pack de", "vazados",
         "vazadas", "amadores quentes", "sex chat", "acompanhantes",
         "garotas de programa", "sexo grátis", "sexo gratis", "xereca",
         "boquete", "siririca", "call girl", "escort", "hookup", "18+ sexual",
         "figurinhas 18", "stickers 18", "sexo no grupo"]
NEG = ["proibido", "proibida", "proibidos", "proibidas", "sem ", "não ", "nao ",
       "nunca", "zero ", "nenhum", "nenhuma"]
def strip_negated(text):
    parts = re.split(r'(?<=[.!;])\s+', text)
    return " ".join(p for p in parts
                    if not (any(n in p.lower() for n in NEG) and any(a in p.lower() for a in ADULT)))
def has_adult(t): return any(a in strip_negated(t).lower() for a in ADULT)
def has_scam(t): return any(s in t.lower() for s in SCAM)
def clean_desc(d, name):
    d = re.sub(r'^Grupo de WhatsApp [^,]+, na categoria [^\.]+\.\s*', '', d, flags=re.I)
    d = re.sub(r'linkado\.app|Linkado', '', d, flags=re.I)
    d = re.sub(r'https?://\S+|www\.\S+', '', d)
    d = re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+', '', d)
    d = re.sub(r'\+?\d[\d\s().-]{7,}\d', '', d)
    d = re.sub(r'\s+', ' ', d).strip()
    return d

verified, pending, dead = [], [], []
for code, og in final_live.items():
    c = cands[code]
    low = (c["title"] + " " + og).lower()
    if has_adult(low):
        exclusions.append({"code": code, "reason": "adult signals in WhatsApp og:title: " + og[:100]})
        dead.append((c, "adult og:title")); continue
    if has_scam(low):
        exclusions.append({"code": code, "reason": "scam signals in WhatsApp og:title: " + og[:100]})
        dead.append((c, "scam og:title")); continue
    if og.endswith("...") or og.endswith("…") or "�" in og or len(og) < 3:
        name = c["name"]
    else:
        name = re.sub(r'\s+', ' ', og).strip()[:120]
    if not name:
        name = c["name"] or "WhatsApp Group"
    d = clean_desc(c["desc"], name)
    if not d or len(d) < 15:
        d = f"Join {name} to chat, share updates and connect with members."
    else:
        d = f"Join {name}, {d}"
    if len(d) > 240:
        d = d[:237].rsplit(" ", 1)[0] + "..."
    verified.append({"name": name, "category": c["category"], "country": "BR",
                     "description": d, "invite": f"https://chat.whatsapp.com/{code}"})
for c, info in final_pending:
    pending.append({"name": c["name"], "category": c["category"], "country": "BR",
                    "description": (f"Join {c['name']}, " + clean_desc(c["desc"], c["name"]))[:240],
                    "invite": f"https://chat.whatsapp.com/{c['code']}", "reason": info})
for c, info in final_dead:
    dead.append((c, info))

raw = json.load(open(f"{WD}/team08_raw3100.json"))
last = raw[-1] if raw else {"idx": -1, "url": "", "lastmod": ""}
fetch_fail = [r for r in raw if "error" in r]
n_nojoin = sum(1 for r in raw if "error" not in r and not r["codes"])
n_tele = sum(1 for r in raw if r.get("telegram_only"))
txt = open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/linkado_sitemap.xml").read()
locs = re.findall(r"<loc>(.*?)</loc>", txt); mods = re.findall(r"<lastmod>(.*?)</lastmod>", txt)
grupo = [(l, m) for l, m in zip(locs, mods) if "/grupo/" in l]
summary = {
    "team": 8,
    "slice": "linkado sitemap 3100-3499",
    "sources": ["https://linkado.app/sitemap.xml (wave_20261110 copy; 19,731 grupo URLs, sitemap order = lastmod desc)"],
    "verified": len(verified),
    "pending": len(pending),
    "leads": len(leads),
    "dead": len(dead),
    "exclusions": exclusions,
    "resume": (f"next index 3500, {grupo[3500][0]}, lastmod {grupo[3500][1]} "
               f"(last mined: index {last['idx']}, {last['url']}, lastmod {last['lastmod']})"),
    "notes": (f"Mined 400/400 grupo detail pages (indices 3100-3499). Fetch failures: {len(fetch_fail)}. "
              f"Pages with no chat.whatsapp.com join link (JS-gated/removed/Telegram-only): {n_nojoin} (telegram-only {n_tele}) — banked as leads. "
              f"Fresh candidates after dedupe vs 112070-code union: {len(cands)}. "
              f"Verified live via python requests Session, browser UA, 90s timeout (HTTP 200 + non-empty og:title only; empty/generic og:title after 2 spaced retries = dead; transport failure = pending). "
              f"CORRECTION 1: first verify pass wrongly used og:description as fallback and banked 173 dead codes (dead pages carry og:description='WhatsApp Group Invite' with empty og:title). Re-verify pass with og:title-only rule corrected this (213 -> 21). "
              f"CORRECTION 2 (pass 3): spot-checks showed chat.whatsapp.com serves og:title intermittently (codes dead in pass 2 showed real og:titles minutes later; one 90s ReadTimeout seen). Pass 3 re-checked all 255 pass-2 dead codes + reconfirmed the 21 kept. Codes live in pass 3 were banked; codes live in pass 2 but dead in pass-3 reconfirm are pending (flaky), not dead. "
              f"Controls first: known-live code from groups.json showed og:title; fabricated code showed empty og:title (and og:description='WhatsApp Group Invite', which is why the fallback is invalid). "
              f"All verified are Brazilian (country BR). No merge into groups.json, no generate.py, no deploy.")
}
json.dump(verified, open(f"{WD}/team08-linkado-3100-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(f"{WD}/team08-linkado-3100-pending.json", "w"), ensure_ascii=False, indent=1)
json.dump(leads, open(f"{WD}/team08-linkado-3100-leads.json", "w"), ensure_ascii=False, indent=1)
json.dump(summary, open(f"{WD}/team08-linkado-3100-summary.json", "w"), ensure_ascii=False, indent=1)
print("PASS3 DONE — VERIFIED:", len(verified), "PENDING:", len(pending), "DEAD:", len(dead),
      "EXCL:", len(exclusions), "NOJOIN:", n_nojoin, "FETCHFAIL:", len(fetch_fail), "LEADS:", len(leads), flush=True)
