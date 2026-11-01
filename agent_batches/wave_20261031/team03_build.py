#!/usr/bin/env python3
"""team03: build final JSON files from verify results (bank partial or final)."""
import json, re, html, os, sys

OUT = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261031"
res = json.load(open("/tmp/team03_verify_result.json"))
cands = {c["code"]: c for c in json.load(open("/tmp/team03_cands.json"))}

PHONE = re.compile(r'\+?\d[\d\s\-\(\)]{7,}\d')

def clean_desc(d, name, cat, cc_name):
    d = html.unescape(d or "")
    d = re.sub(r'https?://\S+', '', d)
    d = re.sub(r'(?i)join\s+(whatsapp\s+)?(group|chat)\s*:?\s*', '', d)
    d = PHONE.sub('', d)
    d = re.sub(r'[*_~`#]', '', d)
    d = re.sub(r'\s{2,}', ' ', d).strip(' .,;:-')
    d = d.replace('&amp;', '&')
    if not d or len(d) < 20:
        loc = f" in {cc_name}" if cc_name else ""
        d = f"{name}: a {cat.lower()} WhatsApp group{loc} — chat, share updates and connect with members."
    if len(d) > 240:
        d = d[:237] + "..."
    return d

CC_NAME = {'IN':'India','PK':'Pakistan','NG':'Nigeria','US':'United States'}

verified_items = []
for cand, ogtitle in res["verified"]:
    code = cand["code"]
    name = cand["name"].strip()
    # prefer og:title when source name is empty; otherwise keep source name
    if ogtitle and len(ogtitle) > 3 and ogtitle.lower() not in ("whatsapp group invite",):
        # use og:title only if source name is missing; source names here are clear
        pass
    # sanitize name: strip phones, emails
    name = PHONE.sub('', name)
    name = re.sub(r'\S+@\S+\.\S+', '', name)
    name = re.sub(r'\s{2,}', ' ', name).strip(' .,;:-')
    if not name:
        name = ogtitle
    desc = clean_desc(cand["desc"], name, cand["cat"], CC_NAME.get(cand["cc"], ""))
    verified_items.append({
        "name": name,
        "category": cand["cat"],
        "description": desc,
        "image": "",
        "invite": f"https://chat.whatsapp.com/{code}",
        "country": cand["cc"],
    })

json.dump(verified_items, open(f"{OUT}/team03-groupor-jobs-business.json", "w"), ensure_ascii=False, indent=1)

pending = []
for p in res["pending"]:
    c = p["cand"]
    pending.append({
        "name": c["name"],
        "category": c["cat"],
        "description": c["desc"][:240],
        "image": "",
        "invite": f"https://chat.whatsapp.com/{c['code']}",
        "country": c["cc"],
        "note": p["note"],
    })
if pending:
    json.dump(pending, open(f"{OUT}/team03-unverified-pending.json", "w"), ensure_ascii=False, indent=1)
elif os.path.exists(f"{OUT}/team03-unverified-pending.json"):
    os.remove(f"{OUT}/team03-unverified-pending.json")

# leads: pagination / remaining categories resume point
leads = []
remaining = 447 - sum(1 for _ in open("/tmp/team03_progress.json").read().count('"') and [1] or [])
leads.append({
    "domain": "www.groupor.link",
    "url": "https://www.groupor.link/group/find?category=jobs-career",
    "why": "team03 resume point: re-fetch these 4 categories (jobs-career, business-advertising-marketing, money-earning, news-magazines-politics) next wave; unverified codes saved in team03-unverified-pending.json with notes. All 461 extracted records from 2026-10-31 07:0x UTC crawl are deduped against the wave union in this run.",
})
json.dump(leads, open(f"{OUT}/team03-leads.json", "w"), ensure_ascii=False, indent=1)

print("verified items:", len(verified_items))
print("pending:", len(pending))
print("sample:", verified_items[0]["name"] if verified_items else None)
