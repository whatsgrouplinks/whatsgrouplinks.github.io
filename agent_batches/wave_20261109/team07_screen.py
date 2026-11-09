#!/usr/bin/env python3
"""Team07 phase 3: screen fresh records (porn / sex / escort / scam)."""
import json, re, os

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
recs = json.load(open(os.path.join(WAVE, "team07_extracted.json")))

# Strip sentences that PROHIBIT adult content before screening
PROHIB = re.compile(r"[^.!?\n]*(?:na karein|not allowed|prohibit|no (?:porn|sex|adult|nude|xxx)|don't share|do not share|strictly prohibited|forbidden)[^.!?\n]*[.!?\n]?", re.I)

DROP_PATTERNS = [
    (r"\bporn\b", "porn"), (r"\bxxx\b", "xxx"), (r"\bsex\b", "sex"),
    (r"sexting", "sexting"), (r"sex chat", "sex chat"), (r"sex video", "sex video"),
    (r"\bhookup\b", "hookup"), (r"hook up", "hookup"),
    (r"\bescort\b", "escort"), (r"cam ?girl", "cam-girl"), (r"\bsexy\b", "sexy"),
    (r"\bhorny\b", "horny"), (r"\bnudes?\b", "nudes"), (r"onlyfans", "onlyfans"),
    (r"adult video", "adult video"), (r"adult group", "adult group"),
    (r"masturbat", "masturbation"), (r"friends with benefits", "fwb"),
    (r"\bvc\b.{0,20}\bsex\b|\bsex\b.{0,20}\bvc\b", "sex-vc"),
    (r"b-?love", "b-love scam"), (r"forsage", "forsage scam"), (r"\bsheyi\b", "sheyi scam"),
    (r"free money", "free-money scam"), (r"double your (money|investment)", "doubling scam"),
    (r"claim (your )?free", "free-claim scam"), (r"\bairdrop\b.{0,30}(free|earn|claim)", "airdrop scam"),
    (r"earn (up to )?\$?\d+.*per day.*no investment", "too-good earning scam"),
]
DROP_RE = [(re.compile(p, re.I), label) for p, label in DROP_PATTERNS]

kept, dropped = [], []
for r in recs:
    name = r.get("name", "") or ""
    desc = r.get("description", "") or ""
    text = f"{name} {desc}"
    text_screen = PROHIB.sub(" ", text)
    hit = None
    for rx, label in DROP_RE:
        if rx.search(text_screen):
            hit = label
            break
    if hit:
        dropped.append({**r, "drop_reason": hit})
    else:
        kept.append(r)

print(f"fresh: {len(recs)} kept: {len(kept)} dropped: {len(dropped)}")
from collections import Counter
print(Counter(d["drop_reason"] for d in dropped))
print(Counter(d["src"].split(":")[0] for d in dropped))
json.dump(kept, open(os.path.join(WAVE, "team07_screened.json"), "w"), indent=1, ensure_ascii=False)
json.dump(dropped, open(os.path.join(WAVE, "team07_dropped_screen.json"), "w"), indent=1, ensure_ascii=False)
