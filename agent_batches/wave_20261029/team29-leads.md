# TEAM 29 — Fresh Discovery Batch A — leads.md (2026-10-29)

## Directories scraped this run (fresh, not in retired list)
- **groupsnest.com** — https://groupsnest.com/ — 9 listing pages scraped via curl (category/buy-sell-groups, category/technology-groups, category/food-groups, category/culture-groups, category/fashion-groups, online-business-whatsapp-group-link-pakistan, gsm-whatsapp-group-links, punjabi-whatsapp-group-links, social-media-whatsapp-group-link). Pages carry schema.org JSON-LD ItemList name+code pairs — clean extraction. 322 raw pairs, 305 unique, only 41 new vs union (73,874 codes); the site is heavily covered already.
- **whtsagrouplinks.com** — https://www.whtsagrouplinks.com/international-whatsapp-groups-links/ — page behind Cloudflare for curl; fetched via browser.open text. 71+ named groups, 8 "Join" links resolved (codes recovered from tool redirect output, NOT by re-opening invite pages). 5 of 8 already in union; 3 fresh.

## Out-of-slice fresh directory leads (NOT scraped — for other teams)
- **groupwhat.com** — named in edopedia Groupsor-alternatives roundup, "verified links, global reach" — not retired.
- **groupinvitelink.com** — edopedia roundup, "simple browsing, crypto & financial groups" — not retired.
- **whatgroups.com** — edopedia roundup, "22,000+ regularly updated links" — not retired.
- **whtspgrouplink.com** — edopedia roundup, "safety-focused, manually tested links" — not retired.
- **groupsor.in** — edopedia roundup, "South Asian audiences, entertainment & memes" — not retired.
- **groupslink.pk** — edopedia roundup, "Pakistani community, South Asian focus" — not retired.
- **whatsgroups.com / groupsorlinks.com / joinwhatsapp.com** — mentioned by thediplomariot as popular directories — not retired.
- **grouplinksor.com / indianwhatsappgrouplinks.com / whatgrouplink.com / whatappgroup.com** — from technofizi sitelike list — not retired (verify before use).
- **togather.in** — https://www.togather.in — 1,794 approved listings (WhatsApp/Telegram/Discord); curl timed out, NOT scraped. Candidate for a browser-capable team.
- **whatsappgrouplinks.com** — https://whatsappgrouplinks.com/ — JS SPA, curl returns empty shell; NOT scraped. Candidate for a browser-capable team.
- whtsagrouplinks.com has more pages worth scraping (Cloudflare-blocked for curl): country pages for Indonesia, Italy, Thailand, Dubai, Indian, New York, Bhutan — same browser.open route works.
- whtsagrouplinks.com code list seen this run: JvglBhpQ8e70kEtHrZ4g2M, FOlywLowMziIS6zFhf4kHh, FRqwueaKpMxAxAsQ4Rl6uR, Lu09Oxy4c932eNKvML36XZ, GEFRH4oPmFNFewefYXen8Q, IQ2PbMJghwgDWwXnhh2Rrg, KK5khc8fRBr9JxJcJiOpLB, KxLpjXYClJUBPpiPYKaKHk (last five already in union).

## Exhausted / blocked notes
- **togather.in**: curl timed out twice (>25s). Not scraped.
- **whatsappgrouplinks.com**: JS SPA shell only via curl. Not scraped.
- **whtsagrouplinks.com**: Cloudflare "One moment, please..." for curl (HTTP 200 challenge page); browser.open rendered text fine, but chat.whatsapp.com invite pages return HTTP 403 in the text-fetch layer — do NOT open invite links via browser.open; extract codes and verify via curl.
- groupsnest.com is largely harvested already (only 13% of its pairs were new). Future runs should prefer its NEWEST category pages first.

## Verification notes
- 44 codes verified via curl (HTTP 200 + invite_link_type_v2 on all 44; zero 429s; 7s spacing respected).
- Verified (6): INTERNATIONAL GROUP, Late Night Vibes, M.A Mobile, Online Shopping Now, Jutt Online Earnings, Its Our South Punjab — all had meaningful og:title + og:image.
- Pending (37): all HTTP 200 with invite_link_type_v2 marker but empty og:title (pending), except "Punjabi Comedy Club" (og:title "Punjab Board Group 1..." — ambiguous school-board reference, moved to pending deliberately) and "Gup Shup" (empty og:title).
- Dropped (1): SmmGreata.com (code Bi5VVZGYRsmI27wsBTe2y1) — og:title is a domain name, spammy, violates name rule.
- Content rules applied: dropped one 🔞-marked entry (Generation URZ), one symbol-only title (•𓆰⎯꯭ Ꮃ 𝙾 ʀ ʟ ᴅ...💋), spaced-out junk names; skipped visa-slot and "1Desire" suggestive entries. No /sex/ /xxx/ /adult/ pages visited.
