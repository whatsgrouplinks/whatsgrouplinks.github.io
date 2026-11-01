# team24 — Sports (wave 20261027)

## Counts
- Verified: 3 — in `team24-cat-sports.json` (VERIFIED only)
- Unverified-pending: 1 — in `team24-unverified-pending.json`
- Name-only leads below: NOT in any JSON, NOT mergeable until a live-browser pass clicks each Join link, captures the real chat.whatsapp.com code, verifies it (HTTP success + non-empty og:title via spaced curl), and dedupes it against groups.json / .existing_codes.json.
- Porn-blocked items in outputs: 0. Gambling-tip groups seen were SKIPPED entirely (no codes recorded for them).

## Verified (HTTP 200 + non-empty og:title, spaced curl, browser User-Agent)
- Trialists — GB — football trialists group, 2026/27 season trial updates.
- Comet Cricket Club — US — Dallas cricket club group.
- BUCS Futsal COP — GB — university futsal network group.

## Pending (code-bearing, NOT verified)
- Football Fanatics — NG — first spaced curl check: HTTP 200 but EMPTY og:title, so pending per task rule (not verified, not claimed dead). Second spaced check hit curl egress failure (HTTP 000), not a pass. Note: its source page prints the link in malformed form (domain missing); the code in the JSON is the code string as printed on that page — parent live check must confirm it resolves to a real group before any merge.

## Dedupe
- Checked against the full union: groups.json (38,051 groups) UNION .existing_codes.json — 73,200 codes total.
- Dropped as already known (codes NOT in outputs): the two other full codes surfaced in the same searches that were already in the union, and all 15 full codes surfaced on the older cricket listicle page checked (all already in the union).
- No internal duplicates in either JSON. No descriptions contain URLs. No personal info in any name/description.

## Name-only leads — live-browser Join-click pass needed (no codes captured, none invented)
### Groupswp sports collections (codes behind "Join Group" buttons in page text)
- Cricket: Only Cricket; Cricket leagues (IPL, BBL, CPL, PSL, BPL fans); Cricket Lovers; Crick Info; We Love CSK; HBL PSL Live Update; Cricket Update; KKR Fan group; AB De Villiers / Virat Kohli; Die Hard fans of cricket; World Cup; Thala Fans; Living for Yuvi; Cricket Fan Club; Virat Kohli Fans group; World cricket updates; Cricket News and Updates with CrickAffinity; Cricket discussion; Cricket Lovers group; Cricket Star Only (videos); MS Dhoni Fans club; Cricket Fans; Cricket Lovers; Cricket club. (31 listings, page shows 1-24.)
- Sports collections index: WWE; PSL; Cricket; Cristiano Ronaldo; Football; Neymar; Lionel Messi; Virat Kohli; Kerala Blasters; RCB; MS Dhoni; IPL; Pro Kabaddi; Rohit Sharma; CSK; Fantasy Sports; SRH; KKR.
### New cricket directory page (codes behind Join buttons / profile links)
- Cricket Lovers; World Cricket Update; Live Match; Cricket World; SGF Cricket Team; Baber X Saim; Cricket Updates; Cricket K Fans; Womens Cricket World Cup; Cricket In Soul; Pakistan Cricket Updates; Khan Cricket Updates; Waqas Cricket Team; Captain 17 Cricket Update; Sports Brand; Pak Cricket 11; Cricket Ke Baithak; Only Cricket Update; Cricket and PSL Information; Cricket Sports Army. Page updated 2026-10-26.
### Other
- Football directory page on a second new domain: bot-challenge page ("One moment, please...") — UNCHECKABLE, not proven dead. Do not retry through another route; live-browser pass only.
- Truncated codes in search snippets (video descriptions etc.) were NOT used and NOT guessed — a truncated code is not a code.

## Sources deliberately NOT reused (per task ban / prior-wave coverage)
- joingroupslink.com and asiamediajournal.com gaming listicle (wave 20261026 team17) — not touched.
- Retired/banned: whatslinkhub, whatsappgrouplink.org, wappgrouplinks, whatsappgroupjoinlinks, grupodewhatsapp, wagroupnest, groupizo sitemaps 1-11, groupda, whatzgrouplink, whatsgroulink, whatsapp-group-link, whtsagrouplinks, groupwhat, groupinvitelink, groupsor.in, wagroupslink, whgroups.link, whatsonly, activewagroup, grouplink.com.in, techapkzone, freewagroup, groupsnest, ongrupos, grupbul, joingram.in, groupwa.com, grouplinks.in, dailygrouplinks — not scraped.
- Wave 20261026 sources, also not re-scraped: meetup.com (teams 06/13/15), wagroupshub.com (team15), appgrouplink.com, minidea.co.in, whtspgrouplink.com, wglfinder.com (all mentioned in wave 20261026 leads as prior-wave / excluded sources).
- Syndication warning: wahublink.com and wagroupshub.com share an identical sports name set (wave 20261025 team27) — its names overlap the Groupswp/new-directory names above; dedupe by CODE, not by name, on the live-browser pass.
- Gambling-tip / betting-tip groups: skipped entirely, no codes recorded.

## Curl egress note
- Egress was DOWN at the start of this run (HTTP 000, timeout, even for the invite host) and RECOVERED mid-run, which is when the 3 verified checks passed. It flaked again on the pending item's second check (HTTP 000). Parent re-check of the 1 pending item is worthwhile when egress is stable.
- No groups.json, generate.py output, or deploy directory was modified.
