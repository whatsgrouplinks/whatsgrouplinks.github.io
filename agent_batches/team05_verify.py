#!/usr/bin/env python3
"""team05: dedupe, filter, verify invites, write final output."""
import json, re, subprocess, concurrent.futures, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OUT = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261023b/team05-groupwhat-tech-game.json"

PORN = re.compile(r"\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b", re.I)
PHONE = re.compile(r"^\+?[\d\s\-().]{7,}$")

existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
print(f"existing codes loaded: {len(existing)}", flush=True)

cands = json.load(open("/tmp/team05_candidates.json"))
print(f"candidates: {len(cands)}", flush=True)

own = set()
filtered = []
stats = {"existing_dup": 0, "own_dup": 0, "porn": 0, "phone": 0, "noname": 0}
for g in cands:
    code = g["code"]
    if code in existing:
        stats["existing_dup"] += 1; continue
    if code in own:
        stats["own_dup"] += 1; continue
    name = g["name"]
    if not name or len(name) < 3:
        stats["noname"] += 1; continue
    if PHONE.match(name.replace(" ", "")):
        stats["phone"] += 1; continue
    desc = g["description"]
    if PORN.search(name) or PORN.search(desc):
        stats["porn"] += 1; continue
    own.add(code)
    filtered.append(g)
print("after filters:", len(filtered), stats, flush=True)

def verify(code):
    url = f"https://chat.whatsapp.com/invite/{code}"
    try:
        p = subprocess.run(
            ["curl", "-sL", "--max-time", "15", "-A", UA, url, "-w", "\n%{http_code}"],
            capture_output=True, timeout=25)
        body = p.stdout.decode("utf-8", "ignore")
        code_http = body.strip().rsplit("\n", 1)[-1] if body else ""
        ok = ("WhatsApp" in body) and ("og:title" in body or "WhatsApp Group" in body
                                       or "Join chat" in body or "Join group" in body)
        return code, ok, code_http
    except Exception as e:
        return code, False, "err"

def make_desc(g):
    cat = g["category"].lower()
    ctry = g["country"]
    name = g["name"].strip()
    d = re.sub(r"\s+", " ", g["description"]).strip()
    # use site description's first 2 sentences if it looks English-ish and clean
    if len(d) >= 20 and re.search(r"[a-zA-Z]", d):
        sents = re.split(r"(?<=[.!?])\s+", d)
        use = " ".join(sents[:2])[:280]
        if not PORN.search(use):
            return use
    return (f"{name} is an active {cat} WhatsApp group for {ctry} members. "
            f"Join to share {cat} updates, tips and discussions with fellow enthusiasts.")

verified = []
dead = 0
CHUNK = 80
codes = [g["code"] for g in filtered]
bycode = {g["code"]: g for g in filtered}

# write final array progressively
results = json.load(open(OUT)) if False else []

for i in range(0, len(codes), CHUNK):
    batch = codes[i:i + CHUNK]
    ok_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as ex:
        for code, ok, httpc in ex.map(verify, batch):
            ok_map[code] = (ok, httpc)
            if not ok:
                dead += 1
    for code in batch:
        ok, httpc = ok_map[code]
        if not ok:
            continue
        g = bycode[code]
        verified.append({
            "name": g["name"],
            "category": g["category"],
            "country": g["country"],
            "description": make_desc(g),
            "image": "",
            "invite": f"https://chat.whatsapp.com/invite/{code}",
        })
    json.dump(verified, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"progress: {i + len(batch)}/{len(codes)} verified={len(verified)} dead={dead}", flush=True)

print(f"DONE. verified-new written: {len(verified)} dead/skipped: {dead}")
print(f"file: {OUT}")
