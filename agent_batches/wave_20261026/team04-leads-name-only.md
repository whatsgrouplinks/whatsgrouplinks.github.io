# Team04 — name-only leads (NO codes extracted, NO items verified) — wave 20261026

## Blocker (why 0 yield)
- Sandbox shell curl to directory sites and to chat.whatsapp.com timed out repeatedly (exit 28).
- Text-fetch of the directory pages works, but it hides full invite URLs (only the domain is shown).
- One attempt to open a directory outlink to an invite page was rejected upstream (HTTP 403) and, per instruction, was NOT retried in any form (no other invite was opened or fetched, via any tool).
- Therefore NO invite code was extracted, invented, or verified by this team. No item is claimed verified or unverified-pending with an invite URL.

## CORRECTION (from a late background grep, after the first report): activewagroup.com was ALREADY reviewed in wave_20261025
- wave_20261025 manifest / team notes show activewagroup.com reviewed by teams 09, 10, 28, 31, 48 and 50 (name-only leads, plus team48 verified regional items from it). It is therefore NOT a genuinely new source for this wave, and the earlier 'new source' claim is withdrawn. The BD/NP/LK pages below are still recorded as name-only leads, but a future pass must check them against the wave_20261025 team48 verified set by CODE, not by name, before any reuse.
- activewagroup.com — Sri Lanka / Nepal / Bangladesh listing pages (updated 2026-10-23).
  - Sri Lanka page: https://activewagroup.com/sri-lanka-whatsapp-group-links/
  - Nepal page: https://activewagroup.com/nepal-whatsapp-group-links/
  - Bangladesh page: https://activewagroup.com/bangladesh-whatsapp-group-links/
- NOTE: this site shares the same group-name template as the retired wagroupnest.com family (many names repeat across its country pages, e.g. "Only girls club", "CHAT GPT", "DREAM CHASERS", "Real Jobs Squad"). A future live-browser pass must dedupe by CODE, not by name, and must re-verify every code (og:title + HTTP success) before any merge. Do not trust its "100% Active" claim.

## Other sites tried / abandoned
- linkgic.top (Sri Lanka, 634 active links claimed): homepage text-fetch works but the group list is JS-rendered with no links exposed; shell curl timed out. Name-only lead for a live-browser pass; do NOT treat its homepage claim as verified.
- groplink.com: homepage is a generic guide with no BD/NP/LK group invite listings on the page fetched — abandoned, 0 candidates.
- grupbul.com individual group pages (e.g. Bangladesh+Sri Lanka friendship group): page text gives a description but no invite code in the fetched text — name-only, abandoned for this wave.
- Excluded sites were NOT reused: groupizo, groupda, whatzgrouplink, whatsgroulink, whatsapp-group-link, whtsagrouplinks, groupwhat, groupinvitelink, groupsor, wagroupslink, whatgroups, whgroups.link, whatsonly, groupjoin.link, whatslinkhub, groupsnest, 77links, groupio.app, linkado.app, pkwhatsgrouplinks, wpgroup.in, whatstele, grouplink.com.in, techapkzone, groupwa.link, whatslists, whatsappgrouplink.org, wappgrouplinks, whatsappgroupjoinlinks, grupodewhatsapp, wagroupnest, elsabagh, meraonlineworld. No /sex/ or /xxx/ pages were opened or harvested.

## Clean name-only candidates seen on the three listing pages (for a future live-browser code-extraction pass ONLY — drop any that fail porn filter / code dedupe / verification at that pass)
### Sri Lanka (country LK) — clean names only; excluded here: "Sex vediyo only", "Viral paid videos", "USA Girls lick's"
- Emoney; Tamilori News; 37 U7 News Tamil; Jobs, Ads and Updates Tamil; Al Hassan online Education Centre; Lets go Romania; TECHSTAR TRICKS; Football; ApeAdz; Tamil Islamic Bayan; News for jobs 1; Only girls club; Only girls allowed; Cute Girls & Boys Group; Education news 18; Up-to-date information about Education, Jobs; Sri Lanka WhatsApp Group; CHAT GPT; DREAM CHASERS; Islami Status Group; Electrical engineering; Friend's Group; Help each other honestly; Real Jobs Squad; Gulf Jobs; Gulf Job 21
### Nepal (country NP) — clean names only; excluded here: "USA Girls lick's"
- Global Job; Direct selling; Nepal WhatsApp Group; Trip To Mountain; CHAT GPT; DREAM CHASERS; Only girls club; Only girls allowed; Cute Girls & Boys Group; AIOU STUDENTS 2023 II; Help each other honestly; Real Jobs Squad; Job available group; GENUINE JOBS ONLY; Jobs in Dubai 2024-2025; Gulf Jobs; World wide friends; Online chatting group
### Bangladesh (country BD) — clean names only; excluded here: "USA Girls lick's", "Online betting I'd club" (gambling — flag, do not merge without parent check)
- Islam is beautiful religion of the World; Learn to earn Common Service Centre; Bangladesh Garments Stock Lot Buyers & Sellers; Up-To-Date-News; Today News; Yarn Trade; ENGLISH UNIVERSE; Islamic life; Information Technology Study Group; My study my life; Education news 18; Al Hassan online Education Centre; Entertainment world; Work From Home; Happy shopping; Bangladesh WhatsApp Group; CHAT GPT; Only girls allowed; Cute Girls & Boys Group; Only girls status group

## Dedupe performed
- Built /tmp/codes_team04.txt from groups.json (37,969 codes) + .existing_codes.json (union 73,092 codes). No candidate code was available to check against it, so no dedupe claim is made for the names above.
