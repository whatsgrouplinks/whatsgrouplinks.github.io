# TEAM 31 — Education category discovery — leads & notes (2026-10-29)

## Result
- Fresh (verified): 0
- Pending (unverified): 6 — see team31-unverified-pending.json
- Fresh file: empty array (no candidate passed the og:title gate)

## Why pending instead of verified
All 6 candidate invites return HTTP 200 with the `invite_link_type_v2` marker, BUT
WhatsApp invite pages are now JS-rendered shells: `og:title` is EMPTY, `"NAME":""`
in embedded data, `og:description` is the generic "WhatsApp Group Invite", and
`og:image` is the default WhatsApp logo. Per the verification rule (HTTP 2xx AND
non-empty meaningful og:title AND invite_link_type_v2) none could be marked
VERIFIED, so all 6 are staged as pending (`_verified:false`).
og:image used is the generic WhatsApp invite logo from the invite HTML.

## Name-only leads (no codes extractable)
groupsinvite.link education page hides invites behind a JS rules flow
(`/group/link/<id>/` -> `/group/rules/<id>/`, no chat.whatsapp.com in HTML).
Names + country context for a future browser round:
1. AMANI SUCCESS PATH -ENGLISH LEARNING CLASS (tanzania)
2. BBC Learning English (united-kingdom)
3. ENGLISH PRACTICE (india)
4. Scholarship opportunities (india)
5. ENGLISH WORLD ACADEMY (india)
6. IELTS & TOEFL type friendship (united-kingdom)
7. PAID Spoken English classes Kerala (india)
8. Ielts one touch (united-states)
9. English Zone (india)
10. Awake Classes English (india)
11. English Language Course (india)

## Fresh directories scraped this wave (not on retired list)
- groupsnest.com (homepage education table + /category/education-groups)
- wahublink.com education page (Academic / Foreign Education / Scholarship sections)
- whtspgrouplink.com (Students Educational + English Learning sections)
- englishums.com/250-active-english-learning-whatsapp-groups/
- whtsagrouplinks.com/english-learning-whatsapp-group-links/
- whtsgrouplink.com/english-learning-whatsapp-groups-links/
- wemakescholars.com MS-in-US WhatsApp groups blog page

## Exhausted / dupe-heavy
~136 of 138 extracted codes already in the existing union (73,873 codes) — the
generic English-learning/education space is heavily harvested. wahublink,
whtspgrouplink, englishums, whtsagrouplinks and whtsgrouplink education sections
yielded ZERO fresh codes this wave.

## Avoided (retired / out of scope)
- grouplink.com.in all-india-study page (retired: grouplink.com.in study)
- groupjoin.link IELTS tag page (retired: groupjoin.link harvested pages)
- groupsnest.com BA section on wahublink = miscategorized online-earning spam (skipped)
- whatsapp.com/channel/ links skipped (channels, not chat invites)
- "Tik Tok videos Funny" + "Official Aviator predictor" entries dropped as off-slice spam
- School-age-sounding titles (SSC 9th/10th, CBSE classes) dropped per content rules

## Notes
- No /sex/ /xxx/ /adult/ pages visited; no banned content encountered.
- No HTTP 429 hit during verification; 6-10s spacing honored.
- Content filters: banned-word regex, suggestive-emoji, symbol-only/meaningless titles applied — 0 hits this wave (dupes dominated).
