# Team27 leads — Education + Jobs, wave 20261027

## Counts
- Verified: 0 (see verification blocker below)
- Unverified pending: 29 (28 Education, 1 Jobs) in team27-unverified-pending.json
- Verified file team27-cat-education-jobs.json is an empty list, by design — nothing passed verification.

## Verification blocker (important)
Direct curl from this VM timed out on every host tested, including example.com and
chat.whatsapp.com, and the browser text-fetch of a chat.whatsapp.com invite returned
403. So NO candidate could meet the "spaced curl + non-empty og:title" rule in this
environment. All 29 candidates are therefore in unverified-pending, NOT verified.
A parent/eligible agent with live network access should re-run the spaced curl check
on the 29 pending invites before merging any of them.

## Sources that yielded pending candidates (full codes exposed in search snippets)
- Kenya university freshers forums directory (23 groups, KE) — Alupe, DeKUT, Egerton,
  JOOUST, JKUAT, KAFU, Karatina, Kenyatta, Kibabii, Kirinyaga, Laikipia, Maasai Mara,
  Machakos, Maseno, MMUST, Meru, Moi, Multimedia University of Kenya, Muranga,
  National Defence University Kenya, Pwani, Rongo, SEKU. NOTE: the source page runs
  university names directly after invite codes with no separator, so codes were
  truncated to the standard 22 characters; re-verify before merging.
- Scholarship community page (scholarshiptab) — 1 Education group.
- Scholarship directory (appgrouplink scholarship page) — 1 Education group
  ("Scholarship in Saudi"); its other 16 named groups have masked links in search
  output, see leads below.
- Fully funded scholarship video comment — 1 Education group.
- Cambridge Africa newsletter — 1 Education group (Ghana society).
- Study support site (Together We Thrive) — 1 Education group.
- Govt job alert video/channel — 1 Jobs group (Govt Job Alert Community, IN).

## Leads for a live-browser agent (codes NOT extracted here — masked links only)
These pages list Education/Jobs groups by name but their invite codes were masked
("Join" links) in search/browser text output, so no code could be copied without
a live-browser extraction. Do NOT re-use the retired sources listed in the task.
- appgrouplink: scholarship page (16 further named groups) and teachers page
  (TEACHERS INFO, Teacher, Study, Home Tutor Services, Physics Doubt solver,
  Education Jobs, Learn Spoken English, etc.)
- wahublink: education page and main directory (jobs + education categories).
- wtgrouplinks: education-news state-wise page (Assam, Bihar, Gujarat, Haryana,
  Jharkhand, Karnataka, Kerala, MP, Maharashtra, Punjab, Rajasthan, Telangana, UP,
  West Bengal education/job groups).
- scholarhunter: international scholarships groups page (list section rendered empty
  in text fetch — needs live browser).
- sarkarijobs.com: Sarkari Jobs groups G1-G11, teaching jobs and railway jobs groups.
- whtspgrouplink: Tamil Nadu jobs page and UPPCL jobs/exam page.
- instantgrouplink, 77links students/educational pages, groupchatlink college page,
  mcqbits exam-prep page, sarkariresult.app, placementstore.com, sarkarivacancy.com.

## Dedupe notes
- Checked against the full union: groups.json (38,051 groups) + .existing_codes.json
  (73,170 codes union). All 29 pending codes are absent from both.
- Many otherwise-promising codes were dropped as already existing, including the
  whole IELTS archive list, GRE prep, UI Ibadan groups, GCC jobs groups, ScholarsRoad,
  Global Jobs Atlas, GETFund, CSEET, SD ONUPRON hospital jobs, Career Pathway,
  ITI job alerts, TCS job notification and Govt Job Alert (non-community) codes.
- No porn/xxx groups were included. No source names, source URLs or personal info
  appear in the JSON name/description fields.
- groups.json, generate.py output and wgl-deploy were NOT modified.
