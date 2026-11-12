# WhatsGroupLinks daily scale-up — wave 20261112 summary

**Date:** Thu 2026-11-12. **Coordinator:** wave coordinator (36 leaf teams).
**Baseline:** 76,448 groups in `groups.json`; dedupe union 112,070 codes.

## Headline

- **7,316 verified new groups** ready to merge → `groups.json` would become **83,764** (+9.6%).
- Raw team items: 7,589. Cross-team dups: 57. Union leaks caught: 131 (all team01, stale union).
- Screen-excluded: 84 (after 14 false-positive restores). Spot-verify drops: 1.
- **Pending: 285** codes (transport failures, mostly WhatsApp 429s). **Leads: 8,252** (5,598 listing URLs + 2,654 code strings) for the next wave.
- Coordinator spot-check: **42/43 sampled clean codes confirmed live** (controls OK: known-live code live, fabricated code dead). One dead code dropped, three banked names corrected to their live og:titles.

## Top contributors

| Team | Source | Kept |
|---|---|---|
| 03 | tglinkhub (verify2 + bank) | 3,958 |
| 02 | leads slice 2 | 1,257 |
| 05 | leads slice 4 | 934 |
| 16 | whts.club sitemap (exhausted) | 783 |
| 01 | leads slice 1 | 41 |
| 06 | leads slice 7 pending re-check | 41 |
| 15 | groupslinks pp. 13–30 | 70 |
| 08 | linkado 3100–3499 | 39 |

Category mix of the clean batch: Community & Social 2,807 · Finance 616 · Education 564 · Friendship 544 · Jobs 490 · Buy Sell 480 · Entertainment 401 · Gaming 393 · Islamic 257 · Sports 232 · Business 149 · News 139 · Online Earning 89 · Funny 77 · Technology 38 · Health 24 · Poetry 8 · Crypto 4 · Cooking 4. Countries: BR 2,255 · IN 466 · PK 136 · ES 99 · AE 76 · ID 53 · OM 51 · CA 49 · NG 46 · ZA 45.

## Method finding — og:description is NOT a live signal

Nine teams independently confirmed this wave: WhatsApp serves `og:description = "WhatsApp Group Invite"` on **every** invite page, live and dead. Using it as a live fallback marks every dead code live. Several teams caught it mid-run and re-verified with og:title-only; team08's first pass had wrongly banked 173 dead codes and corrected them. **Rule for all future waves: LIVE = non-empty, non-generic og:title only** (the generic title "WhatsApp Group Invite" also counts as dead). Also confirmed: og:title serving is intermittent — live pages sometimes serve an empty title, dead pages never serve a group name — so an empty title must be retried (spaced) before a dead verdict.

## Screening

- 98 items flagged by the coordinator screen; **14 restored as false positives** after individual review: 6 team05 prohibition sentences the stripper missed (Portuguese "proibido", "sem porno", stylized-Unicode "SEM PORNO", "❌ porno/hentai" fragments), an 18+-content ban ("não pode NADA que é 18+"), three 18+/🔞 age gates on non-porn groups (dark-reality videos, alcohol sales, a cat group), a prohibition in a name ("LGBTQ MUNDIAL 🚫NO NUDES"), fruit emojis in a plant-game context (Shopee Tanam 🍇🍈🍉), a URL-id misread as a phone number, and an 18+ age gate on a generic fun group.
- 84 kept excluded: hard porn/xxx (call-girl, bokep, Brazzers, Desi bhabhi, Onlyfans, Xvideos, nude/naked/naughty/horny, friends-with-benefits, s3x), 18+ sexual groups (Aunty groups, Ullu/Alt Balaji Hot, Putaria 18+, video-call 18+), sports-betting promos (aposta/palpite), binary-option scams, "earn money without investment".
- **Adjudication needed (parent): 123 casino/slots signal-platform groups kept** (Tigrinho/Fortune Tiger, "plataformas pagantes", "sinais", "banca") — no sports-betting markers, kept per the task's sports-only wording; listed in `team05-casino-flagged.json`. Dropping them would take the batch to 7,193.

## Team01 union leaks

Team01 re-verified yesterday's merged-candidates pool against a stale (pre-merge) union: 131 of its 172 "verified" codes were already in `groups.json` from Nov 11. The coordinator caught all 131; 41 genuinely new codes kept. Same class as team05 (807 already-merged, stripped at team level) and team02 (526, not re-banked).

## Orphan process

