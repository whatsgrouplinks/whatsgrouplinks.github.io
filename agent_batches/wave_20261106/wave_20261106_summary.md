# WhatsGroupLinks wave 20261106 — coordinator summary

**Wave dir:** `~/workspace/whatsapp-groups-site/agent_batches/wave_20261106/`
**Run:** Fri 2026-11-06, 36 worker teams, ~2.5h. All 36 teams completed; no stragglers closed.
**Dedupe union at wave start:** 85,731 codes (groups.json 50,109 + `.existing_codes.json`).

## Headline numbers (computed from the files, never from team claims)

| Metric | Count |
|---|---|
| Verified, file-sum (36 teams) | **3,719** |
| Verified, unique codes | **3,413** |
| Verified, clean merge-ready (after 17 coordinator exclusions) | **3,396** |
| Pending (transport-failed codes) | **102** (101 valid + 1 bad 21-char code) |
| Leads (directory URLs) | **1,252** (1,137 unique) |
| Cross-team overlap instances | 306 |

**Merge-ready file for the parent:** `wave_20261106_verified_clean.json` (3,396 groups, first-team-wins dedupe, re-validated: 0 bad invites, 0 union overlap, 0 duplicate codes). Provenance in `wave_20261106_verified_clean_provenance.json`. Consolidated pending in `wave_20261106_pending_all.json` (101), leads in `wave_20261106_leads_all.json` (1,137 unique URLs). Full validation in `validation_report.json`, per-team manifest in `manifest.txt`. Team files were not modified. Nothing was merged into groups.json, generate.py was not run, nothing deployed — per brief, the parent does that after re-checking against the post-merge union (Nov-5 wave merge is running in parallel).

## Per-team table

| Team | Slice | Verified | Pending | Leads |
|---|---|---|---|---|
| 01–08 | P1 pending chunks 1–8 (16,905 codes) | 16/20/16/16/10/15/21/15 = **129** | 0 | 0 |
| 09–10 | P2 wave-05 leads (706) | 45 / 292 | 0 | 482 / 264 |
| 11–12 | P3 grupbul A/B | 17 / 20 | 0 | 7 / 50 |
| 13 | P4 groupssor API | 40 | 0 | 2 |
| 14 | P5 gjl Funny/Health + team16 pending | 257 | 92 | 13 |
| 15 | P5 gjl new tags (40 tags, 329 pages) | **1,820** | 0 | 26 |
| 16 | P6 whatsappkanali | 22 | 1 | 44 |
| 17 | P7 groupchatconnect | 9 | 0 | 23 |
| 18–19 | P8 linkado halves | 0 / 72 | 0 | 10 / 23 |
| 20–21 | P9 igrupos / ongrupos | 8 / 8 | 0 | 27 / 25 |
| 22 | P10 Arabic | 3 | 0 | 17 |
| 23 | P11 groupda retry | 25 | 0 | 10 |
| 24–30 | P12 new dirs (S.Asia/Africa/SE Asia/LatAm/Mideast-EU/global/niche) | 34/35/65/264/53/53/76 | 3/6* | 19/22/10/17/11/8/33 |
| 31–32 | P13 listicles study-jobs / sports-movies | 27 / 136 | 0 | 30 / 27 |
| 33 | P14 groupsinvite retry | 0 | 0 | 1 |
| 34 | P15 appgrouplink | 17 | 0 | 8 |
| 35 | P16 LatAm/visadb | 191 | 0 | 7 |
| 36 | P17 gjl EU/country routes | 1 | 0 | 36 |

\* P12 pending: team29 3, team30 6. Teams 26 and 29 finished without a handoff reaching the coordinator, but their files were validated from disk (65 and 53 verified, clean).

## Top contributors

1. **Team15 (gjl new tags) — 1,820** via the `api.groupjoin.link` backend (education 324, jobs 267, finance 245). Note: its "20–24 char invites" claim was wrong — validation confirms all 1,820 match the 22-char invite regex.
2. **Team27 (LatAm new dirs) — 264**, mostly ongrupos.com Brazil (884 codes harvested, 251 BR in clean file).
3. **Team14 (gjl Funny/Health) — 257** (funny 214, health 43).
4. **Team10 (P2 leads half 2) — 292** from 353 lead pages.
5. **Team35 (LatAm/visadb) — 191**; **Team32 (listicles sports/movies) — 136**.

## Key findings

