# TEAM BRIEF — WhatsGroupLinks scrape wave 20261103

You are ONE scrape team in a ~50-team parallel wave. Work INDEPENDENTLY. Read this whole brief, then your assignment (team number, slice, filenames) from your coordinator message. Stay inside your slice — never redo another team's slice, never poach. wave dir: `~/workspace/whatsapp-groups-site/agent_batches/wave_20261103/`.

## Your output files (ALL in the wave dir)
1. `teamNN-<desc>.json` — JSON ARRAY of VERIFIED items only (exact filename in your assignment).
2. `teamNN-unverified-pending.json` — optional: plausible-but-unverified items (same schema + "note": "transport failure" / "rate-limited" / why). Retried next wave, NOT merged this wave.
3. `teamNN-leads.json` — optional: NEW-SOURCE leads (fresh domains/URLs discovered but not scraped, incl. resume points), each {"domain","url","why"}.

## Item schema (EXACT — every field)
{"name": "Real Group Name", "category": "Education", "country": "PK",
 "description": "One to two sentence ORIGINAL English description of the group (no URLs, no site names).",
 "invite": "https://chat.whatsapp.com/<CODE>", "image": ""}

- name: the group's real title (source page or the verified og:title). Never a URL, never "https://", never source boilerplate.
- category: ONE of exactly: Sports, Gaming, Jobs, Education, Entertainment, Friendship, News, Islamic, Business, Finance, Buy-Sell, Health, Community, Technology, Crypto, Travel, Music, Movies, Food, Pets, Funny, Girls, Regional, Other. Map to the closest.
- country: 2-letter ISO code (PK, IN, NG, ID, EG, BR...). "International" ONLY if genuinely unknown. Never "XX".
- description: 1-2 sentences, original English, keyword-rich (topic + category + country words). NEVER mention the source site/domain. No URLs.
- invite: "https://chat.whatsapp.com/<CODE>" with the REAL code. NEVER invent or "repair" a code.
- image: "" (empty) unless the source page gives a direct whatsapp.net group image URL — never hotlink the source site's images.

## VERIFICATION (mandatory — every single item)
1. Code quality: code must be 20-24 alphanumeric chars ([A-Za-z0-9]{20,24}). Truncated/garbled codes are dead — SKIP without verifying.
2. /invite/ UPDATE (Nov-2 policy correction): `chat.whatsapp.com/invite/<code>` links are sometimes VALID groups rendered by groupjoin.link in channel-style form. Test the PLAIN form `https://chat.whatsapp.com/<code>` with the liveness check below; include it (stored as the plain URL) ONLY if the plain form returns a non-empty og:title. `whatsapp.com/channel/...` links are NEVER allowed.
3. Liveness check — use PYTHON requests (raw curl is unreliable through the egress proxy; browser.open returns 403 on chat.whatsapp.com). Fresh connection per request (requests Session keep-alive breaks through the proxy). Full Chrome UA, timeout ~25s. Extract `<meta property="og:title" content="...">`, HTML-unescape, strip whitespace.
   - INCLUDE ONLY IF og:title is NON-EMPTY. Dead links return HTTP 200 with EMPTY og:title — status code alone proves nothing.
   - TRANSPORT failure (timeout/DNS) is NOT a dead verdict → teamNN-unverified-pending.json with note "transport failure".
   - Use og:title as the group name when the source page has no clear title.
4. Rate discipline: pause ~0.5-1s between checks; on HTTP 429 STOP verifying for this wave and bank the rest as pending with note "rate-limited" (include resume point).

## DEDUPE (mandatory)
Load the exclusion union ONCE: `~/workspace/whatsapp-groups-site/agent_batches/wave_20261103/dedupe_union.json` (JSON array of invite codes, 86,389). Extract codes with regex `chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})` and EXCLUDE any code already in the union. Each link is added ONCE, ever. Also dedupe within your own batch. Do NOT touch groups.json, .existing_codes.json, dedup_codes.pkl, generate.py, or the deploy dir.

