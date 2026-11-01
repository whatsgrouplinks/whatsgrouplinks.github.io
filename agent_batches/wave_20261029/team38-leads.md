# TEAM 38 — Finance category discovery — leads (2026-10-29)

## Out-of-slice name-only leads (for other teams, NOT finance)
- "App update" (groupwa.link online-earning) — Online Earning slice
- "Online Platforms To Earn Money" (groupwa.link online-earning) — Online Earning slice
- "Karachi Market Place (KMP Official) — Karachi business news, deals and buy & sell offers" (groupwa.link business, 3 codes) — Buy Sell / Business slice
- "Join YouTube Grow Together Pakistan - 1K Subs WhatsApp Group" (groupwa.link business) — Entertainment/Social slice

## Fresh directories hit (all non-retired, scrapeable via curl)
- whatsgroupslinkspk.com — homepage has Business Ideas / Cryptocurrency / Forex Trading / Trading sections (each 13 groups); ~88% of codes already in groups.json — EXHAUSTED for finance.
- groupwa.link — /online-earning/ and /business/ pages (10 cards each, JSON-ish data attrs); most codes already exist — EXHAUSTED.
- joingram.in — /stock-market-whatsapp-groups-link/ and /bank-nifty-whatsapp-groups/ table rows; most codes already exist — EXHAUSTED for now.
- whtsagrouplinks.com — forex/share-market/crypto pages have 40-60 finance groups each but are Cloudflare-challenged ("One moment, please...") for curl; page text IS fetchable via the search crawler (browser.open), though full invite URLs are not exposed in text view. Needs live-browser extraction. NOT scraped by me.

## Retired domains skipped (per wave brief)
whatstele.com, activewagroup.com, whatsgroulink.com (all matched finance queries but retired).

## Verification notes
- 19 new codes tested. 16 returned HTTP 200 but a dead-invite stub (empty og:title, invite_link_type REGULAR with empty v2) = revoked/expired invites → moved to pending, not staged as fresh.
- 1 profane title dropped at filter ("Trading with gOLd fuckers").
- No HTTP 429 encountered.
- Dedupe source: .existing_codes.json (73,873 codes) + groups.json invite codes union.
