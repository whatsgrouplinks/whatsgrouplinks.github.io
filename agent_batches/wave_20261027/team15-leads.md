# Team15 — Spain + Portugal — wave 20261027

## Counts
- Verified (fresh file): 3 — 2 ES, 1 PT
- Unverified-pending: 8 — 7 ES, 1 PT
- Candidates examined: 14 with exposed invite codes
- Dropped as already existing: 3 (see below)
- Hard-porn blocked: 0 (no hard-porn candidate was found; girls/friendship groups were not removed — none were in this candidate set)

## Method
- Dedupe set = union of all invite codes in `groups.json` (38,051 groups) and `.existing_codes.json` — 73,170 codes total. All 14 candidates were checked against both; the 3 duplicates were dropped, not written to either JSON.
- Verification = spaced curl (1.5 s gap, browser User-Agent, follow redirects) of each `chat.whatsapp.com` invite. Verified ONLY on HTTP success AND a non-empty `og:title`. Empty-title results were re-checked once for one case and confirmed genuinely empty (`og:title content=""`), i.e. revoked/empty, not an extraction miss.
- Verification results: 3 verified; 7 returned HTTP 200 with an empty `og:title`; 1 (Huelva sailing) timed out (HTTP 0) and is therefore pending, not proven dead.
- No file outside the three team15 files was modified. `groups.json`, `generate.py` output and `wgl-deploy/` were not touched.

## Verified (in team15-fresh-spain-portugal.json)
- University of Oviedo Informatics Student Delegation — ES, Education — og:title "NOTICIAS - CONSEJO DE ESTUDIANTES"
- University of Oviedo Science Faculty Student Delegation — ES, Education — og:title "Facultad de Ciencias"
- VFF1 Formula 1 Discussion — PT, Sports — og:title "VFF1 Fórmula 1"

## Pending (in team15-unverified-pending.json, all HTTP 200 + empty og:title unless noted)
- ESI Computer School Official Group — ES, Education
- El Partido de Manu Football Community — ES, Sports
- Wuolah Albacete Study Notes — ES, Education
- Wuolah Madrid Study Notes — ES, Education
- Diverso Navalcarnero Neighbours — ES, Community & Social
- Neighbours Housing Community — ES, Community & Social
- Huelva Bay Sailing League — ES, Sports — curl timed out, uncheckable in this run, not proven dead
- Lisbon European Studies Mentorship — PT, Education — code as printed in the university PDF (upper-case); the empty title may reflect that casing

## Dropped as duplicates (already in the existing set — NOT written anywhere)
- Telde news-service group (Gran Canaria, ES)
- Spanish football podcast listeners group (ES)
- Portugal personal-finance podcast group (PT)

## Sources used (new for this slice, not wave-20261026 sources)
- University of Oviedo student-council pages (Informatics and Sciences delegations)
- ESI / UCLM computer-school page, El Partido de Manu football site, Wuolah study-notes listings, nuevosvecinos housing threads, Huelva sailing-league notice, University of Lisbon European Studies mentorship PDF, Portuguese Formula 1 podcast page

## Sources deliberately NOT used (excluded, for the parent's follow-up only — no codes harvested from them)
- whatshub.es, gruposwats.com, meetup.com (all pages, including Barcelona/Madrid/Lisbon/Valencia pages found in search), gruposwhats.app, grupodewhatsapp.com, wpgroup.in, freewagroup, ongrupos — each is either named in the task ban list or appeared as a wave-20261026 source. Their Spain/Portugal groups (e.g. Barcelona entrepreneurs, Lisbon Cake & Tea Club, Lisbon Open Coffee, Madrid run/volleyball groups, Valencia beach-volleyball group) were therefore NOT harvested by this team, even where a code was visible in search results.
- gruposwsp.com (new directory): its group pages hide the invite behind a join button and the text fetch exposes no invite code, so it yielded names only, no harvestable codes in this run. Its Seville 55–65 social group and football-friendship simulation league are leads for a browser-based team.
- Aspirantes Guardia Civil 2027 page (Spain): lists regional exam-preparation groups by autonomous community, but exposes no invite codes in page text — lead only.
- Zinderizar Zaragoza groups, Unoveles Salamanca university groups, Granada UGR faculty groups: group names listed, invite codes not exposed in page text — leads only.
- whtsgroupslinks.com Spanish popular-groups page: not harvested; name is close to a banned source, so it was left as an unharvested lead rather than risk a banned-source mix-up.

## Caveat for the parent
- Exec curl to non-WhatsApp sites timed out in this session (all directory homepages returned 000), while `chat.whatsapp.com` GETs worked. That is why directory scraping was replaced by search-snippet + page-text extraction, and why the Huelva code is pending on a timeout rather than a proven failure.
- Portugal yield is thin (1 verified + 1 pending) because most Portuguese directory pages found are Brazilian-focused or hide invites; the Lisbon/Porto expat directories that do expose codes are meetup-based and were excluded under this slice's rules.
