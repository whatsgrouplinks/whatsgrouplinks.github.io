# Team10 — Latin America regional — wave 20261028

## Sources / pages scraped (search-text only; no wave-20261027 sources reused)
- Argentina directory page (whatzgrouplink.com Argentina page) — 1 code taken (FANS CLUB label).
- Venezuela directory page (whtspgrouplink.com Venezuela page) — 1 code taken (jobs vacancy label).
- Peru pages found via search: retreat welcome packet (Illumination Retreat Peru), hostel events page (Wild Rover Cusco), Cusco news videos (news community code).
- Bolivia social video page (Go Communication Bolivia TikTok description) — 1 code.
- Latin America activists article (corresponsalesclave.org, 2021 vaccine-access piece) — 1 code.
- Chile ski competition programmes (FIS PDFs, La Parva / Corralco) — 2 codes.
- Venezuela/Peru/Bolivia/Paraguay faith video description — 1 code.
- NOT re-scraped: wave 20261027 manifest sources (Bogota district sports, Bogota university pages, Lima listings, Buenos Aires news/gaming, 17 Oct 2021 Brazil forum post, Spanish Mexico/Central America listings) and retired sources (whatslinkhub.com, elsabagh.com, whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, groupda.com, groupizo.com sitemaps).
- NOTE: direct invite-link fetches via the text browser returned 403 for WhatsApp, so codes were taken only from search-result text and page text; verification was done by spaced curl as specified.

## Counts
- Candidates found (full codes): 10
- Verified (fresh file): 4
  - AR — Gay group video (HxPw1lR4K1G83qjMAQY47l)
  - PE — May 2025 Illumination Retreat Peru (I5ADThgGa4l0gPdU2liutV)
  - BO — Go Communication Bolivia 1 (LECCbyRgxTIIcwOYhOwvI4)
  - CL — FIS-SAC Chile 2026 (KUlsGGqhUai9jc6DaOAhad)
- Pending (unverified file): 4 — all HTTP 200 but EMPTY og:title, so not staged as verified:
  - PE Cusco Events Group (CoHN6muECsYGOaHG0e8M5X)
  - International Latin American Vaccine Access Activists (E8hrcBoqbOn8OnT71yWC8k, 2021 article, likely expired)
  - International Venezuela Peru Bolivia Paraguay Faith Community (JtH4X8NnCYFIGeGxbjSPUB)
  - CL FIS Chile Winter Series Corralco (EIDHrVHquoACpfILyMrtx8)
- Dedupe drops (in dedupe_union_codes.txt): 2
  - VE Venezuela jobs vacancy (H8vUkxpIJ69AP29IXyOI61)
  - PE Cusco news community (IzKrBT9uVIXGBo8mhlRThG)
- Porn drops: 0
- Verification method: spaced curl (1–2 s between checks, browser-like User-Agent) of https://chat.whatsapp.com/<code>; verified only on HTTP 200 + non-empty meaningful og:title, with og:title used as the group name.

## Flags / cautions for coordinator
- HxPw1lR4K1G83qjMAQY47l: the Argentina directory labels this "FANS CLUB", but BOTH the plain and /invite/ curl checks return og:title "Gay group video". Staged under the og:title per the verification rule; the directory label appears stale or the code was recycled. Review before merge if label fidelity matters.
- The two 000 curl results on first pass (Cusco Events, Go Communication Bolivia) were transient: on retry both returned HTTP 200 (one empty title → pending, one verified).

## Skipped, not counted as candidates
- Several truncated codes visible only in shortened form in search snippets (e.g. Santiago travel group, ho'oponopono group, teleSUR community, history group, Uruguay campervan group, Fofoca Geopolitica group) — unusable without the full code; do not guess completions.

## Next-pass leads
- Ecuador, Uruguay and Paraguay country directory pages on the same directory sites (Ecuador/Uruguay pages are linked from the Venezuela page) — codes are behind Join buttons, so a live-browser pass is needed to extract them.
- Medellin community directories (mymedellin.org, mdecommunity.com, medellin.co guide) list many named Colombia groups but hide codes behind Join buttons — live-browser lead.
- Chile/Argentina/Peru university, club and event PDFs and video descriptions continue to expose full codes in text — repeat the search-text method with other cities (Valparaiso, Cordoba, Rosario, Arequipa, Quito, Montevideo, Asuncion, Santa Cruz).
