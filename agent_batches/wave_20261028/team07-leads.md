# team07 — South Asia regional — wave 20261028

## Counts
- Candidates found (full 22-char codes from search snippets): 57
- Verified (fresh file): 15
- Pending (unverified file): 2
- Dedupe drops (code already in dedupe_union_codes.txt, 73,684 codes): 39
- Out-of-slice drop: 1 (verified title was a Lagos delegates group, not South Asia — in neither file)
- Porn drops: 0 (no hard-porn titles among candidates; girls/friendship groups were not dropped — none arose in this slice's candidates)
- Internal duplicates: 0

## Sources / pages used (code-bearing)
- University of Mumbai LL.M. CET 2020 notice PDF (mu.ac.in) — 4 codes, all verified (LLM CET groups).
- Mayor Chess Club listing, Colombo (localgymsandfitness.com) — Battle of Minds 2026 Sabaragamuwa, verified.
- Lexpeeps law/career pages (lexpeeps.in) — 2 codes, both verified (Updates 27 Education, Updates 11 Jobs).
- Panthi.lk Sri Lanka tuition-class listings (A/L Physics, A/L Accounting, Biology) — 3 codes, all verified.
- Aliah University Kolkata listing (unis10.com) — 1 code, verified (Alumni Group).
- MAKAUT NSS volunteers blog post (allinfomakaut.blogspot.com) — 1 code, verified.
- Quess Sri Lanka listing (findglocal.com) — 1 code, verified (Career Hub).
- Unstop / Knowafest India hackathon pages (api.unstop.com, knowafest.com) — Mission: Schrodinger's Cat (SRM-AP) and HackElite 26' (SRM IST) verified; Codeathon, Elite Hack, Hackureka, Technothon codes were union dupes.
- Sunday Times Colombo meditation article (sundaytimes.lk) — 1 code, HTTP 200 but empty og:title → pending.
- Bangalore Job Mela Google Form (docs.google.com) — 1 code, HTTP 200 but empty og:title → pending.

## Checked but yielding no usable codes (do not re-mine blindly)
- freewagroup.com Sri Lanka page, grouplink.com.in study/JEE/Kota pages, activewagroup.com Pakistani page, appgrouplink.com Pakistani/Bangalore pages: names listed but invite codes hidden behind Join buttons in fetched text — no codes extracted from them.
- Search-snippet sources whose codes were all union dupes: SSC city blog (blog.oureducation.in, 12 city codes), Pakistan newspaper PDF (10 codes), MDCAT pages, TNPSC YouTube description, ChessWorld Pakistan, NBP jobs page, Nomads in Nepal, Kathmandu Kora, IGDA Sri Lanka, A7tv Sri Lanka news, Colombo Times weather group, careerjobs.lk, StudentLanka teacher-exam page, Bangalore legal-jobs page.

## NOT re-scraped (per task)
- Wave 20261027 sources from manifest.txt, including grouplinkshare.com Bangladesh page, the Gampaha HRM institute notice PDF, and the LK news article.
- Retired sources: whatslinkhub.com, elsabagh.com, whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, groupda.com, groupizo.com sitemaps.
- groups.json, generate.py output, and ~/workspace/wgl-deploy/ were not modified. Only the three team07 files were written in the wave dir.

## Verification method
- Spaced curl (~1.5 s between checks, browser-like User-Agent) of https://chat.whatsapp.com/<code>; fresh = HTTP 200 + non-empty, meaningful og:title used verbatim as the group name. Generic "WhatsApp Group Invite" titles would have gone to pending (none occurred); empty-title HTTP 200 codes went to pending.

## Next-pass leads
- Panthi.lk tuition listings (other subjects/cities) print full invite codes in descriptions — a rich Sri Lanka education source; mine further subject pages the same way.
- Unstop India hackathon/event pages print full WhatsApp links — filter to South Asia campuses and re-check against the union before verifying.
- Sri Lanka local-business listings (findglocal.com) and club/event pages print full codes — Colombo/Kandy/Galle club pages are a good next pass.
- Re-check the 2 pending codes later: Colombo meditation (FwqX6x6cH3RHrRouVqLsAj) and Bangalore Job Mela (Lh6eONMkSeU3nvUWLiZ5td) — both returned HTTP 200 with no og:title on this pass.
- Do NOT re-submit the Lagos delegates code (FfuIvQE0qmHDORAH1Mr2pu) — verified but out of this slice.
