# TEAM 21B leads — joinnchat.com subpages (2026-10-29)

## Verified (1)
- Cricket Today (cricket-whatsapp-group-links) — og:title 'W CRICKET TODAY', invite_link_type_v2 OK

## Pending-name leads (55 — codes not verified, mostly empty og:title = dead/revoked links)
- PSL 9
- Champion Trophy
- HBL PSL
- PSL LIVE
- HBL PSL 9
- Rizoo Fanz
- CHAMPION TROPHY
- Cricket ki dunia
- Pakistan Cricket
- Pak Shaheen Team
- Desi League
- Cricket Lovers
- International Friendship
- Friendship Across Borders
- Boys Not Allowed
- Happy Funny Group
- Fun group
- Just for fun
- Fun charting
- whatsapp group funny
- Drama club
- Indian girls
- Tamil general
- Find lovers from usa
- New Sticker
- Punjab Diyan Kudiyan
- Sohni Punjabi Kudiyan
- Punjab di Roshni
- Random GC
- Pind di Muskan
- KARACHI UPDATE
- ARY news Islamabad
- FAST NEWS PAPER
- Gatoi News
- Love Pubg
- USA Football Fanatics
- Chic Singles
- Charmer Singles
- Malayalam Women Club
- She Speaks Kerala
- Kerala Charmers
- Malayalam WhatsApp Group
- Wisdom Chat
- Tamil Aunty Lifelong
- Talk Therapy
- Aunty Friendship
- Conversations of Marathi
- Heartfelt Guidance
- Inspirational Insights
- Tamil Aunty Group
- Tamil Girls Group
- Pakistani Vibes Network
- Wisdom Exchange
- USA Life Stories
- Aunty Harmony in Kannada

## Content-filter drops (17 — do not re-stage)
- H*t Girl [sexualized]
- Vai vai vai [meaningless]
- School Charm Squad [school-age-sounding]
- Visual Delights [adult-adjacent]
- Thund Group Link [vulgar-slang]
- hot aunty groups [aunty-hot]
- Tamil antys [aunty-obfuscated]
- Local aunty number [aunty-number]
- Divorce Aunty [aunty-dating-pattern]
- Tamil Aunty Number [aunty-number]
- Single Aunty Life [aunty-dating-pattern]
- Madrasi aunty [aunty-dating-pattern]
- mallu aunty whatsapp group [aunty-dating-pattern]
- Indian Aunties [aunty-dating-pattern]
- Aunty number Chennai [aunty-number]
- Chat wit Aunty [aunty-dating-pattern]
- Elite Aunty Affluence [aunty-dating-pattern]

## Out-of-slice / new directories
- joinnchat.com publishes more category pages, but the task slice listed exactly the 13 URLs below — no out-of-slice scraping was done.
- Task said '14 pages' but listed 13 URLs (no 14th URL given). Scraped all 13 given:
  college, cricket, entertainment, funny-memes, girls, indian, news, poetry, pubg, usa, pakistani, malayalam, aunty (each -whatsapp-group-links/)

## Exhausted pages / notes
- All 13 pages fetched HTTP 200 with Chrome UA (301 without -L first, then -L resolved). Group tables are server-side <table> rows.
- 1,245 table rows with chat.whatsapp.com invites -> 779 unique codes -> 706 already in the 73,874-code union (groups.json + .existing_codes.json) -> 73 new candidates.
- 17 candidates dropped by content filter (see above); 56 verification attempts made (within ~60 cap, 7s spacing, no 429s).
- 53 of 56 returned HTTP 200 with EMPTY og:title (verified on re-fetch: og:title content='' on the live invite page) -> these invite links are dead/revoked, kept in pending only for the record; merger should treat them as dead.
- 2 more had og:titles mismatched to the page listing ('Indiana' vs 'Conversations of Marathi'; 'Mighty cruise' vs 'Tamil Aunty Group') -> recycled links, pending.
- channel links (whatsapp.com/channel/...) on the pages were skipped — out of scope (chat.whatsapp.com only).
- 1 pending item 'Love Pubg' had a trailing-dot typo in the source URL; code sanitized (DYhWOZG5ZC6EuPyhYlMfCY) but the link is dead (empty og:title).
- college + poetry subpages: every extracted code was already in the existing union — zero new candidates from those two pages.
- Aunty page filtered strictly: dropped hot/number/obfuscated/dating-pattern titles; kept clean community ones (Wisdom Chat, Aunty Friendship, Conversations of Marathi, Talk Therapy, Tamil Aunty Lifelong, etc.).
- girls/friendship kept clean: 'Indian girls', 'Tamil general', 'Find lovers from usa'.

