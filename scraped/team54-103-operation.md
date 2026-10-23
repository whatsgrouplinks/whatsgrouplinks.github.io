# 50-Team Scraping Operation — launched 2026-10-18 ~00:30 PKT

## Status: RUNNING (50 worker subagents dispatched)

Baseline: 61,245 groups in groups.json

## Team assignments
| Teams | Theme | Output file |
|---|---|---|
| 54 | India North | scraped/team54-india-north.json |
| 55 | India South | scraped/team55-india-south.json |
| 56 | Pakistan | scraped/team56-pakistan.json |
| 57 | Bangladesh/Nepal/Sri Lanka | scraped/team57-bd-np-lk.json |
| 58 | English Africa | scraped/team58-africa-en.json |
| 59 | Brazil/Portuguese | scraped/team59-brazil-pt.json |
| 60 | Indonesia/Malaysia | scraped/team60-id-my.json |
| 61 | Gulf/Middle East | scraped/team61-gulf.json |
| 62 | USA/UK/Canada/Europe/Australia | scraped/team62-western.json |
| 63 | Latin America Spanish | scraped/team63-latam-es.json |
| 64 | Jobs (general) | scraped/team64-jobs.json |
| 65 | Sarkari Naukri | scraped/team65-sarkari.json |
| 66 | Study/exam prep | scraped/team66-study.json |
| 67 | Crypto | scraped/team67-crypto.json |
| 68 | Forex/trading | scraped/team68-forex.json |
| 69 | Fantasy/betting | scraped/team69-betting.json |
| 70 | Movies | scraped/team70-movies.json |
| 71 | Music | scraped/team71-music.json |
| 72 | PUBG/BGMI | scraped/team72-pubg.json |
| 73 | Free Fire | scraped/team73-freefire.json |
| 74 | Online earning | scraped/team74-earning.json |
| 75 | Reseller/shopping | scraped/team75-reseller.json |
| 76 | Matrimonial | scraped/team76-matrimonial.json |
| 77 | Health/fitness | scraped/team77-health.json |
| 78 | Islamic (2nd wave) | scraped/team78-islamic2.json |
| 79 | Business (2nd wave) | scraped/team79-business2.json |
| 80 | Real estate (2nd wave) | scraped/team80-realestate2.json |
| 81 | Travel (2nd wave) | scraped/team81-travel2.json |
| 82 | Technology | scraped/team82-tech.json |
| 83 | News/politics | scraped/team83-news.json |
| 84 | Reddit | scraped/team84-reddit.json |
| 85 | Quora | scraped/team85-quora.json |
| 86 | Facebook | scraped/team86-facebook.json |
| 87 | Telegram | scraped/team87-telegram.json |
| 88 | YouTube | scraped/team88-youtube.json |
| 89 | Blogs | scraped/team89-blogs.json |
| 90 | Forums | scraped/team90-forums.json |
| 91 | TikTok/Instagram | scraped/team91-tiktok.json |
| 92 | Aggregators/mega-lists | scraped/team92-aggregators.json |
| 93 | Search operators | scraped/team93-misdir.json |
| 94 | Fresh directories A | scraped/team94-dirA.json |
| 95 | Fresh directories B | scraped/team95-dirB.json |
| 96 | Misspelling variants | scraped/team96-dirC.json |
| 97 | Country directories | scraped/team97-dirD.json |
| 98 | Niche directories | scraped/team98-dirE.json |
| 99 | City queries | scraped/team99-dirF.json |
| 100 | Blogspot | scraped/team100-dirG.json |
| 101 | Paste dumps | scraped/team101-dirH.json |
| 102 | Alt phrasings | scraped/team102-dirI.json |
| 103 | Mop-up | scraped/team103-dirJ.json |

