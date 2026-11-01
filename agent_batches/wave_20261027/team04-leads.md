# Team04 — Ethiopia + East/Horn Africa (ET/UG/RW/ZM) — wave_20261027

## Counts
- Candidates collected: 28
- Dropped as already in existing set (groups.json UNION .existing_codes.json, 73,170 codes): 12
- Fresh candidates sent to verification: 16
- VERIFIED (HTTP success + non-empty og:title): 0
- UNVERIFIED-PENDING: 16 — see team04-unverified-pending.json

## Important: pending does NOT mean dead
- 11 of the 16 returned curl HTTP 000 (connection failure/timeout from this VM, browser User-Agent, 1.5s spacing).
- 5 of the 16 returned HTTP 200 but the curl body contained no og:title meta tag (WhatsApp serves a JS page to curl).
- None of the 16 was proven revoked/dead. Re-verify them via a browser / different network before discarding or promoting them.
- The 5 HTTP-200-but-no-title ones: A Level History Discussion, Crypto-Forex Lessons, University of Rwanda Admissions Support, Emb Carpet and Home Decor Training, Emb Carpet and Home Decor Community.

## Pending breakdown
- Uganda (UG): 13 — PIPSTECT FX HUB, KYC BUYER, Agriculture Expo, Supporting Ugandan Basketball, Coach D Basketball Academy Players Page, Walkers, Raise Kityerera Ark Peas Again, SGI International Presentations, Support My Education, Mega Community, Affiliate Nobles 002, A Level History Discussion, Crypto-Forex Lessons
- Rwanda (RW): 1 — University of Rwanda Admissions Support
- Zambia (ZM): 2 — Emb Carpet and Home Decor Training, Emb Carpet and Home Decor Community
- Ethiopia (ET): 0 fresh — every ET candidate found was already in the existing set (see dupes below).

## Sources used (new for this wave, not wave-20261026 / retired sources)
- groupjoin.link — Uganda tag page (groupjoin.link/tag/Uganda): the 13 fresh UG groups plus 1 porn group blocked (see below).
- thelightofengineer.com — University of Rwanda admissions article: RW group.
- findglocal.com — Emb Carpet And Home Decor Training listing, Lusaka: the 2 ZM groups.
- whatstele.com — Zambia group-links page: its 3 codes (Trending Videos, Zambian Girls, Zambia Culture) were all already in the existing set.

## Dropped as duplicates (12, already in existing set — do NOT re-add)
- UG: Uganda Real Estate Community
- ET: Game Changers Consulting PLC; Women Entrepreneurs Trade Fair Addis Ababa; African Union Women Peace and Security Training
- RW: Kigali Online Community; Rwanda Trading Support
- ZM: Mukanji Academy Parents; Gideon Robert University Zambia; Chreso University Zambia; Trending Videos Zambia; Zambian Girls Group; Zambia Culture

## Blocked / excluded
- 1 hard-porn group from the Uganda tag page (explicit porn description) — blocked entirely, not in either JSON file.
- 1 Uganda teachers-forum group mentioning leaked/finale exam papers — excluded as illicit exam material, not in either JSON file.
- Truncated invite codes in search snippets (Rwanda YouTube descriptions) — unusable, not included.
- No source names, source URLs, phone numbers, emails or personal info appear in either JSON file.

## Files
- team04-fresh-ethiopia-eastafrica.json — VERIFIED only: [] (empty, 0 items)
- team04-unverified-pending.json — 16 items, exact item schema, image "" throughout
- team04-leads.md — this file

## Note on browser fetches
- Direct page fetches of chat.whatsapp.com invite links via the text-fetch tool returned 403 (access denied) and were not retried; verification above is curl-only, as specified.
