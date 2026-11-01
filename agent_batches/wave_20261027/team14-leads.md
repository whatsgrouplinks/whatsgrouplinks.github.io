# team14 leads — wave 20261027 (Colombia, Peru, Argentina, Chile — Spanish)

## Files
- team14-fresh-latam-south.json: 21 VERIFIED items (CO 13, PE 6, AR 2, CL 0)
- team14-unverified-pending.json: 31 PENDING items (CO 10, PE 3, AR 6, CL 12)

## Verification method
- Dedupe: full code set = groups.json (38,051 groups) UNION .existing_codes.json (73,170 codes total). 73 candidates collected, 21 dropped as already known, 52 fresh kept.
- Verification: spaced curl (1.5 s sleep, browser User-Agent, -L) to each chat.whatsapp.com invite; VERIFIED only on HTTP 200 + non-empty og:title. Verified names are the returned og:title (WhatsApp truncates some to 25 chars).
- 39 of 52 fresh candidates were curl-checked. WhatsApp responses slowed sharply after ~39 checks (tarpitting), so the remaining 13 were cut to pending UNCHECKED, not failed (listed below). No porn/xxx groups were included; girls/friendship/dating groups were not removed (none in this batch needed the filter).

## Pending breakdown
- Curl 000 (network failure, not proven dead): Billar/Tenis/Domino Bogota, Piano Utadeo (4).
- HTTP 200 but empty og:title (not verified, may be revoked/renamed): Ajedrez Bogota, Deportes Al Instante, Ventas Calzado Colombia, Argentinos en Colombia, Reencuentro Misional Colombia/Peru/Chile Norte/Santiago, Voluntariado Refugio de Sonrisas, Comunidad Memoria de la Ribera, Reencuentro Misional Buenos Aires Norte/Cordoba/Rosario/Buenos Aires Sur (14).
- UNCHECKED (verification cut short): Reencuentro Misional Chile Sur, all 8 Mega Te Ayuda Chile community codes, BTS Argentina/Chile/Colombia/Peru (13). These need a fresh curl pass before any merge.

## Sources checked (new for this wave, none on the banned/retired list)
- Direct-code pages found via web search: Bogota district sports institute regulations, Bogota university arts/wellbeing pages, Lima fashion/health/education listings, Buenos Aires news and gaming pages, plus search-result snippets for Peru/Argentina/Chile community pages.
- Checked and NOT usable for codes: igrupos.com (listing + detail pages hide invites behind join buttons; no codes extractable via text fetch; direct curl to the site hung), comunigrupos.lat (mostly Discord listings, few WhatsApp entries, no extractable codes), milchats.com (same operator model as gruposwats — invites behind requests, not direct codes). These are leads for a live-browser join-click pass, codes NOT extracted.
- Dedupe drops (21, already in existing set): all 16 Estudiantes Organizados Argentina regional codes, Experienced Soccer Players Buenos Aires, U2 Argentina tour group, ECCOS FM news group, Mega Te Ayuda Subsidio Familiar code, Catalyst Now migration group.

## Notes for merger
- Verified file contains only the 21 curl-verified items; pending file must NOT be merged without a fresh verification pass.
- No source names, source URLs, or personal info appear in any name/description. Images are "" throughout (pps.whatsapp.net images were seen for some verified groups but were not captured into the file to avoid stale URLs).
- groups.json, generate.py output and ~/workspace/wgl-deploy/ were NOT touched.
