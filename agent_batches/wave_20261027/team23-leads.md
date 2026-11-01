# Team23 — South Africa + Southern Africa — wave 20261027

## Counts
- Verified (team23-fresh-safrica.json): **3**
- Unverified / pending (team23-unverified-pending.json): **11**
- Candidates examined: 25 — 11 dropped as duplicates against groups.json (38,051 groups) UNION .existing_codes.json (73,170 codes total), leaving 14 fresh.
- Porn-filter removals: 0. No hard-porn groups were included; no girls/friendship groups were removed.

## Verified (HTTP 200 + non-empty og:title, spaced curl, browser User-Agent)
- Kaapjag Wynland — ZA, Community & Social — og:title "Kaapjag Wynland"
- MICHARIDGE — ZW, Business — og:title "MICHARIDGE"
- Brand Growth Community — ZA, Business — og:title "Brand Growth Community"

## Pending — why not verified
- 9 codes returned HTTP 000 (curl/proxy timeout in this VM, not a WhatsApp dead-link proof): Kaapjag Koup, Koue, Wes-Boland, Weskus, Witzenberg; Bulawayo Pulse; Marondera Maven's Den; Zimbabwe Stock Market Investors; Cinema Society of Zimbabwe. These need a re-check from a clean connection before any merge.
- 2 codes returned HTTP 200 but an EMPTY og:title (generic WhatsApp invite page, no group name exposed): Geology and Mining Jobs South Africa; ICT Logistics Jobs South Africa. Per the task rule (non-empty og:title required) they stay pending, not verified.

## Sources used (new, not retired, not wave-20261026)
- Kaapjag branch-group PDFs (South African community branches)
- Zimbabwe marketplace / Bulawayo / Marondera listings
- Zimbabwe stock-market investors listing
- Cinema Society of Zimbabwe listing
- Harare business consultancy listing
- South African entrepreneur brand-growth listing
- South African geology/mining jobs listing and ICT logistics jobs listing

## Excluded on purpose
- The SA education PDF and the Gauteng event page from wave 20261026 team09 — not used.
- All retired sources named in the task — not used.
- One Zimbabwe directory page could not be harvested: its invite links are hidden behind join buttons and a fetch attempt was access-denied (403), so no codes were taken from it. Do not retry that page blindly; its group names (Zimbabwe breaking news, Harare buy/sell, jobs, cricket, etc.) remain a lead for a future team with a working fetch path.
- A South African political membership group requiring a fee was skipped (payment-gated, not a free community group).

## Leads for Botswana / Namibia (no codes extracted this run)
- Botswana: a Botswana groups directory page exists but its snippets carried no direct invite codes; needs a page-level fetch that exposes the links.
- Namibia: a Namibia groups page exists on the same directory family as the Zimbabwe page above, but its codes are likewise hidden behind join buttons; needs the same working fetch path.
- Gouritz (Western Cape) community ads hub page: rules page only, no invite code visible in the fetched text — needs a direct link from the site owner/page.
- No BW or NA groups are in the verified or pending files this run; do not merge empty placeholders for them.

## Files
- team23-fresh-safrica.json — verified only (3)
- team23-unverified-pending.json — pending only (11)
- No changes made to groups.json, generate.py output, or the deploy directory.
