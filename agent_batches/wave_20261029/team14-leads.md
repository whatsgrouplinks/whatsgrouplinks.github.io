# Team 14 — Leads & Notes (grouplinkshare.com UAE recheck, 2026-10-29)

## Name-only leads / notes
- grouplinkshare.com UAE page: https://grouplinkshare.com/uae-whatsapp-group-links/
- Page carries exactly 15 invite codes in a "Top Popular UAE Groups" grid (no pagination, no other listing).
- 14 codes were NEW after dedupe; 1 (UAE Travel & Tourism, D58683EExwWEl9mkJ1rZr4) was already in groups.json — dropped.
- Verification: all 14 returned HTTP 200 with invite_link_type_v2 marker present, but WhatsApp serves EMPTY og:title to curl — so NONE qualified as VERIFIED (needs non-empty meaningful og:title). All 14 → pending.
- No HTTP 429 encountered (first pass had 8 timeouts at http=000, all returned 200 on retry).
- No new UAE pages on grouplinkshare.com found beyond this one.

## Out-of-slice (not touched)
- grouplinkshare.com India / Girls / Bangladesh pages — other teams / exhausted.
- No /sex/ /xxx/ /adult/ pages visited.

## Exhausted pages
- grouplinkshare.com UAE page — fully scraped, all 15 codes extracted (this run).
- Retired list (not touched): whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, elsabagh.com, techsslash.

## Flags
- Fresh file is EMPTY (0 verified): WhatsApp returns blank og:title to server-side curl for these links. Parent may retry verification with the live browser to capture real group names/images.
- Name↔code mapping was taken from the card HTML (title sits right after its link) and re-verified via regex before writing; an off-by-one draft was caught and corrected.
- All 14 pending items have clean, plain names; none matched content-drop patterns.
- og:image when present was only WhatsApp's generic invite placeholder, so image left "" for all items.
