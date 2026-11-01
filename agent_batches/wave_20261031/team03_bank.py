#!/usr/bin/env python3
"""team03: bank partial OR final results from /tmp/team03_progress.json."""
import json, re, html, os

OUT = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261031"
prog = json.load(open("/tmp/team03_progress.json"))
cands = {c["code"]: c for c in json.load(open("/tmp/team03_cands.json"))}
total = len(json.load(open("/tmp/team03_cands.json")))

PHONE = re.compile(r'\+?\d[\d\s\-\(\)]{7,}\d')

def clean_desc(d, name, cat, cc):
    d = html.unescape(d or "")
    d = re.sub(r'https?://\S+', '', d)
    d = re.sub(r'(?i)join\s+(whatsapp\s+)?(group|chat)\s*:?\s*', '', d)
    d = PHONE.sub('', d)
    d = re.sub(r'[*_~`#]', '', d)
    d = re.sub(r'\s{2,}', ' ', d).strip(' .,;:-')
    if not d or len(d) < 20:
        cc_name = {'IN':'India','PK':'Pakistan','NG':'Nigeria','US':'United States'}.get(cc, '')
        loc = f" in {cc_name}" if cc_name else ""
        d = f"{name}: a {cat.lower()} WhatsApp group{loc} — chat, share updates and connect with members."
    return d[:240]

verified, pending = [], []
done_count = 0
for code, (st, title) in prog.items():
    c = cands.get(code)
    if not c:
        continue
    done_count += 1
    if st == "live":
        name = PHONE.sub('', c["name"]).strip()
        name = re.sub(r'\S+@\S+\.\S+', '', name)
        name = re.sub(r'\s{2,}', ' ', name).strip(' .,;:-') or title
        verified.append({
            "name": name,
            "category": c["cat"],
            "description": clean_desc(c["desc"], name, c["cat"], c["cc"]),
            "image": "",
            "invite": f"https://chat.whatsapp.com/{code}",
            "country": c["cc"],
        })
    elif st in ("pending", "transport"):
        pending.append({
            "name": c["name"],
            "category": c["cat"],
            "description": clean_desc(c["desc"], c["name"], c["cat"], c["cc"]),
            "image": "",
            "invite": f"https://chat.whatsapp.com/{code}",
            "country": c["cc"],
            "note": "transport failure",
        })

json.dump(verified, open(f"{OUT}/team03-groupor-jobs-business.json", "w"), ensure_ascii=False, indent=1)
if pending:
    json.dump(pending, open(f"{OUT}/team03-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
elif os.path.exists(f"{OUT}/team03-unverified-pending.json"):
    os.remove(f"{OUT}/team03-unverified-pending.json")

leads = [{
    "domain": "www.groupor.link",
    "url": "https://www.groupor.link/group/find?category=jobs-career",
    "why": f"team03 resume: {total - done_count}/{total} candidates NOT yet verified (run stopped after {done_count} verified). Re-fetch the 4 assigned categories (jobs-career, business-advertising-marketing, money-earning, news-magazines-politics) from a fresh crawl; skip codes already in the wave-20261031 union + team03 verified file. Remaining unverified candidate codes are embedded in the 2026-10-31 crawl saved by team03; progress state was in /tmp/team03_progress.json (ephemeral).",
}]
json.dump(leads, open(f"{OUT}/team03-leads.json", "w"), ensure_ascii=False, indent=1)

print(f"banked: verified={len(verified)} pending={len(pending)} done={done_count}/{total}")
for v in verified[:5]:
    print("  +", v["name"][:60], "|", v["invite"][-22:])
