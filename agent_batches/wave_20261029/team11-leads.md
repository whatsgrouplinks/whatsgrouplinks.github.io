# Team 11 — whatstele.com MALAYALAM slice (wave_20261029)

## Result
- fresh: 0 | pending: 0 | leads below

## Method
1. Discovered whatstele.com's category archive (https://whatstele.com/whatsapp/group-links/)
   and its full-list page (https://whatstele.com/whatsapp/group-links/full-list/).
2. The ONLY Malayalam-related page on the whole site is
   https://whatstele.com/whatsapp/group-links/kerala/ ("1000+ Kerela WhatsApp Group Links").
   No other whatstele.com page has a malayalam/kerala slug; site-scoped search also
   returned no additional Malayalam pages.
3. Extracted all chat.whatsapp.com/invite/<code> links from the page HTML:
   19 invite refs → 16 unique codes.
   (Page lists 19 entries but reuses 3 codes: Kerala Tourism = Kerala News;
   Kerala Pets listed twice; Kerala Fans listed twice.)
4. Deduped against union of groups.json + .existing_codes.json (73,874 existing codes):
   ALL 16 codes already exist in the DB. Zero new candidates → nothing to verify,
   pending file is intentionally empty (no HTTP 429 encountered; verification never
   needed).

## Notes
- Never visited /sex/ /xxx/ /adult/ pages (per slice rules); only the Kerala page was fetched.
- Telugu pages untouched (other team's slice).
- Other fresh Malayalam directories spotted in web search (OUT OF SLICE — whatstele.com
  only was assigned; left for other teams):
  - https://joinwagroupnow.com/kerala-whatsapp-group-links/ (Kerala + Malayalam tables)
  - https://whatgroups.com/kerala-whatsapp-group-links/ (large Malayalam business tables)
  - https://appgrouplink.com/kerala-whatsapp-group-links/
  - https://wpgroup.in/kerala-whatsapp-group-link/ (codes printed inline in search snippet)
  - https://wagroupshub.com/malayalam-whatsapp-group-links/ (contains thund/sex entries —
    needs adult filtering)
- Slice status: EXHAUSTED. All whatstele.com Malayalam content is already banked.
