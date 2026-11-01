# TEAM 13 — grouplinkshare.com Girls RECHECK (2026-10-29)

## Slice
- Girls pages: `https://grouplinkshare.com/girls-whatsapp-group/` (50 cards) and
  `https://grouplinkshare.com/girls-chat-whatsapp-group-links/` (30 cards).
- India/UAE pages NOT touched (other teams). Bangladesh pages NOT touched (exhausted).
- No /sex/ /xxx/ /adult/ pages visited — none linked from these two Girls pages.

## Extraction vs prior state
- Parsed 80 unique invite codes across both pages; 42 were already in the
  groups.json + .existing_codes.json union (previous pass captured them).
- 38 NEW codes extracted (33 "seen before" baseline ≈ prior count; recheck found 38 fresh).

## Verification outcome
- All 38 candidates verified via curl (200 on 34/38; 4 hit network timeouts http=000).
- EVERY fetched invite page returned HTTP 200 with `og:title` EMPTY and the
  `invite_link_type_v2` marker present — consistent with revoked/expired or
  WhatsApp bot-gated invite pages. Per the strict verification rule
  (HTTP 2xx + non-empty meaningful og:title + marker), 0 qualified as VERIFIED.
- No HTTP 429 hit — rate-limiting not the cause; results were dumped to pending,
  not blocked.
- `browser.open` on an invite URL returned 403 access-denied; no independent
  cross-check possible from this worker.

## Content filter
- Zero porn/xxx/escort filter hits across all 80 titles. Titles are generic
  SEO-style ("Latest Indian Girls WhatsApp Group Link") — non-pornographic
  friendship/girls groups, kept as allowed.
- "College Girls WhatsApp Group Link" kept (adults, not school-age sounding).

## Notes for parent / merge
- 0 verified → team13-fresh-grouplinkshare-girls.json is an EMPTY array (valid JSON).
- 38 candidates → team13-unverified-pending.json (no _verified fields).
- Recommendation: re-verify pending codes on a later wave with a different egress
  (e.g. browser-based og:title check) — several may be live; WhatsApp shell-pages
  bots, so curl-only verification undercounts here.
- grouplinkshare.com Girls pages appear structurally stable (card layout,
  group-card-link class) — future rechecks can reuse this parse.
