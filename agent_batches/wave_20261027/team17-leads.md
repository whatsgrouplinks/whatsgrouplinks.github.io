# Team17 leads — wave 20261027 — France / Germany / Poland

## Counts
- Verified (curl HTTP success + non-empty og:title): 0
- Unverified pending (dedupe-passed, awaiting verification): 10 — 4 FR, 6 DE, 0 PL
- Dropped as already existing (in groups.json / .existing_codes.json union, 73,169 codes): 11

## Why verified = 0 (environment limit, not a link verdict)
- Exec curl from this VM timed out on every host tested, including a plain
  example.com HEAD request (20 s timeouts, HTTP 000), and a chat.whatsapp.com
  fetch timed out at 60 s. A spaced curl verification pass is still running in
  the background against the 10 pending codes; none had returned a result when
  these files were written.
- A browser-service fetch of a chat.whatsapp.com link returned HTTP 403, so no
  chat link was opened through the browser service again.
- Therefore NO candidate is claimed verified. The parent / merge step should
  re-run the curl + og:title check on team17-unverified-pending.json before
  merging anything into groups.json. Do not merge the pending file unverified.

## Pending (10) — in team17-unverified-pending.json
- FR (4): Paris Business Networking, Paris Inclusion Networking,
  Paris Entrepreneurs and Investors, Paris 20s 30s Social Party
- DE (6): Berlin Womens Monthly Circle, Berlin People Planet Pint,
  Berlin Festival of Lights Walk, Berlin Movie Goers, Berlin Under 30 Social,
  Berlin Womens Community
- PL (0): both Poland candidates found (two Wroclaw student-programme groups)
  were already in the existing code set — see dropped list.

## Dropped as duplicates (already in the existing set)
- FR: LDaalKuMDTNJ9BqaOkrItQ, KxYzoXGSN707c72UotXcvY,
  GzV0ojptK5Z7EvPYI1Zhc8, L2OEHd1krma3gbEzAoE1hn, ITesisMThOFAyNRUJ6uECN,
  GYgNbDXz0L91xi7qKTyY51, CSomQ8KNNen091H0jQ9vzz
- DE: KHZH9G81z99654aGRyG0EI, Cv2wVa23gPMKo5F0PbTAC1
- PL: JTBLrMflJAmBVRhiJEYpYs, C6KNsIqjGiY9vw4JBrLAyJ

## Excluded on purpose (not in either file)
- All retired sources listed in the task, including the Krakow directory page
  that surfaced in search (its one visible code was dropped, not used).
- One Zurich (CH) group — outside the FR/DE/PL slice.
- One truncated code from a video description — never use a partial code.
- One Paris organiser-recruitment link — organiser-only, not a general group.
- Porn filter: no hard-porn candidate was found in this slice, so nothing was
  removed on that ground; friendship/dating/social groups were kept.

## Leads for a follow-up team with a working live browser
1. A Poland directory page (found via the foreign-friends page's related-links
   section) lists about 35 Poland groups by name — Poland students, Polish
   learning, Jobs in Poland, Krakow English-speaking jobs, Warsaw IT tech,
   Wroclaw warehouse work, Gdansk part-time student jobs, Warsaw apartments,
   seasonal farm work, and more. Its Join links could not be extracted here
   (see verification note above); a live-browser pass could harvest and
   verify them.
2. A group-directory site has France (country page, 33 results) and Germany
   country/tag pages, but its group links are rendered behind a blurred /
   script-loaded listing, so no invite codes were extractable from search
   text alone.
3. Poland is the thinnest slice here: beyond the two already-existing
   Wroclaw student groups, no new Poland invite code surfaced in search
   snippets. Warsaw language-exchange / social meetups mention a group chat
   link but the code was not exposed in the indexed text.
4. France and Germany event listings (Paris, Berlin) remain the richest
   source type for this slice — every pending candidate came from one.

## Files
- team17-fresh-france-germany-poland.json — VERIFIED only (currently empty)
- team17-unverified-pending.json — 10 dedupe-passed candidates, NOT verified
- team17-leads.md — this file
- Nothing was written to groups.json, generate.py output, or the deploy dir.
