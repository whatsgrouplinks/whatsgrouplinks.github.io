# Wave 20261026 — coordinator summary

20 teams, all reported. No groups.json, generate.py, or deploy changes made by the coordinator.

## Totals (verified from team files on disk)
- **Verified: 35** — team05 Malaysia/Singapore 14, team16 Education/Scholarship/Jobs 10, team06 Philippines/Vietnam/Thailand 7, team07 Nigeria 3, team18 Islamic/Community 1. All other teams 0 verified.
- **Unverified-pending: 234 items** = 114 code-bearing + 120 name-only (no invite code).
  - Code-bearing pending (113 unique codes): team01 17, team09 15, team15 15, team05 13, team14 11, team20 11, team13 9, team10 8, team12 6, team06 5, team11 3, team08 1.
  - Name-only pending: team02 95 (India), team03 25 (Pakistan).
- **Cross-team dups dropped at coordinator check: 2** — 1 pending-pending duplicate (team13 + team20 share one code) and 1 verified-vs-pending overlap (team16 verified code also sits in team01 pending; verified wins). Merge-ready unique pending codes after those drops: 112.
- **Overlap with existing set: 0** — every verified and pending code was checked against the full 73,092-code union (groups.json 37,969 codes + .existing_codes.json). Verified files: 0 internal duplicates, 0 porn-regex hits, 0 descriptions containing http/www.

## Why verified is low this wave — the dominant blocker
Shell curl egress was dead at the start of the wave (HTTP 000 even for example.com) and recovered mid-run. Teams that ran early banked everything as pending; teams that ran after recovery verified normally (teams 05, 06, 07, 16, 18). The parent should re-run curl verification (HTTP success + non-empty og:title) over the 114 code-bearing pending items — a large share may promote to verified. Two pending subsets need special handling:
- Team05's 13 pending: HTTP 200 + empty og:title on two spaced attempts — prior-wave convention treats that as dead; drop unless a third check passes.
- Team12's 6 pending + team08's 1 pending: codes taken from directory page URL slugs, not from a chat.whatsapp.com link — confirm each slug equals the real invite code before merging.

## Second structural finding: Join-button directories dominate
Most "new" directories found this wave hide codes behind Join buttons/JS or bot challenges, so text-fetch scraping yields names only. The big name-only banks needing a live-browser Join-click pass: team02 (95 India names), team03 (25 Pakistan names), team17 (57 entertainment/gaming names), team19 (~90 crypto/earning/business names), team11 Spanish directories (whatshub.es, gruposwats.com, erappmus.com), team09 Namibia/Gauteng pages, team08 walinking.link catalogue, team03 hubrecipes/theiq.pk/whatsagroupslinks pages.

## New retirements / corrections
- **activewagroup.com — NOT new (correction by team04):** already harvested in wave 20261025 (teams 09/10/28/31/48/50). Treat as covered; any future reuse must be checked by code against team48's verified set, not by name. It shares a name template with the retired wagroupnest.com family and its "100% Active" claim is untrusted.
- **Syndication warning (team18):** whtsgroupslinks.com, scribd.online, dailygrouplinks.com share one common code pool — 36/39, 4/4, 5/5 clean candidates already known. Future waves should prefer genuinely different listing formats over more listicles of the same pool.
- **Confirmed fully harvested (no new codes):** dubai-forever.com (team17 wave 20261025 + team20/team14 re-checks), satyainpoland.com (team37 wave 20261025), sg.theasianparent.com (team13 wave 20261025).
- **No new permanent retirements** beyond the activewagroup correction; no porn-blocked items were included in any output; girls/friendship groups kept per rule.
- **Uncovered slices:** Myanmar (no usable directory found), Ivory Coast (only personal-phone TikTok posts, excluded), Indonesia (names only, no extractable codes), Egypt/Saudi/Morocco/Algeria/Poland (all surfaced codes already known).

## Files
- Per-team verified: `teamNN-fresh-<slice>.json` / `teamNN-cat-<slice>.json` (verified items only, empty `[]` for 0-yield teams)
- Per-team pending: `teamNN-unverified-pending.json`
- Per-team leads: `teamNN-leads.md` (name-only / page-level, never merge input)
- This manifest: `manifest.txt`; this summary: `wave_20261026_summary.md`
- Note: `parent_verify_wave20261026.py` in this dir was created by the parent's separate pass (330 banked codes from wave 20261025) — not touched by the coordinator.

## Parent actions needed (not done by coordinator)
1. Re-run curl verification over the 114 code-bearing pending items (with the team05/team12/team08 caveats above); promote survivors, applying the 2 cross-team drops.
2. Live-browser Join-click pass over the name-only lead banks (team02, team03, team17, team19 first).
3. Then merge + generate + deploy under the normal deploy-completeness gate (not this coordinator's job).
