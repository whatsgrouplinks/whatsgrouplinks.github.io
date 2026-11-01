# Team12 — Wave 20261028 — Africa regional beyond East Africa

## Slice
NEW Nigeria, Ghana, Cameroon, Senegal, Ivory Coast, Morocco, Algeria, Tunisia,
Libya, Egypt, Angola, Mozambique, DRC, Namibia, Botswana directory/community
pages NOT covered in wave 20261027.

## Sources / pages scraped (all new pages for this wave)
- webnews21.com — Top Cameroon 500 New WhatsApp Groups list (40 raw codes, items 1–40)
- human-unity.org PDF — List of Groups Supporting Human Unity (in-slice city groups:
  DRC Goma/Bukavu/Rutshuru/Uvira/Kinshasa/Lomami; Nigeria Abuja/Ebonyi;
  Cameroon Yaounde/Douala; Ghana Accra; Tunisia Tunis; Egypt Cairo;
  Senegal Dakar/Saint Louis; Morocco Rabat)
- Search-snippet raw invites: techapkzone.com COD Nigeria; pastquestion.com.ng and
  cookuf.net Nigeria jobs pages; lekkiinvestor100shares blog (Nigeria finance);
  ireporteronline.com.ng news group; finexinsights.com Ghana news group;
  schoolandcollegelistings.com WAEC GH + EXAMS GHANA; salda.ws Ghana buy/ship;
  meta.wikimedia.org Moore Wikimedia grant page; schoolandcollegelistings.com
  Arabic Tutor Online (Egypt); wingulamashahidi.org Africa faith page;
  unclene.com Cameroon jobs pages (4 codes) + Substack Cameroon Mini-MBA +
  fly4studycm.com Cameroon forex page; news.africa-business.com Africa B2B page;
  classroom.eumetsat.int Africa Regional Focus Group page; itpcglobal.org
  Global Fund CHANGE working-group PDF; africachess.net AYCC 2024 invitation PDF;
  globalsouthopportunities.com opportunities page.
- Attempted but unusable in text fetch (no codes extractable, NOT counted as sources
  of candidates): appgrouplink.com Nigeria page (bot-check wall);
  whatsagroupslinks.com Senegal + Tunisia pages (bot-check wall);
  groupjoin.link Algeria/Egypt country/tag pages (codes blurred behind filter).

## Counts
- Candidates found: 84
- Dedupe drops (code already in wave_20261028 dedupe_union_codes.txt, 73,684 codes,
  or duplicate within this batch): 67
- Candidates actually curl-checked: 17
- Verified (HTTP 200 + non-empty, meaningful og:title used as group name): 13
- Pending (HTTP 200 but empty og:title; names are context-inferred, NOT og:title,
  and must be re-verified before any merge): 4
- Porn drops: 0 (no hard-porn titles among candidates; girls/friendship/dating
  groups were not present in this batch, none dropped on that ground)
- Meaningless/symbol-only titles dropped: 0 (all 17 checked codes had either a
  meaningful title or an empty title → pending)

## Verified (13) — see team12-fresh-africa.json
Cameroon 5 (Uncle Ne's Jobs 08 / 198 / 110 / 47, Mini-MBA Admission Center);
DRC 1 (HUMAN UNITY - RD CONGO - LOMAMI); Ghana 2 (Finex Insights, Buy and ship
from China); International 5 (Nuru Ya Upendo (MASOMO), Africa Business Pages B2B,
Africa Regional Focus Group (ARFG), CHANGE WG4 - Global Fund, AYCC 2024).
Note: EvdoMEsH6qB8XtSOvvMVTm was tentatively Buy Sell from its page context but
its og:title is a jobs group, so it is filed under Jobs.

## Pending (4) — see team12-unverified-pending.json
- Fqfs1JMNtzI8GE8XQrrDJl (CM) — Cameroon list item 40, HTTP 200, empty title
- JkKMnhO8SsD9KBmHmBaAsd (GH) — Moore Wikimedians community, HTTP 200, empty title
- EeZ0JbkOX1BK5TpKTorkBi (CM) — Cameroon forex trading group, HTTP 200, empty title
- IHJmTzQBFDzBVkaowNezNa (International) — opportunities group, HTTP 200, empty title

## Not re-scraped (per task)
Wave 20261027 sources from its manifest (Nairaland threads, schoolgist.ng,
Accra school homepage, Univ. of Ghana scholarship guide, Cameroon diaspora form,
Cameroon music listing, Senegalese drum/dance page, Libya country-page directory,
Kaapjag/Zimbabwe/SA listings) and retired sources (whatslinkhub.com, elsabagh.com,
whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com,
grupodewhatsapp.com, wagroupnest.com, groupda.com, groupizo.com sitemaps).
groups.json, generate.py output and ~/workspace/wgl-deploy/ were NOT touched.

## Next-pass leads
- groupjoin.link country/tag pages for Nigeria, Ghana, Morocco, Tunisia, Senegal,
  Ivory Coast, Angola, Mozambique, DRC, Namibia, Botswana: pages exist with
  dozens of results each, but codes are blurred in text fetch — needs a live-browser
  pass (subagent text fetch cannot extract them).
- whatsagroupslinks.com Senegal/Tunisia and appgrouplink.com Nigeria pages:
  bot-check walls in text fetch — live-browser pass may extract their Join links.
- No raw-code lists found this pass for Ivory Coast, Algeria, Libya, Angola,
  Mozambique, Namibia or Botswana — these 7 countries have ZERO items in this
  batch; they are the priority gap for the next pass.
- Two truncated codes seen in snippets were NOT used (incomplete, unverifiable):
  Morocco retreat group and Cameroon audience group from a video description.
