# Wave 20261103 summary — 66 workers (50 teams + 16 replacements/redirects), all complete/closed

- **Verified banked:** 5,410 items file-sum across 57 verified files (pre-merge). **~4,300 unique codes** after cross-file dedupe (1,094+ dup occurrences — see merge decisions below). Parent MUST re-dedupe everything against the current dedupe_union.json (84,400 codes; note it changed 86,389 → 84,400 mid-wave, so teams verified against both versions).
- **Pending (next-wave retry):** 14,819 items (transport failures / unverified candidates — do NOT merge; retry next wave)
- **Leads banked:** 294 (all in per-team `teamNN-leads.json`)
- **Porn drops (hard-blocked, never written):** ~255 (team41: ~67, team37: 55, team35: 25, team14: 19, team50: 12, team46: 10, team10: 9, team16: 7, team15b: 5, team17: 5, team30: 5, team38b: 5, team25R: 4, team43: 4, team22: 4, 46R: 5, team21: 2, team18: 2, team28b: 2, team12: 2, team36: 1, team48: 1, teams 03/04/07/08: 1 each)
- **Merge files:** per-team `teamNN-<desc>.json` in this dir (list: `manifest.txt`, 172 files). DO NOT merge `*-unverified-pending.json`, `*-leads.json`, `*-state.json`, `*-candidates*.json`, `team14_merged.json`, `team16-verified-raw.json`, scripts, or logs.
- **team11_postfix.py** already run on team11-gjl-sportsfitness.json (244 items, categories remapped, descriptions regenerated). team11b file is separate with 0 code overlap.

