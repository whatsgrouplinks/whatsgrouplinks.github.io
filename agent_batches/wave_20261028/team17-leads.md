# Team17 — wave 20261028 — Entertainment + Funny + News + Health

## Sources / pages scraped (all NEW, not wave 20261027)
- newgrouplinks.pk — news page, Pakistani page, USA page, Dubai page, Karachi page, Peshawar page (direct chat codes in HTML; names mapped from the table row preceding each Join button)
- trickswire.com/whatsapp-group/ — Entertainment section only (Song/Shayari/Jokes/Movies list; codes mapped in document order to the 19 listed names)
- Attempted but yielded NO extractable codes (live-browser leads, see below): whtsagrouplinks.com movies + news pages (Cloudflare check / direct curl timeout), whtsgrouplink.com movies page (Cloudflare check), whatsagroupslinks.com gym page (timeout), freewagroup.com news page (Join links hide the invite), grupbul.com funny + health group pages (Join button hides the invite), whatsapplink.cazajobz.com UAE funny page (no direct codes in HTML), whatzgrouplink.com tag page (no direct codes)
- Deliberately NOT reused: hubrecipes.com movies/news/active pages, walinking.link, wahublink.com, groupwa.link, whtspgrouplink.com, 77links.com, and all wave 20261027 manifest sources + retired sources listed in the task.

## Counts
- In-slice candidates found: 50 (news 19 + Pakistani page 6 + Karachi 3 + Peshawar 3 + trickswire entertainment 19)
- Dedupe drops vs wave 20261028 dedupe_union_codes.txt: 17 (incl. most of the newgrouplinks news first section and several Pakistani/Karachi codes already in the union)
- Candidates verified (spaced curl, ~1.5s apart, browser UA): 33
- Verified (HTTP 200 + non-empty, meaningful, in-slice og:title used as name): 3 — all News (92 Askari News, Trending News, ENB NEWS HUB)
- Pending (empty og:title, or og:title = another invite URL, or decorative title): 17 — listed in team17-unverified-pending.json, using source-page names
- Out-of-slice verified titles dropped from BOTH files: 9 (Karachiites community; Free Online Work earning; Allah is my Lord Islamic; French debate group; GROUPE FERME; SOYONS FOCUS; Arabic religious group Islamic; Indian students education; 1XBET betting)
- Meaningless / symbol-only / personal-info titles dropped from BOTH files: 4 (emoji-only song group; emoji-only status group; profanity title; an email address used as a title — personal info, not reproduced here)
- Porn drops: 0 hard-porn titles found among the 33 checked.
- Health/fitness: 0 in-slice health/fitness candidates found — the USA page's "Smart Health and Fitness" row had no direct chat code, and the gym/health directory pages above hid their codes. No health items staged rather than inventing any.

## Verification notes
- Many directory links are stale/recycled: the og:title often differs completely from the directory label (e.g. a "movies" link now shows a religious or student group). Verified names therefore use the og:title, and any verified title outside Entertainment/Funny/News/Health was dropped, not re-labelled.
- Pending items with an og:title that was just another invite URL (4 trickswire codes) are kept under their source-page names for a re-check, not staged as verified.
- No files outside agent_batches/wave_20261028 were modified. groups.json, generate.py output and ~/workspace/wgl-deploy/ untouched.

## Next-pass leads
- Live-browser pass needed for: whtsagrouplinks.com movies/news, whtsgrouplink.com movies, freewagroup.com news + entertainment, grupbul.com group pages (funny 964840, health 663344, music 890205, funny videos 907145, entertainment 549622), cazajobz UAE funny page, whatsagroupslinks.com gym page — all hide invites behind Cloudflare/JS Join buttons.
- newgrouplinks.pk: re-check the 17 pending codes later (several returned HTTP 200 with empty og:title, which may be transient); also check its other city pages for in-slice rows whose codes were missing (e.g. USA Smart Health and Fitness).
- Health/fitness remains the thinnest slice: prioritise a live-browser pass over gym/fitness directories next wave.
