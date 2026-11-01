# TEAM 03 — wave_20261029 — groupjoin.link Nigeria country pages (p.3+)

## Slice coverage
- Walked `https://www.groupjoin.link/country/nigeria?page=N&limit=20&safeSearch=strict` for N = 3..35.
- Pages 3–28: 20 groups each. Page 29: 6 groups. Pages 30–35: 0 groups (listing exhausted).
- p.1/p.2 were harvested by sibling teams — not revisited. Retired pages (tags 9+, other teams' slices, banned domains) not touched.
- NEVER visited any /sex/ /xxx/ /adult/ pages — country listing only.
- Pagination is flaky: page 5 and page 7 returned empty on first fetch, full on retry; two page fetches (20, 26) needed a longer timeout. Re-try an empty page once before treating it as the end.

## Harvest numbers
- 526 unique invite codes harvested across pages 3–29 (no cross-page duplicates).
- Dedupe vs union of groups.json (38,750) + .existing_codes.json (73,873) = 73,874 codes: **all 526 fresh**.
- Content filters: 49 dropped by regex (porn/xxx/nudes/suggestive-emoji titles 🥵🍆🔞💦🍑); 44 more dropped manually (hookup/sugar-daddy-mummy/ashawo/sex-chat/profane "can you fuck so good"/school-age emoji or (14-18)/symbol-only/meaningless/hookup-adjacent "intimate hub" adult-products).
- Final candidates: 433.

## Verification outcome (IMPORTANT)
- Verified 60 codes (newest-first by groupjoin datePublished), 6–9s spacing, curl + og:title + invite_link_type_v2 check.
- **All 60 returned HTTP 200 with EMPTY og:title, default WhatsApp icon og:image, and invite_link_type_v2 present** → dead/revoked invites.
- Sanity check: known-good codes already live on the site returned real og:titles with the same curl setup — the method works. groupjoin.link's Nigeria invite codes are overwhelmingly stale.
- No HTTP 429 encountered at any point.
- Verified-fresh count: **0**. Fresh file is an empty array (valid JSON).
- Pending file: **433 items** — 60 confirmed-dead (empty og:title), 373 never attempted (hit the ~60-code verification cap).

## Flags / recommendations for parent
1. **groupjoin.link Nigeria pages have a ~100% dead-link rate in the tested sample.** Deprioritize this source in future waves, or re-verify pending codes individually later (admins may rotate codes).
2. Pending items carry `image` from groupjoin's listing JSON-LD (the group's actual WhatsApp profile pic), not from the invite page HTML — noted here for accuracy.
3. Pending items have NO `_verified` fields (per schema).
4. Category "Online Earning" (101) + "Sports" betting (51) dominate — many are "SPORTY-BET"/"earn money" spam-style groups; merge may want extra scrutiny before publishing.
5. /tmp collision note: another worker's scratch file `/tmp/verify_results.json` exists (list format); I used `verify_results_t03.json` for mine — no interference.

## Name-only leads / new directories
- None. This slice was a single country listing; no new directories discovered.

## Exhausted pages
- groupjoin.link/country/nigeria pages 30–35: empty (0 groups). Stop point: page 29 (6 groups).
