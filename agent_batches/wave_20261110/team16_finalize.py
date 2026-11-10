import json, os
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
details={d["gid"]:d for d in json.load(open(os.path.join(W,"team16_details.json")))}
prescreen={p["gid"]:p for p in json.load(open(os.path.join(W,"team16_prescreen.json")))}

# Consolidated verdicts (evidence across all passes):
# DEAD: HTTP 200 + empty og:title after >=2 spaced retries (run 1 and/or final pass)
dead={"315149","207356","962515","380628","593435","197480","430588","696815",
      "377833","856191","976715","792999","813979"}
# PENDING: transport-only, never got an HTTP status in any pass
pending={"791674","757428","175618","444836"}
# EXCLUDED
excluded={"187582":"og:title is 'Xxx group' (adult-sexual signal) + crypto-investment content",
          "638413":"WhatsApp channel (whatsapp.com/channel), not a group"}
dupe={g for g,p in prescreen.items() if p["status"]=="DUPE"}
assert len(dead|pending|set(excluded)|dupe)==30, (len(dead),len(pending),len(excluded),len(dupe))
assert not (dead & pending or dead & set(excluded) or pending & set(excluded) or (dead|pending) & dupe)

verified=[]  # 0 LIVE
pend=[]
DESC={
 "791674":"A vibrant community where friendships blossom and conversations flow freely, a welcoming space to meet new friends and expand your social circle.",
 "757428":"A friendly WhatsApp group for meeting new people, making friends and chatting with like-minded people from different backgrounds.",
 "175618":"A fun and friendly WhatsApp group where girls can connect, share experiences and enjoy each other's company.",
 "444836":"A WhatsApp group for romance, friendship and heartfelt connections, where conversations can spark new friendships.",
}
for gid in sorted(pending):
    d=details[gid]
    pend.append({"name":d["name"],"category":"Community & Social","country":"International",
                 "description":DESC[gid],
                 "invite":"https://chat.whatsapp.com/"+d["code"],
                 "reason":"transport failure (curl error/timeout, no HTTP status) on every verification attempt across 3 passes; code never resolved to a WhatsApp page"})
leads=[
 {"url":"https://grupbul.com/group/694872","note":"Srilankans group detail page found via web search (food-keyword match); NOT in Food/Chat-Friendship categories, unprocessed — out of slice, needs reassignment if wanted."},
 {"url":"https://grupbul.com/group/440817","note":"Tamil Jalsa group detail page found via web search (food-keyword match); NOT in Food/Chat-Friendship categories, unprocessed — out of slice."},
 {"url":"https://grupbul.com/group/729197","note":"Tamilnadu Girls group detail page found via web search (food-keyword match); NOT in Food/Chat-Friendship categories, unprocessed — out of slice."},
 {"url":"https://grupbul.com/group/875264","note":"USA RULES group detail page found via web search (food-keyword match); NOT in Food/Chat-Friendship categories, unprocessed — out of slice."},
 {"url":"https://grupbul.com/group/345633","note":"OFFICIAL TELUGU ADDA group detail page found via web search (food-keyword match); NOT in Food/Chat-Friendship categories, unprocessed — out of slice."},
 {"url":"https://grupbul.com/group/188774","note":"USA group detail page found via web search (food-keyword match); NOT in Food/Chat-Friendship categories, unprocessed — out of slice."},
 {"url":"https://grupbul.com/group/662627","note":"TIGER MAHARASTRA group detail page found via web search (food-keyword match); NOT in Food/Chat-Friendship categories, unprocessed — out of slice."},
]
excl_list=[{"code":details[g]["code"],"reason":r} for g,r in sorted(excluded.items())]
summary={
 "team":16,
 "slice":"grupbul Food + Chat/Friendship",
 "sources":["https://grupbul.com/en/category/whatsapp/53/food",
            "https://grupbul.com/en/category/whatsapp/15/chat-friendship",
            "https://grupbul.com/en/category/whatsapp/15/chat-friendship?page=2",
            "https://grupbul.com/en/category/whatsapp/53/food?page=2"],
 "verified":0,
 "pending":len(pend),
 "leads":len(leads),
 "dead":len(dead),
 "exclusions":excl_list,
 "resume":"Food category page returns an EMPTY listing on every fetch (page 1, ?page=2, /2, Turkish /tr/category/whatsapp/53/yemek) — no Food groups are listed there as of 2026-11-10; do not re-mine without re-checking the page. Chat/Friendship page 1 yields 27 groups; ?page=2 returns the IDENTICAL 27 (pagination param ignored) and /2 returns an empty template — no deeper pages reachable. 4 codes remain transport-only PENDING (791674 Sohbete gel, 757428 Arkadas tanisma, 175618 Girls Fun Masti, 444836 Romantic); re-verify them with a fresh slow pass, they never returned an HTTP status. 11 of 30 codes were already in the 108,365-code union (dupes). 0 verified live.",
 "notes":"Dedupe union was 108,365 codes (.existing_codes.json 108,364 + groups.json). All 30 candidate codes extracted via /group/<id> detail pages -> /redirect/<id>/<n> (HTTP refresh: header, 7s) -> chat.whatsapp.com code. Method validated against a known-live dupe code (Koak6SWE6Nf1QhaTV5vCtL returned og:title 'THE GLOBAL FAMILY'). 13 codes DEAD: HTTP 200 but empty og:title after >=2 spaced retries (WhatsApp's revoked/expired-invite response). WhatsApp verification was flaky throughout: frequent curl 000 (no HTTP status) — likely rate-limiting after many checks; 3 verification passes run (initial 3-parallel, retry, final slow sequential). One /tmp wipe mid-run lost intermediate state; all state was rebuilt and checkpointed in the work dir. Excluded: 187582 Nasi Lemak Bitcoin (og:title 'Xxx group' + crypto-investment pitch) and 638413 HomeCookingShow (WhatsApp channel, not a group). No Food groups found at all — the 3 food-ish candidates came from web search, not the category page."
}
json.dump(verified, open(os.path.join(W,"team16-grupbul.json"),"w"), ensure_ascii=False, indent=2)
json.dump(pend, open(os.path.join(W,"team16-grupbul-pending.json"),"w"), ensure_ascii=False, indent=2)
json.dump(leads, open(os.path.join(W,"team16-grupbul-leads.json"),"w"), ensure_ascii=False, indent=2)
json.dump(summary, open(os.path.join(W,"team16-grupbul-summary.json"),"w"), ensure_ascii=False, indent=2)
print("verified",len(verified),"pending",len(pend),"leads",len(leads),"dead",len(dead),"excl",len(excl_list),"dupe",len(dupe))
print("files written")
