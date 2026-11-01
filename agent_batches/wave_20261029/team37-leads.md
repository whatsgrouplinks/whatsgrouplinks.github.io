# TEAM 37 — News category discovery leads (2026-10-29)

## Fresh directories harvested
- whatgroups.com/news-whatsapp-group-links/ — 146 unique codes scraped; 57 passed dedupe; ALL 56 valid-format codes returned empty og:title on verification (dead/revoked invites), 1 malformed code dropped. Worth a re-crawl in a later wave: if the site refreshes its invite links, new ones may verify.
- groupwa.link/ (News WhatsApp Group section) — 10 codes, ALL already in existing set.
- whtsagrouplinks.com/news-whatsapp-group-links/ — 23 codes, ALL already in existing set.
- whtsgrouplink.com category/news/ → 9 article pages (newspaper, the-hindu, dainik-jagran, express-news, hindi-news, uttar-pradesh-news, ibc24, national-news, dainik-bhaskar) — 105 unique codes, ALL already in existing set.
- cdn-cms.f-static.net "Social Media Pakistan" PDF — 10 Pakistani newspaper codes, ALL already in existing set.

## Leads needing a live browser (not attempted — subagent has no browser)
- freewagroup.com/news-whatsapp-group-links/ — page loads (~130KB) but the group list is JS-rendered; no chat.whatsapp.com links in static HTML and wp-json returns nothing. Live-browser visit likely reveals the links.
- wagroup.in/tag/news-whatsapp-groups/ — curl failed (empty reply, exit 52); live-browser visit may work. NOTE: wagroup.in is NOT the retired wpgroup.in — different domain.
- groupswp.com/whatsapp/channels/ — WhatsApp CHANNELS directory (whatsapp.com/channel/ links, not chat invites). Contains news channels (BBC News 22M followers, Zee Business, etc.). Out of scope for chat invites but a possible channel source for the site's channels feature.

## Verification finding
Calibrated: known-good invite shows HTTP 200 + non-empty og:title + invite_link_type_v2; known-bad invite shows HTTP 200 + empty og:title + marker. All 56 whatgroups.com candidates returned empty og:title → treated as dead/revoked → staged as UNVERIFIED pending, NOT fresh. No HTTP 429 encountered; all checks completed.

## Suggestions for next waves
- Small regional news blog listicles (Kashmir, Punjab, Kerala, Tamil, Bengali news blogs) remain under-harvested; generic big directories are exhausted.
- Re-verify the whatgroups.com pending codes in a later wave; dead links may come back if the site updates them.
