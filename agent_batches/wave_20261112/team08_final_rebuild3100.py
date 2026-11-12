#!/usr/bin/env python3
"""TEAM 08 wave 20261112 — FINAL rebuild (union rule, no network).
Evidence: og:description is ALWAYS 'WhatsApp Group Invite' (live or dead),
so only og:title counts. Live og:title serving is intermittent (pass counts
40/21/9 across three passes; overlap consistent, 0 title inconsistencies),
so a code that showed a real group-name og:title in ANY pass is verified
live — a dead page never serves a group name as og:title. Union of real-title
live results across v1+v2+v3 = final verified set."""
import json, re, html

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
data = json.load(open(f"{WD}/team08_candidates3100.json"))
cands = {c["code"]: c for c in data["cands"]}
exclusions, leads = data["exclusions"], data["leads"]

# union of real-title live results across all three passes
union = {}
for fn in ["team08_verify3100.ckpt.jsonl", "team08_verify3100_v2.ckpt.jsonl",
           "team08_verify3100_v3.ckpt.jsonl"]:
    for line in open(f"{WD}/{fn}"):
        r = json.loads(line)
        if r["status"] == "live" and r["info"] and r["info"] != "WhatsApp Group Invite":
            union.setdefault(r["code"], r["info"])
print(f"union live: {len(union)} of {len(cands)} candidates", flush=True)

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

verified, dead = [], []
for code, og in union.items():
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
for code, c in cands.items():
    if code not in union:
        dead.append((c, "no real og:title in any of 3 verify passes (2 spaced tries each)"))

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
    "pending": 0,
    "leads": len(leads),
    "dead": len(dead),
    "exclusions": exclusions,
    "resume": (f"next index 3500, {grupo[3500][0]}, lastmod {grupo[3500][1]} "
               f"(last mined: index {last['idx']}, {last['url']}, lastmod {last['lastmod']})"),
    "notes": (f"Mined 400/400 grupo detail pages (indices 3100-3499). Fetch failures: {len(fetch_fail)}. "
              f"Pages with no chat.whatsapp.com join link (JS-gated/removed/Telegram-only): {n_nojoin} (telegram-only {n_tele}) — banked as leads. "
              f"Fresh candidates after dedupe vs 112070-code union: {len(cands)}. "
              f"Verification (python requests Session / curl, browser UA, 60-90s timeout, 2 spaced tries per pass): LIVE = non-empty og:title only. "
              f"og:description is ALWAYS 'WhatsApp Group Invite' on live AND dead pages (verified directly), so it is NOT a valid fallback — the task's fallback wording is empirically invalid for chat.whatsapp.com and was not used. "
              f"Pass 1 wrongly used the og:description fallback (213 banked, 173 of them dead). Pass 2 with og:title-only gave 21. Pass 3 re-checked all dead + kept and gave 9. "
              f"og:title serving is intermittent (pass live counts 40/21/9; titles 100% consistent across passes, 0 inconsistencies), so the final set is the UNION of codes showing a real group-name og:title in any pass = {len(verified)}. A dead page never serves a group name as og:title, so union membership is sound; codes never showing a title in 3 passes x 2 tries are counted dead. "
              f"Controls first: known-live code from groups.json showed og:title; fabricated code showed empty og:title. "
              f"All verified are Brazilian (country BR). No merge into groups.json, no generate.py, no deploy.")
}
json.dump(verified, open(f"{WD}/team08-linkado-3100-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump([], open(f"{WD}/team08-linkado-3100-pending.json", "w"), ensure_ascii=False, indent=1)
json.dump(leads, open(f"{WD}/team08-linkado-3100-leads.json", "w"), ensure_ascii=False, indent=1)
json.dump(summary, open(f"{WD}/team08-linkado-3100-summary.json", "w"), ensure_ascii=False, indent=1)
print("FINAL — VERIFIED:", len(verified), "PENDING: 0", "DEAD:", len(dead),
      "EXCL:", len(exclusions), "NOJOIN:", n_nojoin, "FETCHFAIL:", len(fetch_fail), "LEADS:", len(leads), flush=True)
