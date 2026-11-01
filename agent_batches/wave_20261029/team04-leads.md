# TEAM 04 — groupjoin.link UK country pages 3+ (wave_20261029)

## Run summary
- Slice: `https://www.groupjoin.link/country/united-kingdom` pages 3..25 (page 1 already harvested by another team; page 26 returned 0 items = exhausted).
- Raw items parsed: 434 (pages 3–25, ~19–20/page). Category mix dominated by **Adult (341)** — dropped per rules.
- After Adult-category drop, porn-regex/suggestive-emoji drop, school-age drop, and dedupe vs groups.json (38,750 codes) + .existing_codes.json (73,874 union codes): **60 candidates** (1 dupe vs union dropped).
- Verification: curl per invite URL, 6–9s spacing, criteria = HTTP 2xx + non-empty meaningful og:title + `invite_link_type_v2` marker. No HTTP 429 encountered.
- **Fresh (verified): 21** → `team04-fresh-groupjoin-uk.json`
- **Pending (not verified): 39** → `team04-unverified-pending.json`

## Exhausted / covered
- Pages 3–25: fully walked. Page 26: empty (0 items) — pagination ends here. No pages skipped (all fetched 200 OK, no failures).

## Name-only leads (not harvested — out of slice, Adult category)
UK pages are ~79% Adult-category groups. Sample adult titles seen (NOT harvested, do not touch — out of slice): "Family lovers sex🥵", "Young videos 🔞🎭", "No rules group", "Desi site", "Insta viral 🔞🔥", "Only videos 💦". Also present: dozens of Telegram-promo / number-selling spam cards (e.g. "🇺🇸Google voice available… +8801774336782") — personal info, do not harvest.

## Out-of-slice fresh directories (for other teams, NOT touched)
- groupjoin.link UK **page 1** — retired (other team).
- groupjoin.link UK **page 2** — NOT harvested by team04 (slice was 3+); still open.
- groupjoin.link tag pages `tag/Uk` / `tag/uk` — retired per slice list.
- groupjoin.link Asia tags (PK/MY/BD/LK/SG/TH/VN/PH/NP/MM/KH), Indonesia pp.11–30, Nigeria tags 9+, Kenya 5–8 — retired.
- Never visited any /sex/ /xxx/ /adult/ pages.

## Notes / flags
1. **New invite URL format**: pages 20+ use `https://chat.whatsapp.com/invite/<code>` (two-segment path) alongside classic `chat.whatsapp.com/<code>`. Merger must keep the FULL URL; dedupe uses the LAST path segment as the code.
2. Dead links: most pending items returned WhatsApp's generic fallback page (empty og:title, default static.whatsapp.net og:image) = expired/revoked invites. Verified=21 all had real og:titles + invite_link_type_v2 marker.
3. One pending item ("Islam", code …H9dZyGQFRtdLdSMTn3P3QK) had a junk og:title ("Pk") with a pps.whatsapp.net image — left pending, could be re-checked later.
4. Titles were normalized for schema (stylized unicode → readable, e.g. "Gastarbeiter CG Werbung", "Ekta Mein Shakti"); descriptions are generated from name+category, no source names/links.
5. One parse artifact seen: a `category_name` regex over-run producing garbage ('Adult"])</script>…'); fixed by tightening the category regex to `[A-Za-z][^\\"]{0,40}` — the affected item was an Adult-category group and was dropped anyway.
6. Country is "GB" for all items (UK country listing page).
7. All three output files written and validated: exact key schema, valid JSON arrays, categories within the allowed set, zero porn-regex hits, zero HTML entities.
