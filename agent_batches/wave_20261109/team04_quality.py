import json, re, unicodedata

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
cands = json.load(open(f"{W}/team04-candidates.json"))
fresh = json.load(open(f"{W}/team04_fresh_raw.json"))

FRAUD_KW = ["carding", "cc dumps", "dumps", "stolen card", "cloned card",
            "bank log", "bank logs", "paypal hack", "hack facebook", "hack whatsapp"]
RULE_FRAG = re.compile(
    r"^(no|don't|dont|dilarang|jangan|free fire\.?|no share|no spam|no toxic|"
    r"no rules\.?|join bang|please subscribe|galat video|online earnings?\.?|"
    r"earning money ideas\.?|ah dealer|welcome to .*\.?)$", re.I)

def sentence_case(t):
    low = t.lower()
    # capitalize first letter of each sentence
    return re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), low)

def topic_of(name):
    t = re.sub(r"whatsapp group.*$", "", name, flags=re.I).strip()
    t = re.sub(r"[^\w\s&|/-]", "", t).strip()
    return t or "community"

kept, dropped = [], []
for c in cands:
    name = unicodedata.normalize("NFKC", c["name"]).strip()
    name = re.sub(r"\s+", " ", name)
    c["name"] = name
    low = (name + " " + c["description"]).lower()
    if name.isdigit():
        dropped.append({**c, "reason": "name is pure digits"}); continue
    if any(k in low for k in FRAUD_KW):
        dropped.append({**c, "reason": f"fraud kw: {[k for k in FRAUD_KW if k in low]}"}); continue
    d = c["description"].strip()
    letters = [ch for ch in d if ch.isalpha()]
    caps_ratio = (sum(1 for ch in letters if ch.isupper()) / len(letters)) if letters else 0
    if len(d) < 25 or RULE_FRAG.match(d):
        c["description"] = (f"A WhatsApp group for {topic_of(name)} fans and members "
                            "to chat, share updates and connect with each other.")
    elif caps_ratio > 0.6 and len(d) > 30:
        c["description"] = sentence_case(d)
        if not c["description"].endswith((".", "!", "?")):
            c["description"] += "."
    kept.append(c)

kept.sort(key=lambda x: x["name"].lower())
json.dump(kept, open(f"{W}/team04-candidates.json","w"), indent=1, ensure_ascii=False)
json.dump(dropped, open(f"{W}/team04_quality_dropped.json","w"), indent=1, ensure_ascii=False)
print("kept:", len(kept), "quality-dropped:", len(dropped))
for d in dropped: print(" -", d["name"], "|", d["reason"])
from collections import Counter
print(Counter(x["category"] for x in kept))
print(Counter(x["country"] for x in kept).most_common(8))
# final sanity: no phones/urls in any field, categories valid, names non-empty
ALLOWED = ["Gaming","Education","Online Earning","Community & Social","Business",
           "Friendship","Finance","Buy Sell","Islamic","Entertainment","Jobs",
           "Technology","Funny","Sports","Health","News"]
for x in kept:
    assert x["category"] in ALLOWED, x
    assert x["name"] and x["description"] and x["invite"].startswith("https://chat.whatsapp.com/")
    assert "http" not in x["description"] and "whatsapp.com" not in x["description"], x
    assert not re.search(r"\d{9,}", x["description"]), x
print("sanity OK; unique invites:", len({x["invite"] for x in kept}))
