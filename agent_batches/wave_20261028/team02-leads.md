# Team02 — groupjoin.link Asia country tags (wave 20261028) — leads

## Counts
- Verified (team02-fresh-groupjoin-asia.json): 7
- Unverified-pending (team02-unverified-pending.json): 46
- Candidates found (unique invite codes scraped): 108
- Total tag-page listings scanned: 262 (same codes repeat heavily across country tags)
- Checked by verification: 57 (spaced curl, browser User-Agent, ~1.5 s gaps, of chat.whatsapp.com/<code>)
- Dedupe drops vs wave 20261028 dedupe_union_codes.txt: 1
- Porn drops before verification: 50 (explicit porn terms in the directory title — sex/xxx/porn/pron/bokep/xnxx/fuck/nude/bikini/leaked/mms/incest/escort/call-girl, obfuscated "P😯RN", Urdu sex term; codes not recorded here, in neither output file)
- Dropped at build stage (not in either file): 4 — 2 meaningless single-word "Hot" titles, 1 school-age-sounding title, 1 bikini-emoji video-call-girl title
- Post-verification porn drops: 0 (no verified og:title was porn; all 7 verified titles were clean and meaningful)

## Verified breakdown (7)
- By country: PK 5, MY 1, LK 1
- By category: Business 2, Entertainment 2, Online Earning 1, Friendship 1, Community & Social 1
- Names are WhatsApp's own og:title, not the directory title (verified 2026-10-28, HTTP success + non-empty meaningful og:title; generic "WhatsApp Group Invite" would not have counted — none occurred).

## Pending note
- Pending names are the directory's scraped titles and are APPROXIMATE (og:title was empty, so the true name could not be confirmed). Re-verify a pending link before publishing; do not publish pending names as confirmed.
- Pending by country: PK 42, LK 2, MY 1, BD 1.

## Sources (NEW for this slice, not wave 20261027 sources)
- groupjoin.link tag pages only, all in this wave's slice (no Indonesia tags, no non-Asia tags, none of the retired sources):
  - tag/Pakistan pages 1–6 (pages 7–8 returned 0 listings; stopped after 2 zero pages)
  - tag/Malaysia pages 1–4 (pages 3–4 returned 0 listings)
  - tag/Bangladesh pages 1–4 (pages 3–4 returned 0 listings)
  - tag/Sri-Lanka pages 1–4 (pages 3–4 returned 0 listings)
  - tag/Singapore pages 1–4 (page 1: 14 listings, all already seen via earlier tags; pages 3–4 returned 0)
  - tag/Thailand pages 1–4 (page 1: 4 listings, all already seen; pages 3–4 returned 0)
  - tag/Vietnam pages 1–4 (page 1: 2 listings, all already seen; pages 3–4 returned 0)
  - tag/Philippines pages 1–4 (page 1: 13 listings, all already seen; pages 3–4 returned 0)
  - tag/Nepal pages 1–4 (page 1: 11 listings, all already seen; pages 3–4 returned 0)
  - tag/Myanmar pages 1–2: 0 listings
  - tag/Cambodia pages 1–2: 0 listings
- One bogus parse artifact (a short "invite" string, not a real code) was excluded before counting; it is in neither output file.
- No changes were made to groups.json, generate.py output, or ~/workspace/wgl-deploy/.

## Observations
- groupjoin.link country-tag pages overlap heavily: the same high-view groups recur across Pakistan/Malaysia/Singapore/Thailand/Vietnam/Philippines/Nepal tags, so unique yield per extra tag is small. Only Pakistan had depth (pages 1–6, ~99 listings).
- The Pakistan tag pool is dominated by Adult/porn listings (50 of 107 non-duplicate codes were porn-dropped) and most remaining links are dead (empty og:title), which is why verified yield is only 7 from 57 checked.
- Girls/friendship/dating/social groups were NOT dropped by the filter; none of the verified titles fall in an explicit-porn class.

## Next-pass leads (not staged)
- groupjoin.link tag/SriLanka (no hyphen) pages — not scraped this run; likely overlaps tag/Sri-Lanka, dedupe against the union before staging.
- groupjoin.link country pages for this slice (e.g. country/167 Pakistan and the equivalents for MY/SG/TH/VN/MM/KH/PH/BD/LK/NP) — a different listing surface from the tag pages, may hold codes the tag pages do not.
- groupjoin.link city/topic tags for this slice (e.g. Karachi, Lahore, Kuala Lumpur, Colombo, Dhaka, Bangkok, Manila) — same verification (og:title as name) and same dedupe rules.
- Fresh Asia blogs/forums posting 2026 group links (not the retired list) — verify any code the same way before staging.
