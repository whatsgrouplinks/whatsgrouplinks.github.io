import json, re
pool1=json.load(open('team17_verify_pool.json'))
pool2=json.load(open('team17_verify_pool2.json'))
names=json.load(open('team17_listing_names.json'))
fresh=json.load(open('team17_fresh_raw.json'))
carry=json.load(open('team17_carryover.json'))
drops=json.load(open('team17_prescreen_drop.json'))
pool={**pool1, **pool2}
print('pool total:',len(pool),'| prescreen adult drops:',len(drops))

def cat_hint(code, nm, srcs):
    s=(nm or '').lower()
    if any(k in s for k in ['bgmi','pubg','free fire','gaming','game','esports','tournament']): return 'Gaming'
    if any(k in s for k in ['job','naukri','sarkari','recruitment','career']): return 'Jobs'
    if any(k in s for k in ['islam','quran','deen','muslim','hadees','madrasa']): return 'Islamic'
    if any(k in s for k in ['funny','meme','joke','masti','comedy']): return 'Funny'
    if any(k in s for k in ['friend','friendship','girls','girl']): return 'Friendship'
    if any(k in s for k in ['earn','earning','crypto','forex','signal','trading','money','invest']): return 'Online Earning'
    if any(k in s for k in ['movie','film','bollywood','drama','song','music']): return 'Entertainment'
    if any(k in s for k in ['cricket','football','sports','ipl']): return 'Sports'
    if any(k in s for k in ['study','course','exam','upsc','education','school','college','udemy']): return 'Education'
    if any(k in s for k in ['news']): return 'News'
    if any(k in s for k in ['buy','sell','shop','store','business']): return 'Buy Sell'
    if 'team22-carryover' in srcs: return 'Online Earning'
    return 'Community & Social'

pending=[]
for code,v in sorted(pool.items()):
    nm=names.get(code,'')
    pending.append({
        'code': code,
        'invite': f'https://chat.whatsapp.com/{code}',
        'listing_name': nm,
        'sources': v['sources'],
        'category_hint': cat_hint(code, nm, v['sources']),
        'reason': 'verification-unavailable',
        'detail': 'chat.whatsapp.com returns HTTP 200 + empty og:title generic JS shell for every client tested (desktop curl, mobile UA, cookie round-trip), identical for a known-live code (LsogFpLM5viKiCwXaap3US, live candidate Nov 8) and a garbage control code (ZZZZZZZZZZZZZZZZZZZZZZ); browser.open fetch is 403. Curl og:title check cannot discriminate live vs dead from this VM today. NOT marked dead; needs browser leg re-verification.'
    })
json.dump(pending, open('team17-pending.json','w'), ensure_ascii=False, indent=1)
json.dump([], open('team17-candidates.json','w'), ensure_ascii=False, indent=1)

leads=[
 {"url":"https://www.whatsgroup.in/","note":"22 categories; 108 fresh codes extracted Nov 9 (gaming BGMI/Free Fire, memes, movies, education, friendship); homepage mined, category sub-pages unmined"},
 {"url":"https://walink.pk/","note":"NEW directory; homepage adult-heavy (porn/sexy/xxx sections) — screen hard; 51 fresh codes, many adult-dropped; clean Pakistan/girls/funny sections worth browser leg"},
 {"url":"https://walink.pk/whatsapp-group-link-pakistan/","note":"Pakistan groups listing page"},
 {"url":"https://walink.pk/girls-whatsapp-group/","note":"Girls/friendship listing page; screen for adult content"},
 {"url":"https://walink.pk/category/whatsapp-group-links/","note":"Category index"},
 {"url":"https://www.grouplinksforyou.com/2023/03/1000-active-pakistani-whatsapp-group.html","note":"NEW directory; 51 fresh codes (Pakistan jobs/Islamic/friendship)"},
 {"url":"https://groupsnest.com/","note":"NEW directory; 1,495 links, Jobs + Islamic Pakistan collections; 8 fresh codes; structured collections, needs deeper mining"},
 {"url":"https://77links.com","note":"50+ categories, daily updates; 3 fresh codes this run; earning/crypto sections need screening"},
 {"url":"https://wtgrouplinks.com/","note":"16 fresh codes this run"},
 {"url":"https://freewagroup.com/","note":"Spanish/LatAm directory; 4 fresh codes (stickers, football, buy/sell, cinema)"},
 {"url":"https://groupwa.link/","note":"78 categories; 0 fresh codes Nov 9 — pool already in union (clone of mined directories)"},
 {"url":"https://wagroupshub.com/","note":"0 fresh codes Nov 9 — pool already in union"},
 {"url":"https://wagroupnest.com/","note":"0 fresh codes Nov 9 — pool already in union"},
 {"url":"https://instantgrouplink.com/","note":"0 fresh codes Nov 9 — pool already in union"},
 {"url":"https://activewagroup.com/pakistani-whatsapp-group-links/","note":"0 fresh codes Nov 9 — pool already in union"},
 {"url":"https://whtspgrouplink.com/","note":"3,900+ groups claimed; 0 fresh codes Nov 9 — pool already in union"},
 {"url":"https://whatstele.com/whatsapp/group-links/pakistani/","note":"300+ Pakistani groups; 0 fresh codes Nov 9 — pool already in union"},
 {"url":"https://whatsappgrouplink.org/","note":"Groupsor alternative; 0 fresh codes Nov 9 — pool already in union"},
 {"url":"https://groupinvitelink.com/","note":"Groupsor alternative; 0 fresh codes Nov 9 — pool already in union"},
 {"url":"https://groupsgyani.org/","note":"NEEDS-BROWSER-LEG: invite links behind /process/group/<id> redirects; homepage text fetch yielded no direct codes"},
 {"url":"https://groupwhat.com/","note":"NEEDS-BROWSER-LEG: curl returned empty page (JS-gated); top-rated Groupsor alternative, 10,000+ links claimed"},
 {"url":"https://whatgroups.com/","note":"NEEDS-BROWSER-LEG: curl returned 12KB JS shell only"},
 {"url":"https://www.edopedia.com/blog/groupsor-alternatives/","note":"Directory-of-directories: 10 Groupsor alternatives incl. GroupWhat, WhatsAppGroupLink.org, GroupInviteLink, WhatGroups, Groupsor.in, GroupsLink.pk, WhatsGroupJoinLinks.com, WhtspGroupLink"},
 {"url":"https://www.whtsagrouplinks.com/","note":"Already mined heavily in prior waves; 0 fresh codes Nov 9"},
 {"url":"https://grouplink.com.in","note":"team22 Nov 8 source; 14 Funny/Friendship + sub4sub codes carried over (now in team17-pending.json); 72 crypto/earning codes also carried over"},
]
json.dump(leads, open('team17-leads.json','w'), ensure_ascii=False, indent=1)

