#!/usr/bin/env python3
"""Wave 20261116 consolidation — PHASE 2: screens + dedupe + queue build."""
import json, os, re, unicodedata
from collections import Counter

BASE = "/home/hatch/workspace/whatsapp-groups-site"
OUT = os.path.join(BASE, "agent_batches/wave_20261116")

state = json.load(open(os.path.join(OUT, "phase1_state.json"), encoding='utf-8'))
pool, pool_order = state["pool"], state["pool_order"]
team_live, team_dead = state["team_live"], state["team_dead"]
union = set(json.load(open(os.path.join(OUT, "union_codes.json"), encoding='utf-8')))

def strip_acc(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s or "")
                   if not unicodedata.combining(c))

def norm_text(s):
    return strip_acc((s or "").lower())

# ---------------- screens ----------------
PORN_STRONG = [
    r"\bporn\b", r"\bporno\b", r"\bpornô\b", r"\bxxx\b", r"\bxvideos\b", r"\bxhamster\b",
    r"\bredtube\b", r"\bpornhub\b", r"\bonlyfans\b", r"\bonly\s*fans\b",
    r"\bsex\b", r"\bsexo\b", r"\bsexy\b", r"\bsexual\b",
    r"\bnudes?\b", r"\bnudez\b", r"\bvazad[oa]s?\b", r"\bvazamento\b",
    r"\bputaria\b", r"\bsafad[oa]s?\b", r"\bgostos[oa]s?\b", r"\bnovinh[oa]s?\b",
    r"\btesud[oa]s?\b", r"\bpeitud[oa]s?\b", r"\bbundud[oa]s?\b",
    r"\bhentai\b", r"\berotic[oa]s?\b", r"\bescort\b", r"\bcall\s*girls?\b",
    r"\bgarotas?\s+de\s+programa\b", r"\bacompanhantes\b",
    r"\bchicas?\s+calientes\b", r"\bvideos?\s+calientes\b", r"\bv[ií]deos?\s+hot\b",
    r"\bsexy\s+(girls?|women|ladies|meninas?|mulheres?)\b",
    r"\b(girls?|women|ladies|meninas?|mulheres?)\s+(sexy|hot|nua?s?)\b",
    r"\bhot\s+(girls?|women|ladies|meninas?)\b",
    r"\bmeninas?\s+(gostosas?|safadas?|quentes)\b",
    r"\bsex\s+(video|chat|call|girls?|women)\b", r"\bvideo\s+sex\b",
    r"\bpack\s+(de\s+)?(meninas?|novinhas?|gostosas?|mulheres?|sexy|nudes?|vazados?)\b",
    r"\b18\s*\+\s*(sex|porn|xxx|nude|girls?|women)\b",
    r"\b(siririca|punheta|gozar|foder|transar)\b",
    r"\bleaked\b", r"\bnude\s+(pics?|photos?|videos?|girls?)\b",
]
# leet variants (word-boundary, explicit)
PORN_LEET = [
    r"\bs[e3]x[o0]\b", r"\bp[o0]rn\b", r"\bpr[o0]n\b", r"\bn[uü]d[e3]s?\b",
    r"\bv[a4]z[a4]d[oa]s?\b", r"\bs[a4]f[a4]d[oa]s?\b", r"\bg[o0]st[o0]s[a4]s?\b",
    r"\bn[o0]v[i1]nh[a4]s?\b", r"\bh[e3]nt[a4][i1]\b", r"\b[o0]nlyf[a4]ns\b",
    r"\b[e3]sc[o0]rt\b", r"\bp[uü]t[a4]r[i1][a4]\b",
    r"\bx\s*x\s*x\b", r"\bs\s*e\s*x\b", r"\bp\s*o\s*r\s*n\b",
]
CASINO = [
    r"\baposta[s]?\b", r"\bapostador[es]?\b", r"\bcassin[oa]s?\b",
    r"\btigrinho\b", r"\bfortune\s*tiger\b", r"\btiger\s*(game|jogo|win|slots?|bet|cassino|aposta)\b",
    r"\bslots?\b", r"\broleta\b", r"\baviator\b",
    r"\b(bet365|betano|pixbet|vaidebet|f12bet|wjbet|mellbet|blaze|betfair|sportingbet)\b",
    r"\bbet\s*(vip|grátis|gratis|sinais|green|futebol|esportivas?|esportes?)\b",
    r"\b(sinais|sinal)\s*(vip|grátis|gratis|green|de\s*aposta|futebol|forex|crypto|tigrinho)\b",
    r"\bpalpite[s]?\b", r"\bbol[aã]o\b", r"\btipster\b",
    r"\bdicas?\s*vip\b", r"\bdicas?\s*(de\s*)?(aposta|futebol|jogo|green)\b",
    r"\bplataformas?\s+pagantes?\b", r"\bjogo\s+do\s+bicho\b",
    r"\bapostas?\s*esportivas?\b", r"\besportivas?\b.{0,12}\baposta",
    r"\bforex\s*(sinais|sinal)\b", r"\b(sinais|sinal)\s*forex\b",
]
SCAM = [
    r"\bairdrop\b", r"\bton[\s\-]?airdrop\b",
    r"\bbinary\s*option\b", r"\bop[cç][oõ]es?\s*bin[aá]rias?\b",
    r"\bbinary\b.{0,20}\b(investment|investimento|trading|profit)\b",
    r"\b(investment|investimento)\b.{0,25}\b(binary|airdrop|double|guaranteed|profit)\b",
    r"\b(crypto|cripto|trading)\s*(sinais|sinal|signals?)\b",
    r"\b(signals?|sinais)\s*(crypto|cripto|forex|trading)\b",
    r"\bdouble\s+your\s+money\b", r"\bdobrar\s+seu\s+dinheiro\b",
    r"\busdt\b.{0,20}\b(double|free|grátis|airdrop)\b",
    r"\bhamster\s+kombat\b",
]

