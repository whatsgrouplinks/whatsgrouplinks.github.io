# Team 07 leads — groupjoin.link Indonesia city tags (2026-10-29)

## Name-only leads (seen on groupjoin.link, NOT harvested — left for other teams)
- Gatak (Jawa Tengah) city page: /city/gatak-jawa-tengah-indonesia
- Rantauprapat (Sumatera Utara) city page: /city/rantauprapat-sumatera-utara-indonesia
- Both were linked from /country/indonesia but are OUT of this team's slice (10 assigned cities only).
- Capitalized tag pages exist and render client-side, e.g. /tag/Surabaya — untested for SSR data; another team may try the tag route.

## Exhausted pages (fully scraped, all pages)
- /city/surabaya-jawa-timur-indonesia (5 groups)
- /city/medan-sumatera-utara-indonesia (12)
- /city/semarang-jawa-tengah-indonesia (7)
- /city/makassar-sulawesi-selatan-indonesia (12)
- /city/yogyakarta-di-yogyakarta-indonesia (22; 2 pages) — NOTE: slug is `di-yogyakarta`, NOT `yogyakarta-yogyakarta`
- /city/bekasi-jawa-barat-indonesia (4)
- /city/depok-jawa-barat-indonesia (7)
- /city/tangerang-banten-indonesia (29; 2 pages)
- /city/palembang-sumatera-selatan-indonesia (23; 2 pages)
- /city/bogor-jawa-barat-indonesia (4)
- /cities and /states indexes: no Indonesia entries listed (only 24 India/Pakistan entries each).
- /country/indonesia: NOT touched (owned by another team).

## Extraction notes for other teams
- City pages are server-rendered; each group card embeds its own invite in escaped JSON:
  `"group_uid":"<slug>","group_title":"...","group_img":"...","group_desc":"...","link":"https://chat.whatsapp.com/invite/<code>"`
- Use the per-card `"link"` field — the FIRST chat.whatsapp.com code on the page does NOT belong to every group.
- Image URLs contain `\u0026` escapes — unescape to `&` before use.
- Verification: chat.whatsapp.com/<code> returns HTTP 200 even for dead invites, but dead ones have EMPTY og:title; live ones carry a real og:title + invite_link_type_v2. No 429s hit during this run.
- Content on these city pages skews heavily to JB (jual-beli = buy/sell) game-account stores; ~15% were bokep/porn drops.
