# team08-fresh-eastafrica — LEADS & BLOCKER NOTES (wave_20261026)

## Blocker: shell curl verification impossible in this session
- curl from this VM times out for EVERY host (exit 28, HTTP 000), tested against
  chat.whatsapp.com, example.com, and a directory page. The egress proxy is configured
  (http_proxy/https_proxy set) but CONNECT times out. Same failure team09 reported in
  wave_20261025. Consequence: NOTHING could be marked "verified" this run, so the
  verified file is an empty list by rule, and the one extracted candidate sits in
  team08-unverified-pending.json for a live-browser/curl re-check before any merge.
- chat.whatsapp.com was NOT fetched via the text-fetch service (per the wave_20261025
  team09 note, that path returned 403 and must not be retried).

## Pending item provenance (must confirm at verification time)
- MPYA ONLINE (TZ, Health): code FD6A5ohfuQL0EYRmJ4ns95 is taken from the new
  directory's own /join/<code> page URL for that group page. The verifier must confirm
  the slug equals the real WhatsApp invite code (i.e. the directory's Join button
  resolves to chat.whatsapp.com/<same code>) before merging. If it does not match,
  drop the item — do not publish the mapped URL.

## Sources tried
1. walinking.link — NEW directory (zero hits in scrape_log.md and all wave_20261023b/
   20261024/20261025 dirs; not on the banned list). 15,504 groups claimed. Only ONE
   slice-relevant group page is indexed/retrievable via text fetch (MPYA ONLINE, TZ).
   Its listing pages render without extractable links in text fetch, so the rest of its
   KE/TZ/UG/ET catalogue is a LIVE-BROWSER lead, not scraped here.
2. wagroupslink.pro — NEW domain (zero prior-wave hits; distinct from banned
   wagroupslink.com). Homepage text fetch shows rules/FAQ only; group listings sit
   behind Join buttons/JS with no codes exposed. Name-only lead: needs a live-browser
   pass; NO codes taken from it, nothing invented.
3. get.whtsgroupslinks.com — clean in prior waves but only a how-to guide article,
   not a group directory. Not used.

## Deliberately NOT re-scraped (appear in prior waves / banned list)
- groupjoin.link Kenya pages (exhausted, per task), techsslash.com, whatgroups.com,
  whtspgrouplink.com (wave_20261023b team13-16), whatsagroupslinks.com, tzcareers.com,
  assengaonline.com, liquidationuganda.org (all named in wave_20261025 manifest as
  already-tried/next-source — abandoned per the task's abandon rule), wagroupslink.com
  (banned), groupsnest.com (banned), whtsagrouplinks.com (banned).
- One Uganda real-estate code surfaced in search (realestatedatabase.net article) was
  already in the existing code set — dropped as a duplicate, not recorded.

## Dedupe base
- /tmp/codes_team08.txt built from groups.json (37,969 codes) + .existing_codes.json
  = 73,092 codes total. The pending item's code is NOT in that set.
- No porn/explicit items kept. No source names or source URLs in any JSON item.
  No pps.whatsapp.net image was exposed for the pending item, so the image field
  is omitted.
