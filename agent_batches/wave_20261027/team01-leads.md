# team01-fresh-kenya — LEADS (wave_20261027, NEVER merge input)

## Final counts for this team
- Verified (team01-fresh-kenya.json): 3 — Practical Class 25, ELYZZA TOURS GROUP 12, SOB ATTACHMENT SEPTEMBER DECEMBER 2026.
- Unverified-pending (team01-unverified-pending.json): 26 — all 23 freshers-directory codes plus Kenya Times News Group, Kenyatta University Energy Engineering Club, and Newsblaze Kenya Group. All 26 returned HTTP 200 with an empty og:title (REGULAR link type), so they are pending, never verified, per the task rule.
- Leads in this file (name-only, never merge): 9 items below.

## Name-only / Join-button leads (no invite code extracted, do not merge)

- LinkToGroups Kenyan blog (Oct 15, 2026): "Dating Single Mothers Kenya", "Kenyan Hot Girls Trending", "Kenyan Hot Girls Trending Group Chat", "Kenyan Connections and Funmates" — all resolve to Telegram listings, NOT WhatsApp groups, on the pages checked. No chat.whatsapp.com code exposed. Live-browser/Telegram check only; do not invent codes.
- Summit Recruitment job alerts (Kenya recruitment agency): a "newly created WhatsApp group" Join link exists on its job page, but the code is behind the Join button and was not exposed in text fetch. Name-only lead for a live-browser pass.
- Pata Kazi jobs WhatsApp groups (Kenya): a jobs page describing Kenya job-seeker WhatsApp groups, but the invite links are behind interactive/JS elements and no code was exposed in text fetch. Name-only lead for a live-browser pass.
- Fitbeat Run Club and Urban Swaras Running Club (Nairobi, Kenya): running clubs whose WhatsApp groups are joined via social-media registration, not a published invite code. Name-only leads.
- Diplomat Trekkers (Kenya hiking): WhatsApp group link is sent only after booking a hike. Name-only lead.
- Eastern Region Holy Catholics (Kenya, Machakos/Kitui/Makueni community): TikTok posts invite people to DM to join — no public invite code published. Name-only lead; no contact details recorded here.
- Game World KE (Kenya gaming community, Nairobi/Mombasa/Kisumu/Nakuru/Diani): a forum thread promotes the group but the page fetch failed and no code was extracted. Name-only lead.
- Kenya Times news group: the site's own group link code was already in the existing code set (dedupe drop, see below), so it is not a fresh candidate.

## Dedupe drops (code already in the full existing set — NOT in verified/pending)
- Taita Taveta University Freshers, Technical University of Mombasa Freshers, Tharaka University Freshers, Co-operative University of Kenya Freshers, University of Eldoret Freshers, University of Embu Freshers, University of Kabianga Freshers, University of Nairobi Freshers (all from the Kenyan freshers directory below) — codes already known.
- Likoni TVC group and Luxury Whips Kenya buyers group — codes already in groups.json / existing set.
- France teaching-posts Kenyan students group code (short code) — already in existing set.

## Sources tried and NOT reused (per task exclusions)
- groupjoin.link Kenya pages (excluded by task), and all retired sources listed in the task (including walinking.link, wagroupslink.pro, whtsagrouplinks, activewagroup, techsslash, whatgroups, pkwhatsgrouplinks as a wave-20261026-mentioned source).
- whatzgrouplink.com and whtspgrouplink.com — not used (retired / wave-20261026-mentioned).

## Fresh source actually used for code-bearing candidates
- A Kenyan creative agency homepage carrying a "Directory of All Kenyan Universities 2026/2027 Freshers WhatsApp Groups" (Alupe, DeKUT, Egerton, JOOUST, JKUAT, KAFU, Karatina, Kenyatta, Kibabii, Kirinyaga, Laikipia, Maasai Mara, Machakos, Maseno, MMUST, Meru, Moi, Multimedia, Muranga, National Defence, Pwani, Rongo, SEKU, plus the dedupe-dropped ones above).
- Individual Kenya pages found via web search: KCA University School of Business attachment memo, Kenyatta University Energy Engineering Club page, Elyzza Tours hike listing, TikTok Kenya accounting post, Kenya Times news articles (code already known), and a Kenyan news site's published group link (Newsblaze Kenya Group — code verified as HTTP 200 / empty og:title, so it sits in pending, not verified).

## Verification note
- Verification was by spaced curl (1-2 s+ between requests, browser User-Agent) against chat.whatsapp.com, checking HTTP status, non-empty og:title and invite_link_type. A known-good control code from groups.json returned HTTP 200 with a real og:title, confirming the method works; empty-og:title results are therefore treated as dead/revoked, not verified.
- Curl egress was intermittent during this run (early requests timed out / HTTP 000, later requests succeeded). Items that returned HTTP 200 with an empty og:title, or HTTP 000, are in team01-unverified-pending.json, never in the verified file.
