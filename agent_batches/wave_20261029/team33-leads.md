# TEAM 33 — Islamic category leads (wave_20261029)

## Fresh verified / pending (staged this run)
- 5 verified → `team33-fresh-cat-islamic.json`
- 11 pending (HTTP 200 + invite_link_type_v2 marker but EMPTY og:title → per rules, junk title = pending) → `team33-unverified-pending.json`

## Exhausted / fully harvested pages (all codes already in union — do not re-scrape)
- 77links.com islamic-whatsapp-group-links/ (103 links, 0 fresh)
- 77links.com madani-channel-whatsapp-group-links/ (74 links, 0 fresh)
- whatgroups.com islamic-whatsapp-group-link/ (0 direct links; JS buttons)
- whatgroups.com online-quran-students-whatsapp-group-links/ (52 links, 0 fresh)
- groupda.com spiritual/best-islamic-whatsapp-group-link-2022/ (82 links, 0 fresh)
- whtspgrouplink.com islamic-whatsapp-group-links/ (73 links, 0 fresh — archive page has NO direct codes; individual posts only)
- groupsnest.com category/islamic-groups (8 links, 7 fresh)
- groupsnest.com sunni-islamic-whatsapp-group-link (33 links, 7 fresh — real names live in JSON-LD ListItem, not aria-labels)
- findglocal.com Daily Quranic Verses & Hadiths page (2 codes staged: males + females)

## Out-of-slice / fresh-directory leads for other teams
- whtspgrouplink.com/category/religious-whatsapp-groups/ — archive only; islamic tag pages: /tag/indian-muslim-whatsapp-group-link/, /tag/dubai-islamic-whatsapp-group-link/, /tag/bangla-islamic-whatsapp-group-link/, /tag/tamil-islamic-whatsapp-group-link-malayalam/
- groupwa.link/ — homepage listicles (Qurano Hadeesh Islamic Post, Daily Qur'an-o-Hadees, Ghazi Islamic Institute, Alhamd Islamic Academy) — no dedicated Islamic category page found; codes via Join buttons
- whatsshare.com/blog/best-whatsapp-groups-to-join-in-2026 — religion & spirituality section, no direct codes
- abundantmuslim.com/whatsapp/ — single Jannah Sisters group page (no direct code on page)
- groupsnest.com/Islamic-Whatsapp-Group-Links — alternate Islamic page URL (partially scraped via category page)

## Notes
- No /sex/ /xxx/ /adult/ pages visited. No emoji-only titles staged. No personal info, no source names/links in items.
- Dropped: one groupda entry "🕋🕋" (symbol-only title); findglocal chat.whatsapp.com/invite/*-style links (not standard codes).
- Verification: curl -sL per code, 7s spacing, no HTTP 429 hit. 11 codes returned 200 + invite_link_type_v2 marker but empty og:title → staged as pending, not verified.
- All fresh codes (16) are NEW vs the 73,874-code union (groups.json + .existing_codes.json).
