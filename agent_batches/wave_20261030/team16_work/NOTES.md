# Team 16 work notes (2026-10-30)
Slice: university / student-union society pages in FRANCE and SWEDEN.

## Harvested (all FRESH vs dedupe_union_codes.txt, 38,835 codes)
- 7 codes from pamplemousse-magazine.co law-students page (code->section mapped by page order): BrhRiLrfdX7D83EyM4IsGf (community), Cgr1ZHRQZMw4gaDumCDOXw (L1), GBIA3PQuH5mAd5zFGW24xk (L2), Chcj9I5BURS6EXakErBzRf (L3), JTBX7NcXB0gLG2j7mb1omI (Master), DkSmjHaa4DG3NSPH66i9H7 (CRFPA/ENM), JCEiEMzd4tl786lnUfFLfc (jobs/stages) — all 22-char.
- EeqM2X2YsMa3m2FIZ584fm — EDHEC Alumni Monaco (French school alumni), 22-char.
- HiA1QEP6ffTBBX48UO2tGS — ESN Toulouse climbing event (helloasso.com), 22-char.
- F7DfkHChOWE7l6DAf2vuCni — Lyon-Sud Univ Lyon 1 Erasmus guide PDF ("Groupe WhatsApp des 4e années", Externes en Médecine). PUBLISHED AS 23 CHARS in the PDF link URI (verified in raw PDF bytes) — likely a source typo; marked uncertain.

## Excluded
- Gz6pdMRLd022l2f6jZ69mY (Toulouse Erasmus party, meetup.com) — already in dedupe.
- ESN Lugano codes (I9tav0vMvgv8vsrb7x5UME, JYP8DXizQKR5EFF75Fkumg) — Switzerland, out of slice.
- coesenegal.com education codes — Senegal, out of slice.
- liep.fr Parcoursup group — lycée parents group, out of slice. livementor.com — commercial funnel, skipped.

## VERIFICATION BLOCKED — parent must handle
chat.whatsapp.com could NOT be reached from this sandbox:
- curl: CONNECT tunnel via hatch-egress-proxy timed out after 20s (code 000).
- python requests: read timed out (25s).
- browser.open on a chat.whatsapp.com URL: upstream 403 "access denied", with an instruction not to retry via any tool.
=> No item could be verified => fresh file is empty []; all 10 candidates are in team16-unverified-pending.json with notes.
