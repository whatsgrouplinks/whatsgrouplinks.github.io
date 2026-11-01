# Team06 leads — Egypt + Arab Gulf — wave 20261027

## Result
- Examined: 26 full invite codes found in plain text (search snippets / page text)
- Dropped as duplicates (in groups.json 38,051 groups UNION .existing_codes.json; union = 73,170 codes): 19
- Fresh candidates verified by spaced curl (browser User-Agent, 1.5 s sleep): 7
- VERIFIED (HTTP 200 + non-empty og:title): 1 — Adventure Partners (AE)
- PENDING (HTTP 200 but og:title empty = dead/revoked invite page): 6 — all SA, listed in team06-unverified-pending.json
- No hard-porn groups found in this batch; no groups removed on that filter.
- dubai-forever.com codes were seen in search results and were EXCLUDED entirely per slice rules (not used, not counted).
- No retired wave-20261026 source was used. No groups.json / generate.py / wgl-deploy file was touched.

## Sources actually used (new, not retired)
- whtspgrouplink.com country pages (Saudi Arabia, Qatar, UAE Business, Egypt) — group NAMES harvested, but invite codes are hidden behind Join buttons in the text fetch; see blockers below.
- Meetup community pages (Dubai, Sharjah, Abu Dhabi) — plain-text invites; most already in the union set.
- Travel-blog Gulf evacuation page — Kuwait / Dubai / Doha invites; all three already in the union set (dropped).
- Arabic forum thread (mstaml) — old Saudi/Gulf invites; 6 fresh, all dead on verification.
- Job/career pages (jobscounter UAE) — invites already in the union set (dropped).

## Blockers / leads for a follow-up team (NOT verified, do not merge blindly)
1. whtspgrouplink.com Egypt page lists ~25 named groups (Guide Of Egypt Tours, Egypt job news, Education news Egypt, Travel and tourism in Egypt, Buy and sell in Egypt, Dahab Walking Group, Foreigners in Egypt learning Quran, Daily News Egypt, Hurghada Residents, Egypt News updates chat, English Practice Club, Pyramid history, Only Egypt people group, Epsilon School student Egypt) and its Qatar page lists ~50 named groups (Qatar Study & Job, Doha Foodie & Social Qatar, Home Based Sellers, Qatar Education Forum, Qatar jobs news, Qatar friendship group, Qatar Hotel Jobs, Qatar Driver Jobs Group, Qatar Recruitment Times, GCC JOB GROUP, Qatar Expat Support, Q-BUY RENT & SELL, etc.), plus Saudi (~45 names) and UAE Business (~16 names). Their invite codes could not be extracted by the routes available to this agent: the page-text fetch hides href targets, direct curl to the directory hung/timed out, and a first chat.whatsapp.com outlink fetch was rejected (403) so no further chat outlink fetches were attempted.
2. groupjoin.link — Egypt tag page reports 116 communities, Kuwait 18, Lebanon 13; direct curl timed out (HTTP 000) and its page text shows no codes, so nothing usable was extracted.
3. groupwa.link groups gallery — behind a Cloudflare-style verification page in the text fetch; its Egypt Arabic groups (General Chat Egypt Arabic, Friends Egypt Arabic) could not be extracted.
4. Meetup Gulf groups already in the union set (Dubai Business Community, Founders Connect Dubai & Sharjah, Abu Dhabi Expats Community, Dubai Web3 Networking, Kuwait quiz group, Cairo Social Group, Founders Live Cairo, Cairo Morning Club, Human Unity Egypt Cairo) — no action; they are duplicates, not missing groups.
5. Jordan, Lebanon, Oman, Bahrain, Kuwait, Qatar fresh-group yield was zero in this run: every plain-text invite found for those countries was already in the union set or was a truncated code (unusable). A follow-up team with live-browser access to the whtspgrouplink.com country pages would be the highest-value next step for those countries.