from collections import Counter
summary={
 "team":"team17",
 "slice":"Fresh web search for NEW WhatsApp group directories — South Asia focus (wave_20261109)",
 "sources":[
   "groupwa.link","wagroupshub.com","wagroupnest.com","instantgrouplink.com","activewagroup.com",
   "walink.pk (+5 sub-pages)","whatsgroup.in","groupsgyani.org","wtgrouplinks.com","freewagroup.com",
   "whtspgrouplink.com","groupsnest.com","whatstele.com","grouplinksforyou.com","77links.com",
   "whatsappgrouplink.org","groupinvitelink.com","whatgroups.com","groupwhat.com","edopedia.com/groupsoralternatives",
   "team22 Nov 8 carry-over (grouplink.com.in + 77links/crypto)"
 ],
 "extracted_total": 2008,
 "already_in_union": 1768,
 "fresh_extracted": 240,
 "team22_carryover_fresh": 86,
 "prescreen_adult_dropped": len(drops),
 "verify_pool": len(pool),
 "verified": 0,
 "pending": len(pending),
 "leads": len(leads),
 "dead": 0,
 "notes":[
   "VERIFICATION BLOCKED (environment, not data): curl to chat.whatsapp.com returns HTTP 200 + empty og:title + generic 'WhatsApp Group Invite' shell for EVERY code tested, across desktop UA, mobile UA, and cookie round-trip. Control tests: (a) LsogFpLM5viKiCwXaap3US — live candidate Nov 8 — empty title; (b) garbage code ZZZZZZZZZZZZZZZZZZZZZZ — identical 200 + empty title; (c) fresh whatsgroup.in code Ei5y4yo1SH7DXnCiMueg6D — empty title. Pages are identical JS shells (group data loads client-side). browser.open fetch of an invite URL is 403. Team15 same wave also found 0 live / 76 with the same method. Therefore NO code was marked dead and NO candidate was claimed verified — all 307 pool codes are pending for a browser leg. Marking them dead on this signal would be false.",
   "Fresh directories found and mined: whatsgroup.in (108 fresh), walink.pk (51 fresh, homepage adult-heavy — 18 adult listing names pre-screen-dropped, rest pending), grouplinksforyou.com (51 fresh), wtgrouplinks.com (16), groupsnest.com (8), freewagroup.com (4), 77links.com (3). groupwa.link / wagroupshub / wagroupnest / instantgrouplink / activewagroup / whtspgrouplink / whatstele / whatsappgrouplink.org / groupinvitelink.com contributed 0 fresh — their pools are already in the 106,883-code union.",
   "Team22 carry-over mined as instructed: 14 Funny/Friendship grouplink.com.in codes (skip_oos list) + 72 crypto/earning codes (todo list) = 86 fresh vs union (1 already in union). All 86 are in pending (unverified); crypto-signal ones need scam screening on og:title at browser-leg stage (VIP-signals / free-airdrop style pitches drop per rules).",
   "NEEDS-BROWSER-LEG: groupwhat.com (empty curl response), groupsgyani.org (/process/group/<id> redirects), whatgroups.com (JS shell). All banked in team17-leads.json.",
   "walink.pk porn/sexy/xxx/viral-video section URLs deliberately NOT banked as leads.",
   "Work files: team17_raw/ (25 fetched pages), team17_extracted_raw.json, team17_fresh_raw.json, team17_listing_names.json, team17_verify_pool.json, team17_verify_pool2.json, team17_prescreen_drop.json, team17_verify_evidence.json."
 ]
}
json.dump(summary, open('team17-summary.json','w'), ensure_ascii=False, indent=1)
print('pending:',len(pending),'leads:',len(leads))
print(Counter(p['category_hint'] for p in pending))
