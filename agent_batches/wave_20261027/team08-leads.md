# Team08 — Nepal + Sri Lanka — wave 20261027

## Counts
- Verified (fresh file): 1 — all LK, 0 NP
- Unverified-pending: 1 — LK, 0 NP
- Leads (truncated codes only, NOT items): 7 groups below

## Verified method
- Dedupe: full union of groups.json (38,051 groups) + .existing_codes.json = 73,200 codes. Both fresh candidates checked against that union.
- Verification: spaced curl (browser User-Agent, 2s gaps). The verified item was fetched TWICE, both HTTP 200 with non-empty og:title "DHRM 55".
- Note: curl egress in this cell was intermittent early in the run (timeouts even for a code already in groups.json and for google.com), then succeeded. Do not treat the early timeouts as dead links.
- One directory-page text fetch failed upstream and was NOT retried in any form, per instruction.

## Verified item (in team08-fresh-nepal-srilanka.json)
- DHRM 55 — Education, LK — invite code HdoptVTLH3f44PVOuOC5lG — og:title "DHRM 55", HTTP 200 twice, group icon taken from the invite page itself. Found via an institute notice PDF (Gampaha, HRM batch group).

## Unverified-pending item (in team08-unverified-pending.json)
- Sri Lanka News Updates Group — News, LK — invite code DpmxyJkPCSSBUwQE3oIlv1 — HTTP 200 BUT og:title EMPTY, so it FAILS the verified rule and is pending only. Name is inferred from the news-article context where the link appears (og:title gives no name). Parent re-verify should drop it if the title stays empty.

## Dropped by dedupe (not items, do not re-add)
- DVAsLvidGWS7x0BjvzCrwf — already in groups.json as a Sri Lanka careers group.
- JeszAGheQFcG6yFueSSpyQ — already in .existing_codes.json.
- Hc0FhNU6ppnKJoDw24Q2MH — already in the union (Nepal nomads group).
- KPwuJQ0TdG4FuY6FBPOmZy — groupda-family listing, excluded per task; not used.

## Leads — truncated codes only (search snippets cut them with "..."; NEVER complete or guess them; a live-browser pass must extract the full code, then dedupe + verify)
- LK government jobs group — snippet prefix JjpM0O1aALU... (YouTube description, Sri Lanka government vacancies 2026).
- NP scholarship updates group for Nepali students — snippet prefix H14LFi5Jp5R... (MGSS/GJSS 2026-27 video; page fetch also truncates at the same point).
- NP medical entrance (CEE 2083) notes group — snippet prefix J4Tk0fR4mHq... (multiple Kathmandu entrance-prep videos, same group).
- NP stock-market watchlist group — snippet prefix KsLZKwPvsFj... (NEPSE weekly watchlist video).
- NP gaming group — snippet prefix FR9CYaOF4Qh... (Dashain gaming video).
- LK Tamil sports/cricket news groups — snippet prefixes IlrWDEsJgrG... and CkimXfurZTa... (sports news videos).

## Sources NOT used (per task exclusions)
- activewagroup.com LK/NP pages, wagroupnest, groupda (+groupda1.link), grupbul, whtsagrouplinks, wagroupslink, groupjoin.link, groupwa.link/com, and all other wave-20261026 / retired sources listed in the task — none reused.
- No porn/xxx groups included; the only hard-porn-adjacent directory seen (a Nepali-girls listicle heavy with xxx titles) was skipped entirely, and no personal phone numbers from its pages were copied anywhere.

## Nepal gap (honest)
- No full, fresh, verifiable NP invite code was found in this pass: every NP code surfaced was either truncated in the snippet, already in the union, or on an excluded/retired directory. NP = 0 verified, 0 pending. The NP leads above are the best next pass for a live-browser extractor.
