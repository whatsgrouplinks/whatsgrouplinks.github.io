#!/usr/bin/env python3
"""TEAM05 final clean pass (propose step) — applies, on top of team05_finalize.py:
 (1) union dedupe vs CURRENT .existing_codes.json (Nov 11 10:49 rebuild, which
     now contains team04's 472 merged items — the inherited miner/finalize only
     dedupe at mine time, so carried-over team04 items must be stripped now);
 (2) the task's hard screen gaps the inherited script misses, as proven by the
     Nov-11 coordinator's own exclusions of team04 items:
     - hentai, blanket 18+/sticker-group handling, sports-betting promos.
     - negated-prohibition restores are respected (reuse team05_mine.strip_prohibitions).
 Writes team05-proposed-drops.json for manual review; does NOT modify outputs.
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import team05_mine as M

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
EXISTING = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"

def fold_zw(s):
    """Remove zero-width/variation chars and decode regional-indicator
    flag letters (🇫🇮🇬...) back to ASCII, so obfuscated words match."""
    s = re.sub(r"[\u200b\u200c\u200d\ufe0f\u00ad]", "", str(s or ""))
    s = "".join(chr(ord(ch) - 0x1F1E6 + ord("A")) if "\U0001f1e6" <= ch <= "\U0001f1ff" else ch
                for ch in s)
    return s

def code_of(v):
    return re.search(r"chat\.whatsapp\.com/([A-Za-z0-9_-]+)", v["invite"]).group(1)

# --- extra porn tokens (coordinator PORN list) that team04's screen lacks,
#     applied to prohibition-stripped text. 'sex' substring deliberately NOT
#     used (false-positives on 'sexta-feira'); '18+' text deliberately NOT
#     used (task restore: 18+ age gates on non-porn groups are kept).
EXTRA_PORN = ["hentai", "sexy", "nude", "naked", "onlyfans", "pornhub", "xvideos",
              "brazzers", "escort", "call girl", "camgirl", "cam girl", "erotic",
              "sexting", "sexchat", "nekopoi", "xnxx", "xxnx", "desi bhabhi",
              "leak", "leaked", "mms", "bokep", "jav "]
EMOJI_18 = "🔞"

SPORTS_BET_RES = [
    (r"apostas?\s+esportivas?", "sports-betting promo (apostas esportivas)"),
    (r"\bapostador(es)?\b", "sports-betting promo (apostador)"),
    (r"\bpalpites?\b", "sports-betting promo (palpites/tips)"),
    (r"\bbilhetes?\b", "sports-betting promo (bilhetes/slips)"),
    (r"casa\s+de\s+aposta", "sports-betting promo (casa de aposta/bookmaker)"),
    (r"\bcambista\b", "sports-betting promo (cambista/bookmaker)"),
    (r"\befootball\b.{0,40}\b(apostad|aposta|bet|banca|bilhete|palpite)", "sports-betting promo (efootball betting)"),
    (r"\b(apostad|aposta|bet|banca|bilhete|palpite)\b.{0,40}\befootball\b", "sports-betting promo (efootball betting)"),
    (r"dicas\s+de\s+apostas?", "sports-betting promo (dicas de apostas)"),
    (r"links?\s+de\s+apostas?", "sports-betting promo (links de apostas)"),
    (r"grupo\s+de\s+apostas?\b", "sports-betting promo (grupo de apostas)"),
    (r"jogos?\s+de\s+aposta", "sports-betting promo (jogos de aposta)"),
    (r"aposta\s+online\b", "sports-betting promo (aposta online)"),
    (r"lucro\s+garantido", "betting promo (lucro garantido/guaranteed profit)"),
    (r"fature\s+de\s+[\dkm]+", "betting promo (fature de .../earnings claim)"),
    (r"seja\s+s[óo]cio\b", "betting recruitment (seja socio/partner)"),
    (r"dono\s+de\s+um\s+cassino", "betting recruitment (dono de cassino)"),
    (r"\bbet\b.{0,20}\baposta\b|\baposta\b.{0,20}\bbet\b", "sports-betting promo (bet+aposta)"),
    (r"\btips\b.{0,20}\baposta\b|\baposta\b.{0,20}\btips\b", "sports-betting promo (tips+aposta)"),
]

def main():
    ver = json.load(open(os.path.join(WAVE, "team05-leads-slice4.json")))
    existing = set(json.load(open(EXISTING)))
    verify = {r["code"]: r for r in M.load_jl(os.path.join(WAVE, "team05-verify.jsonl"))}
    drops = []   # {"code","name","reason","stage"}
    keeps = []
    for v in ver:
        c = code_of(v)
        og = (verify.get(c) or {}).get("og_title", "")
        name, desc = v["name"], v["description"]
        if c in existing:
            drops.append({"code": c, "name": name, "description": desc,
                          "reason": "already in groups.json (existing code)",
                          "stage": "union-dedupe"})
            continue
        # inherited screen (already applied by finalize, re-checked for the record)
        r0 = M.screen(name, desc, og)
        if r0:
            drops.append({"code": c, "name": name, "description": desc,
                          "reason": r0, "stage": "inherited-screen"})
            continue
        stripped = M.strip_prohibitions(f"{name} {desc} {og}")
        slow = stripped.lower()
        hit = None
        for tok in EXTRA_PORN:
            if tok in slow:
                hit = f"hard porn/xxx marker '{tok}'"
                break
        if hit:
            drops.append({"code": c, "name": name, "description": desc,
                          "reason": hit, "stage": "extra-porn"})
            continue
        blob = f"{name} {desc} {og}"
        low = fold_zw(blob).lower()
        # 18+ handling: drop only 18+ STICKER groups (figurinhas) and
        # "anything goes" (pode tudo) groups; age gates on non-porn groups kept.
        if EMOJI_18 in blob:
            if "figurinha" in low:
                drops.append({"code": c, "name": name, "description": desc,
                              "reason": "18+ sticker group (figurinhas + 🔞)",
                              "stage": "18plus-sticker"})
                continue
            if "pode tudo" in low:
                drops.append({"code": c, "name": name, "description": desc,
                              "reason": "18+ anything-goes group (pode tudo + 🔞)",
                              "stage": "18plus-anything-goes"})
                continue
            if "links da sorte" in low or "destrui" in low:
                drops.append({"code": c, "name": name, "description": desc,
                              "reason": "18+ betting-links group (🔞 + links da sorte)",
                              "stage": "18plus-betting"})
                continue
            # streaming group listing 🔞 among content types (adult channels)
            if "canais" in low and ("stream" in low or "tv" in low):
                drops.append({"code": c, "name": name, "description": desc,
                              "reason": "18+ adult content offered (streaming + 🔞)",
                              "stage": "18plus-streaming"})
                continue
            # otherwise: age gate on a non-porn group -> KEEP (task restore)
        for pat, reason in SPORTS_BET_RES:
            if re.search(pat, low):
                drops.append({"code": c, "name": name, "description": desc,
                              "reason": reason, "stage": "sports-betting"})
                break
        else:
            keeps.append(v)
    print(f"total={len(ver)} union-drops={sum(1 for d in drops if d['stage']=='union-dedupe')} "
          f"screen-drops={sum(1 for d in drops if d['stage']!='union-dedupe')} keeps={len(keeps)}")
    from collections import Counter
    print(Counter((d['stage'], d['reason']) for d in drops))
    with open(os.path.join(WAVE, "team05-proposed-drops.json"), "w", encoding="utf-8") as f:
        json.dump(drops, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WAVE, "team05-proposed-keeps.json"), "w", encoding="utf-8") as f:
        json.dump(keeps, f, ensure_ascii=False, indent=1)
    print("wrote team05-proposed-drops.json + team05-proposed-keeps.json (NOT applied yet)")

if __name__ == "__main__":
    main()
