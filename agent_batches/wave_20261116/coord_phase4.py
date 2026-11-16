#!/usr/bin/env python3
"""Wave 20261116 — PHASE 4 (draft): screen verified og:titles.
Screens the LIVE og:title (the true group name) with the same hard rules,
plus title-specific patterns (baddies, hot viral video, broker money-making).
Run AFTER phase 3b finishes; this file only TESTS the screen on team-live titles now.
"""
import json, os, re, unicodedata
from collections import Counter

BASE = "/home/hatch/workspace/whatsapp-groups-site"
OUT = os.path.join(BASE, "agent_batches/wave_20261116")

def strip_acc(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s or "")
                   if not unicodedata.combining(c))

def norm_text(s):
    return strip_acc((s or "").lower())

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
    # title-specific
    r"\bbaddies?\b", r"\bhot\b.{0,15}\bviral\s+videos?\b",
    r"\bviral\s+videos?\b.{0,15}\bhot\b",
    r"\bsexy\s+videos?\b", r"\bhot\s+videos?\b",
]
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
    r"\bbroker\b.{0,25}\bmoney\s+making\b",
    r"\bmoney\s+making\s+(platform|system|machine|app)\b",
    r"\bforex\b.{0,20}\b(vip|money|profit|signals?)\b",
]

def screen_title(text):
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

if __name__ == "__main__":
    accepted = json.load(open(os.path.join(OUT, "accepted_team_live.json"), encoding='utf-8'))
    state = json.load(open(os.path.join(OUT, "phase1_state.json"), encoding='utf-8'))
    team_live = state["team_live"]
    flagged = Counter()
    examples = []
    for rec in accepted:
        title = team_live.get(rec["code"].lower(), "")
        r = screen_title(title) if title else None
        if r:
            flagged[r] += 1
            if len(examples) < 30:
                examples.append((r, rec["name"][:50], title[:60], rec["code"]))
    print("team-live accepted:", len(accepted), "flagged by TITLE screen:", dict(flagged))
    for e in examples:
        print(" ", e)
