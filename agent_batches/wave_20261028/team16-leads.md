# team16 — Sports + Gaming — wave 20261028

## Sources / pages scraped
- grouplink.com.in/active-sports-whatsapp-group-links-2026/ — 52 codes, all already in the dedupe union (0 fresh)
- newgrouplinks.pk/cricket-whatsapp-group-links/ — 24 codes, 18 fresh (10 verified, 8 pending)
- techapkzone.com/free-fire-whatsapp-group-links — 15 codes, all already in the dedupe union (0 fresh)
- bgmi.in/bgmi-whatsapp-group-links/ — fetched 0 bytes, no codes extracted (retry lead)
- asiamediajournal.com/gaming-whatsapp-group-links/ — fetched 0 bytes, no codes extracted (retry lead)
- minidea.co.in/cricket-whatsapp-group-link/ — 2 codes, 0 fresh
- wglfinder.com/cricket-whatsapp-group-link/ — 12 codes, 6 fresh (2 verified, 4 pending)
- appgrouplink.com/football-whatsapp-group-links/ — page fetched but invite links are obfuscated/redirected, 0 direct codes extracted (live-browser lead)
- whatzgrouplink.com/premier-league-whatsapp-group-link/ — page fetched but invite links are obfuscated/redirected, 0 direct codes extracted (live-browser lead)
- Search-snippet tournament document (Sportity delegates PDF) — 1 fresh sports-delegates code, verified
- NOT reused, per task: wave 20261027 team24/team25 pages (football trialists, Dallas cricket club, university futsal network, Unstop BGMI/Brawl Stars pages, DGL Sri Lanka PUBG page), all wave 20261027 manifest sources, and all retired sources (whatslinkhub.com, elsabagh.com, whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, groupda.com, groupizo.com sitemaps). No Unstop page was used at all.
- groups.json, generate.py output and ~/workspace/wgl-deploy/ were NOT touched.

## Counts
- Candidates found: 105 (104 codes extracted from directory pages + 1 Sportity code)
- Verified: 13 (all Sports: 12 cricket groups + 1 sports-delegates group; 0 Gaming — every fresh gaming/esports code found was already in the union)
- Pending (unverified, in team16-unverified-pending.json): 12
- Dedupe drops: 80 (candidates whose invite code was already in dedupe_union_codes.txt)
- Porn drops: 0 (no hard-porn titles among candidates; no girls/friendship groups were dropped)
- Internal duplicates: 0; verified-vs-pending overlap: 0

## Verification notes
- Each fresh candidate was checked with spaced curl (about 1–2 s between checks, browser-like User-Agent) against https://chat.whatsapp.com/<code>.
- Verified = HTTP 200 + a non-empty, meaningful og:title, used verbatim as the group name (HTML entities decoded).
- Pending = HTTP 200 but og:title empty on two separate fetches (11 codes), plus 1 code whose og:title was the bare word "Welcome" while its listing name was "CRICKET Welcome". Pending names are the directory listing names, NOT og:titles — re-verify before any merge.
- Country: PK where the title carries a Pakistan flag / "Pakistan" / PSL, PT for the Lagos delegates group (Portugal flag in title), otherwise International.

## Next-pass leads
- appgrouplink.com football page and whatzgrouplink.com Premier League page: resolve their obfuscated/redirected "Join" links in a live browser to recover football/eFootball codes.
- bgmi.in and asiamediajournal.com gaming pages: retry fetching (both returned 0 bytes this run).
- groupswp.com sports collections (Pro Kabaddi, Kerala Blasters, RCB, CSK, IPL, Virat Kohli, MS Dhoni, Rohit Sharma) — a fresh directory not used in wave 20261027; not scraped this run for time, worth a dedicated pass.
- Search-snippet BGMI tournament/YouTube descriptions carry truncated codes (shown with "...") — only usable if the full code is recovered from the source page itself.
