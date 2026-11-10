# Wave 20261110 — Summary (REPAIR RUN)

**Date:** Tue 2026-11-10. **Coordinator outputs were missing at resolution** (no manifest.txt,
wave_20261110_clean.json, *_pending.json, *_leads_all.json, *_summary.md). This repair run
consolidated the 32 teams' final files directly and completed the pipeline.

## Result

- **Verified new groups added: 628**
- **Total: 72,742 → 73,370 groups** (groups.json verified before and after merge)
- **Dedupe union: 108,364 → 108,992 codes**
- **Deploy:** git push to whatsgrouplinks/whatsgrouplinks.github.io (commit TBD — see manifest.txt)
- **Deploy gate:** TBD (see manifest.txt)

## Consolidation

- Raw team items: 646 across 21 final team files (11 teams verified 0).
- Cross-team dups removed: 14 (first-team-wins, team-number order).
- Union leaks: 0. Schema errors: 0.
- Coordinator screen drops: 3 (crypto-airdrop scam signals, team18).
- Parent-verify og:title drop: 1 (HOLIVERSE/meta-whale scam, team18 — banked name hid it).
- False-positive restored: 1 (Cook & bake, team04 — 🍆 emoji in food context).
- Parent-verify spot re-check: 35/35 sampled clean codes live; controls OK
  (known-live groups.json code live, fabricated code dead).
- Pending (transport failures, NOT merged): 397 — 309 team09 recheck + 88 others.
  Banked in wave_20261110_pending_all.json for a future browser-leg re-check only.
- Leads (unique listing URLs): 28,822 in wave_20261110_leads_all.json.
- Excluded: 4 in wave_20261110_excluded.json.

## Per-team kept counts

team01 11, team04 1, team05 15, team07 2, team08 22, team10 73, team11 19,
team12 3, team14 8, team18 4, team20 23, team23 4, team24 23, team25 8,
team26 38, team27 6, team28 15, team29 1, team30 3, team32 349.
Zero: teams 02, 03, 06, 09, 13, 15, 16, 17 (dups of team07), 19, 21, 22, 31.

## Files

- manifest.txt — full manifest (per-team table, parent-verify notes, deploy gate)
- wave_20261110_clean.json — 628 verified groups merged
- wave_20261110_clean_teams.json — code → team attribution
- wave_20261110_pending_all.json — 397 pending (future re-check only)
- wave_20261110_leads_all.json — 28,822 unique lead URLs
- wave_20261110_excluded.json — 4 coordinator/parent-verify drops
- wave_20261110_cross_dups.json — 14 cross-team dups
- wave_20261110_union_leaks.json — empty (0 leaks)
- wave_20261110_schema_err.json — empty (0 errors)
- parent_verify_state_20261110.json — 35 spot checks + 2 controls
- coordinator_build_clean_20261110.py / parent_verify_wave20261110.py /
  merge_wave20261110.py / aggregate_pending_leads_20261110.py /
  build_changeset_20261110.py / cp_sync_20261110.py — repair-run scripts
- deploy_changes_20261110.json — build → deploy blob-SHA changeset
- groups.json.bak-20261110-premerge — pre-merge groups.json backup

## Notes / residual risks

- og:title-vs-banked-name mismatches can only be caught by sampling: 1 of 35
  sampled codes hid a scam name (HOLIVERSE). Full re-verification of all 628
  was not feasible at ~10s/check from this VM.
- team32 (tglinkhub) names come from directory listing titles, not og:title —
  same mismatch risk class as the HOLIVERSE case; its own exclusions already
  dropped ~100 scam/adult codes on og:title.
- Search Console indexing NOT attempted (balochaiza47 sign-in is device-gated).
