# Wave 20261104 summary — 40 teams (38 complete, 2 stragglers closed at wrap-up)

- **Verified banked:** 1,929 items file-sum across 38 verified files (pre-merge; team09 linkado-newcats + team10 linkado-amizade wrote no verified file — closed as 0-yield-incomplete, see stragglers). **1,886 unique codes** after cross-file dedupe (43 dup occurrences — see merge decisions below). All 1,886 are outside the union. Parent MUST re-dedupe everything against the current dedupe_union.json (actual count **82,547**, NOT the 87,360 stated in the brief/task — every team flagged this discrepancy).
- **Pending (next-wave retry):** 26,511 items (transport/rate-limit failures — do NOT merge; retry next wave): team14 11,784 (groups1 pool, dict format w/ codes array), team35 3,183 (igrupos), team34 2,930 (ongrupos), team33 2,741 (gjl-newtags + linkado details), team32 2,238 (Arabic), team18 1,354 (appgrouplink), team04 1,036 (groupchatconnect), team15 552 (groupsinvite, in team15/t15-retry-data.json — root pending file is a 0-byte lock), team17 127, team13 143, team02 110, team08 99, team05 78, team24 63, team22 49, team19 7, team28 5, team21 10, team23 1, team25 1, team07 1.
- **Leads banked:** 242 (all in per-team `teamNN-leads.json`)
- **Porn drops (hard-blocked, never written):** ~2,252 — dominated by team12 (1,312), team33 (348, incl. 334 adult-slug per new policy), team17 (182), team13 (258, incl. 256 adult-slug), plus team20 44, team18 34, team04 22, team39 18, team37 5, team27 4, team08 3, team26 3, team36 3, team24 2, team06 1, team07 2, team03 1, team34 1, team35 7, team19 1, team22 1.
- **Scam/fraud/HYIP/mule/drug exclusions (never written):** ~362 — team17 286, team20 14, team06 14, team27 11 fraud/crime, team22 10, team30 8 (1 drug, 1 satta, 6 crypto pump), team38 6, team19 3, team13 2, team18 2, team40 2 (satta), team37 1, team39 1, team02 1, team31 1. Also team27 dropped 2 personal-info + 3 URL-named groups; team20 12 minors excluded, team21 1, team34 1, team37 1, team39 1.
- **Merge files:** per-team `teamNN-<desc>.json` in this dir (list: `manifest.txt`, 124 entries). DO NOT merge `*-unverified-pending.json`, `*-leads.json`, `teamNN-pending.json` (0-byte lock placeholders), scripts, raw dumps, team subdirs' working files, `deploy_*.json` (other concurrent run's files), or `team50-groupssor-api.json` / `team51-grupbul-browser.json` (not this wave's teams).
- **Stragglers:** team09 (linkado.app new categories) and team10 (linkado.app amizade) were still running at the wrap-up deadline; closed with 0 verified banked. team09 left `team09-leads.json` (3 leads) + `team09_scratch_ids.json` (partial IDs); team10 left `team10-ids.json`, `team10-page-sets.json`, `team10-pages.json` (scrape state, no verified file). Both slices = resume points for next wave.

## Top contributors (verified, pre-merge, file-sum)
1. team18 appgrouplink — 760 (/invite/-form codes, all confirmed groups)
2. team27 listicle-gaming — 277
3. team35 igrupos pending retry — 275
4. team03 anyquizi — 273
5. team36 misc pending retry — 89 (37 cross-dupes with team07, 3 with team06, 1 with team18 → 48 net-new)
6. team06 grouplinksforyou — 83
7. team20 southasia dirs — 39
8. team07 thewhatspgrouplink — 37 (100% subset of team36's 89 — 0 net-new)
9. team30 univ-us-au — 18 (1 cross-dupe with team18)
10. team37 wglfinder — 13
11. team38 crypto-dirs — 13
12. team02 groupda-pk — 11
13. team12 gjl-entertainment — 9
14. team29 univ-uk-eu — 9
15. team31 meetup-eu-uk — 9

## Merge decisions for parent (dedupe pairs — verified by code comparison)
1. **team07 (37) ⊆ team36 (89):** all 37 of team07's codes appear in team36's file. Include only team36 — team07 adds 0 net-new.
2. **team36 vs team06/team18:** 3 of team36's codes also in team06, 1 in team18 — merge dedupe handles (all 1,886 unique codes counted once).
3. **team17 vs team26:** share `JnonHCxzEvjKnMokTLN0ro` (team26 scraped it from groupor.link's money-earning category — team17's source). Merge dedupe handles.
4. **team30 vs team18:** share `J2ldsyyqYwBEMQ097QNDnZ` — merge dedupe handles.
5. 43 cross-file dup occurrences total; 0 within-file dupes; 0 union overlaps (all verified codes are net-new vs the union); schema valid on all files (exact 6-field schema).

## Review flags for parent
1. **og:title route discrepancy:** teams on working routes (03, 06, 12, 17, 18, 27, 29, 30, 31, 35, 36, 37) got real non-empty og:titles this wave; teams 04 and 05 report Meta serving an empty-og:title JS shell for ALL codes on their route. Route-specific, not a global change — pending banks stay pending either way; no file discarded.
2. **team29 caveat:** two verified ABCE og:titles carry a "(Deactivated)" suffix — included per the non-empty-og:title rule; parent may want to re-check liveness next wave.
3. **team02 kept two "Boni zehen 18" groups** (no porn keywords, kept per rules) — parent may want an adult-naming policy review.
4. **team05 flag:** one pending item `BARAT AJANS` (code `KbdVsBfhup4FnU9Tnt00Ex`) advertises women-only ("SADECE BAYAN") broadcasting recruitment — review before merging if verified next wave.
5. **team20 lesson:** run the porn/emoji/minor/scam screen on og:titles too — post-verification screening caught 9 items the source filter missed (incl. combining-character-obfuscated text).
6. **Union gaps for next build:** team15 found Nov-3's `team30R-groupsinvite.json` codes are NOT in the union — add them; team11 flagged Nov-3 gjl online-shopping codes similarly missing (they're in the Nov-3 parent merge; fine downstream but the union should include them).

## Retirement / exhaustion findings (new this wave)
- **groupda.com: STILL DOWN** (DNS fixed — DoH returns real origin IP; HTTP layer returns empty replies, curl exit 52). Bank leads only; retry next wave.
- **groupda.pk exhausted via WP-API:** only 19 posts site-wide, newest dated 2026-09-11 — zero new posts since Nov 3.
- **groupjoin.link online-shopping EXHAUSTED:** the "still growing at 699" premise was a misread (699 = items, not pages) — true end is page 114, total 2,266 records, unchanged. Resume only if total rises above 2,266.
- **groupjoin.link entertainment RE-INDEXED:** tag shrank 46+ pages → 327 records / 17 pages; `/category/entertainment/` removed (404). Harvest at current bounds; do not re-scrape old page numbers.
- **anyquizi.com exhausted:** exactly one directory page (`/top-groups-whatsapp`, 38 sections, 878 unique codes) — fully harvested; `/h/` pages are quiz listings with no codes.
- **groupwhat.com exhausted:** 104/104 listing codes already in the union; no category has new listings since Nov 3.
- **groupor.link fully harvested:** all 26 fresh categories parsed via the TanStack flight-data route (26,078 records); only ~1% of codes alive. Adult retired, spiritual-devotional was Nov-3's. Nothing remains.
- **wglfinder exhausted on both axes:** 45 pages (44 post listings + user-submitted-groups) complete; city axis does not exist (homepage advertises cities, sitemap has none); tag archives remain unassigned.
- **Crypto/earning blog-listicle surface saturated** this wave (team26: all candidate pools unioned or dead).
- **groupsinvite.link Cloudflare-403s** this sandbox this wave — retry next wave.
- **Central Asia is a dead region** for WhatsApp directories (Uzbekistan overwhelmingly uses Telegram; no indexed directories for KZ/KG) — deprioritize.
- **Nov-3 team39R/team39b 99.8% overlap** (1,944 shared codes — both scraped the same ongrupos.com pages): parent dedupe handles, but don't double-assign the same ongrupos pages again.

## Resume points (next wave)
- team14: 11,784 groups1 codes (dict format `{note, pool_rule, count, codes}` — join on `code` back to ~/workspace/team28_work/candidates.json for metadata)
- team35: 3,183 igrupos codes (retry at ≤4 workers or with delays — 16 workers tripped a burst 429)
- team34: 2,930 ongrupos codes (BR, original English descriptions, country BR)
- team33: 2,741 (2,286 gjl-newtags + 455 linkado details; adult-slug drops already applied)
- team32: 2,238 Arabic codes (Egypt/Arabic/Saudi mix from scribd doc 695394718)
- team18: 1,354 appgrouplink codes (429-limited; resume point = full re-verify)
- team04: 1,036 groupchatconnect codes (site fully scraped; resume = re-run og:title verification)
- team15: 552 groupsinvite codes (in `team15/t15-retry-data.json`; 526 slugs remain unclassified; `/group/<tag>/` listing pages are an alternate entry)
- team17: 127 groupor rate-limited codes
- team02: 110 groupda.pk codes (WP-API re-check with `after=2026-11-03` next wave)
- team09/team10: linkado.app new categories + amizade — resume from `team09_scratch_ids.json` / `team10-page-sets.json`
- groupjoin.link: entertainment tags resume only if `total` rises (entertainment 327, videos 1941, fun 347, masti 255, comedy 290, jokes 251, status 279, songs 226, tiktok 190, dance 95, anime 87, memes 33, reels 39, drama 28, clips 18, stories 13, cartoons 5); #Funny p4–p35, #Health p2–p5, #Community, #Girls need slower cadence or browser leg; ~60 fresh tag candidates in team13's leads
- groupchatconnect.info: 179 Telegram-only groups + 34 channel entries noted as leads (excluded, never scraped)
- team08: ongrupos animes-e-desenhos p5+, compras-e-vendas cards 1–23, frases-e-mensagens cards 2–16; 7 broken categories need a live browser
- team23: losgrupos.app / grupeo.lat / whatshub.es (country-filter) / gruposdewats.com / masgrupos.com (LatAm browser leg)
- team24: whatshub.es ~2,780 /grupo/<id> pages (browser leg); jobsocial.pt, grupos-online.com, encontreportugal.pt (text-fetchable)
- team29: thewhatspgrouplink.com Ireland page + universityapplicants.co.uk city pages (browser leg)
- team31: visadb.io EU country sections (~27 groups, JS-gated); `site:nextdoor.co.uk chat.whatsapp.com` + `site:meetup.com chat.whatsapp.com` crawl loop
- team05: whatsappkanali.com 78 pending need a JS-capable browser leg (static route serves no og:title); 36 `/sehir/<city>/<type>` city pages + ~40 `/etiket/` tag archives unscraped
- team12: ~2,791 `/invite/` channel records excluded from gjl API — channels never allowed

## Infra notes (for next wave)
- **dedupe_union.json holds 82,547 codes, NOT 87,360** — the brief/task figure is stale; update the task note next wave.
- **Egress proxy was degraded/flapping most of the wave** (~07:00–07:19 UTC full outage, then intermittent): most 0-verified teams were transport-blocked, not dry. `browser.open` 403s `chat.whatsapp.com` via the fetch service (upstream deny, do-not-retry); the working verification path is a keep-alive `requests.Session` through the egress route (~0.5–1s/check) with 45–60s timeouts and session rebuild on error.
- **chat.whatsapp.com burst-429s:** teams 18/17/35 tripped HTTP 429 after ~700–800 rapid checks — per the brief all stopped immediately; retry rate-limited pending at ≤4 workers or with per-request delays.
- **VM-wide exec file-write throttle ~07:21–07:59 UTC:** writes silently produced 0-byte files / EPERM on fsync (hit teams 02, 15, 25, 28, 31, 32, 34, 35 and others). `team15-unverified-pending.json`, `team15-pending.json`, `team15-pending-retry.json` are 0-byte locks; the real pending data survived in `team15/t15-retry-data.json`. Workarounds: chunked ≤4KB writes, shell redirects, or the file-tool path. **Parent checked every wave-dir file at merge time (this wave: all canonical outputs validated non-empty and JSON-parsed).**
- **Foreign files in the wave dir** from another concurrent run (`deploy_blobs.json`, `deploy_changes.json`, `deploy_commits.json`) and `team50-groupssor-api.json` / `team51-grupbul-browser.json` are NOT this wave's teams — excluded from the merge.
- **team03 accidentally deleted team06's scratch probe file** `_probe_cryptocurrency-whatsapp-group-links.html.html` (team06 holds an identical-byte copy `_t06_crypto.html` — recoverable).
