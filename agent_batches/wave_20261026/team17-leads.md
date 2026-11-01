# team17 — NAME-ONLY LEADS (NOT FOR MERGE)

NO invite codes are recorded in this file. NOTHING here passed verification and NOTHING here may be merged into groups.json until a live-browser pass clicks each Join link, captures the real chat.whatsapp.com code, verifies it (HTTP success + non-empty og:title via curl), and dedupes it against groups.json / .existing_codes.json.

Why no codes: (1) curl egress is down in this environment — the egress proxy CONNECT tunnel times out for every host tested (example.com, directory site, chat host; HTTP 000), so the task-required curl verification cannot run here. (2) On both usable directory sites the invite code sits behind a Join button / Join link, not in page text, and codes were NOT invented or guessed. (3) One chat-invite text-fetch attempt was denied (403) and, per instruction, was NOT retried through any other tool; its code is deliberately NOT recorded anywhere in this team's outputs.

## Source 1: joingroupslink.com (genuinely new — not in the banned list, not found in wave_20261023b/20261024/20261025 files or scrape log)
Categories checked: Cricket (2 listings), Football (1), Movies & Entertainment (5), PUBG (1). Free Fire and Music category pages render with no listings in text view despite a count of 1 each — recheck on live-browser pass.

- Pakistan vs England | Sports | Cricket match discussion group for Pakistan vs England fans.
- AJ Cricket Reports~ | Sports | Cricket discussion group.
- Football | Sports | Football fan discussion group.
- Videos WhatsApp Group | Entertainment | Entertainment video discussion group.
- Masti Group | Entertainment | Fun and entertainment discussion group.
- Company Movie's | Entertainment | Movie discussion group.
- MOVIE'S Entertainment's Group | Entertainment | Movie and entertainment discussion group.
- PUBG group | Gaming | PUBG squad and strategy discussion group.

Excluded from this source (not listed as leads): 1 Movies & Entertainment listing whose name is a suggestive 'girl video viral' title — dropped as borderline under the content rules. All homepage listings outside the Entertainment/Gaming/Sports slice (friendship, love, girls, news, technology, etc.) were skipped, including suggestive out-of-slice listings, which are not reproduced here.

## Source 2: asiamediajournal.com — Best Gaming WhatsApp Group Links page (genuinely new — not in the banned list, not found in prior wave files)
49 gaming names seen in page text; codes are behind Join Here links only. Note: two Join links are reused for two names each in page order (Gaming Points reuses the Bgmi paid scrim link; PUB G UC reuses the Gamer Unity link), so distinct codes will be fewer than names — dedupe by code, not by name, on the live-browser pass.

- FLANKY GAMING | Gaming | Gaming/sports discussion group.
- Gaming from Worldwide | Gaming | Gaming/sports discussion group.
- Gamers arena | Gaming | Gaming/sports discussion group.
- FootBall Gamers | Sports | Gaming/sports discussion group.
- Gaming World | Gaming | Gaming/sports discussion group.
- Hackers club | Gaming | Gaming/sports discussion group.
- Bgmi paid scrim | Gaming | Gaming/sports discussion group.
- Gamer Unity | Gaming | Gaming/sports discussion group.
- PUBG Mobile | Gaming | Gaming/sports discussion group.
- Gaming Points | Gaming | Gaming/sports discussion group.
- PS4 Gaming | Gaming | Gaming/sports discussion group.
- BGMI YOUTUBE INDIA | Gaming | Gaming/sports discussion group.
- Gamers Heaven | Gaming | Gaming/sports discussion group.
- AK GamerX | Gaming | Gaming/sports discussion group.
- Gamers Zone | Gaming | Gaming/sports discussion group.
- GAMING DRAGONS | Gaming | Gaming/sports discussion group.
- PUB G UC | Gaming | Gaming/sports discussion group.
- PTV Sports | Sports | Gaming/sports discussion group.
- Indian Gamer Adda | Gaming | Gaming/sports discussion group.
- PUBG | Gaming | Gaming/sports discussion group.
- Apps and Games | Gaming | Gaming/sports discussion group.
- Indian Gamers | Gaming | Gaming/sports discussion group.
- LUDO | Gaming | Gaming/sports discussion group.
- Gaming Adda | Gaming | Gaming/sports discussion group.
- TEAM CRF daily scrims | Gaming | Gaming/sports discussion group.
- Gaming King | Gaming | Gaming/sports discussion group.
- GTA 5 heist & missions | Gaming | Gaming/sports discussion group.
- JF17 Gamers | Gaming | Gaming/sports discussion group.
- PES HERO7 | Gaming | Gaming/sports discussion group.
- TheDKGamer | Gaming | Gaming/sports discussion group.
- Total gamer | Gaming | Gaming/sports discussion group.
- All Predator Boys | Gaming | Gaming/sports discussion group.
- Mini Militia Team | Gaming | Gaming/sports discussion group.
- Supermall | Gaming | Gaming/sports discussion group.
- alone._bgm_. | Gaming | Gaming/sports discussion group.
- GAMEING BOYS | Gaming | Gaming/sports discussion group.
- Simba gaming yt hack | Gaming | Gaming/sports discussion group.
- WIXZERD GAME | Gaming | Gaming/sports discussion group.
- Dilip FF Killer | Gaming | Gaming/sports discussion group.
- Gamer | Gaming | Gaming/sports discussion group.
- MYCON GAMING | Gaming | Gaming/sports discussion group.
- Tech Gamer gang | Gaming | Gaming/sports discussion group.
- Trusted Ludo King Group | Gaming | Gaming/sports discussion group.
- Gamming | Gaming | Gaming/sports discussion group.
- Ludo King Money Maker | Gaming | Gaming/sports discussion group.
- Ps4 Digital Games | Gaming | Gaming/sports discussion group.
- AK GAMING | Gaming | Gaming/sports discussion group.
- FF Gaming | Gaming | Gaming/sports discussion group.
- Pubg Lover | Gaming | Gaming/sports discussion group.

Excluded from this source: 1 crypto/mining listing (out of slice) — not listed as a lead.

## Sources tried and abandoned (no usable items)
- digitalnamanji.com/whatsapp-group-link/ — genuinely new domain, but the page is a guide only: it names gaming/entertainment/sports categories in prose and lists NO actual group names or invite links. No leads.
- findgroups.net — genuinely new domain, but the homepage renders as a coupon/deal listing with no group names in text view; no slice listings extractable. Abandoned.
- globalwpgroups.com — text-fetch failed (unresolvable); per instruction this request was NOT retried. Treated as uncheckable, not as proven dead. No leads.
- Banned/retired sources were NOT scraped: grouplink.com.in, whatsonly.com, whtsagrouplinks.com, whatzgrouplink.com, 77links.com, bgmi.in, groupsnest.com, wagroupnest.com and all other domains on the task banned list. groupwa.link /sex/ and /xxx/ pages were not visited.

## Counts
- Candidates examined by name: 8 (joingroupslink) + 49 (asiamediajournal) = 57 name-only leads
- Verified kept: 0 (curl verification impossible — egress proxy CONNECT timeout, HTTP 000)
- Unverified-pending JSON items: 0 (no codes were captured, so no code-bearing pending items were fabricated)
- Porn-blocked items in outputs: 0 (1 borderline suggestive title excluded, 1 crypto item excluded as out-of-slice)
