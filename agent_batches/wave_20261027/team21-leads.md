# Team21 leads — Canada + Australia + New Zealand — wave 20261027

## Counts
- Candidates collected: 33
- Already in existing set (dropped): 20 — checked against the full union of
  groups.json (38,051 groups) + .existing_codes.json (73,170 codes total).
  This includes 5 codes from a Canada directory page that were already in the
  existing set; they were not re-fetched and are not listed here.
- Fresh candidates curl-checked: 13
- VERIFIED (HTTP 200 + non-empty og:title): 7
  - CA: 2 (both Vancouver baseball coaching/training)
  - AU: 1 (Sydney international-student social)
  - NZ: 4 (Auckland hikers, Auckland homeschool, Y88 sailing, Wellington parents)
- UNVERIFIED-PENDING: 6 — all returned HTTP 200 but an empty og:title, so per
  the verification rule they stay pending, not verified:
  - CA: Toronto documentary film club, Toronto first-time mums
  - AU: Australia Gita learning community
  - NZ: NZ immigration updates, Auckland club sailing, NZ coaches community
- Porn filter: no hard-porn groups found in this slice; nothing removed on
  that ground. Friendship/social groups were kept.

## Sources checked (new directories/pages, none from the retired list)
- Canada directory pages: whatgroups.com Canada page, whatsgroupslinkspk.com
  Canada page, whtsgrouplink.com international page,
  thinkingoutsidethesandbox.ca business groups page, group-hubs.com Canada page
- City/community pages with inline invite links: Meetup city pages (Toronto,
  Vancouver, Sydney, Melbourne, Brisbane, Perth, Auckland), Humanitix event
  pages, KeepActive, club/school/chapter pages (sailing, coaching, homeschool)
- Excluded on sight: grupbul (retired list) and any other retired source.

## Method notes / caveats
- Direct curl to the directory sites timed out from this environment, so
  candidates were taken from invite links exposed inline in search/page text
  rather than from directory-page link tables.
- A text-fetcher attempt on 5 Canada directory invite links returned 403
  from WhatsApp; those requests were not repeated by any route. All 5 codes
  were already in the existing code set, so they were dropped as duplicates
  and do not appear in either output file.
- Verification: spaced curl (1.5 s between requests, browser User-Agent) of
  each fresh invite; verified only on HTTP success + non-empty og:title.
  Image fields left empty (no pps.whatsapp.net image URL captured for these).
- groups.json, generate.py output and wgl-deploy were NOT touched.
