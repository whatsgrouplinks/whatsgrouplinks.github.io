# TEAM 22 — groupsor.com slice — 2026-10-29

## Outcome
- Fresh verified: 0
- Pending unverified: 0
- Extracted invite codes: 0

## Page-structure / JS-heaviness findings (groupsor.com)
- `curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" --max-time 25 https://groupsor.com` → **exit 28 (timeout, 0 bytes downloaded)**. No static HTML received at all.
- `browser.open https://groupsor.com` → **failed**: "requires a resolvable public HTTP(S) URL / upstream_fetch_failed". Not retried per runtime instruction.
- Category-page probing was not possible: no verifiable groupsor.com category URL was returned by search, and URL-guessing is prohibited.
- Conclusion: groupsor.com is **inaccessible from this worker via both curl and browser.open**; it is JS-heavy/blocked at the network level from here. Per slice instructions, no JS interaction was forced — no codes were extracted.
- ⚠️ Reputation flag: SEMrush data (pl.semrush.com/website/groupsor.me/overview) shows groupsor's top keywords include "sexy whatsapp group", "tamil sex whatsapp group", "xxx whatsapp group", "whatsapp sex group" — the site carries a large adult/adult-adjacent section. A future team must stay strictly on clean categories and NEVER touch /sex/ /xxx/ /adult/ paths (per standing rule).

## Categories known to exist on the groupsor family (from search snippets, groupssor.com listing 16 categories)
Education, Entertainment, Gaming, Technology, Business, Sports, News & Media, Music, Health & Fitness (+ "View All Categories"). Also advertised: group submission, country sections (India, Pakistan, Nigeria, USA, UK), mobile-friendly.

## Exhausted pages
- https://groupsor.com (root) — curl timeout; browser.open refused.
- No category pages attempted (no verified URLs available).

## Out-of-slice fresh directories (NOT in retired list — suggested for other teams)
- **groupssor.com** — "Groupsor — #1 Free WhatsApp & Telegram Group Links" — claims 964+ active groups, 16 categories, 751 WhatsApp groups, 213 Telegram groups. Not retired. → candidate for a future scraping team.
- **groupor.link** — "Join Active WhatsApp Groups by Category & Country" — category + 180-country hub structure. Not retired. → candidate for a future scraping team.
- edopedia.com/blog/groupsor-alternatives/ — list of groupsor alternatives; useful as a lead source for more directories.
- wayssay.com/groupsor/ — guide article on the groupsor directory; useful background.
- wagroupnest.com — appears in search results but is RETIRED; do not use.

## Notes
- Dedupe files read: groups.json (38,755 groups), .existing_codes.json (73,873 codes) — union not needed, no candidates found.
- Both output JSON files written as empty arrays (valid JSON).
- No adult/suggestive content was scraped; nothing touched /sex/, /xxx/, /adult/ pages.
- A future run with a live-browser agent may succeed where curl/browser.open failed; recommend reassigning groupsor.com to a browser-capable team with the adult-path ban restated.
