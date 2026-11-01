# Team 11 — Southeast Asia regional — wave 20261028

## Sources / pages scraped (NEW, not wave 20261027)
- Meetup: Drink and talk social gathering & language exchange Malaysia (Kuala Lumpur)
- Meetup: Friends of Kuala Lumpur / Kuala Lumpur Friends Meetup (Tutor A Child)
- Universiti Malaya postgraduate Telegram/WhatsApp page (codes all dupes)
- Jobs directory page (meraonlineworld jobs listing — Singapore jobs, Singapore workpermit, Malaysia agents codes all dupes)
- Meetup: Singapore Weekend Photography; Practical Philosophy Singapore (two codes)
- Meetup: Bangkok Expat Digital Nomads; Chit Chat and Chill Bangkok; Bangkok language-exchange meetup; BKK Funminton Squad
- whtspgrouplink Bangkok page (first five Join links only — all five codes were already in the dedupe union; no further Join-link extraction was attempted after the text reader blocked those links)
- whtspgrouplink Cambodia page (listed only; codes not extracted via the blocked reader path)
- Bible Study event in Phnom Penh page
- Global Jobs Atlas Cambodia scholarship article (code dupe)
- Singapore American School alumni city-clubs document (Singapore club only; other cities out of slice)
- Padel Phuket listing; Ironguides Bangkok updates (Ironguides code dupe)
- Searches: Singapore/Malaysia/Thailand/Vietnam/Cambodia/Laos/Myanmar Meetup, university, expat and community pages

## NOT re-scraped
- Wave 20261027 manifest sources, and the seven forbidden wave-20261027 team11 pages (Hanoi dance/fitness studio, Hoi An meditation event, Hanoi coffee course, HCMC design community, Thailand news community, Bangkok school booster news, Bangkok triathlon club). Two further hits matching those forbidden page types (a Hanoi dance/fitness studio code and a Hanoi coffee-course code) were excluded on sight; both were also dedupe dupes.
- Retired sources (whatslinkhub, elsabagh, whatsappgrouplink.org, wappgrouplinks, whatsappgroupjoinlinks, grupodewhatsapp, wagroupnest, groupda, groupizo sitemaps) and groupjoin.link tags (team02's slice).

## Counts
- Distinct codes examined: 32
- Candidates found (distinct, code-bearing): 32
- Dedupe drops (code already in dedupe_union_codes.txt, 73,684 lines on disk): 25
- New codes after dedupe: 7
- Verified (spaced curl, HTTP 200 + non-empty meaningful og:title, og:title used as name): 2
- Pending (HTTP 200 but empty og:title, so not verified under the rule): 5
- Porn drops: 0 (no hard-porn titles seen; girls/friendship/social groups were not dropped)
- Meaningless/symbol-only drops: 0 in the new set

## Verified (in team11-fresh-seasia.json)
- Language Exchange in BKK — TH — Education
- Phnom Penh Bible Study Group — KH — Community & Social

## Pending (in team11-unverified-pending.json, source-listed names)
- Drink and talk social gathering Malaysia — MY — Community & Social (empty og:title)
- Practical Philosophy Singapore — SG — Community & Social (empty og:title)
- Chit Chat and Chill Bangkok — TH — Friendship (empty og:title)
- SAS Alumni Singapore — SG — Community & Social (empty og:title)
- Padel Phuket — TH — Sports (empty og:title)

## Notes / caveats
- The five Bangkok directory Join codes could not be mapped with certainty beyond the reader's return order, but all five were dedupe dupes, so no Bangkok directory item is in either output file and no mapping error affects the outputs.
- WhatsApp invite pages returned HTTP 200 with an empty og:title for the five pending codes; they may be live groups whose title is not served to curl, or revoked/empty invites — re-check before any merge.
- No groups.json, generate.py output, or wgl-deploy files were touched.

## Next-pass leads
- whtspgrouplink Singapore Jobs, Malaysia, Vietnam, Myanmar and Laos country pages (not opened this wave; the Bangkok/Cambodia pages show the same Join-button pattern, so a live-browser pass may be needed to extract codes reliably).
- whtspgrouplink Cambodia page Join links (12 listed names) — same live-browser lead.
- Meetup Bangkok Digital Nomads community links (three community links, codes hidden behind Meetup links, not extracted this wave).
- More recent Meetup Singapore/Kuala Lumpur/Bangkok event pages (photo walks, hiking, social clubs) — search snippets expose codes directly and are a productive route.
- Laos and Myanmar: no new code-bearing pages found this wave beyond dupes; these two countries remain the thinnest part of the slice.
