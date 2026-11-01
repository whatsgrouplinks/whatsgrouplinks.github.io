# Team13 — Jobs/career — wave 20261028

## Sources / pages scraped (all NEW, none from wave 20261027 manifest)
- whgroups.link Pakistan jobs page (24 codes extracted) — ALL 24 already in the
  wave 20261028 dedupe union, so 0 fresh from this page.
- grouplink.com.in Indian govt jobs page, Oct 2026 update (54 codes extracted) —
  ALL 54 already in the dedupe union, so 0 fresh from this page.
- whatzgrouplink.com jobs page (48 codes extracted) — 13 fresh after dedupe;
  the other 35 were already in the dedupe union (3 codes overlap between the
  grouplink and whatzgrouplink pages: EyTyZ2HjaOjBPVS6MJd9ax, 0m2OugTcL40HOz1cbb5u3y,
  FUtaa7rQvRiEWf1A6ECiSd — counted once).
- Spot-checked, NOT scraped: careerpathway.co.in job posts (2 codes, both dupes),
  globaljobsatlas.com job-alert group (1 code, dupe), zigsaw.in freelance-recruiter
  group (1 code, dupe).
- NOT re-scraped per brief: wave 20261027 sources (Kenya freshers forums,
  scholarship pages, Govt Job Alert Community, mavusu.com AjiraCoach, UAE job
  pages) and all retired sources (whatslinkhub.com, elsabagh.com,
  whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com,
  grupodewhatsapp.com, wagroupnest.com, groupda.com, groupizo.com sitemaps).
- groups.json, generate.py output, and ~/workspace/wgl-deploy/ were NOT modified.

## Counts
- Candidates found: 123 unique codes across the 3 pages (24 + 54 + 48, minus
  3 cross-page overlaps).
- Dedupe drops (code already in dedupe_union_codes.txt): 110.
- Fresh candidates checked: 13.
- Verified (HTTP 200 + non-empty meaningful og:title, name = og:title): 5 total.
  - Staged in team13-cat-jobs.json: 3 (2 Jobs, 1 Online Earning).
  - Verified but OUT OF SLICE, NOT staged (see below): 2.
- Pending (HTTP 200 but empty og:title — WhatsApp serves the generic invite
  shell, so the real group name is not exposed): 8, in
  team13-unverified-pending.json.
- Porn drops: 0. No hard-porn titles seen.
- Within-output duplicates: 0.

## Verified but out of slice (for coordinator / other category teams, NOT in my files)
- A2WljYlmybTFU0ASKQ16m6 — og:title "Xshall Mobiles" — a mobiles-shop group,
  not a job group; would fit Buy Sell, not Jobs.
- 4xsYlPhJCLmATRxQiEp0GM — og:title "Business Talk's" — a business-talk group,
  not clearly a job/career group; would fit Business, not Jobs.
- Directory labels on the source page are often stale (e.g. the code whose page
  label read "Need people for jobs" resolves to "Xshall Mobiles"), so og:title
  was treated as authoritative for every verified item.

## Pending notes
- All 8 pending items returned HTTP 200 with an EMPTY og:title (verified by
  inspecting the raw invite page for one code: og:title content="" and the
  generic "WhatsApp Group Invite" title). They are likely revoked/expired invites.
- Pending names are best-effort source-page labels. The source page has 4
  unlinked rows in its first table (Work from Home, Indian Job in 2024,
  Home Base Job, Assam Job) and 2 in its second (Malayalam Jobs, Jobs in Dubai),
  so a pending label could be off by one row; re-check og:title before merging.
- Two pending items share the label "Online Jobs" (different codes, different
  rows on the source page) — that is a genuine label repeat, not a duplicate code.

## Next-pass leads
- wagroup.in job / government-job tag pages: search results show large job
  listings, but the site returns an empty reply to direct curl (server blocks
  it). Needs a live-browser pass; do not re-fetch via curl.
- whgroups.link has sibling pages (online-earning, study, cricket) — the jobs
  page itself is fully harvested now, but its earning page may hold fresh
  Online Earning groups for a future earning-slice pass.
- The Pakistan-jobs and Indian-govt-jobs directory pages above are now fully
  covered (100% of their codes already in the union) — no value in re-scraping
  them next wave unless their lists change.
