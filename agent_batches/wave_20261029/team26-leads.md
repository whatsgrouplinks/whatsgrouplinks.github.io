# TEAM 26 — Libya slice report (wave_20261029, 2026-10-29)

## Result: 0 fresh, 0 pending
19 invite codes extracted from 3 Libya directories; ALL 19 were already in the
existing union (.existing_codes.json + groups.json invites, 73,874 codes).
No codes needed curl verification this run. No HTTP 429 encountered.

## Directories scraped (exhausted)
1. **whtspgrouplink.com/libya-whatsapp-group-links/** — 16 codes, all dupes.
   Groups seen: "Libya jobs news", "Inter students of Libya", "Libya sport fans",
   "College Libya group", "Libya niger group", "Famous Libya Places",
   "Famous place in Libya", "Libya Media Chat", "Foreigners South Libya",
   "Libya People academy", "Libya language learning", "Libya Jobs News",
   "Work from home jobs", "Libya Job news", "Remote part time Jobs in Libya",
   "All Libya Jobs". Fully covered by a prior wave — do not re-scrape this page.
2. **thewhatspgrouplinks.com/libya-whatsapp-group-links/** ("980+ Libya WhatsApp
   Group Links 2026") — only 3 codes exposed in static HTML; remainder loads via
   JS (page has no pagination markup, no load-more button in HTML). All 3 dupes:
   "Benghazi group for Jobs News", "Libya Politics & Economy",
   "Benghazi Tourism Friends". Live-browser teams: this page may yield many more
   codes once its JS group-list renders (claim is 980+ groups).
3. **groupjoin.link/country/libya** — 5 groups listed. ⚠️ ADULT-CONTAMINATED:
   4 of 5 groups have adult/porn-style titles; 1 is symbol-only/meaningless.
   ALL excluded per content rules. Invite codes are NOT in page HTML — they sit
   behind a JS click-reveal ("blur" SafeSearch component), so no codes were
   obtainable without a live browser. RECOMMENDATION: do NOT harvest this country
   page in future waves unless a live-browser team can filter it.

## Server note
thewhatspgrouplinks.com timed out 3 consecutive curl attempts (000) over ~10 min
before finally returning 200 on a 45s-timeout retry. Its server is extremely
slow/flaky — live-browser teams may have better luck.

## Dead ends (no usable group directories found)
- `mstaml.com` Libya forum pages — phone-number/SMS-join posts, not invite-link
  directories; personal numbers everywhere. Not suitable.
- `help.unhcr.org` Libya pages (surfaced by search) — UNHCR aid hotlines
  (+218 numbers), not groups. Not suitable.
- `tgoop.com/libya_max/telegram-link` — Telegram, out of scope.
- `techlibya2026.blogspot.com` — WhatsApp tips article, no group links.
- `thewhatspgrouplinks.com` cross-links reference a "Libya" page but give no
  direct URL in search results; constructed URL pattern (…/libya-whatsapp-group-links/)
  was verified live this run.
- International/multi-country listicles (`whtsagrouplinks.com`,
  `whatspgroupslink.com/foreign-whatsapp-group-links-join`) carry no
  Libya-tagged groups — out of slice, skipped.

## Name-only leads for live-browser teams
- thewhatspgrouplinks.com/libya-whatsapp-group-links/ — up to ~980 Libya groups
  claimed; static HTML exposes only 3 (all already in DB). A browser-rendered
  pass could harvest genuinely new codes if any exist beyond the 19 seen.
- groupjoin.link/country/libya — 5 Libya groups, invites behind JS reveal;
  source is adult-contaminated, so use only with the adult-content filter ON and
  manual title review (4 of 5 titles fail the adult filter).
