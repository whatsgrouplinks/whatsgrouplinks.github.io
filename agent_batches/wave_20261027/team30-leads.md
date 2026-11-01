# Team 30 — Fresh English-language directories + expat/community listicles — wave 20261027

## Counts
- Verified: 0
- Unverified-pending: 20
- Leads / candidates examined: 50+ codes checked against the full dedupe set; 20 fresh, rest already in groups.json / .existing_codes.json and dropped.
- Porn-filter removals: 0 (no hard-porn groups in the fresh set; friendship/social groups retained per rules).

## Files
- `team30-fresh-english-dirs.json` — VERIFIED only: empty list (see verification note below).
- `team30-unverified-pending.json` — 20 fresh candidates, exact item schema, no source names/URLs, no personal info in name/description.
- `team30-leads.md` — this file.

## Pending breakdown (20)
- Dubai (AE): The Chameleon Club Dubai, Badminton For All Al Quoz Jumeirah — 2
- Alicante (ES): Beach Volleyball — 1
- UK farm/garden community (GB): New Farm Models, Farm Fundraising, Seedling Sales, Farm Shop Pop Up, Pick Your Own, Workshops Creative Therapeutic, Growing Flowers/Medicinal Herbs/Natural Dyes, Farm Events/Talks/Film, Environmental Biodiversity, Schools Visits, Cooking/Sharing Meals, Allotment Gardening Chat, School Garden Group, Rock Farm Residency Volunteers — 14
- University societies, other universities (GB/TR): TEKNOFEST Student Society (TR), KCL Nepalese Society, Leeds University Caving Society — 3

## Sources used (fresh, not wave-20261026 / not retired)
- Web searches: "whatsapp group links directory", "best whatsapp groups to join 2026", "join whatsapp groups site", expat/community searches for Dubai, Amsterdam, Alicante, Valencia, Sydney, Toronto, Rome, and hobby searches (gardening, cooking, hiking, running, book clubs).
- Directory pages reviewed for leads: whatgroups.com, wahublink.com, whatsshare.com, groupchatlink.com, 77links.com, whatsgrouply.com, mdecommunity.com.
- Snippet-sourced community pages: Dubai Meetup groups, Alicante/Valencia Activities Meetup pages, Sutton Community Farm update, Rosendale Allotments, Michael Hall garden, SAWA Rock Farm, LSE PPE, University of London Mountaineering, KTO Karatay TEKNOFEST, KCL Nepalese Society, Leeds Caving Society, Medellin Hike Club (dropped on dedupe — see below).

## Excluded / dropped on purpose
- Retired sources NOT used: whatslinkhub, whatsappgrouplink.org, wappgrouplinks, whatsappgroupjoinlinks, grupodewhatsapp, wagroupnest, groupizo, groupda, whatzgrouplink, whatsgroulink, whatsapp-group-link, whtsagrouplinks, groupwhat, groupinvitelink, groupsor.in, wagroupslink, whgroups.link, whatsonly, activewagroup, dubai-forever, satyainpoland, sg.theasianparent, elsabagh, grouplink.com.in, techapkzone, freewagroup, groupsnest, joinnchat, farmersvoice, hubrecipes, theiq.pk, whatsagroupslinks, linkgic, groplink.com, walinking.link, wagroupslink.pro, whatshub.es, gruposwats, ongrupos, grupbul, joingroupslink, asiamediajournal, joingram.in, freshgrouplinks, grouplinksforyou, groupwa.com, grouplinks.in, dailygrouplinks, scribd.online.
- Wave-20261026 excluded pages NOT used: Tbilisi digital-nomad guide, India tech-community pages, Lima/Paris/Madeira expat pages, TU Dresden / HNBGU / Manchester / Bristol / EUI Florence / DPS Numaligarh pages (Bristol Arab Society and EUI Orto codes found in searches were deliberately NOT included).
- Dedupe drops (already in groups.json / .existing_codes.json, union 73,170 codes): Explore Dubai, Dubai Business Community, Badminton Deira, Kaapjag branches (5), Amsterdam expat guilds (2), Alicante main group, Valencia Activities, LSE PPE, UL Mountaineering, Leeds LGBT+ Society, Sheffield Irish Dance, Stellenbosch hiking (2), Fade Fit Run Club, Bikepacking Sydney, Toronto Rouge walk, Sydney Beach Events, Rome Dolce Vita, Medellin Hike Club, and others.

## Verification note — why verified = 0 (important, do not promote pending to verified without re-check)
- Direct curl from this VM timed out for every site tested, including a plain example site (connection timeout after 15s) — VM egress is not usable for WhatsApp verification in this run.
- One browser fetch of a WhatsApp invite returned HTTP 403 access denied, and that request must not be retried through another tool/endpoint.
- Therefore NO pending invite was verified by the required spaced-curl + non-empty og:title test. All 20 are unverified-pending only. A parent/root agent with working WhatsApp access must re-verify each pending invite (spaced curl, browser User-Agent, HTTP success + non-empty og:title) before any promotion to the verified file or to groups.json.
- groups.json, generate.py output, and ~/workspace/wgl-deploy/ were NOT modified.
