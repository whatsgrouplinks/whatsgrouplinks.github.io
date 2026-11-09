import json, re

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
fresh = json.load(open(f"{W}/team04_fresh_raw.json"))

# sentences that prohibit adult content -> strip before screening
PROHIBIT_RE = re.compile(
    r"[^.\n!?]*(?:not allowed|na karein|nahi kare|not allow|prohibit|no porn|no xxx|no sex|"
    r"links and pron not allowed|inappropriate content)[^.\n!?]*[.!\n]?",
    re.I)

ADULT_KW = [
    "xxx", "porn", "sex video", "sex chat", "sex group", "sexy", "escort",
    "cam girl", "camgirl", "call girl", "call boy", "video call service",
    "paid service", "incest", "mom son", "real incest", "family lovers",
    "desi bhabhi", "bhabhi video", "hot girl", "hot aunty", "aunty video",
    "viral video link", "desi viral video", "mms", "maal", "unseen",
    "role play", "cp ", " c p", "child", "14 years old", "15 years old",
    "16 years old", "school girl", "college girl video", "nude", "naked",
    "boobs", "bobs", "vagina", "penis", "dick", "pussy", "lesbian video",
    "gay sex", "hand job", "blowjob", "hookup", "hook up", "one night stand",
    "adult video", "adult group", "18+ video", "18 +", "🔞", "💦", "🍌",
    "🍆", "🍑", "👅", "💋 video",
]
SCAM_KW = ["b-love", "blove", "forsage", "sheyi", "s-heyi", "free money",
           "double your money", "money doubling", "airdrop", "crypto airdrop",
           "earn $1000 daily", "100% free money"]
# "free dollar", "earn money" alone are NOT drops (Online Earning is a legit category)

def text_of(g):
    t = " ".join([g.get("title","") or "", g.get("desc","") or "",
                  g.get("context","") or "", g.get("page_title","") or ""])
    t = PROHIBIT_RE.sub(" ", t)
    return t

def drop_reason(g):
    if (g.get("category") or "") == "Adult":
        return "category Adult"
    t = text_of(g).lower()
    for kw in ADULT_KW:
        if kw in t:
            return f"adult kw: {kw}"
    for kw in SCAM_KW:
        if kw in t:
            return f"scam kw: {kw}"
    return None

kept, dropped = {}, {}
for code, g in fresh.items():
    r = drop_reason(g)
    if r:
        g["drop_reason"] = r
        dropped[code] = g
    else:
        kept[code] = g

print("fresh:", len(fresh), "pre-screen dropped:", len(dropped), "to verify:", len(kept))
from collections import Counter
print(Counter(g["drop_reason"].split(":")[0] for g in dropped.values()))
print(Counter(g.get("category","") or "html" for g in kept.values()))
json.dump(kept, open(f"{W}/team04_to_verify.json","w"), indent=1, ensure_ascii=False)
json.dump(dropped, open(f"{W}/team04_prescreen_dropped.json","w"), indent=1, ensure_ascii=False)
