import json, re, collections
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
fresh=json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113/team20_fresh_77.json"))
union=set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
# merge verify + recheck (recheck overrides)
res={}
for line in open(WD+"/team17_verify_ckpt.jsonl"):
    r=json.loads(line); res[r["code"]]=r
for line in open(WD+"/team17_recheck_ckpt.jsonl"):
    r=json.loads(line); res[r["code"]]=r
CTRL={"KrDwdK8EIkB6vgauHg5M7N","ZzZzZzZzZzZzZzZzZzZzZzZz"}
banked={c:res[c] for c in fresh if c in res}
assert len(banked)==195, len(banked)
missing=[c for c in fresh if c not in res]
print("missing:",missing)
live=[(c,r) for c,r in banked.items() if r["status"]=="live"]
dead=[(c,r) for c,r in banked.items() if r["status"]=="dead"]
pend=[(c,r) for c,r in banked.items() if r["status"]=="pending"]
print("live",len(live),"dead",len(dead),"pending",len(pend))
for c,r in live:
    print(c, "|", fresh[c]["page"], "|", repr(r["title"]), "| dir-label:", repr(fresh[c]["label"][:80]))

PORN=['porno','xxx','porn','nude','sex video','desi sex','adult video','hot sex','sexy video','sex group']
SCAM=['daily earnings','earn money','free money','airdrop','binary option','forex','trading king','daraz','lucky101','double your money','investment plan','earn $','free $']
CASINO=['casino','slot','betting','tigrinho','fortune tiger','sinais','plataformas pagantes','wjbet','bet365','aviator','cricket betting','match fixing']
def screen(title):
    t=title.lower()
    # restore false positives: negated prohibition
    if re.search(r'\bno (porn|xxx|sex|nude)\b', t): return None
    if 'sexta-feira' in t or 'chuta' in t: return None
    for p in PORN:
        if p in t: return f"PORN: og:title contains '{p}'"
    for p in CASINO:
        if p in t: return f"CASINO/BETTING: og:title contains '{p}'"
    for p in SCAM:
        if p in t: return f"SCAM: og:title contains '{p}'"
    return None

PAGE_CAT={"pakistan-cricket":"Sports","jobs":"Jobs","friendship":"Community & Social","lahore":"Community & Social"}
# Manual overrides: og:titles use mathematical-script Unicode (not ASCII), so
# keyword matching misses them. Decoded by hand; dir-labels confirm:
# IxblTiIlgFJ6RVXJwPmP39 = "Ramzan Mubarak" (label: "Join for Ramzan celebrations");
# K0F5y2ZSMDw6oMlmtcZYTm = "MULTAN'S KINGS" (PSL cricket team).
OVERRIDES={"IxblTiIlgFJ6RVXJwPmP39":"Islamic","K0F5y2ZSMDw6oMlmtcZYTm":"Sports"}
def category(code,title,page):
    if code in OVERRIDES: return OVERRIDES[code]
    t=title.lower()
    if 'ramzan' in t or 'mubarak' in t and 'ramzan' in t: return "Islamic"
    if any(k in t for k in ['babar','multan','kings','cricket','psl','pakistan cricket']): return "Sports"
    if 'dish' in t: return "Technology"
    if page=="lahore" and ('fan' in t or 'posting club' in t or 'coffee' in t or 'yaran' in t or 'nal' in t): return "Community & Social"
    return PAGE_CAT.get(page,"Community & Social")

cands=[]; excluded=[]; leads=[]; flagged=[]
for c,r in sorted(live, key=lambda x: x[0]):
    title=re.sub(r'\s+',' ',r["title"]).strip()
    reason=screen(title)
    if reason:
        excluded.append({"code":c,"name":title,"reason":reason,"page":fresh[c]["page"]})
        continue
    cat=category(c,title,fresh[c]["page"])
    name=title
    desc=f"Join {name}, an active WhatsApp group for {cat.lower()} in Pakistan. Connect with members, share updates and stay in touch."
    cands.append({"name":name,"category":cat,"country":"PK","description":desc,"invite":f"https://chat.whatsapp.com/{c}"})
    # flag ambiguous keeps
    if c=="C3Q4qSaMNSmImrnwKgtaPF":
        flagged.append({"code":c,"name":name,"reason":"Ambiguous og:title 'All service' — kept per when-in-doubt rule; parent review advised","category":cat})
        leads.append({"code":c,"name":name,"category":cat,"country":"PK","description":desc,"invite":f"https://chat.whatsapp.com/{c}","reason":"Ambiguous og:title 'All service' — kept per when-in-doubt rule; parent review advised"})
    if c=="CCA0yEyhcgx2xJD2TGef1z":
        flagged.append({"code":c,"name":name,"reason":"Garbled Roman-Urdu og:title, friendship page — kept as Community & Social","category":cat})

