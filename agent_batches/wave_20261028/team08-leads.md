# Team08 leads — Middle East regional — wave 20261028

## Result
- Candidates examined: 193 unique invite codes
- Verified (spaced curl, HTTP 200 + meaningful og:title): 6 → team08-fresh-mideast.json
- Pending (HTTP 200 but og:title empty = dead/revoked invite page): 6 → team08-unverified-pending.json
- Dedupe drops (code already in wave 20261028 dedupe_union_codes.txt, 73,684 codes): 181
- Porn drops: 0 (no hard-porn titles found; the singles/relationship-advice group is allowed social content and went to pending on verification, not on content)
- No groups.json, generate.py output, or ~/workspace/wgl-deploy/ file was touched. Only the three team08 files in wave_20261028 were written.

## Sources / pages scraped (all NEW for this slice, none from wave 20261027)
- dubai-forever.com/whatsapp-jobs.html (GCC jobs page; team06 in wave 20261027 explicitly EXCLUDED these codes, so this page was fresh for this wave) — 101 codes, ALL 101 already in the union set. Direct curl to this host timed out; codes were read via the page-text fetch.
- grouplink.com.in UAE jobs page (45 rows), Kuwait jobs page (18 rows), Saudi Arabia jobs page (12 rows) — 75 rows → 68 unique codes, ALL already in the union set (7 codes repeat across its own pages).
- groupwa.com city pages via curl (Riyadh, Jeddah; Dammam, Khobar, Makkah, Madinah, Sharjah, Ajman, Salalah, Aqaba, Irbid returned placeholder pages with 0 codes) — Riyadh 9 codes, all dupes; Jeddah 9 codes, 8 fresh + 1 dupe.
- Search-snippet / article pages with plain-text invites: namamuglobaltravels.com Oman/Qatar visa page (code already in union), muscatdaily.com stranded-expats article (fresh), play.limitlesstcg.com PTCG Qatar tournament pages (fresh), themedialine.org Manama meditation event (fresh), jobzsearcher.com Doha teaching-jobs article (code already in union).
- anygulfjobs.com Saudi Arabia jobs page via curl — 1 code, fresh, verified as "Saudi Arabia #19".

## Verified (6, all SA Jobs except one)
- Saudi Arabia #19 (SA, Jobs), LOGISTICS JEDDAH (SA, Jobs), Together We Grow_jeddah (SA, Community & Social), Elite Home Services Group (SA, Jobs), UAE Qatar KSA Jobs (SA, Jobs), Saudi Arabia new job's (SA, Jobs). og:title flag/emoji decorations were stripped to the plain group name; the stylised "UAE Qatar KSA Jobs" title was decoded from mathematical-alphanumeric characters.

## Pending (6, HTTP 200 but empty og:title — re-check before any merge)
- Manama New Year Eve Meditation (BH, Health), THE SINGLES' SPOT (SA, Friendship), Jeddah Cars Sale (SA, Buy Sell), PTCG Qatar (QA, Gaming), Muscat Expats Return Support (OM, Community & Social), MyAsia Grocer Jeddah (SA, Buy Sell). Pending names come from source-page context, NOT og:title (titles were empty).

## Blockers / next-pass leads
- newgrouplinks.pk Dubai page and whtspgrouplink.com country pages hide invite codes behind Join buttons in text/curl fetches (whtspgrouplink SA/QA/UAE pages are banned for this slice anyway — do not reuse); newgrouplinks.pk Dubai names (Way2Home Dubai Properties, Dubai Promotion, Leaders & Friends In Action – Dubai, Invest In SOBHA Dubai, Career Crafters Hub UAE, GCC VISA Consultants, Freelance Visa UAE) need a live-browser pass to extract codes.
- whatsagroupslinks.com Gulf/Yemen pages and groupwa.com Gulf-job category page are Cloudflare-blocked in text fetch (curl returned a ~12 KB challenge page, 0 codes) — live-browser lead.
- groupjoin.link tag/country pages for Bahrain (101 results), Kuwait (18), Lebanon (13), Iraq (5) were noted by wave 20261027 team06 but codes are not extractable via text fetch/curl — live-browser lead for QA/KW/BH/LB/IQ coverage.
- Meetup UAE hiking event snippet showed a garbled/corrupted invite code (Cyrillic-mixed characters) — NOT included in either file; needs the live event page to recover the true code.
- Coverage gap: no fresh verified groups found this wave for UAE, Qatar, Kuwait, Oman, Bahrain, Jordan, Lebanon, Iraq or Yemen beyond the pending items above — the big directories for those countries are already fully harvested into the union set. Next pass should prioritise small organisation/event pages (sports clubs, churches, schools, tournament sites like Limitless TCG) over directories.
