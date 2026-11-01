# Team09 — Indonesia (wave 20261027) — leads

## Counts
- Verified (team09-fresh-indonesia.json): 58 — all country ID
- Unverified-pending (team09-unverified-pending.json): 94 — all country ID
- Scraped from source pages: 194 candidates
- Checked by verification: 153 (137 first batch + 16 second batch, see below)
- Dropped before verification: 41 (hard-porn / sexual / profanity titles, school-age SMP title, or meaningless symbol-only titles — no codes listed here, do not re-add)
- Duplicates vs existing set: 0 — none of the 194 codes were in the full union
- Blocked entirely after verification: 1 candidate whose real WhatsApp og:title was hard porn — excluded from BOTH files, code deliberately not recorded here

## Category breakdown (verified)
- Buy Sell: 38
- Gaming: 11
- Community & Social: 8
- Sports: 1

## Sources (NEW for this slice)
- groupjoin.link — tag/Indonesia pages 1–10 and tag/indonesian pages 1–3. This source is NOT in the task's retired list and is NOT a wave-20261026 source. It is the only source codes were taken from.
- NOT used: any retired source in the task list (including wagroupslink, groupda, grupbul, techapkzone, grouplinks.in, groupwa.com and the rest), and NOT the Malaysian university / Singapore alumni pages from wave 20261026 team05.
- Investigated but yielded no staged codes:
  - cheetahlinks.com/indonesia-whatsapp-groups/ — Cloudflare-blocked, no codes taken.
  - groupwa.link/groups-gallery/ — Cloudflare challenge page, no codes taken.
  - hubrecipes.com active-groups page — one Indonesia entry could not be fetched (upstream access failure); it was NOT retried in any form and its code was NOT staged anywhere, per instruction.

## Method
- Dedupe: full union = invite codes in groups.json (38,051 groups) UNION .existing_codes.json = 73,169 codes. Every candidate was checked against both files.
- Verification: spaced curl (browser User-Agent, 1.5 s gaps) of each chat.whatsapp.com invite. Verified ONLY on HTTP success AND a non-empty, meaningful og:title. Empty-title / meaningless-title (e.g. ".", "23b") links went to pending, not fresh.
- Names: verified items use WhatsApp's own og:title as the name, NOT the directory's scraped title — the directory's payload pairs titles to codes with an offset (e.g. one code's scraped title was a different group's name, while its og:title matched a neighbouring entry), so scraped titles cannot be trusted for pairing.
- Images: left "" for all items — the directory's group icons were subject to the same offset, so a scraped icon could belong to a different group. Blank is safer than mismatched.
- Categories/descriptions: mapped from the verified og:title keywords (JB/STORE/STOK = Buy Sell; FT/ISIAN/game names = Gaming; predictions = Sports; otherwise Community & Social). Descriptions are plain generic sentences, no URLs, no source names, no personal info.
- Porn filter: only hard porn/xxx groups blocked. Girls/friendship/dating/social groups were NOT removed by the filter (none of the verified titles fall in that class; the verified set is overwhelmingly game-account buy/sell stores).

## Caveats for the parent / merger
- Pending names are the directory's scraped names and are APPROXIMATE (og:title was empty, so the true name could not be confirmed, and scraped titles are offset as noted). Re-verify a pending link before publishing it; do not publish pending names as confirmed.
- The first scrape/verify attempt was lost when /tmp was wiped (VM restart). Everything above is from a complete second run (re-scraped 194, re-verified all 153 checked candidates) stored in ~/workspace/team09-scratch/ — the counts above are from that complete run only.
- No changes were made to groups.json, generate.py output, or ~/workspace/wgl-deploy/.

## Next-pass leads (not staged)
- Deeper groupjoin.link Indonesia pages (11+) and its city/topic tags (Jakarta, Bali, Bandung, Surabaya, jual-beli) — same method, same dedupe, same og:title-as-name rule.
- Fresh Indonesian blogs/forums posting 2026 group links (not the retired list) — verify any code the same way before staging.