def screen(text):
    t = norm_text(text)
    for pat in PORN_STRONG + PORN_LEET:
        if re.search(pat, t, re.I):
            return "porn"
    for pat in CASINO:
        if re.search(pat, t, re.I):
            return "casino"
    for pat in SCAM:
        if re.search(pat, t, re.I):
            return "scam"
    return None

# ---------------- category mapping ----------------
CANONICAL = {"Education","Jobs","Friendship","Community & Social","Entertainment","Gaming",
 "Business","Sports","Funny","Islamic","Health","News","Finance","Buy Sell","Technology",
 "Online Earning","Crypto","Cooking","Travel","Religion","Poetry","Real Estate",
 "Social Media","Movies","Politics","Animals And Pets","Study","General"}
CATMAP = {
 "girls":"Friendship","girl":"Friendship","ladies":"Friendship",
 "esportes":"Sports","esporte":"Sports","sport":"Sports","sports":"Sports",
 "tecnologia":"Technology","tech":"Technology","technology":"Technology",
 "educacao":"Education","educação":"Education","education":"Education",
 "study":"Study","studies":"Study","estudos":"Study","estudo":"Study",
 "empregos":"Jobs","emprego":"Jobs","trabalho":"Jobs","jobs":"Jobs","job":"Jobs",
 "amizade":"Friendship","amizades":"Friendship","friendship":"Friendship",
 "friends":"Friendship","friend":"Friendship",
 "comunidade":"Community & Social","community":"Community & Social",
 "community & social":"Community & Social","community and social":"Community & Social",
 "entretenimento":"Entertainment","entertainment":"Entertainment",
 "jogos":"Gaming","games":"Gaming","gaming":"Gaming","gamers":"Gaming",
 "negocios":"Business","negócios":"Business","business":"Business",
 "humor":"Funny","funny":"Funny","engracado":"Funny","memes":"Funny",
 "islam":"Islamic","islamico":"Islamic","islâmico":"Islamic","islamic":"Islamic","islamica":"Islamic",
 "saude":"Health","saúde":"Health","health":"Health",
 "noticias":"News","notícias":"News","news":"News",
 "financas":"Finance","finanças":"Finance","finance":"Finance",
 "compra e venda":"Buy Sell","buy sell":"Buy Sell","buy & sell":"Buy Sell",
 "buy-sell":"Buy Sell","vendas":"Buy Sell","compras":"Buy Sell",
 "ganhar dinheiro":"Online Earning","online earning":"Online Earning","renda extra":"Online Earning",
 "cripto":"Crypto","crypto":"Crypto",
 "culinaria":"Cooking","culinária":"Cooking","receitas":"Cooking","cooking":"Cooking",
 "viagem":"Travel","viagens":"Travel","travel":"Travel","turismo":"Travel",
 "religiao":"Religion","religião":"Religion","religion":"Religion",
 "poesia":"Poetry","poetry":"Poetry","poemas":"Poetry",
 "imoveis":"Real Estate","imóveis":"Real Estate","real estate":"Real Estate",
 "redes sociais":"Social Media","social media":"Social Media","midia social":"Social Media",
 "filmes":"Movies","movies":"Movies","cinema":"Movies",
 "politica":"Politics","política":"Politics","politics":"Politics",
 "animais":"Animals And Pets","pets":"Animals And Pets","animals":"Animals And Pets",
 "geral":"General","general":"General",
 "chat":"Community & Social","conversa":"Community & Social","bate-papo":"Community & Social",
 "grupo":"General","group":"General","whatsapp group":"General",
}
def map_category(c):
    c0 = (c or "").strip()
    if c0 in CANONICAL:
        return c0, False
    key = norm_text(c0)
    if key in CATMAP:
        return CATMAP[key], True
    return "General", True

