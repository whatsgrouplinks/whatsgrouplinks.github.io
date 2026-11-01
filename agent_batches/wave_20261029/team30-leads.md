# TEAM 30 — leads & notes (wave_20261029, 2026-10-29)

## Slice result (blog listicles + regional slices)
- **whtsagrouplinks.com international listicle — PARTIALLY EXHAUSTED.** Scraped
  `https://www.whtsagrouplinks.com/international-whatsapp-groups-links/` (330+ listing,
  67 unique codes): **58 of 67 codes already in the union** of groups.json +
  .existing_codes.json — a previous wave ingested this page almost fully. Only 9 fresh
  codes found (6 verified, 3 pending). Further runs should skip this page.
- **whatsshare.com — FRESH, PARTIALLY MINED.** New directory (homepage +
  `/blog/` posts + `/ajax/load-groups.php` JSON pagination, 50 cards/page, 150 cards
  fetched across 3 pages, 113 unique group detail pages `/group/<slug>`). Detail pages
  embed direct `chat.whatsapp.com` codes. I fetched 25 detail pages → 18 codes → 4 dup,
  14 fresh (6 verified, 8 pending). **Still ~88 detail URLs unvisited** — good follow-up
  for another team: iterate `/ajax/load-groups.php?page=N&limit=50` for pages 4+ and
  fetch `/group/<slug>` pages for codes. Server is slow (~20-30s per ajax call).

## Out-of-slice fresh directories (name-only leads, NOT scraped)
- `https://thinkingoutsidethesandbox.ca/135-best-business-whatsapp-group-links/` —
  Canadian blog with a "verified" table of ~50 business WhatsApp groups (current group
  names + verification dates). Invite links behind "View invite" anchors — needs a
  dedicated fetch pass. Not in retired list, not covered by teams 01/10/20.
- `https://mixchatroom.org/central-asia-cities.html` — MixChatRoom Central Asia city
  guides (Kazakhstan, Uzbekistan, Kyrgyzstan, Tajikistan, Turkmenistan, Almaty, Astana)
  — community pages, not a WhatsApp link directory; low priority.
- `https://groupsnest.com/` — directory with 1,495 links in 33 collections (0 added in
  last 30 days); not retired — candidate for a full crawl.
- `https://groupwa.link/` — "8000+ WhatsApp Group Link" directory; not retired —
  candidate for a full crawl.
- `https://www.whtsagrouplinks.com/` — homepage + many category pages beyond
  international (social media, blogger, etc.); mostly mined here, category pages may
  still hold fresh codes.

## Exhausted / parked pages (do not re-assign)
- `https://www.whtsagrouplinks.com/international-whatsapp-groups-links/` — 58/67 codes
  already in union; keep only as a lead for its other category pages.
- whatstele.com, grouplink.com.in Malayalam Islamic — handled by teams 10/20 this wave.
- Retired-list domains untouched: whatzgrouplink.com, dubai-forever.com,
  newgrouplinks.pk, wagroupnest.com, whatasgrouplink.com, whatsgroulink.com.

## Counts
- Fresh (verified): 12
- Pending (unverified): 11

## Notes / flags
- No 429 hit on chat.whatsapp.com; 8s spacing used, all invite checks completed.
- All 11 pending items have HTTP 2xx + `invite_link_type_v2` marker but EMPTY
  og:title → per rules they stay pending (likely expired/reset links, but not proven).
- "Gayyy Chattt" kept as Friendship (no banned-pattern match; social/friendship
  chat, not adult content) — flag for coordinator to confirm policy.
- Verified-by field on all fresh items: "curl og:title + invite_link_type_v2 check, 2026-10-29".
- whatsshare group names are often Arabic — kept as plain-text Arabic names (no
  translation in name field; descriptions are English).
- og:image: real pps.whatsapp.net group photos used where present; generic
  static.whatsapp.net default icon replaced with "".
- Files written: team30-fresh-discovery-b.json (12), team30-unverified-pending.json
  (11), team30-leads.md (this file). All valid JSON arrays.
