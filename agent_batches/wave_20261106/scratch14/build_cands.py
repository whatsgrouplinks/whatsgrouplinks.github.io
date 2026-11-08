#!/usr/bin/env python3
"""team14 P5 build candidates from raw.json:
- drop cat_slug adult, porn/scam regex on name+desc+tags, minors/sexual content
- dedupe within file + against dedupe_union.json + against pending codes already handled
- category = tag (funny/health), country = iso2
- name cleaned; description 1-2 sentences keyword-rich, no source name/URL
Writes harvest_cands.json (to verify) and prints stats.
"""
import json, re

SCRATCH = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106/scratch14"
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106"

PORN_RE = re.compile(r"porn|pornhub|xxx|nudes?|sex video|escort|call girl|randi|fuck|dick|pussy|boobs|anal|orgasm|cumshot|blowjob", re.I)
SCAM_RE = re.compile(r"receiver and loader|money[- ]?mule|double (your|the) money|counterfeit currency|buy (drugs|cocaine|heroin)|phishing|investment.*(double|2x|guaranteed profit)", re.I)
MINOR_RE = re.compile(r"\b(minor|under ?18|child|teen.*sex|school ?girl.*sex)\b", re.I)
ADULT_EMOJI = ["\U0001f975", "\U0001f48b"]  # 🥵 etc - not used alone; only with other signals

def clean_name(n):
    n = n.strip()
    n = re.sub(r"\s+", " ", n)
    return n[:120]

def clean_desc(raw, name, cat, country):
    d = (raw or "").strip()
    # strip boilerplate
    d = re.sub(r"^Welcome to my whatsapp group\s*", "", d, flags=re.I)
    d = re.sub(r"Please join my whatsapp group\.?\s*", "", d, flags=re.I)
    d = re.sub(r"\s+", " ", d).strip()
    # drop junk descs
    if len(d) < 8 or d in ("$b7", "$b8") or set(d) <= set("$b78"):
        d = ""
    if d:
        # keep first 1-2 sentences, cap length
        sents = re.split(r"(?<=[.!?])\s+", d)
        d = " ".join(sents[:2])[:220].strip()
        if d and d[-1] not in ".!?":
            d += "."
        return d
    cname = {"funny": "funny jokes, memes and comedy", "health": "health, fitness and wellness tips"}.get(cat, cat)
    ctry = "" if country in ("International", "") else f" from {country}"
    return f"Join this {cat} WhatsApp group{ctry} to enjoy {cname} with active members. Chat, share and have fun with the community every day."

def main():
    raw = json.load(open(f"{SCRATCH}/raw.json"))
    cands = raw["candidates"]
    union = set(json.load(open(f"{WAVE}/dedupe_union.json")))
    pending_codes = set(x["code"] for x in json.load(open(f"{SCRATCH}/pending_in.json")))
    seen = set()
    out, dropped = [], {"union": 0, "dup": 0, "adult": 0, "porn": 0, "scam": 0, "minor": 0, "pending_overlap": 0, "badname": 0}
    for c in cands:
        code = c["code"]
        if code in union:
            dropped["union"] += 1; continue
        if code in seen:
            dropped["dup"] += 1; continue
        seen.add(code)
        if c["cat_slug"] == "adult":
            dropped["adult"] += 1; continue
        blob = f"{c['name']} {c['desc_raw']} {c['tags_raw']}"
        if PORN_RE.search(blob):
            dropped["porn"] += 1; continue
        if SCAM_RE.search(blob):
            dropped["scam"] += 1; continue
        if MINOR_RE.search(blob):
            dropped["minor"] += 1; continue
        name = clean_name(c["name"])
        if not name or len(name) < 2:
            dropped["badname"] += 1; continue
        cat = c["tag"]  # funny / health
        country = c["country"] if c["country"] else "International"
        out.append({
            "code": code,
            "name": name,
            "category": cat,
            "country": country,
            "description": clean_desc(c["desc_raw"], name, cat, country),
            "invite": f"https://chat.whatsapp.com/{code}",
            "image": "",
            "src": f"{c['tag']} p{c['page']}",
            "pending_overlap": code in pending_codes,
        })
        if code in pending_codes:
            dropped["pending_overlap"] += 1
    print("raw:", len(cands), "kept:", len(out), "dropped:", dropped)
    print("pending_overlap kept (will merge with pending verdict):", sum(1 for o in out if o["pending_overlap"]))
    json.dump(out, open(f"{SCRATCH}/harvest_cands.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
