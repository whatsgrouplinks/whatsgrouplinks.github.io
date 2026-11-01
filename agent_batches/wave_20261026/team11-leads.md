# team11 leads — wave 20261026 (Spanish LatAm + Spain)

## Why verified = 0
- Direct curl egress was dead during this run (even example.com returned 000), so the
  required curl verification (HTTP success + non-empty og:title) could not be performed.
- A text-fetch of an invite page was rejected with HTTP 403 and was not retried.
- All 3 code-bearing candidates below are therefore in
  team11-unverified-pending.json, NOT in the verified file. They still need a live
  verification pass (curl or live browser) before merging.

## Verified file
- team11-fresh-latam-spanish.json: [] (empty — no item passed verification this run)

## Pending items (3, all deduped against groups.json + .existing_codes.json)
1. Grupo SICUE Valencia 2024/2025 — Education — ES
2. Grupo oficial de WhatsApp de la ESI — Education — ES
3. Diario Primicia — News — VE

## Dedupe drops (codes already in the existing set)
- Alicante activities group (Spain, Community & Social) — code already known.
- Telde local news service group (Spain, News) — code already known.

## Content drops (codes deliberately NOT recorded)
- A 2020 Chilean forum car group whose own thread jokes that porn is allowed — dropped
  on content caution, code withheld.
- A private class chat export found on a document-sharing site — personal chat log,
  not a public directory listing; code withheld, do not harvest.

## Join-button-only leads (need a live-browser Join-click pass; codes NOT extracted)
- whatshub.es — 2,769 groups, mostly Spain; listing text gives names/descriptions
  but invites sit behind detail-page Join buttons. One code surfaced only because a
  group pasted its own link inside its description (already known — see dedupe drops).
- gruposwats.com — large Spanish directory; same Join-button model.
- whtsgroupslinks.com/grupos-de-whatsapp/ — Spanish listicle, ~15 named groups,
  invites behind Join buttons.
- erappmus.com — Erasmus WhatsApp groups by country/city (Spain pages exist);
  invites behind Join buttons.
- WHTS Club — press-release articles only, no working directory URL found; not scraped.

## Sources checked and abandoned
- solion.app — app-only directory (Google Play listing), no web listing pages with
  extractable codes.
- gruposwhats.app / linkdegrupo.com.br / gruposwhats — Brazilian/Portuguese focus,
  out of this Spanish-language slice (already noted as leads by the 20261025 LatAm team).
- grupodewhatsapp.com, wagroupnest.com, elsabagh.com, meraonlineworld.com — on the
  banned/retired list, not touched.
