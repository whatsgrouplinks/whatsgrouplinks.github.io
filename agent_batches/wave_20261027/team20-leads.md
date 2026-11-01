# Team20 — UK regional — wave 20261027

## Counts
- Verified (team20-fresh-uk.json): 0
- Unverified-pending (team20-unverified-pending.json): 11
- Leads / candidates examined: 32 (11 new after dedupe; 21 dropped as duplicates)
- Dropped as duplicates: 21 — their codes were already in groups.json (38,051 groups) UNION .existing_codes.json (union 73,170 codes).

## Verification note (important)
- Verification was attempted with spaced curl (1.5s sleep, browser User-Agent, 20s timeout per invite).
- Every invite returned empty output / connection timeout from this VM — no HTTP success and no og:title could be obtained for any candidate.
- Per the task rule, NONE are claimed verified. All 11 are in unverified-pending only; the fresh file is intentionally empty.
- A separate text fetch of one invite was denied upstream (403). That invite's outcome is treated as unknown, not as dead, and it was NOT re-attempted.
- Recommendation for parent: re-run the curl verification for the 11 pending codes from a host where chat.whatsapp.com is reachable before merging; do not merge pending as verified.

## Pending groups (11, all country GB)
1. Ladies Badminton Birmingham — Sports — Birmingham
2. Break Thru Birmingham Music — Entertainment — Birmingham
3. Trekkers UK Hiking Community — Sports — Birmingham/UK-wide
4. Edinburgh University Cycling Club — Sports — Edinburgh
5. Edinburgh Wakeboard and Water Ski — Sports — Edinburgh
6. Glasgow Coworking Digital Nomads — Business — Glasgow
7. Edinburgh Strike Support Community — Community & Social — Edinburgh
8. Wales Outdoors Social Hikes — Sports — Wales
9. Bristol Women in STEM — Education — Bristol
10. Bristol Sailing Freshers — Sports — Bristol
11. UCL Taekwondo Club London — Sports — London

## Sources used (new, not retired, not wave-20261026)
- UK city/region search results for Birmingham, Edinburgh, Glasgow, Cardiff/Wales, Bristol, London student societies, and Nottingham (web search, Oct 27 2026).
- Excluded on purpose: all retired sources listed in the task; meetup.com Birmingham/Manchester/London/Oxford pages; Manchester Squash and Bristol Motorsport pages from wave 20261026; groupjoin.link / joinnchat.com fetches (curl hung, abandoned — no groups taken from them).

## Porn filter
- No hard porn/xxx groups found or included. No groups were removed on friendship/dating grounds.

## Files (not touched)
- groups.json, generate.py output, and ~/workspace/wgl-deploy/ were NOT modified.