AR_COUNTRY = {"مصر":"EG","السعودية":"SA","اليمن":"YE","العراق":"IQ","سوريا":"SY",
 "الأردن":"JO","الاردن":"JO","فلسطين":"PS","لبنان":"LB","المغرب":"MA","الجزائر":"DZ",
 "تونس":"TN","ليبيا":"LY","السودان":"SD","الكويت":"KW","قطر":"QA","البحرين":"BH",
 "عمان":"OM","الإمارات":"AE","الامارات":"AE","تركيا":"TR","الهند":"IN","باكستان":"PK",
 "أمريكا":"US","امريكا":"US","بريطانيا":"GB","البرازيل":"BR","إندونيسيا":"ID",
 "اندونيسيا":"ID","ماليزيا":"MY","كل الدول":"","جميع الدول":"","العالم":"",
 "السعوديه":"SA","اليمن ":"YE"}
def map_country(c):
    c0 = (c or "").strip()
    if re.fullmatch(r"[A-Za-z]{2}", c0):
        return c0.upper()
    if c0 in AR_COUNTRY:
        return AR_COUNTRY[c0]
    return ""

# ---------------- classify ----------------
excluded = []   # {code,name,team,reason}
queue = []      # needs my verification
accepted_live = []  # team-verified live, passed screens+dedupe
counts = Counter()
noncanon = 0

for nc in pool_order:
    rec = pool[nc]
    code = rec["code"]
    name = rec["name"]
    # channel codes
    if code.startswith("0029V"):
        excluded.append({"code": code, "name": name, "team": rec["team"], "reason": "channel"})
        counts["channel"] += 1; continue
    if not re.fullmatch(r"[A-Za-z0-9_-]{15,30}", code):
        excluded.append({"code": code, "name": name, "team": rec["team"], "reason": "bad-link"})
        counts["bad-link"] += 1; continue
    # dupe vs union
    if nc in union:
        excluded.append({"code": code, "name": name, "team": rec["team"], "reason": "dupe-union"})
        counts["dupe-union"] += 1; continue
    # junk name (no alphanumeric) — but allow team-live title to rescue
    title = team_live.get(nc, "")
    eff_name = name or title
    if not re.search(r"[A-Za-z0-9\u0600-\u06FF\u0900-\u097F\u4E00-\u9FFF\u0E00-\u0E7F]", eff_name or ""):
        excluded.append({"code": code, "name": name, "team": rec["team"], "reason": "junk-name"})
        counts["junk-name"] += 1; continue
    # screens on name + description + team title
    scr = screen(" ".join([name, rec["description"], title]))
    if scr:
        excluded.append({"code": code, "name": name, "team": rec["team"], "reason": scr})
        counts[scr] += 1; continue
    # category / country mapping
    cat, was_noncanon = map_category(rec["category"])
    if was_noncanon:
        noncanon += 1
    country = map_country(rec["country"])
    clean = {"code": code, "name": eff_name, "category": cat, "country": country,
             "description": rec["description"], "team": rec["team"],
             "invite": "https://chat.whatsapp.com/" + code}
    if nc in team_live:
        accepted_live.append(clean)
        counts["team-live-accepted"] += 1
    else:
        queue.append(clean)
        counts["needs-verify"] += 1

print("counts:", dict(counts))
print("non-canonical categories mapped:", noncanon)
print("accepted team-live:", len(accepted_live), "| verify queue:", len(queue),
      "| excluded:", len(excluded))

# save
json.dump(accepted_live, open(os.path.join(OUT, "accepted_team_live.json"), "w", encoding='utf-8'), ensure_ascii=False)
json.dump(queue, open(os.path.join(OUT, "verify_queue.json"), "w", encoding='utf-8'), ensure_ascii=False)
json.dump(excluded, open(os.path.join(OUT, "excluded_phase2.json"), "w", encoding='utf-8'), ensure_ascii=False)
print("saved phase2 outputs")
# screen breakdown sample for sanity
from collections import Counter as C
print("excluded by team:", C(e["team"] for e in excluded).most_common(10))
print("accepted by team:", C(r["team"] for r in accepted_live).most_common(10))
print("queue by team:", C(r["team"] for r in queue).most_common(10))
