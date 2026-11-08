# TEAM BRIEF — WhatsGroupLinks scrape wave 20261101

You are one scrape team in a ~37-team parallel wave. You work INDEPENDENTLY and write ONLY your own output files. Do NOT merge anything into groups.json.

## Your files (all in ~/workspace/whatsapp-groups-site/agent_batches/wave_20261101/)
1. `teamNN-<desc>.json` — JSON ARRAY of verified items (exact filename given in your assignment).
2. `teamNN-unverified-pending.json` — optional JSON array of plausible-but-unverified items (transport failures / rate limits), same schema, plus a "note" field explaining why unverified. These are retried next wave, NOT merged this wave.
3. `teamNN-leads.json` — optional JSON array of new-source LEADS (fresh directory domains/URLs discovered but not yet scraped), each: {"domain": "...", "url": "...", "why": "..."}.

## Item schema (EXACT)
{"name": str, "category": str, "description": str, "image": str, "invite": "https://chat.whatsapp.com/<CODE>", "country": "XX"}

- name: the group's real title (from the source page or the verified og:title). No source names, no "WhatsApp Group" boilerplate.
- category: map to ONE of these canonical categories (pick closest): Community & Social, Education, Jobs, Entertainment, Gaming, Business, Friendship, Online Earning, Sports, Islamic, Technology, News, Health, Buy Sell, Finance, Shopping, Travel & Tourism, General Chat, Religion, Crypto, Fashion, Social Media, Study Groups, Language Learning, Food & Drinks, Movies, Music, Comedy & Funny, Poetry, Scholarships, Family, Dating & Social, Auto & Vehicles, Real Estate, Pets & Animals, Spiritual, Quotes & Jokes, Other.
- description: 1-2 sentences, keyword-rich (use the group's topic + category + country words). NEVER mention the source site/domain.
- image: "" (leave empty unless the source page gives a direct group image URL from whatsapp.net — never hotlink the source site's images).
- invite: "https://chat.whatsapp.com/<CODE>" with the REAL 22-char code. NO /invite/ channel-format links (those are channels, not groups).
- country: ISO 2-letter code of the group/source country (e.g. PK, IN, NG, ID, EG, BR). Use "XX" only if truly unknown.

## VERIFICATION (mandatory, every single item)
1. Code quality first: the code MUST be exactly 22 alphanumeric characters ([A-Za-z0-9]{22}). Truncated/garbled codes (8/11/20/21/24-char or cut-off) are ALWAYS dead — SKIP without curling.
2. Liveness check — curl the invite URL with a full Chrome UA and read og:title:
   curl -sL --max-time 25 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" "https://chat.whatsapp.com/<CODE>"
   Extract `<meta property="og:title" content="...">`, HTML-unescape it, strip whitespace.
   - INCLUDE ONLY IF the title is NON-EMPTY. Live groups return their real group name; dead links return an EMPTY og:title. (Dead pages also return HTTP 200, so status code alone proves nothing.)
   - A curl TRANSPORT failure (timeout/DNS) is NOT a dead verdict — put the item in teamNN-unverified-pending.json with note "transport failure".
   - Rate discipline: pause ~0.5–1s between checks; if you hit HTTP 429, STOP verifying for this wave and bank the rest as pending with note "rate-limited" (resume point included).
3. Use the og:title as the group name when the source page has no clear title (it is the group's real title).

## DEDUPE (mandatory) — THREE exclusion sources
Build the exclusion union yourself from ALL THREE:
  (a) every code from the "invite" field of ~/workspace/whatsapp-groups-site/groups.json (38,722 groups), PLUS
  (b) every code in ~/workspace/whatsapp-groups-site/.existing_codes.json (~74k codes), PLUS
  (c) every code in the VERIFIED outputs of the previous wave: ~/workspace/whatsapp-groups-site/agent_batches/wave_20261031/team*-<desc>.json (all teamNN-*.json files that are verified-item arrays — include team13 shards; EXCLUDE *-leads.json and *-unverified-pending.json files). These 1,904 codes were banked but are NOT yet in groups.json — re-adding them now would create duplicates at merge time.
Exclude EVERY code already in that union — each link is added ONCE, ever. Dedup within your own batch too.

## HARD CONTENT RULES
- BLOCK hard-porn/xxx/escort/call-girl/nudes: if the name/description contains porn, pornhub, xxx, nude, sex video, escort, call girl, fuck, dick, pussy, boobs, anal, or adult emojis 🥵🍆🍑🔞💦👅👄💋, or is a clearly sexual 18+ title — DROP it. For Brazil/Spanish/LatAm sources: FILTER PORN HARD — these niches are porn-saturated.
- Girls/friendship/dating-social groups are ALLOWED — never remove them.
- NO source names or source URLs anywhere (not in name, description, image, country, or any field).
- NO personal info (no phone numbers, emails, personal names as group names).
- Fake/placeholder codes are always dead — never invent or "repair" a code.

## RETIRED / EXHAUSTED SOURCES — NEVER use these (0 yield, dead, or poisoned)
groupor.link ENTIRELY (harvested last wave — do not re-scrape any groupor.link URL).
whatsgroulink.com, whatzgrouplink.com, whatslinkhub.com (parked), elsabagh.com (POISONED — fake synthesized codes, never trust), grouplinkshare.com non-Bangladesh pages, grouplink.com.in (incl. Malayalam Islamic page), whts.club, wagroupslink freelance listicles, whatsgroulinks.com poetry, dubai-forever.com, satyainpoland.com, sg.theasianparent.com, universidadesecuador vanity codes, team08 numeric-pattern domains, activewagroup.com, whtsgroupslinks.com / scribd.online / dailygrouplinks.com (shared harvested pool), whtspgrouplink SG/MY/Mekong pages, freewagroup.com sports/news AND freewagroup.com Spanish dir, groupsnest.com technology, techapkzone.com gaming, whatgroups.com (~99% dead), whatspgroupslink variants (covered), meetup.com Amsterdam/Oslo/Copenhagen/Berlin/Gothenburg/Melbourne pages (covered), Ecuador/Uruguay/Paraguay/Colombia/Medellin/Bogota directories (covered), groupjoin.link gaming tag pp.1-40 (covered), groupjoin.link Indonesia tag pp.1-220 EXCEPT the gap pages listed for team04 (covered), groupjoin.link pubg/freefire/bgmi/gamer tags (exhausted), groupjoin.link Kenya pp.3-4 / UK ?page=2 / Nigeria pp.1-8 / Indonesia city tags / EU tags / Balkan tags / Saudi-Gulf directories (old country-route listings, covered under old scheme), kompak.or.id (scraped), banjirembun.com (scraped), carakami.com (scraped via team04? — verify before re-scraping), groupsnext.com/.net/.org/.io/.app/.co/.xyz, groups-next.com/.net, groupnext.com, thenextgroups.com (all dead domains), igrupos.com (CAUTION — do NOT scrape without explicit parent approval), virenial.com / tutorial1001.com / fulusnesia.com (porn-saturated), quizlandia.club (low-priority, mostly /invite/ channel links), linkgrupwa.com (low priority, 2022-dated), grouplinkshare Bangladesh (1 dead page only).

## WORKING METHOD
- Prefer curl + regex for server-side pages (fastest). Use browser_search/browser_open for discovery and JS-heavy pages. Do NOT use the live-browser route (you cannot launch browser tasks); if a source is JS-gated and text-fetch fails, record it as a lead and move on.
- Scope your assignment to finish in reasonable time. If a source is slow, BANK the verified results you have, note the resume point in your leads file, and stop — do not stall the wave.
- Write your output JSON as a valid JSON array. Count your verified items at the end.
- Do NOT touch groups.json, .existing_codes.json, or any other team's files.

## groupjoin.link technical notes (UPDATED Nov 1 — old notes are WRONG)
- PAGINATION SCHEME CHANGED. The old `/tag/<tag>/page/<N>/` form now 404s, and the old country routes (`/usa`, `/uk`, `/nigeria`, `/kenya`) now 404 too.
- WORKING scheme: `https://www.groupjoin.link/tag/<tag>/?page=N&limit=20&safeSearch=blur` (with or without trailing slash; the server sometimes 308-redirects to the no-slash form — follow redirects with curl -L). 20 records per page.
- Category routes: `/category/education`, `/category/business`, `/category/entertainment`, `/category/gaming`, `/category/money`, `/category/marketing`, `/category/online-shopping`. NEVER scrape `/category/adult` (porn).
- Listing HTML embeds the invite link directly: `chat.whatsapp.com/<22-char-code>`. Extract with regex. `/invite/` records are CHANNELS — always excluded.
- Detail pages live at `/group/<id>` if you need a group's real name.
- Bounds discovery: page past the last real page returns 200 with ~0 records. Check empirically (e.g. /tag/usa pages 1-2 have records, page 4 is empty).
- Indonesia tag has exactly 220 pages; pages beyond 220 return nothing (verified Oct 31).
- Rate discipline: pause ~0.5–1s between listing fetches; deep pages may 429 — bank resume point and stop.

## Your assignment
Your coordinator will give you one assignment (teamNN filename + slice). Stay inside that slice — do not redo other teams' sources. If your slice is exhausted early, record the exhaustion in your leads file and stop; do not poach.
