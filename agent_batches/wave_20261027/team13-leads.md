# team13 leads — wave 20261027 (Mexico + Central America, Spanish)

## Counts
- Verified: 12 in `team13-fresh-mexico.json`
  - MX 3, CR 3, GT 3, PA 1, HN 1, SV 1
- Unverified-pending: 6 in `team13-unverified-pending.json`
  - All returned HTTP 200 on a spaced curl fetch but with an empty og:title,
    so per the task rule they are NOT verified. They need a re-check before merging.
  - CR 5, GT 1
- Leads / rejected: see below

## Method
- Searched Spanish queries for Mexico, Guatemala, Costa Rica, Panama, Honduras
  and El Salvador groups, plus directory and university/organisation listings.
- Dedupe: every candidate code was checked against the FULL existing set =
  all invite codes in `groups.json` (38,051 groups) UNION `.existing_codes.json`
  (combined set 73,170 codes). 7 candidates were dropped as already known.
- Verification: spaced curl (1-2 s between fetches, browser User-Agent) of each
  `chat.whatsapp.com` invite. Verified ONLY on HTTP success AND a non-empty
  og:title. First verification run failed on a script file-output bug (no files
  were written, no invites were verified); the run was redone with stdout
  capture and completed cleanly.
- Porn filter: only hard porn/xxx groups are blocked. No candidate was dropped
  for being a girls/friendship/dating/social group; none of the final items is
  hard porn.
- No groups.json, generate.py output, or deploy directory was modified.

## Sources used (new for this wave, not the banned list)
- Public web search results for Mexico / Central America groups, including
  university, union, chess-federation, community-volunteer, hostel, alumni
  and local-business listings. None of these are whatshub.es, gruposwats.com,
  whtsgroupslinks.com, or any wave-20261026 source, and none are on the
  retired list in the task (whatslinkhub, whatsappgrouplink.org, wappgrouplinks,
  whatsappgroupjoinlinks, grupodewhatsapp, wagroupnest, groupizo sitemaps 1-11,
  groupda, whatzgrouplink, whatsgroulink, whatsapp-group-link,
  whtsagrouplinks, groupwhat, groupinvitelink, groupsor.in, wagroupslink,
  whgroups.link, whatsonly, activewagroup, grouplink.com.in, techapkzone,
  freewagroup, groupsnest, ongrupos, grupbul, joingroupslink, joingram.in,
  groupwa.com, grouplinks.in, dailygrouplinks).

## Dedupe drops (already in the existing set, names only, codes withheld)
- Sol y Luna Vaquera sales group (MX, Buy Sell)
- Divine Mercy School Mexico (MX)
- Amistades FIFAS womens football fans (MX, Sports)
- Quintana Roo Hoy news updates (MX, News)
- Divine Mercy School Guatemala (GT)
- Divine Mercy School Panama (PA)
- Divine Mercy School Honduras and Nicaragua (HN)

## Content / quality drops (codes withheld, do NOT merge as labelled)
- One fan-community candidate passed the HTTP + og:title check, but its
  og:title pointed to a different follower community (Soledad leaders) than
  the Panama topic found in search. It is in NEITHER output file, to avoid a
  mislabelled country/topic. It needs a fresh topic check before any use.
- One Guatemala spa listing and one truncated (incomplete) Guatemala code
  from search snippets were skipped without recording codes: the spa listing
  was adult-adjacent and the truncated code cannot be verified as shown.
- Several blog listicles naming Mexico groups without any invite codes were
  checked and abandoned — names without codes are not candidates.

## Notes for the merge step
- Country codes: the task schema example listed MX/GT/CR/PA, but the slice is
  Mexico + Central America, so the two verified Central America items outside
  that example are filed with their accurate codes: HN (ASUEPC, Honduras)
  and SV (Colegio Juridico lawyers group, El Salvador). If the merge only
  accepts MX/GT/CR/PA, those two need a mapping decision, not a silent drop.
- Pending items are HTTP 200 / empty-og:title only — they are not confirmed
  dead, and not confirmed live. Re-check with a live-browser pass if possible.
- The 6 pending items are the only unverified items retained; all other
  non-verified candidates were either dedupe drops or the quality drops above.
