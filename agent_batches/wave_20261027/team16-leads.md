# Team16 — Italy — Wave 20261027

## Counts
- Verified (fresh): 2
- Unverified / pending: 2
- Candidates examined: 13
- Dropped as duplicates: 9 (already in groups.json ∪ .existing_codes.json, union = 73,170 codes)

## Verified
- Chapter35 (Friendship, Rome 35+ social) — HTTP 200, og:title "Chapter35"
- WASZP Eurocup Italia Cup Univela (Sports, Campione del Garda sailing) — HTTP 200, og:title "WASZP EUROCUP - ITALIACUP UNIVELA"

## Pending (HTTP 200 but empty og:title — strict rule, so NOT verified)
- Solar Cooking Italy (Community & Social)
- Milan Picnic and Social Group (Community & Social)

## Dropped duplicates (not in either file)
- All 4 Italy-listing-page candidates, plus Dolce Vita Rome, Italy Scholarship Updates, Sotto il Cielo di Roma, Scholars Road Italy Scholarships, and Milan Cardio Tennis / Language Exchange — all already in the existing code set.

## Sources checked (new, not wave-20261026 / retired)
- Italy listing page on techsslash.com (all 4 codes were duplicates)
- Meetup Rome / Milan event pages (Dolce Vita, Chapter35, Sotto il Cielo di Roma, Milan picnic — some duplicates, some new)
- Scholarship pages for Italy (duplicates)
- WASZP Italia Cup notice of race PDF (verified)
- Solar cooking wiki page (pending)
- groupjoin.link Italy city pages (Rignano Flaminio, Pomarolo, Santo Stefano Lodigiano, Cantalupo Ligure): 0 groups found — dead end for this slice
- whatsappgroups.shop homepage: an Italy entertainment group is listed, but its invite code is not shown in page text and was not extracted (chat-link text fetch returned 403; not retried)

## Notes / gaps
- WhatsApp invite pages now mostly return HTTP 200 with an empty og:title via plain curl; only groups with a populated og:title passed the strict verification rule. The 2 pending items may still be live — they need a re-check with a different verification method before promotion.
- No hard-porn groups were encountered; no girls/friendship groups were removed.
- groups.json, generate.py output and ~/workspace/wgl-deploy/ were NOT modified.