## Top contributors (verified, pre-merge)
1. team10 groupjoin.link online-shopping — 699 (deep pagination, still growing at close)
2. team30 groupjoin.link groupsinvite residual — 596 (team30b file is a 100% duplicate — merge counts 596 once)
3. team38b Egypt/Arabic directories — 514 (all fresh vs union; +14 net-new from team38R's 66)
4. team14 groupjoin.link new tags — 372
5. team46 crypto/earning — 264 (team46b file is a 100% duplicate — merge counts 264 once)
6. team11 groupjoin.link sports/fitness — 244 (+220 from team11b, 0 overlap — both additive)
7. team39R Brazil ongrupos.com — 239 (completed 24/40 categories)
8. team28b groups1 Colombia — 236 (+94 from team28R, 0 overlap — both additive)
9. team15b igrupos Mexico — 178 (+1 net-new from team15R's 25)
10. team30R groupjoin.link groupsinvite — 162 (+24 net-new beyond team30's 596)
11. team25R linkado.app — 143 (listing cards hide codes; /grup/<id> pages expose them)
12. team16 igrupos conosur — 125 (team16-verified-raw.json is a 100% duplicate — ignore it)
13. team12 groupjoin.link entertainment — 50
14. team22 groupwhat.com — 43
15. team51 groupda.pk — 32 (NEW source: groupda.com clone, reachable, 19 WP posts)

## Merge decisions for parent (dedupe pairs — verified by code comparison)
1. **team46-crypto-earning.json vs team46b-crypto-earning-extra.json: 264/264 IDENTICAL codes.** Include only ONE (264).
2. **team30-groupsinvite.json vs team30b-groupsinvite.json: 596/596 IDENTICAL codes.** Include only ONE (596).
3. **team16-igrupos-conosur.json vs team16-verified-raw.json: 125/125 IDENTICAL codes.** Include only conosur; ignore verified-raw.
4. **team41-germany.json (24) supersedes team41b-germany.json (5)** — the original worker appended its 5 to 41R's 19 before the guard arrived (strict superset, verified). Include team41-germany.json ONLY.
5. **team15b (178) vs team15R (25): 24 overlap** — 15R adds ~1 net-new code.
6. **team28b (236) vs team28R (94): 0 overlap** — include BOTH (330).
7. **team38b (514) vs team38R (66): 52 overlap** — include BOTH (528 unique).
8. **team30 (596) vs team30R (162): 138 overlap** — include BOTH (620 unique).
9. **team11 (244) vs team11b (220): 0 overlap** — include BOTH (464).
10. team14-gjl-newtags.json shares 3 codes with team11/team11b/team12 files — normal cross-team overlap, merge dedupes.
11. team46's handoff claimed "314 verified" but the file holds 264 — file is authoritative.

## Review flags for parent
1. team43 flagged 8 minors-targeted dating groups (excluded from verified, noted in leads) — brief only mandates porn drops; a minors-targeting policy may be needed.
2. team34 excluded 9 scam/HYIP groups; team27 excluded 1 NADRA data-sale scam; team49 excluded 1 drug-dealer og:title hijack; team46 excluded 1 USDT FLASH fraud; team13 flagged mule patterns (team13-mule-flags.json, empty).
3. team09 lead: a groupda.com Brazil page slug ends in "-18" — needs adult-content check before any future scrape (drop on sight if 18+).
4. team14: one verified item is a satta (numbers-gambling) group — kept (not on drop list), flagged. team14 also kept ~476 category_slug='adult' records whose titles had no adult keyword/emoji (mapped to Other) — parent may want to review this policy.
5. Porn-filter gaps found this wave: add "bokep" (team28b) and Urdu/Hindi sexual terms — team12 caught an Urdu video-call solicitation ("ویڈیو کال پر مزا دینے والی لڑکی") the English blocklist missed.

## Retirement / exhaustion findings (new this wave)
- **groupda.com: DOWN all wave from this VM** (DNS sinkholed to 198.18.104.48; real IP 94.229.208.10 per DoH; worked Nov 2). All 8 country-slice teams (02–09) banked 0 verified + leads. Retry next wave after recovery. groupda.pk (sister clone) WORKS — 32 verified, worth expanding.
- **groupjoin.link /tag/sports-and-fitness/ is EMPTY** (currentCount=0); the live route is /category/sports-and-fitness/ (team11R route correction).
- **Fresh sports listicles saturated** (team47R: 0 verified — every code already in union or dead).
- **elyex tag archives structurally exhausted** (team26: 1 verified).
- **groupwa.link category gallery is AJAX-only** (team21: 2 verified).
- **groupssor.com: 964 groups but JS-gated** (team20: 0 verified) — needs live browser.
- **New veins for next wave:** whatsappkanali.com (Turkish, server-rendered), grouplinksforyou.com (crypto/forex), thewhatspgrouplink.com (jobs/edu), ongrupos.com Brazil 40 categories (16 done by orig 39, 24 by 39R — recheck), appgrouplink.com /invite/-form codes (works under Nov-2 policy), groupor.link SSR flight-data route (best fresh-source technique), grupbul.com (JS-gated codes — needs live browser).

## Infra notes (for next wave)
- **Verification speed breakthrough (team16):** a keep-alive `requests.Session` does og:title checks in ~0.5–0.6s vs ~9s with fresh connections through the egress proxy (identical results). Standardize on session+rebuild-on-error next wave — this is the main reason verification-heavy slices took 60–90 min.
- chat.whatsapp.com verification is SLOW through the proxy (~8–60s/check) — workers need 45–60s timeouts, not 25s.
- Egress proxy died completely for ALL hosts ~07:00–07:15 PKT (even example.com), then recovered.
- web.archive.org 429-blocks this egress IP as "suspected abusive bot traffic" after ~15 availability checks + 3 fetches — next wave: ≥10s spacing, no parallelism on wayback.
- /tmp gets wiped mid-run by another process — workers must keep scratch in the wave dir.
- Runtime "restart drain" killed 8 original workers mid-run (19, 25, 45, 46, 47, 48, 49, 50); replacements covered all slices.
- Workers frequently mislabel team numbers in handoffs — file contents are authoritative, not labels. Filename-guard redirects (teamNNb/teamNNR names) prevented 6 clobber collisions this wave.
- dedupe_union.json changed 86,389 → 84,400 codes mid-wave (~06:56 UTC) — parent merge MUST re-dedupe everything against the current union regardless of what teams checked.
- team14's parser had a `unicode_escape` mojibake bug (fixed mid-run with repair_text(); tainted checkpoint wiped, verification restarted). team14_verify.py auto-resumes from team14_verify_ckpt.jsonl.
- team10: groupjoin.link `/tag/online-shopping/` is client-rendered (zero server-side records) — the `/category/` route server-renders 20/page and is the same pool.

## Resume points (next wave)
- team14: 2,625 pending (groupjoin.link new-tag candidates, incl. adult-slug records to drop)
- team38b: 2,238 pending (Egypt/Arabic candidates)
- team39b: 2,929 pending + team39R: 1,947 pending (Brazil ongrupos.com candidates)
- team17: 1,408 pending, team16: 936 pending, team15b: 896 pending, team15R: 949 pending (igrupos candidates)
- team25R: 464 pending (linkado.app candidates — detail pages harvested, liveness not attempted; resume: category ?page=2..N + detail pages; amizade category holds 4,763+ groups; new categories found: carros, cidades, comprar-e-venda, figurinhas, fitness, lgbt, moda-e-beleza, musica, namoro, series, status, games, tecnologia)
- team51: 4 pending (groupda.pk transport failures); resume: WP-API posts endpoint with after= date filter; groupda.pk homepage (520KB, "18+ Pakistan groups") timed out 3x — banked as lead
- team13: 156 candidates + 156 pending (tails — verification never completed)
- team29: 121 pending (thewhatspgrouplink.com)
- team01: 8 verified + groupda.com new-posts retry after origin recovery; team09: 8 leads (LatAm pages via wayback)
- 294 leads in teamNN-leads.json — heaviest JS-gated: grupbul.com, groupssor.com, groupmaster.app, linkado.app categories.
- team28b: 11,778 candidate codes from groups1.com remain UNVERIFIED (only 381 liveness-checked) — full pool at ~/workspace/team28_work/candidates.json (documented in team28b-leads.json); re-verify next wave, newest-post-first order.
- team38b: 2,218 Saudi scribd codes banked unattempted ("not attempted — resume point"); new Arabic leads: anyquizi.com (283 verified this wave), addwats.com (Cloudflare /go/ redirect — needs live browser), groupchatconnect.info (1,412 groups, 71 pages).
- team22: groupwhat.com detail pages add zero new codes — re-scrape listing pages (10 latest groups each) for newly added groups.
- team41: groupmaster.app exhausted (222 IDs, all resolved); grupbul.com + groupler.me need live browser / registration.
- groupjoin.link resume: online-shopping (team10 was still growing at 699 when closed), entertainment pp.47+ (team12), new tags (team14).
- team30R: classification stopped at 1,800/2,326 groupsinvite.link slugs (1,573 chat codes extracted; 71 timeout-errors unretried); verification covered 200 codes; 130/162 verified items have country=International (detail-page fetch cut short by wrap-up). Resume pipeline saved in `_team30R_state/` (copied from /tmp before wipe): re-run classify_rules.py → verify_codes.py → fetch_details.py → finalize.py. Structural notes: slugs starting 0029v*/029v* → WhatsApp channel links (231 excluded, channels never allowed); codes are case-sensitive (exact case only from /group/rules/ pages); 156 rules pages with no join button = dead listings.
