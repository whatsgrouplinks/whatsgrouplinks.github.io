# Team04 — wave 20261028 — fresh new directories, names A–M

## Files written (only these three, in this wave dir)
- `team04-fresh-newdirs-am.json` — 43 verified
- `team04-unverified-pending.json` — 59 pending
- `team04-leads.md` — this file

No changes made to `groups.json`, `generate.py` output, or `~/workspace/wgl-deploy/`.

## Sources / pages scraped
- `instantgrouplink.com/` (homepage, via curl) — table rows with group name + direct invite link.
- `joinnchat.com/` (homepage, via curl) — same table structure; this is the only source that yielded fresh codes.
- `groupssor.com/` (homepage, via curl) — 0 direct `chat.whatsapp.com` codes on the homepage (listing is JS-loaded); no candidates taken.
- `groupsnest.com/` (homepage, text fetch only) — inspected, NOT scraped for codes: its Join links hide codes behind redirects, and one Join-link fetch was access-denied, so the source was dropped entirely for this wave rather than retried. No groupsnest code from that fetch was used in any output.
- `groupslink.pk/` (homepage, inspected) — REJECTED as a source: group entries carry no names (Join buttons only) and its sections are porn-heavy (XXX / Sexy headings). No codes taken from it.

Excluded by slice / prior waves (not touched): `groupjoin.link`, `grouplinkshare.com`, `whatgroups.com`, `wahublink.com`, `whatsshare.com`, `groupchatlink.com`, `77links.com`, `whatsgrouply.com`, `mdecommunity.com`, all wave 20261027 sources (per `wave_20261027/manifest.txt`), and retired sources (`whatslinkhub.com`, `elsabagh.com`, `whatsappgrouplink.org`, `wappgrouplinks.com`, `whatsappgroupjoinlinks.com`, `grupodewhatsapp.com`, `wagroupnest.com`, `groupda.com`, `groupizo.com` sitemaps). Note: `groupwa.link` was also left alone — it appears in the 20261027 manifest (team29).

## Candidates found
- instantgrouplink.com: 448 table rows, 289 unique codes — 0 fresh.
- joinnchat.com: 437 table rows, 380 unique codes — 102 fresh.
- Total unique candidates considered: 669 (289 + 380).

## Dedupe (against `wave_20261028/dedupe_union_codes.txt`, 73,684 codes)
- instantgrouplink: all 289 unique codes already in the union — 289 dedupe drops.
- joinnchat: 278 unique codes already in the union (326 row-level hits including repeated rows); 102 fresh codes passed to verification.
- Internal dedupe within outputs: 0 duplicates in either final file (checked).

## Verification (spaced curl, ~1.2 s between checks, browser-like User-Agent, `https://chat.whatsapp.com/<code>`)
- Verified (43): HTTP page returned a non-empty, meaningful `og:title`, used verbatim as the group name. Categories were mapped from the source section, then corrected where the verified title clearly indicated another category (e.g. Binance/Crypto Hub → Finance, Tilawat-e-Quran status → Islamic, Pakistan jobs info → Jobs).
- Pending (59): no `og:title` returned on the spaced curl check (empty title). None of the 102 were pending for a generic "WhatsApp Group Invite" title. Pending names are the source-page names (not verified titles) — re-check before any merge.
- Porn drops: 0 among the 102 checked (explicit porn-term regex + porn-emoji check on the verified title; girls/friendship/dating groups were NOT dropped).
- Meaningless / symbol-only title drops: 0.

## Counts summary
- Candidates found: 669 unique (from 2 productive homepages)
- Dedupe drops: 567 unique (289 instant + 278 joinnchat)
- Fresh candidates verified-checked: 102
- Verified: 43
- Pending: 59
- Porn drops: 0

## Next-pass leads
- groupssor.com category/listing pages (JS-loaded — needs a rendered-page route, not homepage curl).
- joinnchat.com sub-pages beyond the homepage (same table format; homepage already harvested).
- Other A–M directories not yet scraped: groupwhat.com, groupinvitelink.com, groupsor.in, groupslink.pk sub-pages (only with strict porn filtering, given the homepage's XXX/Sexy sections).
- "allwhatsappgroups" / "bestwhatsappgroups": web search surfaced only Google Sites mirrors, no standalone directory with extractable codes — low priority.
- Re-check the 59 pending joinnchat codes later; many returned no title at all, which may be transient WhatsApp fetch behaviour rather than dead links.