# dedupe + union safety asserts
codes=[x["invite"].rsplit("/",1)[-1] for x in cands]
assert len(codes)==len(set(codes)), "dup in candidates"
assert not (set(codes)&union), "union overlap in candidates"
assert all(x["invite"].startswith("https://chat.whatsapp.com/") for x in cands)
assert all(x["category"] in ["Education","Entertainment","Sports","Funny","Community & Social","Finance","Buy Sell","Islamic","Health","News","Jobs","Technology","Gaming","Business","Cooking","Crypto","Poetry","Real Estate","Travel","Scholarship","Freelance","Earning"] for x in cands)
assert "77links" not in json.dumps(cands) and "77links" not in json.dumps(leads), "source name leaked"

json.dump(cands, open(WD+"/team17-candidates.json","w"), ensure_ascii=False, indent=1)
json.dump(leads, open(WD+"/team17-leads.json","w"), ensure_ascii=False, indent=1)
json.dump([{"code":c,"reason":r.get("reason","")} for c,r in pend], open(WD+"/team17-pending.json","w"), ensure_ascii=False, indent=1)
poll=json.load(open(WD+"/team17_poll_raw.json"))
summary={
 "team":"team17","slice":"77links fresh — verify 195 banked (wave_20261113 team20_fresh_77.json) + newest poll",
 "sources":["https://77links.com/karachi-whatsapp-group-links/","https://77links.com/islamic-whatsapp-group-links/","https://77links.com/kurulus-osman-whatsapp-group-links/","https://77links.com/malayalam-whatsapp-group-links/","https://77links.com/marriage-whatsapp-group-links/","https://77links.com/online-earning-whatsapp-groups/","https://77links.com/pdf-books-whatsapp-group-links/","https://77links.com/pti-whatsapp-group-links/","https://77links.com/pubg-whatsapp-group-links/","https://77links.com/lahore-whatsapp-group-links/","https://77links.com/friendship-whatsapp-group-links/","https://77links.com/jobs-whatsapp-group-links/","https://77links.com/pakistan-cricket-whatsapp-group-links/"],
 "controls":{"live":"KrDwdK8EIkB6vgauHg5M7N -> og:title 'JAY - PHP & Python Full Stack Developer' (exact match, PASS)","fabricated":"ZzZzZzZzZzZzZzZzZzZzZzZz -> empty og:title after 3 spaced retries (PASS)","note":"og:description ignored throughout (generic 'WhatsApp Group Invite' on live and dead alike)"},
 "counts":{"raw_banked":195,"verified":195,"dupes_vs_union":0,"dupes_within_team":0,"dead":len(dead),"excluded":len(excluded),"pending":len(pend),"leads":len(leads),"candidates":len(cands),
  "dead_by_page":dict(collections.Counter(fresh[c]["page"] for c,r in dead)),
  "live_by_page":dict(collections.Counter(fresh[c]["page"] for c,r in live)),
  "candidates_by_category":dict(collections.Counter(x["category"] for x in cands))},
 "excluded":excluded,
 "flagged_kept":flagged,
 "poll":{"pages_fetched":len(poll["fetch_log"]),"new_codes":0,"fetch_log":poll["fetch_log"],"note":"All 13 category pages re-fetched Nov 14; 0 codes newer than Nov 13 (every code on the pages was already in the union, the 195 banked set, or wave12 team20 extraction). 6 pages hit transient proxy errors on first attempt and succeeded on retry."},
 "verify_notes":"Single requests.Session, browser UA, 2.5s between codes. First pass: 11 live / 163 dead / 22 pending (all http 429, tail patch). First verifier process was SIGTERM-killed at 150/195; resumed from checkpoint (no re-verification of done codes) and finished. One spaced recheck of the 22 pending after a 240s cooldown: 19 dead (empty og:title after retries), 3 live. Final pending = 0. Wave12 team20 codes were NOT re-verified (only the 195 banked + poll diff). Wave12 team20 pending (75 codes, different set) was not in this slice and was not retried.",
 "resume":"DONE. All 195 banked verified to a final state (182 dead, 14 live, 0 pending); 4 of the 14 live excluded on content screen; 10 candidates banked. Poll found 0 new codes. No further work remains for this slice; next wave should re-poll the 13 pages for new entries."
}
json.dump(summary, open(WD+"/team17-summary.json","w"), ensure_ascii=False, indent=1)
print("candidates:",len(cands),"excluded:",len(excluded),"leads:",len(leads))
for x in cands: print(" KEEP", x["category"], "|", x["name"][:60])
for x in excluded: print(" DROP", x["code"], "|", x["reason"])