## HARD CONTENT RULES
- DROP ON SIGHT (hard porn/xxx): name/description containing porn, pornhub, xxx, nude, sex video, escort, call girl, fuck, dick, pussy, boobs, anal, or adult emojis (🥵🍆🍑🔞💦👅👄💋), or clearly sexual 18+ titles. Never write them to any file. Log your porn-drop count in your final report.
- Money-mule/phishing flavor groups (fake investment "passcodes", PayPal loader, counterfeit currency) — exclude and flag in your report.
- Girls/friendship/dating-social groups are ALLOWED — never remove them.
- NO source names or source URLs anywhere (name, description, image, country — no field).
- NO personal info (no phone numbers, emails, personal names as group names).

## RETIRED / EXHAUSTED — NEVER scrape these (your assignment may name a narrow exception; only that exception applies)
whatslinkhub.com, elsabagh.com (POISONED — fake synthesized codes, never trust), whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, grouplink.com.in, techapkzone.com, freewagroup.com, groupsnest.com, groupizo.com, groupwa.link (general/homepage — see narrow exceptions), whatzgrouplink.com, whatsgroulink.com, whatsapp-group-link.com, groupio.app, dubai-forever.com, satyainpoland.com, sg.theasianparent.com, universidadesecuador, whts.club, whatsgroulinks.com, whatstele.com, activewagroup.com, 77links.com, wpgroup.in, whtsagrouplinks.com sitemap URLs (fully processed Nov 2 — homepage daily-update section ONLY where assigned), groupda.com WP-API categories (all 33 paginated Nov 2 — country pages + new posts still fresh), groupjoin.link Kenya pp.3-4, groupjoin.link USA ?page=4+ / UK ?page=3+ / Nigeria ?page=9+ / UG-GH deep pages (all empty), groupjoin.link Indonesia tag past p.220 (nothing exists), groupjoin.link Indonesia city tags, groupjoin.link old country routes + EU tags (unreachable from this VM), groupjoin.link Balkan tags, groupor.link Adult/18+ category, groupjoin.link /tag/indonesia, PH/VN/TH directories, Spanish directories, Central Asia / Mongolia / Caucasus / Myanmar / Khmer / Lao / Philippines / USA-regional / Caribbean / Baltic slices (structurally exhausted for curl-based scraping), alatekno.com/carakami.com Indonesian code pools (harvested), igrupos.com Mexico/Central America (done Nov 2 — new city slugs ONLY where assigned), UNICAS/Ferrara university groups (done).

## WORKING METHOD
- Fetch listing pages with curl / python requests / browser.open / browser.search ONLY. You CANNOT use a live browser. If codes hide behind Join buttons or Cloudflare/JS, bank name-only leads in teamNN-leads.json and move on — never guess codes.
- Prefer python requests + regex for server-rendered pages. Use browser.search for discovery of new directories.
- Time budget: if sources are slow, BANK the verified results you have, note the resume point in teamNN-leads.json, and STOP. Do not stall the wave.
- Write valid JSON arrays. Count your verified items. Report: verified count, pending count, leads count, porn-drop count, and any exhaustion/resume point.

## SITE-SPECIFIC NOTES
- groupda.com: WP-API at https://groupda.com/wp-json/wp/v2/ (posts endpoint, `after=` date filter for new posts). Country pages follow pattern https://groupda.com/<category>/<country>-<category>-whatsapp-group-link-join-2022/ . Discover country pages via /wp-json/wp/v2/search?search=<country>, /wp-json/wp/v2/posts?search=<country>&per_page=100, or https://groupda.com/sitemap.xml / page-sitemap.xml. Categories were fully paginated Nov 2 — your slice is country pages and/or new posts, never re-do categories.
- groupjoin.link: pagination `https://www.groupjoin.link/tag/<tag>/?page=N&limit=20&safeSearch=blur` (curl -L, 20 records/page). Listing HTML embeds `chat.whatsapp.com/<code>` directly. Detail pages /group/<id>; API https://api.groupjoin.link/groups/<id> resolves the code. Past-last-page returns 200 with ~0 records — discover bounds empirically. Site sets contentRating=18 + nsfw=1 on ALL records (safeSearch blur artifact) — NOT an adult signal; only category_slug='adult' + keyword/emoji block counts.
- igrupos.com: team30's pipeline saved at agent_batches/wave_20261102/team30-scrape.py + team30-finalize.py (READ IT before writing your own scraper).
- Do NOT merge anything into groups.json. Do NOT touch other teams' files.