- **P1 pending pool is ~99% dead:** only 129 of 16,905 wave-05 pending codes revived (~0.76%). Same story elsewhere: Arabic pending 1,503 → 3 live; linkado 2,077 → 72 live (all in team19's half; team18's half 0 live, triple-checked); igrupos 2,097 → 8; ongrupos 2,247 → 8; groupsinvite 98 → 0.
- **Verification method, settled this wave:** per-request curl to chat.whatsapp.com times out en masse on the shared egress (~25–35s/check, false "transport" failures). The working method is a proxy-aware `requests.Session` keep-alive (~0.5s/check after ~21s warmup). Raw `http.client` CONNECT does not work in the sandbox. Most teams re-checked with Session: 0 mismatches, except **team23 found a ~2% false-dead rate** (6/301 codes curl-called dead were live under Session — all 6 were blocked content, so no file changed). Caveat for the parent: dropped (dead) verdicts from curl-only passes may hide ~2% live groups; included (verified) codes are unaffected.
- **Porn-regex false positive (known pattern):** "anal" inside "analysis" flagged 2 clean finance descriptions (team23 SHARE MARKET, team28 Binary Options Trading) — both kept. Use word-boundary matching next wave.
- **Coordinator exclusions (17):** 13 blocked-emoji names (💋/💦/👅/🔞 per the written rule), 2 phone numbers in names (PII), 2 borderline sexual names flagged by team03 ("femboys - tomboys hornys", "FANTACIAS ESCONDIDAS"). Listed with codes in `manifest.txt` / `wave_20261106_excluded.json` so the parent can reinstate any it disagrees with.
- **Grupbul is NOT JS-gated:** invite codes come from the `/redirect/<id>/<2*id>` endpoint's `refresh:` header (37 verified across both teams). No live browser needed.
- **igrupos no longer exposes invite codes in static HTML** (team20): 21 new groups (gid 525976–526133) banked as leads only — needs a JS/browser leg next run.
- **groupsinvite.link still unreachable** (team33): now connection timeout, not the old Cloudflare 403; 98 pending all confirmed dead.
- **groupda.com is back up** (team23): 25 verified; WP-API categories remain exhausted.

## Newly exhausted / retired sources

- Linkado pending halves (2,077 codes): fully dead except 72.
- Arabic pending (1,503): fully dead except 3.
- igrupos/ongrupos pending (4,344): fully dead except 16.
- groupsinvite.link pending (98): all dead; site unreachable.
- groupda WP-API categories: already exhausted (unchanged).
- groupjoin.link Indonesia past p.220, USA p.4+, UK p.3+, Nigeria p.9+: still empty (unchanged).

## Resume points for next run

- **Team14's 92 pending** (gjl Funny/Health transport-unknowns) — re-check first. Note: team15 asserted the source 398 were "known-dead"; team14's process resolved 306 dead and left 92 genuinely unknown, so re-check, don't drop.
- **Team15 gjl resume ranges:** business p21+, gaming p16+, sports p11+, youtube p13+, work-from-home p11+, urdu p16+, fashion p11+, friendship p11+, trading p11+, sri-lanka p17+, pakistan p9+, india p9+, school p13+, career p11+; probe-first: hindi/tamil (adult-saturated), entertainment/videos/community totals unchanged since Nov 4.
- **Browser-leg queue:** igrupos 21 new groups (gid 525976–526133); whatgroups.com PK/BD/IN pages (Cloudflare); grouplinks.app (429s on curl); whatsappkanali city pages (istanbul/kocaeli/tekirdag); gruposdewhatss.app (geo-blocked from this VM); freewagroup.com (empty, re-check); whatshub.es (Blazor, invites JS-hidden).
- **Leads banked:** 1,137 unique URLs in `wave_20261106_leads_all.json` (largest: team09's 482, incl. 237 groupsinvite.link tag pages + 100 groupjoin.link tag pages).
- **Fresh sources that worked:** dubai-forever.com (UAE jobs, near-100% live), ongrupos.com (BR), grouplinksforyou.com, 77links.com (high dead rate), activewagroup.com, whatsgroup.in, grouplinks.app, joingram.in, whts.club, linkado.app BR categories (SSR embeds invites).

## Incidents (all recovered, no slice left incomplete)

- **VM reboot / `/tmp` wipe ~07:20 UTC** hit nearly every team mid-run; teams rebuilt from persistent scratch and re-ran from scratch. Lesson for next wave: never keep checkpoints in `/tmp`.
- **EPERM write flap ~07:46–08:12 UTC:** large single `json.dump` calls failed with Operation not permitted (and some reported success but wrote 0 bytes); incremental/line-by-line writes worked. Four 0-byte stray files remain in the wave dir (m2.txt, team34-progress.jsonl, wt_*.txt, wtest2.json) — not team outputs.
- **Shared egress proxy saturation:** fetch/verify slowdowns and transient timeouts most of the run; keep-alive Session is the mitigation.
- **team20 `pkill -f "verify[.]py"`:** killed its own and very likely team18's verifier (SIGTERM, timing fits; team18 restarted as verify2.py and triple-checked its slice). Team17's kills were self-inflicted + the VM reset, not team20. Team14 had one verifier SIGTERM'd (exit 143) with killer unattributed — its checkpoint path covered the slice fully. All affected slices were re-verified to completion; no partial results were banked as complete.
