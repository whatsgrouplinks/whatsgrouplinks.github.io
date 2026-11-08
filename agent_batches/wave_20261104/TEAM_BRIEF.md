# TEAM BRIEF — WhatsGroupLinks scrape wave 20261104

You are ONE scrape team in a 40-team parallel wave. Work INDEPENDENTLY. Read this whole brief, then your assignment (team number, slice, filenames) from your coordinator message. Stay inside your slice — never redo another team's slice, never poach.

## Your output files (ALL in `~/workspace/whatsapp-groups-site/agent_batches/wave_20261104/`)
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
3. Liveness check — curl the invite URL with a full Chrome UA and read og:title.
   SPEED FINDING: use a keep-alive `requests.Session()` (persistent connection) — og:title checks run ~0.5-0.6s vs ~9s with fresh curl connections through the proxy (identical results). Rebuild the session on error. 45-60s per-request timeouts.
   Extract `<meta property="og:title" content="...">`, HTML-unescape, strip whitespace.
   - INCLUDE ONLY IF og:title is NON-EMPTY. Live groups return their real name; dead links return HTTP 200 with EMPTY og:title — status code alone proves nothing.
   - TRANSPORT failure (timeout/DNS) is NOT a dead verdict → teamNN-unverified-pending.json with note "transport failure".
   - Use og:title as the group name when the source page has no clear title.
4. Rate discipline: 30+ parallel requests are fine with keep-alive sessions; on HTTP 429 STOP verifying for this wave and bank the rest as pending with note "rate-limited" (include resume point).

## DEDUPE (mandatory)
Load the exclusion union ONCE at start: `~/workspace/whatsapp-groups-site/agent_batches/wave_20261104/dedupe_union.json` (87,360 codes — groups.json + .existing_codes.json + Nov-3 banked files). Extract the code from every candidate invite URL with regex `chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})` and EXCLUDE any code already in the union. Each link is added ONCE, ever. Also dedupe within your own batch. Do NOT touch groups.json or .existing_codes.json. Parent re-dedupes everything regardless — if a mid-wave union change confuses you, check at start and parent handles the rest.

## HARD CONTENT RULES
- DROP ON SIGHT (hard porn/xxx): name/description containing porn, pornhub, xxx, nude, sex video, escort, call girl, fuck, dick, pussy, boobs, anal, bokep (Indonesian porn), or Urdu/Hindi sexual terms like مزا دینے / مزہ دینے (video-call solicitation), or adult emojis (🥵🍆🍑🔞💦👅👄💋), or clearly sexual 18+ titles. Log your porn-drop count in your final report.
- Minors-targeted dating/friendship groups: EXCLUDE, note in leads (do not write to verified file).
- Satta/numbers-gambling, HYIP/scam-looking, money-mule ("PayPal Receiver and Loader" type), phishing-flavored items: EXCLUDE, note in leads or final report.
- Girls/friendship/dating-social groups are ALLOWED — never remove them.
- NO source names or source URLs anywhere (name, description, image, country — no field).
- NO personal info (no phone numbers, emails, personal names as group names).

## RETIRED / EXHAUSTED — NEVER scrape these (your assignment may name a narrow exception; only that exception applies)
whatslinkhub.com, elsabagh.com (POISONED — fake synthesized codes, never trust), whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, grouplink.com.in, techapkzone.com, freewagroup.com, groupsnest.com, whatzgrouplink.com, whatsgroulink.com, whatsapp-group-link.com, whtsagrouplinks.com, groupizo.com, groupwa.link (except team18 appgrouplink exception), Philippines/Vietnam/Thailand dirs, whatstele.com, activewagroup.com, 77links.com, wpgroup.in, groupio.app, dubai-forever.com, satyainpoland.com, sg.theasianparent.com, universidadesecuador, whts.club, whatsgroulinks.com, groupjoin.link Indonesia city tags, groupjoin.link EU tags, groupjoin.link Balkan tags, groupor.link Adult/18+ category, elyex tag archives, groupmaster.app, fresh sports listicles (saturated), groupjoin.link USA ?page=4+ / UK ?page=3+ / Nigeria ?page=9+ / UG-GH deep pages, groupjoin.link Kenya pp.3-4, groupjoin.link /tag/sports-and-fitness/ (EMPTY — use /category/sports-and-fitness/), grouplinkshare.com non-Bangladesh pages, Saudi/Gulf dirs (fresh scraping; team39's Arabic-residual slice is the one exception), whtspgrouplink SG/MY/Mekong, groupssor.com, grupbul.com, groupler.me (all JS-gated → parent browser leg, do not attempt via text fetch).

## WORKING METHOD
- Fetch listing pages with curl / python requests (keep-alive session) / browser.open ONLY. You CANNOT use a live browser (no browser.browse, no clicking Join buttons). If codes hide behind Join buttons or Cloudflare/JS, bank name-only leads in teamNN-leads.json and move on — never guess codes.
- groupjoin.link technical notes: pagination `https://www.groupjoin.link/tag/<tag>/?page=N&limit=20&safeSearch=blur` (follow redirects with curl -L). 20 records/page. Listing HTML embeds `chat.whatsapp.com/<code>` directly. `/invite/` records are CHANNELS — always excluded. Category routes: /category/education, /category/business, /category/entertainment, /category/gaming, /category/money, /category/marketing, /category/online-shopping. NEVER /category/adult. Detail pages at /group/<id>; API `https://api.groupjoin.link/groups/<id>` resolves the code. Past-last-page returns 200 with ~0 records — discover bounds empirically.
- groupda.com was DOWN (DNS sinkholed) during Nov 3 — only team01's slice retries it; everyone else stays off it.
- Groupor.link technique: SSR flight-data route exposes group codes server-side.
- Time budget: if sources are slow, BANK the verified results you have, note the resume point in teamNN-leads.json, and STOP. Do not stall the wave.
- Write valid JSON arrays. Count your verified items. Report: verified count, pending count, leads count, porn-drop count, and any exhaustion/resume point.
- Keep all scratch inside the wave directory — /tmp is wiped mid-run by another process.
- Do NOT merge anything into groups.json. Do NOT touch other teams' files.
