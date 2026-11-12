#!/usr/bin/env python3
"""Team19 wave 20261112: write candidates/pending/leads/summary. Zero fresh non-Adult groups."""
import json, os
WORK="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
RAW=os.path.join(WORK,"team19_raw")
excl=json.load(open(f"{RAW}/exclusions_scan.json"))
controls=json.load(open(f"{RAW}/controls.json"))
window=json.load(open(f"{RAW}/all_notag_window.json"))
p2=json.load(open(f"{RAW}/notag_p2.json"))

candidates=[]
pending=[]
leads=[
 {"note":"WORKING newest-first feed (no tag param): page 1 spans 2026-11-08..2026-11-12; poll until created_at < cutoff. Page 2 spans 2026-11-05..2026-11-08, max 2026-11-08 06:08 — nothing fresher than yesterday's newest there.","url":"https://api.groupjoin.link/groups?page=1&limit=20&safeSearch=blur"},
 {"note":"Homepage listing (JS-rendered, backed by the same API). Detail pages /group/<group_uid> return HTTP 200 — usable for content screening if a title is ambiguous.","url":"https://groupjoin.link/"},
 {"note":"STALE — tag=onlynew feed is Adult-only, May-Aug 2026 items; do not use as the 'new' source.","url":"https://api.groupjoin.link/groups?tag=onlynew&page=1&limit=20&safeSearch=blur"},
]
exclusions=[
 {"code":"EFAp0cvM6WJAM36g4k2boh","reason":"Adult category dropped wholesale (hard rule this wave). Title 'Sell lill vdio', created 2026-11-12 05:50 — the only item newer than yesterday's newest on the whole feed; also a porn-video-selling title, doubly excluded. NOT verified/banked."},
 {"code":"Bfn5q5D7yXgDoqjjteQ6or","reason":"Adult category dropped wholesale. Title 'Collectionz aunty', created 2026-11-11 18:29 (newer than yesterday's run). NOT verified/banked."},
 {"code":"LGmitOjn68iCGRHQWDEbZr","reason":"Adult category dropped wholesale. Title '11yπ$', created 2026-11-11 14:40 (newer than yesterday's run). NOT verified/banked."},
 {"code":"IuLIZTcOmehGQ8lSnT0fko","reason":"Adult category dropped wholesale. Title 'HOTBABY', created 2026-11-11 14:06 (newer than yesterday's run). NOT verified/banked."},
 {"code":"C9BRC2yDkizLr4y9kMsCv7","reason":"Adult category dropped wholesale (title 'Nosto may', created 2026-11-11 05:12) — also yesterday's team13 banked code, so already processed; not re-banked."},
]
summary={
 "team":19,
 "slice":"groupjoin.link newest poll (no tag param), fresh since yesterday's newest (2026-11-11 05:12:31)",
 "verified":0,
 "pending":0,
 "leads":len(leads),
 "exclusions":exclusions,
 "dead":0,
 "controls":{
   "live":"KrDwdK8EIkB6vgauHg5M7N returned HTTP 200 + og:title 'JAY - PHP & Python Full Stack Developer' (matches yesterday) — method valid",
   "fabricated":"ZZZZZZZZZZZZZZZZZZZZ99 returned HTTP 200 + empty og:title — correctly dead",
   "detail":controls,
 },
 "notes":"ZERO fresh non-Adult groups on this feed today. Page 1 (20 items, 2026-11-08..2026-11-12) contains exactly 5 items newer than yesterday's newest (2026-11-11 05:12:31) and ALL 5 are groupjoin Adult category, dropped wholesale per this wave's hard rule (never fetch/verify/bank Adult). The single Nov-12 item ('Sell lill vdio') is Adult. Page 2 checked as a guard (feed ordering verified descending): 20 items, 2026-11-05..2026-11-08, max 2026-11-08 06:08 — nothing fresher. Non-Adult items on page 1 (Business GB ADOY MARKET, Money SHEYI LEGIT ONLINE UPDATE, Entertainment Online Celebs, Business Digital Card Trading) are all dated 2026-11-08/09, i.e. older than yesterday's newest and outside this slice's fresh window; not verified or banked. No transport failures, no pending items, no scams banked. API: first page-1 attempt returned http 000 twice (transport flake) then succeeded on retry; 4s+ spacing kept, no 429s.",
 "sources":[
   "https://api.groupjoin.link/groups?page=1&limit=20&safeSearch=blur",
   "https://api.groupjoin.link/groups?page=2&limit=20&safeSearch=blur",
 ],
 "resume":"Next run: poll https://api.groupjoin.link/groups?page=N&limit=20&safeSearch=blur (NO tag param — newest-first) starting page 1 until created_at < cutoff date; keep 4s+ spacing (API 429s on bursts). Fresh = created_at > 2026-11-12 05:50:38 (this run's newest seen). Dedupe against .existing_codes.json + yesterday's banked codes (C9BRC2yDkizLr4y9kMsCv7, HJS2ZkSzI99B7ldzHA7rhW) + this run's Adult drops (EFAp0cvM6WJAM36g4k2boh, Bfn5q5D7yXgDoqjjteQ6or, LGmitOjn68iCGRHQWDEbZr, IuLIZTcOmehGQ8lSnT0fko) before verifying; verify via chat.whatsapp.com og:title with a known-live control code each run; screen detail page /group/<group_uid> when a title is ambiguous. HARD RULE: never fetch, verify, or bank anything from the groupjoin.link Adult category.",
 "resume_point":{"newest_created_at_seen":"2026-11-12 05:50:38","last_page_polled":2,"page1_date_range":"2026-11-08..2026-11-12","page2_date_range":"2026-11-05..2026-11-08"},
}
json.dump(candidates,open(f"{WORK}/team19-groupjoin-candidates.json","w"),ensure_ascii=False,indent=1)
json.dump(pending,open(f"{WORK}/team19-groupjoin-pending.json","w"),ensure_ascii=False,indent=1)
json.dump(leads,open(f"{WORK}/team19-groupjoin-leads.json","w"),ensure_ascii=False,indent=1)
json.dump(summary,open(f"{WORK}/team19-groupjoin-summary.json","w"),ensure_ascii=False,indent=1)
print("FILES_WRITTEN verified=0 pending=0 leads=3 exclusions=5")
