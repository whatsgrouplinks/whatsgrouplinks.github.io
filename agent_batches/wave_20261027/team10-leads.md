# Team10 — Philippines (wave 20261027) — leads

## Counts
- Verified (fresh file): 0
- Unverified-pending: 1
- Dropped as duplicates: 5
- Leads / not staged: see below

## Sources investigated (NEW for this slice, not wave-20261026 / retired)
- techsslash.com Philippines WhatsApp group links page — text fetch worked, direct curl timed out (25s).
  - 5 named entries extracted: Philippines crypto investment, Update News, Premium Spot, Bablu Official, Boula.
  - ALL 5 invite codes were already in the full existing code set (groups.json UNION .existing_codes.json, 73,170 codes) — dropped as duplicates, NOT staged in pending.
  - Remaining named entries on that page without a recovered code (do not stage without an invite): Atlegang's gift group, osm friends, Good Friendship, Good Friends, Fixerking_chinku, Trading forex Academy, All forage Team, WCS, Philippines girls, Sanam Ray, Books, Philippines Market, Friends, Wallpapers Hub, Philippines Musics, Movies and Series. Note: one entry on the page is explicitly adult-themed in its original wording and was excluded from staging consideration; friendship/girls/social entries were not removed on that basis.
- Philippine Sailing community notice (racing-rules PDF, 2026 National Elimination Series) — 1 candidate, staged in unverified-pending.
- Pinoy Shuttle Smashers Qatar (local gyms/fitness listing) — Filipino badminton community based in Qatar, code recovered from a search snippet. NOT staged in the PH file because its base is Qatar, not PH — parent decision needed on country tagging before any staging.
- Excluded, per task: meetup.com Manila pages, and all retired sources (whatslinkhub, whatsappgrouplink.org, wappgrouplinks, whatsappgroupjoinlinks, grupodewhatsapp, wagroupnest, groupizo sitemaps 1-11, groupda, whatzgrouplink, whatsgroulink, whatsapp-group-link, whtsagrouplinks, groupwhat, groupinvitelink, groupsor.in, wagroupslink, whgroups.link, whatsonly, activewagroup, grouplink.com.in, techapkzone, freewagroup, groupsnest, ongrupos, grupbul, joingroupslink, joingram.in, groupwa.com, grouplinks.in, dailygrouplinks). The grouplink.com.in Philippines Girls page and techapkzone Call of Duty Philippines page were seen in search but NOT used, for this reason.

## Verification note (important, honest)
- The 1 pending item passed dedupe (fresh vs 73,170 codes) but could NOT be curl-verified from this VM: spaced curl to chat.whatsapp.com returned HTTP 000 / proxy CONNECT timeout (20s), for both fresh candidates tried. That is a network/proxy timeout, NOT proof the links are dead or revoked.
- 5 techsslash preview fetches via the text-fetch tool returned 403 access-denied; those requests were not retried, and those 5 codes then turned out to be duplicates anyway, so no loss.
- No item is claimed verified. The fresh file is intentionally empty rather than filled with unverified links.
- No porn/xxx group was staged. No source name, source URL, or personal info appears in any staged item name/description.

## Next step for parent
- Re-verify the 1 pending sailing link from a host where chat.whatsapp.com is reachable, or via the live browser, before merging. If it returns a non-empty og:title, move it to the fresh file unchanged.
- The techsslash page needs a fresh code extraction (its remaining named entries) in a later run — do not re-use the 5 duplicate codes.
