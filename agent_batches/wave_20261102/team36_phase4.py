#!/usr/bin/env python3
"""Team36 phase 4: asiamediajournal gaming + whtsgrouplink movies listicles."""
import json, re, html as h, time, sys
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261102")
import team36_pipeline as P
from team36_phase2 import headings, heading_for, name_ctry

WAVE = P.WAVE
PLAIN = r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})"
T36 = "/tmp/t36b/"

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
    pages = [
        (T36 + "p4_asiamediajournalcom_gaming-whatsapp-group-links.html", "Gaming",
         r"<td[^>]*>([^<]{1,140})</td>\s*<td[^>]*>\s*<a\s+href=\"https?://" + PLAIN + r"\""),
        (T36 + "p4_whtsgrouplinkcom_movies-whatsapp-group-links.html", "Movies",
         r"<li>([^<]{1,160}?)\s*(?:&#8211;|&#8212;|–|—|-)\s*(?:<strong>)?<a\s+href=\"https?://" + PLAIN + r"\""),
    ]
    cands, seen = [], set()
    for path, cat, pat in pages:
        html = open(path, encoding="utf-8", errors="ignore").read()
        hs = headings(html)
        for m in re.finditer(pat, html, re.S | re.I):
            name, code = h.unescape(m.group(1)).strip(), m.group(2)
            if code in union or code in seen: continue
            seen.add(code)
            cands.append({"src_name": name, "code": code, "cat": cat,
                          "country": name_ctry("", name), "hd": heading_for(hs, m.start())[:60]})
    print(f"phase4 candidates after dedupe: {len(cands)}", flush=True)
    for c in cands: print("  cand:", c["src_name"][:40], c["code"], c["cat"], c["country"], c["hd"], flush=True)

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
        print(f"  [{i+1}] {c['code']} http={http_code} title={title[:40]!r}", flush=True)
        if not title: continue
        name = c["src_name"]
        if not name or name.strip().lower() in ("link", "join", "click here", "view invite", "join now", "join link", "join group", "join here"):
            name = title
        if P.porn_hit(name) or P.porn_hit(title):
            porn_drops += 1; continue
        name = name.strip()
        if not name or name.startswith("http"): name = title.strip()
        if not name: continue
        verified.append({"name": name, "category": c["cat"], "country": c["country"],
                         "description": P.make_desc(name, c["cat"], c["country"]),
                         "invite": "https://chat.whatsapp.com/" + c["code"], "image": ""})
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
    print(f"PHASE4 DONE: verified={len(final)} pending={len(pending)} porn_drops={porn_drops} rate_limited={rate_limited}", flush=True)

if __name__ == "__main__":
    main()
