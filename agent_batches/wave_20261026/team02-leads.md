# team02 leads — wave 20261026 (India slice)

## Yield
- Verified: 0 (file team02-fresh-india.json = [])
- Unverified-pending (name-only, no invite codes): 95 in team02-unverified-pending.json
  - Sources: joinnchat.com Indian page (names transcribed from page text) + farmersvoice.in agriculture page (4 main + 5 category groups).
  - No source name/URL, phone, email or personal name appears in the JSON items.
  - Dropped: hard-block items (adult / sex-video / hot / aunty / naughty / paid-girls / private-moments), minors-adjacent (School Girls), generic junk names, and 15 names exactly matching groups.json names.
  - 1 attempted invite item excluded after a 403 fetch; its code was not recorded and is not in any output file.

## Why no verified items (blocker, not a source failure)
- Shell egress down this run: curl/python to example.com, google.com, joinnchat.com, farmersvoice.in and minidea.co.in all timed out (HTTP 000), so the mandated curl verification (HTTP success + non-empty og:title) could not run.
- Page-text fetching via browser worked for directory pages, but it does not expose invite codes in text; codes sit behind Join buttons/outlinks.
- Next step for coordinator: re-run verification on the 95 pending names once shell egress recovers, resolving codes via a live-browser Join-click pass on joinnchat.com / farmersvoice.in, then dedupe against /tmp/codes_team02.txt (73,092 codes built this run) and verify by curl.

## Name-only / JS-only leads (no names harvested, do not treat as verified)
- shareyourgroup.com Punjab page (2026/04): opened, contains only a JS submission form and SEO keywords — no actual group names listed.
- blog.waziper.com Kannada page: page fetch failed with a local worker error; source NOT proven dead, do not retry that exact failed fetch — re-check via a fresh independent request in a later wave.
- minidea.co.in WhatsApp collection: not page-fetched this run (shell timeouts); old 2021 list, low priority.
- joinnchat.com Punjabi-girl page: search snippet shows only example category tables, not a harvestable group list — not used.

## Sources checked and NOT reused
- Banned/retired list in the task (all avoided).
- whtspgrouplink.com / thewhatspgrouplinks.com / wtgrouplinks.com / appgrouplink.com / wglfinder.com / grouplink.com.in: appear in prior waves/scrape_log — abandoned, not scraped.
- joinnchat.com, farmersvoice.in, shareyourgroup.com: no hits in prior wave manifests or scrape_log (grep checked) — genuinely new this wave.
