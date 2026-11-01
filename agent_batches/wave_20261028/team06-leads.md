# team06 — East Africa deeper pages — wave 20261028

## Sources / pages scraped
- techsslash.com Kenya WhatsApp group links page (Join-link list; 3 links sampled, all dupes — see below)
- findglocal.com Qejani Student Residences, Nairobi listing (2 codes — NOT the banned Lusaka listing)
- Scribd "Share - Zimbabwejobs-MONDAY" document (profession waiting-list codes)
- tengesai.com Zimbabwe advertising/community articles (Marondera, Masvingo, Kadoma, Beitbridge, Harare, Chitungwiza groups)
- zimbabwejobs263.blogspot.com jobs page (e-learning marketing-agents group)
- unis10.com UNZA Environmental Education student association listing, Lusaka (Zambia)
- CBU application-guidance listing via search snippet (Zambia)
- University of Kabianga Gender Club registration form (Kenya)
- Search snippets: realestatedatabase.net Uganda real estate community (dupe), thekenyatimes.com news group (dupe)

## Deliberately NOT reused (banned / wave 20261027 sources)
- Kenyan 2026/2027 university freshers directory, KCA Univ. attachment memo, Kenyatta Univ. Energy Eng. Club page, mavusu.com AjiraCoach, mtaala.co.tz teachers pages, groupjoin.link Uganda tag, thelightofengineer.com Rwanda article, findglocal.com Lusaka listing, whatstele.com Zambia page
- Retired directories: whatslinkhub.com, elsabagh.com, whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, groupda.com, groupizo.com sitemaps
- Note: search results surfaced the banned KCA memo, Kenyatta Energy Club and Kenya Times codes during discovery; all three were already in the dedupe union and were excluded, not staged.

## Counts
- Candidates found / examined: 32
- Verified (fresh file): 4
- Pending (unverified file): 9
- Dedupe drops (code already in dedupe_union_codes.txt): 19
  - techsslash Kenya sampled links: 3; Uganda real estate snippet: 1; banned-source codes found in search: 3; Scribd waiting-list codes: 11; Tengesai Marondera code: 1
- Porn drops: 0 (no hard-porn titles encountered; no girls/friendship groups dropped)
- Within-output duplicates: 0

## Verification
- Spaced curl (1.5s between checks, browser-like User-Agent) of https://chat.whatsapp.com/<code>.
- Fresh = HTTP success AND a non-empty, meaningful og:title, used verbatim as the group name.
- Pending = HTTP success but empty og:title (7 Zimbabwe community/profession codes + UNZA code), or a truncated og:title (Kabianga Gender Club, "UOK GENDER CLUB ORGAN..."), so the name is source-context only and the code needs a re-check before any merge.
- Direct VM curl to one directory site timed out once; directory pages were instead read via text fetch. WhatsApp invite pages via the text-fetch tool returned 403, so verification used the prescribed spaced curl, which returned results.

## Verified (4)
- KE, MMU/ Qwetu accommodation (Community & Social)
- KE, TUK 1st Years group (Education)
- ZW, Marketing Agents for Countrywide software, myeclass & zjobs tech (Business)
- ZM, CBU application guidance with Wana Seint (Education)

## Pending (9)
- ZW: Men Group, Women Group, Masvingo, Kadoma, Beitbridge, Harare, Chitungwiza community groups (7)
- ZM: UNZA Environmental Education Students (1)
- KE: University of Kabianga Gender Club (1, truncated og:title)

## Next-pass leads
- whatsagroupslinks.com Tanzania/Zimbabwe pages and whatgroups.com Tanzania page: both returned a Cloudflare verification interstitial on text fetch, no codes extractable this run — try a live-browser pass or a later fetch.
- techsslash.com Kenya page: only 3 of ~35 Join links were sampled (all dupes); the remaining Join links are unexamined but likely largely dupes — a full pass needs a method that resolves Join links to codes without hitting the invite-fetch 403.
- tzcareers.com Tanzania "kada" groups page and assengaonline.com Tanzania page: listed in search but not opened this run (Tanzania yielded no raw codes in snippets); good next-pass targets for Tanzania coverage, which produced 0 new codes this run.
- Rwanda and Ethiopia produced no new raw invite codes this run (job-board pages only linked WhatsApp channels, not groups) — deeper university/club-page search needed there.
- Pending codes above: re-run the spaced curl check before merge; several may simply be expired/revoked invites (empty og:title despite HTTP success).
