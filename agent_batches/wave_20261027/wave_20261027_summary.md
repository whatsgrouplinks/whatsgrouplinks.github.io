# WhatsGroupLinks wave 20261027 — summary

30 parallel leaf teams, each owning a distinct country/category slice. All counts below were verified from the team files on disk, not from team claims alone.

## Totals (from files on disk)
- **Verified: 166** (166 unique codes, 0 internal duplicates)
- **Pending (code-bearing, unverified): 372 items = 349 unique codes**
- **Cross-team dupes dropped: 23** — all 23 are team01 ↔ team27 duplicates of the same Kenya university freshers codes. Merge-ready unique pending after this drop: 349.
- **Overlap with existing dropped: 0 in the output files** — neither the verified nor the pending files contain any code from the existing 73,170-code union (groups.json 38,051 groups UNION .existing_codes.json 73,169 codes). Teams additionally reported dropping hundreds of already-known candidates during collection (per-team counts in manifest.txt).
- **Porn drops:** team04 blocked 1 hard-porn Uganda group; team29 dropped 2 porn-named candidates; team09 dropped 41 pre-verify candidates (hard porn/sexual/profanity/meaningless titles) plus 1 post-verification hard-porn title; team02 excluded an explicit sexual-content directory entirely. Girls/friendship/dating/social groups were kept throughout — none removed on that ground.
- **Porn/URL regex hits in the output files: 0.** No source name, source URL, or personal info in any item name/description (regex-checked).

## Biggest contributors
- team09 Indonesia: 58 verified, 94 pending (groupjoin.link Indonesia tag pages; verified names taken from WhatsApp's own og:title because the directory pairs titles to codes with an offset — do not re-pair with scraped titles).
- team14 LatAm South: 21 verified, 31 pending. team02 Tanzania: 17 verified, 4 pending. team13 Mexico/Central America: 12 verified, 6 pending. team18 Turkey/Europe: 10 verified, 5 pending (all verified are RO Education).
- Zero-verified teams (pending only): team04, team05, team10, team11, team12, team17, team20, team25, team27, team28, team30.

## Verification caveat — read before merging (the wave's main blocker)
Many teams could not complete curl verification in this environment: VM shell curl egress was dead or intermittent (HTTP 000 even for example.com in several cells), and text-fetches of chat.whatsapp.com invites returned HTTP 403 (never retried). Consequences:
- Most pending items are **unverified-by-circumstance, not proven dead**. The bulk of pending items returned HTTP 200 with empty og:title (WhatsApp serves a JS page to curl) or HTTP 000/timeout.
- The parent must re-run the spaced-curl + non-empty og:title check on all 349 unique pending codes from a host where chat.whatsapp.com is reachable (or via live browser) before promoting any of them.
- Notable pending subsets: team14 has 13 UNCHECKED items (verification cut short by WhatsApp tarpitting — Chile-Sur mission group, 8 Mega Te Ayuda codes, 4 BTS fan codes); team27's 23 Kenya freshers codes were truncated to 22 chars from a separator-less page and may be wrong; team01's matching 23 freshers codes are the cross-team dupes above.
- Items that look genuinely dead/revoked (HTTP 200 + empty og:title confirmed on a working connection, e.g. team01's freshers codes after a control code returned a real title, team06's 6 SA items): still held as pending per the rule, never deleted — the parent's re-check decides.

## Merge-time fixes needed (all in pending files only; verified files are clean)
- team18 pending: strip the extra "verification" key from 5 items.
- Code-length anomalies in pending — re-check, do not guess: team01 20-char (Kenyatta Energy Eng Club), team09 8-char (GC UTAMA APRILIO), team11 11-char (Thailand News Community), team14 21-char (Comunidad Empleo y Bonos Chile), team16 24-char (Milan Picnic, likely concatenated), team22 20-char (Nigeria University News Updates).
- team19 pending UChicago link is in /invite/ form — convert only after a plain-form re-check.
- team24 pending code was printed in malformed form (domain missing) — confirm it resolves.
- team08 pending name is inferred from article context, not og:title — drop if the title stays empty.
- team13 excluded one technically-verified candidate whose og:title pointed to a different (Soledad) community than the Panama topic — it is in neither file; do not re-add as PA.
- team29 dropped one curl-verified code whose live title was religious/out-of-slice (code GOYQuZGnwlYF66AcARZmWA) — in neither file.
- team13 verified includes HN and SV items — merge needs a country-code mapping decision, not a silent drop.

## Retired-source findings
No team re-scraped a retired source; exclusions were honoured (groupizo sitemaps, groupda, retired directory domains, and all wave-20261026 sources). New findings for future waves:
- groupjoin.link Indonesia tag pages are productive (team09) — worth revisiting for other country tags.
- grouplinkshare.com Bangladesh page is new and clean (team07: 15 cards, 0 dupes).
- whtspgrouplink.com country pages hold large name-only pools (Egypt ~25, Qatar ~50, SA ~45 names) behind Join buttons — needs a live-browser pass.
- The recurring ceiling this wave is Join-button-hidden codes: Chicago/LA directories (~40 city groups each), Poland directory (~35 names), Groupswp sports collections, cricket directories, gaming directories (77links/bgmi.in/groupwa.link/whatstele), and Brazil directories (centraldegruposwhats.com.br, redgrupos.com, grupos.top — porn-heavy, filter hard). A live-browser Join-click pass is the single highest-value follow-up.
- /tmp is unsafe for intermediate work: two teams lost a full verification run when /tmp was wiped mid-run and had to redo it in workspace scratch. All final outputs are in the persistent wave dir.

## Resume point for the next run
1. Re-verify the 349 unique pending codes (list in manifest.txt; dedupe the 23 team01/team27 overlaps first) from a host with working WhatsApp access; promote passers, drop confirmed-dead.
2. Live-browser Join-click pass over the name-only leads in every teamNN-leads.md (Libya, Poland, Egypt/Gulf, Chicago/LA, sports/cricket, gaming, Brazil, Nepal/Sri Lanka truncated codes).
3. Next-wave fresh slices: Jordan, Lebanon, Oman, Bahrain, Kuwait, Qatar (zero fresh this wave), Chile (0 verified), Portugal depth (thin — most PT directories are Brazilian-focused), Ethiopia (0 fresh), Botswana/Namibia (leads only).
4. Do NOT re-assign wave-20261027 sources (listed per-team in manifest.txt) or the retired list.

## Files
- Per-team outputs: ~/workspace/whatsapp-groups-site/agent_batches/wave_20261027/teamNN-*.json + teamNN-leads.md (30 teams × 3 files)
- Manifest: ~/workspace/whatsapp-groups-site/agent_batches/wave_20261027/manifest.txt
- This summary: ~/workspace/whatsapp-groups-site/agent_batches/wave_20261027/wave_20261027_summary.md
- NOT merged, NOT generated, NOT deployed by the coordinator — groups.json, generate.py output, and ~/workspace/wgl-deploy/ were not touched. That is the parent's step.
