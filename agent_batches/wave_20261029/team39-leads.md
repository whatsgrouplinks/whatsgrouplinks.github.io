# TEAM 39 — Entertainment category discovery (wave_20261029)

## Result summary
- Fresh (verified): 0
- Pending (unverified): 5
- Sources harvested: 8 directory pages; ~350 codes extracted; union dedupe left only 5 fresh (union already held the rest — see verification caveat below).

## Fresh pending codes (names only)
- DRAMA + MOVIES (whtspgroup.com, PK)
- Har Pal Geo Pakistan (whtspgroup.com, PK)
- Apna Time Ay Ga Moves Aur Drama Group (whtspgroup.com, PK)
- Girls Or Boys drama movies group (whtspgroup.com, PK)
- Anime (77links.com, International)

## Exhausted pages (all extracted codes already in the union — do not re-harvest)
- whtsgrouplink.com/movies-whatsapp-group-links/ — 55 codes, all duplicates
- whtsagrouplinks.com/movies-whatsapp-group-link/ — 8 codes, all duplicates
- wahublink.com/entertainment-whatsapp-group-links/ — 16 codes, all duplicates (rendered page lists ~30 titles; the rest are AI filler with no invite hrefs, e.g. H*t Girl, Time P**s Girls)
- whtspgrouplink.com/south-indian-whatsapp-group-links/ — 23 codes, all duplicates (one bad code "invite" on South Indian Business Group — dead link)
- wagroupshub.com/drama-whatsapp-group-links/ — 38 codes, all duplicates (fresh domain, same list as wagroupnest clone)
- whtspgroup.com/pakistani-drama-whatsapp-group/ — 45 codes, 4 fresh (the pending ones above)
- 77links.com/anime-whatsapp-group-links/ — 90 codes, 1 fresh (fresh domain; one name "STRAW HAT PIRATES 🥵" dropped for suggestive emoji)
- groupwa.link/ homepage — 229 codes; all entertainment-ish codes already in union; its Islamic/Jobs/Online-Earning sections are out-of-slice but every code is already in the union too (checked — 0 fresh leads for other teams)
- zoneofwagroup.com/drama-whatsapp-group-links/ — curl rc=52 (empty reply); page renders in search-cache text and content matches wagroupshub exactly (same owner clone); likely no fresh codes

## Out-of-slice fresh directories (for other teams; entertainment slice did not harvest)
- 77links.com — anime/movies directories (90 anime codes checked)
- wagroupshub.com — drama/entertainment hub (fresh domain, wagroupnest-clone)
- groupwa.link — big directory (229 codes on homepage alone; has Movies, Girls, Anime, Islamic, Jobs, Earning sections)
- wagrouplinks.online — Memes page exists (search-verified list) but curl is server-blocked (rc=52 empty reply); needs browser-task extraction
- whatsapplink.cazajobz.com — UAE funny/groups section, not harvested this run

## Dropped items
- "JAV MOVIE HD" (whtsgrouplink.com) — adult-industry term (JAV), dropped
- "STRAW HAT PIRATES ❤️‍🔥🛐🥵" (77links) — suggestive emoji, dropped
- "🥵Doctor Girls 🥵🩺" and "Girls 🥵❤️💦" (groupwa.link) — suggestive emoji, dropped

## Verification caveat (IMPORTANT for the merge team)
WhatsApp's invite pages serve the SAME ~224KB JavaScript SPA shell with HTTP 200 for a completely bogus code as for real codes (calibrated with a fake code): og:title is always empty, og:description is "WhatsApp Group Invite", invite_link_type=REGULAR. Group names only render client-side. So **curl alone cannot verify invite validity** — all 5 candidates are pending. Do not count HTTP-200-only checks as verification.
