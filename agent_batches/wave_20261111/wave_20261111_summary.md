# Wave 20261111 — Summary

**Date:** Wed 2026-11-11. **Coordinator outputs on disk** (unlike Nov 10, when they went missing).

## Result

- **Verified new groups ready to merge: 3078**
- **Total would become: 73370 → 76448 groups** (parent merges; coordinator does not merge/deploy)
- **Dedupe union: 108992 codes** (groups.json codes are a subset)
- **Pending (transport failures, NOT merged): 1111** — banked in wave_20261111_pending_all.json
- **Leads (unique URLs + unverified codes): 21834** — banked in wave_20261111_leads_all.json
- **Excluded (coordinator screen): 21** — banked in wave_20261111_excluded.json

## Consolidation

- Raw team items: 3183 across 32 team files (24 teams banked verified items; 22 kept items after dedupe/screen).
- Cross-team dups removed: 84 (first-team-wins, team-number order; team06 won 64 linkado dups).
- Union leaks: 0. Schema errors: 0 (5 team09 empty names recovered via og:title).
- Coordinator screen drops: 41 initial → 22 false positives restored → 19 kept excluded, plus 2 spot-verify drops.
- Coordinator spot re-check: 35/35 sampled clean codes live; controls OK (known-live live, fabricated dead).
- False-positive restores: 22 (13 Portuguese prohibition sentences, sexta-Friday, chuta-verb, 4 18+/🔞 age gates, 3 more prohibition cases).
- Spot-verify drops: 2 (AI-trading daily-profits scam, team28 flag; sports-betting recruitment group).
- Schema-error name recoveries: 5 (team09 empty names → og:title names, all live and clean).

## Per-team kept counts

team01 125, team02 524, team03 196, team04 472, team05 807, team06 180, team07 45, team08 37, team09 14, team10 66, team11 34, team12 3, team13 0, team14 115, team15 0, team16 0, team17 1, team18 0, team19 0, team20 10, team21 0, team22 0, team23 16, team24 0, team25 12, team26 16, team27 73, team28 31, team29 9, team30 0, team31 292, team32 0.
Zero: teams 13, 15, 16, 18, 19, 21, 22, 24, 30, 32 (team13 Adult-excluded; team24 all dups of team09; team32 leads-only by design).

## Categories / countries (clean file)

Community & Social 772, Buy Sell 575, Friendship 399, Gaming 285, Online Earning 283, Jobs 180, Education 152, Sports 104, Entertainment 104, Finance 85, Technology 51, Islamic 24, Health 17, Business 13, News 13, Poetry 10, Funny 5, Cooking 3, Crypto 2, Real Estate 1.
Countries: (blank) 1385, BR 1344, PK 134, ID 84, IN 35, SA 20, BD 15, MY 12, LK 12, EG 9.

## Files

- manifest.txt
- wave_20261111_clean.json
- wave_20261111_clean_teams.json
- wave_20261111_pending_all.json
- wave_20261111_leads_all.json
- wave_20261111_excluded.json
- wave_20261111_cross_dups.json
- wave_20261111_union_leaks.json
- wave_20261111_schema_err.json
- coordinator_verify_state_20261111.json
- coordinator_build_clean_20261111.py
- coordinator_repair_20261111.py
- coordinator_verify_20261111.py
- coordinator_finalize_20261111.py
- coordinator_generate_manifest_20261111.py

## Notes / residual risks

- **Parent flag — Nov-10 scam codes in groups.json (team18):** KD408PRv4Kh1j81OBGMB6O,
  FQAEuMQvBZJKtOlCrsnmac, KkdRrp9oFNxLY9Q6eAwpGR, EghZlHeOTD406TCI21NChX — all 4 have
  airdrop/scam og:titles; the source site has since removed them. Consider purging from groups.json.
- og:title-vs-banked-name mismatches can only be caught by sampling: 1 of 35 sampled codes
  was a betting group (dropped). Full re-verification of all 3,078 was not feasible at ~25s/check.
- team31 (tglinkhub) names come from directory listing titles + og:title — same mismatch risk
  class as the Nov-10 HOLIVERSE case; its own exclusions already dropped ~500 scam/adult codes.
- team01 stream verifier still running at finalize; team31 checker dead (reboot); team02 has
  2,160 candidates awaiting verification — all banked as leads for the next wave.
- Egress lesson: use 60-90s timeouts + keep-alive sessions; short-timeout curls produced false
  transport failures mid-wave (read as a VM-wide outage by team30).
- Search Console indexing NOT attempted (balochaiza47 sign-in is device-gated) — parent handles.
