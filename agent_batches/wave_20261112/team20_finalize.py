import json, re, glob, os
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
fresh=json.load(open(os.path.join(WD,"team20_fresh_raw.json")))
rows=[json.loads(l) for l in open(os.path.join(WD,"team20_recheck_ckpt.jsonl"))]
final={r["code"]:r for r in rows}
assert set(final)==set(fresh), (len(final), len(fresh))
PAGE_CAT={"karachi":"Community & Social","islamic":"Islamic","kurulus-osman":"Entertainment",
 "malayalam":"Community & Social","marriage":"Community & Social","online-earning":"Jobs",
 "pdf-books":"Education","pti":"News","pubg":"Gaming"}

def clean_label(label):
    if not label: return ""
    if "MENU Toggle" in label or "1000+" in label: return ""
    # label often "Name: description" -> take name part
    name=label.split(":")[0].strip()
    name=re.sub(r"\s+"," ",name)
    name=re.sub(r"(https?://\S+|\+?\d[\d\s\-]{7,}\d)","",name).strip()
    return name[:120]

def final_dedupe_check(code):
    union=set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
    if code in union: return False
    for f in glob.glob('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/*.json'):
        if 'team20' in f: continue
        txt=open(f,encoding='utf-8',errors='ignore').read()
        if code in txt: return False
    return True

candidates=[]; pending=[]; exclusions=[]
for code,r in sorted(final.items()):
    v=fresh[code]; page=v["page"]
    if r["status"]=="live":
        title=r["title"].strip()
        # CONTENT SCREEN
        low=title.lower()
        if "ebl" in low and ("earning" in low or "online" in low):
            exclusions.append({"code":code,"name":title,"reason":"SCAM: EBL Pakistan referral/online-earning scheme (paid join, earn-by-referring) - same family as dropped binary-option/AI-trading earning scams","page":page})
            continue
        if not final_dedupe_check(code):
            exclusions.append({"code":code,"name":title,"reason":"DEDUPED at finalize: already in union or banked by another wave-12 team","page":page})
            continue
        name=title
        cat=PAGE_CAT.get(page,"Community & Social")
        desc=f"Join {name}, a PDF books group for sharing and reading books." if page=="pdf-books" else f"Join {name}, an active WhatsApp group. Connect with members, share updates and stay in touch."
        candidates.append({"name":name,"category":cat,"country":v["country"],
                           "description":desc,"invite":f"https://chat.whatsapp.com/{code}"})
    elif r["status"]=="pending":
        nm=clean_label(v.get("label",""))
        pending.append({"name":nm,"category":PAGE_CAT.get(page,"Community & Social"),
                        "country":v["country"],
                        "description":(f"Join {nm}, an active WhatsApp group. Connect with members, share updates and stay in touch." if nm else ""),
                        "invite":f"https://chat.whatsapp.com/{code}",
                        "reason":r.get("reason","transport failure")})
    # dead: dropped silently (counted in summary)

json.dump(candidates, open(os.path.join(WD,"team20-77links-candidates.json"),'w'), ensure_ascii=False, indent=1)
json.dump(pending, open(os.path.join(WD,"team20-77links-pending.json"),'w'), ensure_ascii=False, indent=1)
json.dump([], open(os.path.join(WD,"team20-77links-leads.json"),'w'), indent=1)

from collections import Counter
fetch_log=json.load(open(os.path.join(WD,"team20_fetch_log.json")))
summary={
 "team":20,
 "slice":"77links.com Karachi/Islamic + 7 failed pages (kurulus-osman, malayalam, marriage, online-earning, pdf-books, pti, pubg)",
 "sources":[e["url"] for e in fetch_log],
 "fetch_log":fetch_log,
 "extracted_total":len(json.load(open(os.path.join(WD,"team20_all_extracted.json")))),
 "extracted_by_page":dict(Counter(v["page"] for v in json.load(open(os.path.join(WD,"team20_all_extracted.json"))).values())),
 "already_in_union":320,
 "already_verified_yesterday_team14":51,
 "already_banked_by_other_wave12_team":1,
 "fresh_to_verify":len(fresh),
 "fresh_by_page":dict(Counter(v["page"] for v in fresh.values())),
 "verified_kept":len(candidates),
 "pending":len(pending),
 "pending_by_page":dict(Counter(fresh[r["invite"].split("/")[-1]]["page"] for r in pending)),
 "pending_reasons":dict(Counter(r.get("reason","").split(":")[0] for r in pending)),
 "dead":sum(1 for r in final.values() if r["status"]=="dead"),
 "dead_by_page":dict(Counter(fresh[c]["page"] for c,r in final.items() if r["status"]=="dead")),
 "leads":0,
 "exclusions":exclusions,
 "controls":"live control KrDwdK8EIkB6vgauHg5M7N (groups.json) showed og:title 'JAY - PHP & Python Full Stack Developer'; fabricated code ZZZNotARealCode1234567890 showed empty og:title. NOTE: og:description is the generic 'WhatsApp Group Invite' on ALL pages (live and dead) and must never be used as a live fallback - first verify run mis-flagged the fake control via that fallback; fixed before verifying.",
 "rate_limit_note":"First verify pass (4 workers) hit HTTP 429 on 119/187 codes and mislabelled them dead; rechecked all 187 slowly (1 worker, then 3 workers, 2-3s sleeps, 20-30s backoff on 429). 74 codes still 429 after 2 spaced recheck attempts + 1 proxy transport failure = 75 pending. Do NOT call them dead.",
 "resume":"DONE: all 9 pages fetched 200 (all 7 failed pages recovered). 187 fresh codes verified: 1 kept, 110 dead, 75 pending (74x HTTP 429 + 1 proxy error). Next wave: retry the 75 pending codes in team20-77links-pending.json (spaced, low concurrency); re-fetch Karachi + Islamic + the 7 pages for new codes. Raw extraction team20_all_extracted.json; checkpoints team20_verify_ckpt.jsonl + team20_recheck_ckpt.jsonl. Karachi/Islamic/marriage pages yielded 0 fresh codes (all already in union or verified yesterday). Overlap code BcoHLF6PNplFc4FcPR0tAD already banked by another wave-12 team - not re-banked."
}
json.dump(summary, open(os.path.join(WD,"team20-77links-summary.json"),'w'), ensure_ascii=False, indent=1)
print("candidates",len(candidates),"pending",len(pending),"exclusions",len(exclusions))
print(json.dumps(candidates,indent=1,ensure_ascii=False))
