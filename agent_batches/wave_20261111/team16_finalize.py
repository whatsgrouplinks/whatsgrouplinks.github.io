import json, os
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"

# Final verdicts = latest checkpoint state per gid (ckpt2 overrides ckpt)
state={}
for fn in ("team16_ckpt.jsonl","team16_ckpt2.jsonl"):
    p=os.path.join(W,fn)
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line=line.strip()
            if line:
                e=json.loads(line); state[e["gid"]]=e
assert len(state)==10, len(state)
from collections import Counter
print(Counter(e["status"] for e in state.values()))

# Nov-10 pendings re-verified this run: all DEAD
reverify=json.load(open(os.path.join(W,"team16_pending_reverify.json")))
assert all(r["verify"]=="DEAD" for r in reverify), reverify
dead_old=[r for r in reverify]

# Pending (transport-only / no-code) this run: 5 fresh
pend_order=["440817","865745","219135","662627","400673"]
CAT={"440817":"Community & Social","865745":"Community & Social","219135":"Community & Social",
     "662627":"Community & Social","400673":"Friendship"}
COUNTRY={"440817":"","865745":"IN","219135":"","662627":"IN","400673":""}
pend=[]
for gid in pend_order:
    e=state[gid]
    assert e["status"]=="PENDING", (gid, e["status"])
    entry={"name":e["name"],"category":CAT[gid],"country":COUNTRY[gid],
           "description":e["desc"]}
    if e.get("code"):
        entry["invite"]="https://chat.whatsapp.com/"+e["code"]
    entry["reason"]=e["reason"]+f" (grupbul group id {gid}; re-verify the code / re-follow the redirect after a longer cool-down)"
    pend.append(entry)

verified=[]  # 0 live

leads=[
 {"url":"https://grupbul.com/group/621903","note":"GARIBO KI MADAD KARO charity group, food-keyword match via web search only; OUT OF SLICE (charity, not Food/Chat-Friendship), unprocessed."},
 {"url":"https://grupbul.com/group/419221","note":"ISKCON DELHI 03 spiritual group, food-keyword match via web search only; OUT OF SLICE (spiritual, not Food/Chat-Friendship), unprocessed."},
]

summary={
 "team":16,
 "slice":"grupbul Food + Chat/Friendship deeper pages",
 "sources":[
  "https://grupbul.com/en/category/whatsapp/53/food",
  "https://grupbul.com/en/category/whatsapp/53/food?page=2",
  "https://grupbul.com/en/category/whatsapp/53/food?page=3",
  "https://grupbul.com/en/category/whatsapp/53/food/2",
  "https://grupbul.com/tr/category/whatsapp/53/yemek",
  "https://grupbul.com/en/category/whatsapp/53/food?sort=newest",
  "https://grupbul.com/en/category/whatsapp/15/chat-friendship",
  "https://grupbul.com/en/category/whatsapp/15/chat-friendship?page=2",
  "https://grupbul.com/en/category/whatsapp/15/chat-friendship?page=3",
  "https://grupbul.com/en/category/whatsapp/15/chat-friendship?page=4",
  "https://grupbul.com/en/category/whatsapp/15/chat-friendship/2",
  "https://grupbul.com/en/category/whatsapp/15/chat-friendship/page/2",
  "https://grupbul.com/en/category/whatsapp/15/chat-friendship?sort=newest",
  "https://grupbul.com/group/694872","https://grupbul.com/group/440817",
  "https://grupbul.com/group/729197","https://grupbul.com/group/875264",
  "https://grupbul.com/group/345633","https://grupbul.com/group/188774",
  "https://grupbul.com/group/662627","https://grupbul.com/group/865745",
  "https://grupbul.com/group/219135","https://grupbul.com/group/400673"
 ],
 "verified":0,
 "pending":len(pend),
 "leads":len(leads),
 "dead":len(dead_old),
 "exclusions":[],
 "resume":"Food category page STILL returns zero groups on every fetch (p1, ?page=2, ?page=3, /2, Turkish, ?sort=newest) — 0 /group/ links in the HTML; no Food groups listed as of 2026-11-11. Chat/Friendship is capped at the SAME 27 groups as Nov-10: ?page=2/3/4 and ?sort=newest return byte-identical 27, /2 and /page/2 return an empty template, and the page carries no pagination markup — no deeper pages exist and no new groups appeared. All 27 Chat gids are now fully resolved across the two runs (11 dupes + 12 dead Nov-10, 4 Nov-10 pendings now DEAD Nov-11). Fresh work this run: 10 food-keyword candidates (7 Nov-10 leads + 3 new web-search finds) -> 5 dupes, 5 pending, 0 live. NEXT RUN: re-verify the 3 transport-pending codes (440817 ACtQYie1P32IceedwfPY9p, 865745 I39fLwOHZ730XJ5glkcE82, 219135 58IfJaAavCGId7CEz0vNJH) and re-follow the 2 failed redirects (662627 /redirect/662627/1325254, 400673 /redirect/400673/801346) ONLY after a long cool-down — WhatsApp returned http 000 on all 15 retry attempts and grupbul /redirect returned empty/proxy-only responses by end of run (both endpoints rate-limiting). Do NOT re-mine the Food/Chat category pages without re-checking them first; they are empty/capped.",
 "notes":"Dedupe union was 108,993 codes (.existing_codes.json 108,992 + groups.json). Fresh dupes (5): Srilankans KcfWgEC9OuO98QgG3AZlj2, Tamilnadu Girls IbYavWgwRKyHawlfNODQ5D, USA RULES 0si2UWAUSMb0WUqqRTOHt7, OFFICIAL TELUGU ADDA FOEeowUwhz11L7lT0I2Xd0, USA FIE1xZwG7iO1dTRn6oMpah. Fresh pending (5): Tamil Jalsa + Mumbaikar! + I Like India = WhatsApp transport failure (http 000, 3 attempts x 2 passes = 6 attempts each, never an HTTP status); TIGER MAHARASTRA + Yaar Beli = no invite code extracted (detail page fetched, redirect URL found, but /redirect follow returned empty on 2+3 attempts). Nov-10 pendings resolved DEAD this run (4): Sohbete gel H3H6SCPltU22xsKwEtM97A, Arkadas tanisma EuosowMQIqe833l9le383G, Girls Fun Masti Bo6Splc8d3oC3gr4xf0UA2, Romantic FlFcwNtXfzP0DB52GQ7uZ4 — each HTTP 200 + empty og:title on 3 spaced attempts. No fresh exclusions: no scam/adult signals in any banked name or og:title seen (no og:title was ever returned for a fresh candidate); Nov-10 exclusions (Nasi Lemak Bitcoin, HomeCookingShow channel) stand and were not re-processed. No verified groups this run; verified file is an empty list. Country: 'IN' only where the group is place-tied (Mumbaikar!/Mumbai, TIGER MAHARASTRA/Maharashtra), else ''."
}
json.dump(verified, open(os.path.join(W,"team16-grupbul.json"),"w"), ensure_ascii=False, indent=2)
json.dump(pend, open(os.path.join(W,"team16-grupbul-pending.json"),"w"), ensure_ascii=False, indent=2)
json.dump(leads, open(os.path.join(W,"team16-grupbul-leads.json"),"w"), ensure_ascii=False, indent=2)
json.dump(summary, open(os.path.join(W,"team16-grupbul-summary.json"),"w"), ensure_ascii=False, indent=2)
print("verified",len(verified),"pending",len(pend),"leads",len(leads),"dead",len(dead_old),"excl 0")
print("files written")
