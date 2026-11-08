#!/usr/bin/env python3
"""Team36 phase 3: whatsgroupslinkspk.com mega listicle (fixed span pattern)."""
import json, re, html as h, time, sys
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261102")
import team36_pipeline as P
from team36_phase2 import headings, heading_for, mega_map, name_ctry

WAVE = P.WAVE
PLAIN = r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})"

def main():
    union = set(json.load(open(WAVE + "/dedupe_union.json")))
    for fn in ("team36-new-listicles.json", "team36-unverified-pending.json"):
        try:
            for it in json.load(open(WAVE + "/" + fn)):
                inv = it.get("invite", "")
                m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})", inv)
                if m: union.add(m.group(1))
        except FileNotFoundError:
            pass
    path = "/tmp/t36b/whatsgroupslinkspkcom.html"
    html = open(path, encoding="utf-8", errors="ignore").read()
    hs = headings(html)
    pat = (r"<span[^>]*>([^<]{1,160}?)\s+(?:[–—\-_]|&#8211;)\s*"
           r"(?:<strong>)?<a\s+href=\"https?://" + PLAIN + r"\"")
    cands, seen = [], set()
    for m in re.finditer(pat, html, re.S | re.I):
        name, code = h.unescape(m.group(1)).strip(), m.group(2)
        if code in union or code in seen: continue
        seen.add(code)
        hd = heading_for(hs, m.start())
        cat, ctry = mega_map(hd)
        if ctry == "International":
            ctry = name_ctry(hd, name)
        cands.append({"src_name": name, "code": code, "cat": cat, "country": ctry, "hd": hd[:100]})
    print(f"phase3 candidates after dedupe: {len(cands)}", flush=True)

    verified = json.load(open(WAVE + "/team36-new-listicles.json"))
    pending = json.load(open(WAVE + "/team36-unverified-pending.json"))
    porn_drops, rate_limited = 0, False
    i = -1
    for i, c in enumerate(cands):
        try:
            http_code, title = P.verify(c["code"])
        except RuntimeError:
            pending.append({"name": c["src_name"], "category": c["cat"], "country": c["country"],
                            "description": "", "invite": "https://chat.whatsapp.com/" + c["code"],
                            "image": "", "note": "transport failure"})
            time.sleep(0.7); continue
        if http_code == "429":
            rate_limited = True
            print("HTTP 429 at index %d — stopping" % i, flush=True)
            break
        time.sleep(0.7)
        if not title: continue
        name = c["src_name"]
        if not name or name.strip().lower() in ("link", "join", "click here", "view invite", "join now", "join link", "join group"):
            name = title
        if P.porn_hit(name) or P.porn_hit(title):
            porn_drops += 1; continue
        name = name.strip()
        if not name or name.startswith("http"): name = title.strip()
        if not name: continue
        verified.append({"name": name, "category": c["cat"], "country": c["country"],
                         "description": P.make_desc(name, c["cat"], c["country"]),
                         "invite": "https://chat.whatsapp.com/" + c["code"], "image": ""})
        if len(verified) % 10 == 0:
            print(f"[{i+1}/{len(cands)}] verified total={len(verified)} latest={name[:45]}", flush=True)

    if rate_limited:
        for c in cands[i:]:
            pending.append({"name": c["src_name"], "category": c["cat"], "country": c["country"],
                            "description": "", "invite": "https://chat.whatsapp.com/" + c["code"],
                            "image": "", "note": "rate-limited"})
    seen_inv, final = set(), []
    for it in verified:
        if it["invite"] not in seen_inv:
            seen_inv.add(it["invite"]); final.append(it)
    json.dump(final, open(WAVE + "/team36-new-listicles.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(WAVE + "/team36-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
    print(f"PHASE3 DONE: verified={len(final)} pending={len(pending)} porn_drops={porn_drops} rate_limited={rate_limited}", flush=True)

if __name__ == "__main__":
    main()