## Merge plan (after all teams report)
1. Load groups.json, build normalized invite set
2. For each team54..team103 file: load, validate chat.whatsapp.com links, dedup
3. Append new groups, save groups.json
4. Update scraped/merged.log
5. Report final verified count to parent
---
## Completions log
- Team 58 (africa-en): 31 new groups, file verified OK
- Team 60 (id-my): 537 new groups, file verified OK
- Team 77 (health): 23 new groups, file verified OK
- Team 67 (crypto): 14 new groups, file verified OK
- Team 83 (news): 11 new groups, file verified OK
- Team 86 (facebook): 29 new groups, file verified OK
- Team 61 (gulf): 23 new groups, file verified OK
- Team 63 (latam-es): 59 new groups, file verified OK
- Team 82 (tech): 52 new groups, file verified OK
- Team 91 (tiktok): 16 new groups, file verified OK
- Team 70 (movies): 31 new groups, file verified OK
- Team 81 (travel2): 19 new groups, file verified OK
- Team 89 (blogs): 54 new groups, file verified OK
- Team 68 (forex): 3 new groups, file verified OK
- Team 93 (misdir): 18 new groups, file verified OK
- Team 84 (reddit): 0 new (no reachable Reddit threads), empty file OK
- Team 96 (dirC): 14 new groups, file verified OK
- Team 68 (forex): 3 new groups, verified OK
- Team 93 (misdir): 18 new groups, verified OK
- Team 84 (reddit): 0 new (blocked, needs live browser), empty file OK
- Team 96 (dirC): 14 file entries, 1 truly new by invite-code (13 overlap via /invite/ URL variant); merge will dedup by code
- Team 57 (bd-np-lk): 23 new groups, file verified OK
- Team 72 (pubg): 7 new groups, file verified OK
- Team 64 (jobs): 21 new groups, file verified OK
- Team 99 (dirF): 91 new groups, file verified OK
- Team 75 (reseller): 8 new groups, file verified OK
- Team 100 (dirG/blogspot): 615 new groups, file verified OK (77 adult codes excluded by team; kept links have generic names)
- Team 54 (india-north): 41 new groups, file verified OK
- Team 90 (forums): 79 new groups, file verified OK
- Team 98 (dirE): 23 new groups, file verified OK
- Team 97 (dirD): 192 new groups, file verified OK
- Team 73 (freefire): 8 new groups, file verified OK
- Team 102 (dirI): 217 new groups, file verified OK
- Team 71 (music): 7 new groups, file verified OK
- Team 95 (dirB): 53 new groups, file verified OK
- Team 92 (aggregators): 37 new groups, file verified OK
- Team 65 (sarkari): 36 new groups, file verified OK
- Team 69 (betting): 221 file entries, verified OK (many /invite/ form; merge dedups by code)
- Team 103 (dirJ): 300 new groups, file verified OK
- Team 85 (quora): 4 new groups, file verified OK
- Team 56 (pakistan): 36 new groups, file verified OK
- Team 87 (telegram): 16 new groups, file verified OK
- Team 80 (realestate2): 5 new groups, file verified OK (+3 /invite/ links recovered from team report)
- Team 74 (earning): 27 new groups, file verified OK
- Team 76 (matrimonial): 1 new group, file verified OK
- Team 94 (dirA): 2697 new groups, file verified OK
- Team 79 (business2): 5 new groups, file verified OK
- Team 62 (western): file has 155 entries, verified (overlap check above)
- Team 78 (islamic2): 196 entries, verified (overlap check above)
- Team 66 (study): 19 new groups, file verified OK
- Team 101 (dirH): 772 entries, verified (overlap check above)

## MERGE COMPLETE (2026-10-18 ~01:10 PKT)
- Merged 50 team files (team54..team103 + team80-recovered-invite.json, which contributed 0 — its 3 codes were already covered) via scraped/merge_teams54-103.py
- Merge rules: dedup by invite CODE (chat.whatsapp.com/invite/CODE treated identical to /CODE), canonical invites https://chat.whatsapp.com/CODE, junk names cleaned (URL fragments), no source field stored
- ADDED: 6,694 new unique groups | skipped 538 cross-team/existing dup codes
- FINAL groups.json count: 67,938 (was 61,245)
- Verification: 0 missing codes; 0 dup codes after removing 1 pre-existing duplicate pair (code F10hvBAf3672JpkWzO99Sj, entries idx 2971/51965)
- Pre-existing data-quality note (NOT from this operation): 91 legacy entries have non-canonical invite formats (e.g. /invite/ form, one 'PASTE_LINK_HERE' placeholder at idx 882) — flagged for the weekly link-checker cron
