# Team18 — Business / Buy Sell / Finance / Online Earning — wave 20261028

## Sources / pages scraped
- groupsnest.com homepage and Online Business Pakistan collection page (names only; Join links hide codes in text fetch — only one code was surfaced, and it was a dedupe drop, see below)
- IndiaMART product listings (Lucknow kurti reseller/wholesale listing; Delhi laptop-parts deals listing; Delhi wholesale daily-offers listing)
- YouTube video descriptions (Royals Kid wholesale kids-wear video)
- Nicegram business directory page (Boom account-store listing)
- MQL5 product page (trading-signals group — dedupe drop)
- Google Sites online-earning page (dedupe drop)
- msha.ke creator page (Africa marketplace — dedupe drop)
- mlmgateway.com recharge-earning page (dedupe drop)
- globuya.com marketplace listing (dedupe drop)
- Fraser Bond UK property-deals article (dedupe drop)
- DansDeals forum buy/sell wigs thread (pending)
- findglocal.com e-commerce hub listing (pending)
- brisbanedine.com restaurant deals posts (verified)
- MacGregor Yacht Club of British Columbia AGM minutes PDF (pending)
- whtsagrouplinks.com forex / work-from-home / watch-wholesale pages — ATTEMPTED, Cloudflare-blocked on text fetch, no codes extracted from them; not counted as scraped codes
- No wave 20261027 manifest sources and no retired sources were re-scraped. No forex/earning/community pages from wave 20261027 team26, and no Zimbabwe stock-investors / Harare business / SA brand-growth listings from wave 20261027, were reused.

## Counts
- Candidates found: 18
- Verified: 5 (in team18-cat-biz-finance.json)
- Pending (spaced-curl check returned no meaningful og:title): 4 (in team18-unverified-pending.json)
- Dedupe drops (code already in dedupe_union_codes.txt, 73,684 codes): 9
- Porn drops: 0
- Within-output duplicates: 0

## Verification
- Spaced curl (1.5s between checks, browser-like User-Agent) of https://chat.whatsapp.com/<code>.
- Verified only on HTTP success plus a non-empty, meaningful og:title, used as the group name.
- Pending items had a full invite code but an empty og:title on check; their names are generic context names, not og:title claims.
- One groupsnest Join link was attempted via text fetch and returned a 403; that request was NOT repeated or retried through another tool. Its surfaced code was already in the dedupe union, so it was dropped as a dupe and does not appear in either output file.

## Dedupe drops (9)
BAkf5IOTirWK2uQTR1P35X, JX1k9FAN9UNHY62qptWGFN, DMgLeJckd7CKrT1VSbOM0C, DiAkL53lqmf5Kn9YTZCXsZ, IWc1CaxviFw8Bu94JGRIQv, CuExhHdrJkjKgQbnvlmbnQ, DrlA32z3Hwc20rl7L4iuQc, FqzFnPokvCXJo7Z9g9GmSG, LxOUjCDYoBi2PJOuOjYLa5.

## Notes / next-pass leads
- groupsnest.com Buy & Sell / Crypto / iPhone Sell collections list many in-slice groups, but their Join-link codes are not exposed in text fetch — a live-browser pass could extract them (do NOT re-use the single 403-blocked invite above without a fresh check).
- whtsagrouplinks.com forex, work-from-home, reseller and watch-wholesale pages are Cloudflare-gated for text fetch; a live-browser pass could extract their Join codes, then dedupe + verify as usual.
- Truncated codes seen in search snippets (e.g. several YouTube/Facebook deals groups) were NOT staged, as only full codes were used.
- groups.json, generate.py output and ~/workspace/wgl-deploy/ were not modified.
