# Team12 leads — wave 20261027 (Brazil / Portuguese slice)

## Counts
- Verified (team12-fresh-brazil.json): 0
- Unverified-pending (team12-unverified-pending.json): 1
- Dedupe base: 73,170 codes (groups.json 38,051 groups UNION .existing_codes.json)

## Why verified = 0 (blocker, not a choice)
- Shell curl egress is dead in this session: HTTP 000 even for google.com
  (egress-proxy CONNECT failures, same failure mode as wave-20261026 team12).
- Text fetcher returns 403 on chat.whatsapp.com (confirmed on one invite URL;
  not repeated after the denial).
- So no invite could meet the "HTTP success + non-empty og:title" rule.
  NOTHING is claimed verified. The 1 pending item needs a live-browser
  verification pass before any merge.

## Unverified-pending (1, deduped fresh)
- Indie Hackers Brasil — Business — code ImPkJ3MnlvaKxRNbkxdsx8.
  Found in full in a 17 Oct 2021 forum post about Brazil. Old post, so
  treat as likely stale until the live-browser check proves otherwise.

## Dropped as duplicates (not in any file)
- Ultra Ouro Fino trail-running group, Casa Branca / Minas Gerais
  (code LwmBOdrQE8U2wgoahnlNbk, Wikiloc route page) — already in the
  existing code set.
- Blogspot post "join WhatsApp Groups" (code OPG67cbiCHJolenkjDSACX) —
  already in the existing code set. Truncated codes seen in YouTube
  descriptions (e.g. sticker-trading, football-fan groups) were NOT used:
  a truncated code is not a candidate.

## Fresh directories needing a live-browser Join-click pass (no codes
## obtainable by text fetch; none used as a source this wave)
- centraldegruposwhats.com.br — largest BR directory found (433K visits/mo,
  Sept 2026); heavily porn-keyword driven, so any future scrape must
  filter hard-porn categories and keep only clean categories (amizade,
  futebol, empregos, estudos, etc.). Its group pages are not indexed by
  search, so no codes surfaced.
- redgrupos.com — second BR directory (37K visits/mo); same porn-heavy
  profile and same non-indexed pages problem.
- grupos.top — BR-focused directory (85% Brazil traffic); also porn-heavy
  (adulto subdomain); group pages not indexed.

## Seen but EXCLUDED (prior-wave sources — do not re-claim as new)
- entregrupos.com.br — its category pages resolve to solion.app, which
  was a wave-20261026 team11 lead source; treated as the same prior-wave
  source and excluded. Its group pages hide codes behind a Join button
  (confirmed on one group page + one category page).
- All retired-list and wave-20261026 sources were re-checked and
  avoided: ongrupos.com, groupjoin.link, gruposbrasil.com.br,
  grupos-zap.com, gruposwhats.app, linkdegrupo.com.br, solion.app,
  gruposwats.com, plus the full retired list in the task).

## Porn filter applied
- No hard-porn/xxx group is in either JSON file. No girls/friendship/
  dating group was removed on that ground (none was a candidate this wave).
