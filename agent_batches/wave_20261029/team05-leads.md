# TEAM 05 — leads.md — groupjoin.link Kenya pages 3 & 4 (wave_20261029, 2026-10-29)

## Name-only leads (from harvested pages, not submitted as links)

Pages scanned: https://www.groupjoin.link/country/113 (Kenya) ?page=3 (20 groups) and ?page=4 (4 groups) — 24 groups total. Every single invite code on both pages already existed in the dedupe union (groups.json + .existing_codes.json), so no links were submitted. Names listed here for record-keeping only:

**Page 3 (20):** LEGIT FAST MONEY TRANSFER Agent · CRYPTO MINING BOX · sax Chart · 90MIN F⚽⚽TBALL✅ · Ab Top Show · pron Videos ad flirting · 🌏BETFUSE AND SPORTYBET AND BET9JA ✅ SURE ODDS 💼🫂 · Money deals🤑Kyc,binance, WeChat... Legit ✅ · Kenya real hookups no scum · Justine fixed odds · Vans' Team♂️KYC💰 · Meri Ghar ki · 𝗥𝗘𝗔𝗟 𝗞𝗘𝗡𝗬𝗔𝗡𝗦 𝗗𝗟𝗦 𝗚𝗥𝗢𝗨𝗣 · 🤤🫦മഴ കുളിർ 0.1💦 · Niccur Drips💥 · ... · NASA space science Elites 🚀👨‍🚀 · 👅കളിക്കൊട്ട 0.2💦 · video
**Page 4 (4):** Art & Animation [gigs| events |funding | call outs] Kenya🇰🇪 · 💪Winning mentality 🔥 · Gay videos · 💦കളിയോട് കളികൾ OG💥

## Out-of-slice fresh directories

- None found this wave. The groupjoin.link Kenya country page (country/113) is the only in-slice directory; no new Kenya-specific directories surfaced on groupjoin.link.

## Exhausted pages

- groupjoin.link Kenya p.3 — fully harvested (20 groups), 0 fresh codes (all dup).
- groupjoin.link Kenya p.4 — fully harvested (4 groups), 0 fresh codes (all dup).
- (Per task briefing: pp.1–2 harvested by sibling workers, pp.5–8 confirmed empty — not revisited.)

## Notes

- Country listing pages (Next.js) do not embed chat.whatsapp.com codes; invite codes come from the per-group API: `https://api.groupjoin.link/groups/<numeric-id>` (numeric id extracted from each group page's `/report?id=NNNN` link). API field `group_id` = the chat.whatsapp.com invite code; `invites[].groupCode` mirrors it. API was rate-flaky (timeouts/IncompleteRead); retried with curl + backoff until all 24 records resolved.
- Content rule: even without dedupe, several titles on these pages would be dropped on content grounds (adult/leet-adult: "Gay videos", "pron Videos ad flirting", "sax Chart", Malayalam suggestive-emoji titles; meaningless: "video", "...", "Ab Top Show", "Meri Ghar ki", "Niccur Drips"). Nothing worth chasing on re-scan unless the country pages rotate in new groups.
- Verification budget untouched this wave (0 candidates survived dedupe, so no curl verification was needed; no 429 encountered).
- Files: `team05-fresh-groupjoin-kenya.json` = [] (verified), `team05-unverified-pending.json` = [] (candidates). Both valid JSON arrays.
