# Team06 — groupjoin.link tag/Indonesia pages 31+ (wave 20261029) — leads

## Counts
- Scraped: 1,351 group entries from tag/Indonesia pages 31–100 (parsed from the page's
  embedded group flight-data: title, image, desc, invite code, category, tags)
- Dedupe drops vs union (74,156 codes from groups.json + .existing_codes.json +
  wave_20261028 union): 2
- Porn pre-drops: 172 (bokep/xxx/porn/VCS/crot/sange/onlyfans/jb-bokep-style sexual terms in
  title/desc/category/tags); suggestive-emoji drops: 16; meaningless titles: 49
- Candidates after filter: 1,112
- Curl-verified: 60 codes (all HTTP 200 + invite_link_type_v2; og:title populated ~35%)
- Verified fresh (team06-fresh-groupjoin-indonesia.json): 14 — og:title names, all country ID
- Unverified-pending (team06-unverified-pending.json): 1,093 — directory scraped names
  (APPROXIMATE — re-verify before publishing); includes the 35 curl-200 codes whose og:title
  was empty
- NO HTTP 429 hit during verification; no sex/xxx/adult groupjoin pages visited.

## Sources / pages scraped (groupjoin.link only, this slice only)
- tag/Indonesia pages 31–100 (`?page=N&limit=20&safeSearch=blur`) — all had ~17–20 live
  listings; page 100 still returned 20 full listings, so the slice DOES NOT end there.
- Did NOT touch: tag/indonesian, tag/jual-beli, Jakarta/Bali/Bandung city tags (other teams),
  any retired source.

## Method
- Pagination: https://www.groupjoin.link/tag/Indonesia?page=N&limit=20&safeSearch=blur
- Invite codes sit in the page's RSC flight data as
  `"group_uid":"<gid>",...,"group_title":"<t>","group_img":"<img>","group_desc":"<d>",...,"link":"https://chat.whatsapp.com/invite/<code>"`
  plus `"category":{"category_name":"..."}` and `"tags":[...]`. Titles pair 1:1 with codes
  (verified against the card aria-labelledby anchors — no offset problem on this site).
- Dedupe: every candidate vs the union file (groups.json codes + .existing_codes.json +
  wave_20261028/dedupe_union_codes.txt). All 1,112 staged candidates were new.
- Verification: spaced curl of https://chat.whatsapp.com/<code> with browser UA (~6s gaps).
  VERIFIED only on HTTP 2xx + non-empty meaningful og:title + invite_link_type_v2 marker.
  Empty og:title is common (WhatsApp client-renders these pages) — such codes went to
  pending with the directory's scraped title (APPROXIMATE names — re-verify before publishing).
- Fresh names are WhatsApp's own og:title (not the directory title). Fresh categories are
  mapped from og:title + scraped category into the 16 allowed categories. Descriptions are
  plain generic sentences — no source names, no URLs, no phone numbers, no personal info.
- Girls/friendship/dating/social groups KEPT; hard porn/xxx/sexual-explicit dropped.

## Name-only leads (not staged, for future passes)
- **tag/Indonesia pages 101+** — page 100 was still full (20 listings); walk until two
  consecutive empty pages. Same method works.
- **tag/indonesian pages 16+** — overlaps the Indonesia tag heavily; dedupe against union
  before staging (converges on the same listing pool per wave 20261028 team01).
- **?safeSearch=off variant** — blur-filtered cards (a few per page, esp. 18+/nsfw-tagged)
  hide codes behind safeSearch=blur; the `off` variant may expose extra codes. Content
  filter handles what shows up.
- **Per-group detail pages** (groupjoin.link/group/<gid>) — useful to re-check pending
  items' titles; too request-heavy for this run's budget.

## Exhausted / open
- Exhausted this run: tag/Indonesia pages 31–100 (all parsed, candidates staged).
- Open: tag/Indonesia pages 101+ (never empty — walk must continue).
- Capped by budget, not by data: only 60/1,112 candidates curl-verified; the rest are
  pending with directory titles. A later pass can verify more (6s spacing, ~7 min per 60).

## Notes
- Category mix deep in the tag (pp.31–100): Adult 424, Sports & Fitness 278, Gaming 264,
  Business 143, Online Shopping 111, Money 58 — far more Adult-heavy than pp.11–30.
  The 241 surviving Adult-category candidates passed the hard porn regex (dating/social/
  relationship-type names); the parent merge's adult-emoji flagging still applies.
- WhatsApp og:title is empty for ~70% of invite pages via curl; og:image (pps.whatsapp.net)
  is usually present in the directory's own group_img field and was carried over where clean.
- Transient empty-page responses seen once (page 40 returned empty on first walk, full on
  retry) — retry once before treating a page as the end of the listing.
- No changes made to groups.json, generate.py output, or any deployed files.
