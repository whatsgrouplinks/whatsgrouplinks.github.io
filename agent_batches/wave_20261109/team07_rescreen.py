#!/usr/bin/env python3
"""Team07 phase 5b: re-screen the 53 verified candidates on og:title with
unicode-folded + multilingual + adult-emoji rules."""
import json, re, os, unicodedata

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
cands = json.load(open(os.path.join(WAVE, "team07-candidates.json")))

def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = s.replace("ß", "s").replace("ẞ", "S")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.casefold()

DROP_WORDS = [
    "sexo", "sexe", "freaky", "previas", "tesao", "puta", "putaria", "punheta",
    "polla", "verga", "cono", "caralho", "pussy", "dick", "cock", "blowjob",
    "handjob", "squirting", "gangbang", "onlyfans", "porn", "xxx", "sexting",
    "hookup", "escort", "camgirl", "cam girl", "sexy", "horny", "nudes", "nude",
    "masturbat", "s3x", "sex", "pr0n", "b-love", "blove", "forsage", "sheyi",
    "activos y pasivos", "activo y pasivo", "ativos e passivos",
]
# Word-boundary matching: avoids "cono" ⊂ "conocer" and "sex" ⊂ "bisexuales".
DROP_RES = [(re.compile(r"\b" + re.escape(w).replace(r"\ ", r"\s+") + r"\b"), w)
            for w in DROP_WORDS]
ADULT_EMOJI_HARD = ["🔞", "🍆", "💦"]  # drop on sight
ADULT_EMOJI_SOFT = ["🍑", "🍌", "😈"]  # drop only with a sex word / hard emoji

kept, dropped = [], []
for c in cands:
    text = f"{c['name']} {c['description']}"
    f = fold(text)
    hit = None
    if any(e in text for e in ADULT_EMOJI_HARD):
        hit = "adult-emoji"
    else:
        for rx, w in DROP_RES:
            if rx.search(f):
                hit = w
                break
    if not hit and any(e in text for e in ADULT_EMOJI_SOFT) and any(
            rx.search(f) for rx, w in DROP_RES):
        hit = "adult-emoji+context"
    if hit:
        dropped.append({**c, "drop_reason": hit})
    else:
        kept.append(c)

print(f"candidates {len(cands)} -> kept {len(kept)} dropped {len(dropped)}")
for d in dropped:
    print(" DROP:", d["drop_reason"], "|", d["name"][:70], "|", d["invite"])
json.dump(kept, open(os.path.join(WAVE, "team07-candidates.json"), "w"), indent=1, ensure_ascii=False)
json.dump(dropped, open(os.path.join(WAVE, "team07_dropped_postverify.json"), "w"), indent=1, ensure_ascii=False)
