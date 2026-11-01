# TEAM 12 — grouplinkshare.com India page RECHECK (wave_20261029)

**Run time:** 2026-10-29 ~12:01–12:20 PKT | Slice: https://grouplinkshare.com/indian-whatsapp-groups/ only
**Page state:** 90 unique invite codes found on the India page. 6 already in the existing set (73,874 codes union).
**Fresh candidates:** 84 | verified 0 | pending 81 | dropped 3 (suggestive "hot girls" titles — see below)

## Result files
- team12-fresh-grouplinkshare-india.json — 0 items (empty array)
- team12-unverified-pending.json — 81 items (fresh India-page codes, NOT verified)

## Verification outcome (important)
curl verification failed its acceptance criterion for ALL codes: chat.whatsapp.com invite pages are now
client-side rendered and serve **empty og:title** / generic og:description ("WhatsApp Group Invite") / generic
og:image for every link. A deliberately bogus code returned HTTP 200 + invite_link_type_v2 marker too —
so HTTP 200 + v2 marker does NOT discriminate valid vs dead links anymore. Per task rules (verified only
with non-empty meaningful og:title), all 81 candidates were filed as pending rather than falsely "verified".
60 codes curl-checked (6–9s spacing, no HTTP 429 hit); remaining 21 not curled at all.

## Dropped (content rules, not pending)
- LRWFI5nqQan7XaPvaITEOC — "Hot Girls WhatsApp Group Join Link"
- IipaE327rj2K2IrGc24HsP — "Hot Indian Girls WhatsApp Group 2026"
- HMZZOvU6Iy67ZhOg6xwf7P — "Hot Girls Online WhatsApp Group Link"
Excluded as suggestive/adult-adjacent; do not re-add.

## Notes
- India page cross-links "Nepal / Pakistan / Worldwide" country pages — left untouched (out of slice).
- Bangladesh + Girls + UAE pages: NOT touched (Bangladesh exhausted; Girls/UAE owned by other teams).
- No /sex/, /xxx/, /adult/ pages visited.
- Other grouplinkshare pages (all 13 non-Bangladesh) are RETIRED for this wave — do not re-scrape.
- Names were sanitised: emojis/flags stripped, no URLs/phones/entities. Hindu-devotional titles
  (Bhajans/Bhakti) filed under "Community & Social" (no "Hindu" slot in the allowed category list).
- The pending file uses the exact item schema WITHOUT _verified fields.

## Out-of-slice fresh directories (for coordinator, not scraped)
- grouplinkshare.com Worldwide page (worldwide country links) — needs a team if in scope.
- grouplinkshare.com Nepal page — needs a team if in scope.
