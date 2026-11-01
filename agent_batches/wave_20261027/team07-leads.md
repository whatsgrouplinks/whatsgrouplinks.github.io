# Team07 — Bangladesh (wave 20261027)

## Results
- VERIFIED: 7 items in `team07-fresh-bangladesh.json`
- UNVERIFIED-PENDING: 8 items in `team07-unverified-pending.json`
- All 15 candidates checked against the FULL dedupe set (groups.json 38,051 groups UNION .existing_codes.json = 73,170 codes): all 15 FRESH, 0 duplicates dropped.

## Source actually harvested (NEW — zero prior mentions in agent_batches)
- grouplinkshare.com Bangladesh listing page (15 group cards with names, member counts and invite codes in the page HTML; text-fetch alone shows only an FAQ shell, curl returned the full cards).

## Verification method
- Spaced curl fetches (1.5s sleep, browser User-Agent) of each chat.whatsapp.com invite.
- VERIFIED = HTTP 200 AND non-empty og:title (og:title matched the directory card name in all 7 cases).
- PENDING = HTTP 200 but EMPTY og:title (8 cases: Jobs Alerts, Students Hub, BGMI/Free Fire BD, Dhallywood Movies Fans, Bangla Memes & Jokes, Shopping Deals, Online Earning Bangladesh, Islamic Groups Bangladesh). Per task rules these are NOT claimed verified; they may be revoked or title-less and need a live-browser recheck.
- No pps.whatsapp.net group images were returned (only the generic WhatsApp static image), so all items have `"image": ""`.
- No hard-porn/xxx groups encountered; nothing was removed on porn grounds. Girls/friendship groups: the verified Chat Group is a general friendship/chat group and was kept.

## Sources deliberately NOT reused (retired / prior-wave)
- whatgroups.com, groupjoin.link, wagroupslink.com, groupwa.link, wglfinder.com, groupsor family, whatzgrouplink, whtsagrouplinks, freewagroup, grupbul, activewagroup.com BD pages, linkgic.top, grouplink.com.in — all appear in wave-20261026 (or earlier) team notes/leads, so none were scraped.
- grouplinkshare.com's other country pages (Pakistan, Nepal, Worldwide) were NOT harvested — out of this slice (Bangladesh only). Its Worldwide page may hold further BD-relevant groups for a future slice.

## Notes / limits
- grouplinkshare.com is slow over sandbox curl (~22s for the listing page; one earlier fetch timed out and was retried successfully). A future pass should allow long timeouts.
- The 8 pending items are the highest-value recheck targets: if their og:titles appear on a live-browser pass, they are ready to promote to verified with no further dedupe needed (already deduped).
- groups.json and deploy outputs were NOT touched.