Team03's agent was interrupted while its background `verify2_team03.py` was still running; it survived and kept appending results, and a bank re-run at ~10:21 UTC grew its candidates file 3,609 → 4,026. The coordinator killed the orphan (pid 1744) and re-ran build + repair + verify + finalize on the frozen file (team03 kept 3,553 → 3,958). Remaining unverified tglinkhub codes are banked as code strings in `leads_all`; `verify2_results_20261112.jsonl` is the resume checkpoint.

## Flags for the parent

- **4 Nov-10 crypto-airdrop scam codes still in `groups.json`** (re-flagged by team28): `KD408PRv4Kh1j81OBGMB6O`, `FQAEuMQvBZJKtOlCrsnmac`, `KkdRrp9oFNxLY9Q6eAwpGR`, `EghZlHeOTD406TCI21NChX` — the source site removed all four; purge candidate. Plus "LEGIT CRYPTO AIRDROPS" already in the union.
- `DiPrrTG7xdKB58iUQBk11l` ("LGBT COVEN", merged Nov 11) now shows live og:title "novinhos libertinos🔥🔞" — review for removal.
- Team23 dropped "Earing free money daily" (`Lj6vfsu3nrY3guCSY6kDjf`) as a daily-profits scam lure; last wave's coordinator kept generic earn-money pitches — parent can overrule.
- Team16's 9 borderline keeps (crude-but-not-explicit names) are in clean; listed in its summary.
- Team06 note: 4 kept candidates share the identical directory-style name "1000+ Online Earning WhatsApp Group Link" (different codes).
- Browser-leg backlog (leads needing live-browser clicks): igrupos 268 codes (JS/login-gated), grupbul /redirect ×2, groupsinvite 61 JS-gated pages, whts.club 372 codeless pages, tugrupo.online p4 + 26 detail pages (bot-blocked), SE Asia leads (aussiesin, joinnchat, groupwa wagd_more, Cloudflare pages), LatAm leads (grupodewhatsapp Turnstile, gruposdewats, whatshub.es 2,781 sitemap ids), listicles 6 grupbul JS-hidden pages.

## Resume points for the next wave (20261113)

- **tglinkhub:** ~2,394 codes still unverified — resume from `verify2_results_20261112.jsonl` + the code strings in `leads_all`.
- **linkado:** next index 3500 (`https://linkado.app/grupo/692b9aad3331053de980f389`, lastmod 2025-11-30); slices 0–3499 mined. Live rate falls with age (Mar–May ~36%, Jan–Mar ~1%).
- **groupslinks:** pages 31+ (13–30 done). **groupslinks.com** 45 pages fail with ProxyError — needs a different fetch route.
- **whts.club:** sitemap exhausted (1660/1660) — re-check for new entries only.
- **Pending re-check:** 285 codes (team20's 75 429s + team13's 101 transport failures + team06's 31 429s) — spaced, low concurrency.
- **Leads slices:** team01's 2,654 code strings (merged+deep pools) + 1,448 listing URLs; team10's 172, team11's 241 (Telegram/Channel — do not re-fetch), team12's 71, team14's linktogroups p5+, team16's 372 codeless pages, team30's 75 South-Asia leads.
- **Closed/exhausted:** tugrupo.com, walink.pk clean groups (3 waves zero), groupsnest, freewagroup, grouplinksforyou, groupjoin Adult, whatsappkanali, appgrouplink, groupizo, ongrupos, wglfinder tag archives, 77links Karachi/Islamic/marriage unchanged.

## Files

All in `~/workspace/whatsapp-groups-site/agent_batches/wave_20261112/`:
`wave_20261112_clean.json` (7,316) · `wave_20261112_clean_teams.json` · `wave_20261112_pending_all.json` (285) · `wave_20261112_leads_all.json` (8,252) · `wave_20261112_excluded.json` (84) · `wave_20261112_restored.json` (14) · `wave_20261112_cross_dups.json` (57) · `wave_20261112_union_leaks.json` (131) · `wave_20261112_schema_err.json` (0) · `wave_20261112_spotverify_drops.json` (1) · `coordinator_verify_state_20261112.json` (43 sampled: 42 live, 1 dead) · `manifest.txt` · this summary · `coordinator_build_clean_20261112.py` · `coordinator_repair_20261112.py` · `coordinator_verify_20261112.py` · `coordinator_finalize_20261112.py` · per-team `teamNN-<slice>-candidates.json` / `-pending.json` / `-leads.json` / `-summary.json` (team01/05 use `teamNN-leads-sliceN.json` for candidates).

**Not done by the coordinator:** no merge, no build, no deploy, no changes to `groups.json` — the parent handles merge/build/deploy.
