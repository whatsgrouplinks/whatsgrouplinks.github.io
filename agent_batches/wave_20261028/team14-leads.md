# team14 — Education — wave 20261028

## Sources / pages scraped (NEW, not wave 20261027)
- All India Study page, grouplink.com.in (October 2026 study/exam/English/technical groups) — 30 codes extracted
- Class 12th WhatsApp Group Links 2026, whatzgrouplink.com — 15 codes extracted
- Best WhatsApp Group for NEET 2026 Preparation, sarvgyan.com — 4 codes extracted
- Public search snippets for university freshers / student groups (Cambridge ISA freshers page, Queen's University Belfast offer-holder page, IE University class of 2026/27 page, IEEE student-branch event page, plus older IELTS/GRE/scholarship snippets) — 14 codes collected
- NOT reused: wave 20261027 sources (Kenya freshers forums, mtaala.co.tz teachers pages, wave-20261027 scholarship pages, institute notice PDFs) and retired sources (whatslinkhub.com, elsabagh.com, whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, groupda.com, groupizo.com sitemaps).

## Counts
- Candidates found: 63
- Verified (fresh file): 16
- Pending (unverified file): 3
- Dedupe drops (code already in wave 20261028 dedupe_union_codes.txt): 44
- Porn drops: 0
- Out-of-slice items not staged: 2 (a Southampton darts club listing — Sports, not Education; a University of Ibadan students' fellowship listing — religious fellowship, not a study group)
- Note: the two All India Study codes first hit by the text fetcher were also in the dedupe union, so they are counted as dedupe drops, not pending.

## Verification method
- Spaced curl (about 1.5s between checks, browser-like User-Agent) of https://chat.whatsapp.com/<code>.
- Verified only on HTTP 200 plus a non-empty, meaningful og:title, used verbatim as the group name.
- Pending = HTTP 200 but empty og:title (3 items: Class 12th Agriculture 2026; QUB North America Offer Holders 2026; IE University Madrid Class 2026). Those three were NOT put in the fresh file.

## Dedupe detail
- All 30 All India Study codes were already in the union (0 new from that page).
- All 4 SarvGyan NEET codes were already in the union.
- 1 of 15 Class 12th codes was a dupe (BIHAR BOARD update); the other 14 yielded 13 verified + 1 pending.
- 9 of 14 search-snippet codes were dupes (HAN scholarships, VU ENG506, GRE Prep, all 5 old IELTS codes, ScholarshipTab community); the remaining 5 yielded 3 verified + 2 pending.

## Next-pass leads
- grouplink.com.in sibling pages (IIT groups, NEET groups, Kota coaching, bank exam groups) — the text fetcher returned a bot-check page for the IIT page, so codes need a curl fetch, then the same spaced verification + union dedupe.
- groupsinvite.link English-learning page (6 named groups listed, codes not exposed in text view) — needs a curl fetch of the page HTML.
- whtsgrouplink.com / whtsagrouplinks.com English-learning pages — text fetcher returned bot-check pages; curl fetch may expose codes.
- wemakescholars.com MS-in-US 2026 page — university-wise group list, not yet extracted; check for codes not already in the union before staging.
- Delhi University / DU SOL group pages (bestdelhi.in) — only 2 group links shown in snippet, not yet extracted.
