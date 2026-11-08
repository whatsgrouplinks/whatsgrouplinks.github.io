# TEAM BRIEF — WhatsGroupLinks scrape wave 20261102

You are ONE scrape team in a 36-team parallel wave. Work INDEPENDENTLY. Read this whole brief, then your assignment (team number, slice, filenames) from your coordinator message. Stay inside your slice — never redo another team's slice, never poach.

## Your output files (ALL in `~/workspace/whatsapp-groups-site/agent_batches/wave_20261102/`)
1. `teamNN-<desc>.json` — JSON ARRAY of VERIFIED items only (exact filename given in your assignment).
2. `teamNN-unverified-pending.json` — optional JSON array of plausible-but-unverified items (same schema + a "note" field: "transport failure" / "rate-limited" / why). Retried next wave, NOT merged this wave.
3. `teamNN-leads.json` — optional JSON array of NEW-SOURCE leads (fresh directory domains/URLs discovered but not scraped, incl. resume points), each: {"domain","url","why"}.

## Item schema (EXACT — every field)
{"name": "Real Group Name", "category": "Education", "country": "PK",
 "description": "One to two sentence ORIGINAL English description of the group (no URLs, no site names).",
 "invite": "https://chat.whatsapp.com/<CODE>", "image": ""}

- name: the group's real title (source page or the verified og:title). Never a URL, never "https://", never source boilerplate.
- category: ONE of exactly: Sports, Gaming, Jobs, Education, Entertainment, Friendship, News, Islamic, Business, Finance, Buy-Sell, Health, Community, Technology, Crypto, Travel, Music, Movies, Food, Pets, Funny, Girls, Regional, Other. Map to the closest.
- country: 2-letter ISO code of the group's country (PK, IN, NG, ID, EG, BR...). Use "International" ONLY if genuinely unknown.
- description: 1-2 sentences, original English, keyword-rich (topic + category + country words). NEVER mention the source site/domain. No URLs.
- invite: "https://chat.whatsapp.com/<CODE>" with the REAL code. NEVER invent or "repair" a code.
- image: "" (empty) unless the source page gives a direct group image URL from whatsapp.net — never hotlink the source site's images.

## VERIFICATION (mandatory — every single item)
1. Code quality: code must be 20-24 alphanumeric chars ([A-Za-z0-9]{20,24}). Anything else (truncated, garbled, cut-off) is dead — SKIP without curling.
2. ONLY chat.whatsapp.com group links. NEVER whatsapp.com/channel/ links (channels don't belong). NEVER chat.whatsapp.com/invite/<code> (channel format).
3. Liveness check — curl the invite URL with a full Chrome UA and read og:title:
   curl -sL --max-time 25 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" "https://chat.whatsapp.com/<CODE>"
   Extract `<meta property="og:title" content="...">`, HTML-unescape, strip whitespace.
   - INCLUDE ONLY IF og:title is NON-EMPTY. Live groups return their real name; dead links return HTTP 200 with EMPTY og:title — status code alone proves nothing.
   - TRANSPORT failure (timeout/DNS) is NOT a dead verdict → teamNN-unverified-pending.json with note "transport failure".
   - Use og:title as the group name when the source page has no clear title.
4. Rate discipline: pause ~0.5-1s between checks; on HTTP 429 STOP verifying for this wave and bank the rest as pending with note "rate-limited" (include resume point).

## DEDUPE (mandatory)
Load the exclusion union ONCE: `~/workspace/whatsapp-groups-site/agent_batches/wave_20261102/dedupe_union.json` (JSON array of invite codes — groups.json + .existing_codes.json + previous-wave verified outputs, ~84k codes). Extract the code from every candidate invite URL with regex `chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})` and EXCLUDE any code already in the union. Each link is added ONCE, ever. Also dedupe within your own batch. Do NOT touch groups.json or .existing_codes.json.

## HARD CONTENT RULES
- DROP ON SIGHT (hard porn/xxx): name/description containing porn, pornhub, xxx, nude, sex video, escort, call girl, fuck, dick, pussy, boobs, anal, or adult emojis (🥵🍆🍑🔞💦👅👄💋), or clearly sexual 18+ titles. Log your porn-drop count in your final report.
- Girls/friendship/dating-social groups are ALLOWED — never remove them.
- NO source names or source URLs anywhere (name, description, image, country — no field).
- NO personal info (no phone numbers, emails, personal names as group names).

## RETIRED / EXHAUSTED — NEVER scrape these (your assignment may name a narrow exception; only that exception applies)
whatslinkhub.com, elsabagh.com (POISONED — fake synthesized codes, never trust), whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, grouplink.com.in, techapkzone.com, freewagroup.com, groupsnest.com, Saudi/Gulf directories (fresh scraping), groupjoin.link Kenya pp.3-4, groupjoin.link USA ?page=3+ / UK ?page=2+ / Nigeria ?page=9+ / UG-GH deep pages, grouplinkshare.com non-Bangladesh pages, whatzgrouplink.com, whatsgroulink.com, whatsapp-group-link.com, whtsagrouplinks.com (general — see team05 exception), groupizo.com, groupwa.link, Philippines/Vietnam/Thailand dirs, whatstele.com, activewagroup.com, 77links.com, wpgroup.in, groupio.app, dubai-forever.com, satyainpoland.com, sg.theasianparent.com, universidadesecuador, whts.club, whatsgroulinks.com, groupjoin.link Indonesia city tags, groupjoin.link EU tags, groupjoin.link Balkan tags, groupor.link Adult/18+ category.

## WORKING METHOD
- Fetch listing pages with curl / python requests / browser.open ONLY. You CANNOT use a live browser (no browser.browse, no clicking Join buttons). If codes hide behind Join buttons or Cloudflare/JS, bank name-only leads in teamNN-leads.json and move on — never guess codes.
- Prefer curl + regex for server-rendered pages. Use browser.search for discovery of new directories.
- Time budget: if sources are slow, BANK the verified results you have, note the resume point in teamNN-leads.json, and STOP. Do not stall the wave.
- Write valid JSON arrays. Count your verified items. Report: verified count, pending count, leads count, porn-drop count, and any exhaustion/resume point.
- groupjoin.link technical notes: pagination `https://www.groupjoin.link/tag/<tag>/?page=N&limit=20&safeSearch=blur` (follow redirects with curl -L). 20 records/page. Listing HTML embeds `chat.whatsapp.com/<code>` directly. `/invite/` records are CHANNELS — always excluded. Category routes: /category/education, /category/business, /category/entertainment, /category/gaming, /category/money, /category/marketing, /category/online-shopping. NEVER /category/adult. Detail pages at /group/<id>; API `https://api.groupjoin.link/groups/<id>` resolves the code. Past-last-page returns 200 with ~0 records — discover bounds empirically.
- Do NOT merge anything into groups.json. Do NOT touch other teams' files.
