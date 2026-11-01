# Team01 — Indonesia pages 11+ (wave 20261028) — leads

## Counts
- Verified (team01-fresh-indonesia-p11.json): 127 — all country ID
- Unverified-pending (team01-unverified-pending.json): 264 — all country ID
- Scraped from source pages: 574 candidates (unique codes, within-slice deduped)
- Dedupe drops vs wave 20261028 union (73,684 codes): 98
- Porn drops pre-verification (scraped name): 58 — bokep/porn/xxx/VCS/18+ video-sharing and related Indonesian sexual terms; codes not staged
- Sent to verification: 418 (spaced curl, browser User-Agent, ~1.5 s gaps, HTTP code + og:title)
- Post-verification drops: 27 — 22 with meaningless og:title AND meaningless scraped name (symbol-only / "no name" type), plus 5 with sexual/profanity titles found on re-scan (1 og:title "GRUP FULL CROT 💦" that initially slipped through, 4 pending scraped names)
- Verified breakdown: Buy Sell 96, Community & Social 25, Gaming 5, Online Earning 1
- Pending breakdown: Buy Sell 170, Community & Social 71, Gaming 22, Online Earning 1
- All fresh names are WhatsApp's own og:title (not the directory's scraped title — scraped titles are offset-paired on this site, per wave 20261027 team09). Pending names are the directory's scraped names and are APPROXIMATE — re-verify before publishing.
- Categories for fresh items are mapped from the og:title only; pending categories from the scraped name. Descriptions are plain generic sentences, no source names, no URLs, no personal info, no phone numbers.
- No changes were made to groups.json, generate.py output, or ~/workspace/wgl-deploy/.

## Sources / pages scraped (groupjoin.link only, this slice only)
- tag/Indonesia pages 11–30 (pages 11–12 first fetched empty, retried successfully; page 11's 20 codes were already captured via the indonesian tag, page 12 added 4 new)
- tag/indonesian pages 4–15 (pages 12–15 mostly duplicates of the Indonesia pages: only 2+1+1+1 new)
- Indonesia city tags: Jakarta (4 new), Bali (6 new), Bandung (1 new); Surabaya, Medan, Yogyakarta, Semarang, Makassar, Palembang yielded 0 new (no such tag listings)
- tag/jual-beli pages 1–2 (38 new)
- NOT touched: wave 20261027 sources (Indonesia pages 1–10, indonesian 1–3 — already covered), other countries, other sites, or any retired source.

## Method
- Dedupe: every candidate checked against ~/workspace/whatsapp-groups-site/agent_batches/wave_20261028/dedupe_union_codes.txt (73,684 codes, which already includes wave 20261027 team09's 58 fresh + 94 pending).
- Verification: spaced curl of https://chat.whatsapp.com/<code> with browser User-Agent. Verified ONLY on HTTP success AND a non-empty, meaningful og:title (bare "WhatsApp Group Invite" would not count; none appeared as og:title in this batch). Empty/generic og:title → pending (if the scraped name is meaningful) or dropped (if both names meaningless).
- Content filter: only hard porn/xxx blocked (explicit porn terms including Indonesian bokep/VCS/crot/sange, porn emojis in sexual titles). Girls/friendship/dating/social groups were NOT dropped.

## Next-pass leads (not staged)
- groupjoin.link tag/Indonesia pages 31+ and tag/indonesian pages 16+ — same method; expect diminishing returns as the two tags converge on the same listing pool.
- More groupjoin.link topic/city tags (e.g. tag/Jakarta pages 2+, tag/Bali pages 2+ returned empty this run, but new listings may appear).
- Fresh Indonesian blogs/forums posting 2026 group links (not the retired list) — verify any code the same way before staging.
- Pending re-check: the 264 pending links mostly returned HTTP 200 with empty og:title — a later re-check may resolve titles for some of them.
