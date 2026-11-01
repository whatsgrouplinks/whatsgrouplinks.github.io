# TEAM 21 — joinnchat.com sub-pages — leads & notes (wave_20261029, 2026-10-29)

Slice: joinnchat.com category/country SUB-PAGES only. Homepage already harvested by another team — NOT re-scraped (only fetched once for nav discovery, no codes taken from it).

## Sub-pages scraped (21 fetched, all via curl)
WITH group links (14):
- /college-whatsapp-group-links/ — Education
- /cricket-whatsapp-group-links/ — Sports
- /entertainment-whatsapp-group-links/ — Entertainment
- /funny-memes-whatsapp-group-links/ — Funny
- /girls-whatsapp-group-links/ — Friendship
- /indian-whatsapp-group-links/ — Community & Social (IN)
- /news-whatsapp-group-links/ — News
- /poetry-whatsapp-group-links/ — Entertainment
- /pubg-whatsapp-group-links/ — Gaming
- /usa-whatsapp-group-links/ — Community & Social (US)
- /pakistani-whatsapp-group-links/ — Community & Social (PK)
- /malayalam-whatsapp-group-links/ — Community & Social (IN)
- /aunty-whatsapp-group-links/ — Friendship (heavily filtered, see content notes)
- (homepage nav only, no codes harvested)

WITHOUT group links (7 — category archives / guides, zero chat.whatsapp.com links):
- /entertainment/, /sports/, /technology/, /news/ (WP category archives — no group tables)
- /whatsapp-group-links/ (zero chat.whatsapp.com links — appears to be a thin/placeholder page)
- /friendship-girls-group-whatsapp/ (guide article, no link tables)
- /kannada-girl-whatsapp-group-join-link/ (guide article, no link tables)
- /stock-market-whatsapp-group/ (guide article, no link tables)

## Yield summary
- Raw (name, code) pairs extracted: 1245
- Already in site (dedupe vs groups.json + .existing_codes.json, 73,874-code union): 1132
- Self-dupes across sub-pages: 41
- Dropped by content rules: 7 ("H*t Girl", "Vai vai vai", "hot aunty groups", "Local aunty number", "Tamil Aunty Number", "Aunty number Chennai")
- Fresh candidates: 65

## Content-rule notes
- /aunty-whatsapp-group-links/ contains many "aunty number" / suggestive-coded titles; kept only clean friendship/community names. "Madrasi aunty", "Divorce Aunty", "Single Aunty Life", "Tamil Girls Group" kept (no banned pattern).
- Channel links (whatsapp.com/channel/...) present on pages — skipped, not group invites.
- Both invite forms seen: chat.whatsapp.com/<code> and chat.whatsapp.com/invite/<code> — normalized to the short form in output; dedupe used last path segment.

## Name-only leads (no code on page — names only, no fresh invites to take)
- None this run; every group row on these pages carried a direct chat.whatsapp.com link or was already in the site.

## Out-of-slice fresh directories (NOT scraped — for other teams)
- Retired list honored: joinnchat.com homepage, whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, elsabagh.com, techsslash — none touched.
- joinnchat.com /blog/ archive exists but was out of slice time budget; blog POSTS may contain additional group links not on the 14 pages above.

## Flags
- Pages render group tables server-side; curl + UA string worked (first plain-curl attempt timed out once, retry with full Chrome UA succeeded).
- Heavy overlap: most sub-page codes already in the site's 73,874-code union (homepage harvest + prior waves).
- LINK ROT: joinnchat.com pages are 400-600 days old; verification (curl, 7s spacing, criteria = HTTP 2xx + non-empty meaningful og:title + invite_link_type_v2 marker) on the first 30 fresh codes: 29 returned HTTP 200 with EMPTY og:title — WhatsApp's signature for revoked/dead invite links (calibrated against a known-live site invite which returned full og:title + og:image from the same host/UA) — and 1 had an emoji-flags-only og:title (not meaningful). Zero codes met the bar, so the fresh file is an empty array and all 65 candidates sit in pending. No HTTP 429 encountered. Remaining 35 codes unattempted (time budget) — also filed to pending.
