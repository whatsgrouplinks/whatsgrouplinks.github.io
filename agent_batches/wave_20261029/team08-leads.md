# TEAM 08 — wave_20261029 — wpgroup.in Spanish pages (re-verification)

## Result summary
- Source: https://wpgroup.in/spanish-whatsapp-group-links/ ("1600+ Spanish WhatsApp Group Links", page footer says last updated ~284 days ago; content is mostly 2017–2018 era groups).
- No usable wpgroup.in Spanish candidates existed in wave_20261028 pending files (team15's wpgroup.in codes were Kerala-page; retired). Re-extracted fresh from the Spanish page per task fallback.
- Raw extraction: 182 unique `chat.whatsapp.com` codes (11 top-section "Link" entries + 17 inline Turkish entries + 154 emoji-section entries).
- Union dedupe (groups.json + .existing_codes.json, 73,874-code union): 9 already existed → 173 candidates.
- Pre-verify content drops: 39 (see below) → 134 sent to spaced curl verification (8–12s spacing, no 429 encountered, run completed fully).
- VERIFIED: 2. Pending (dead/empty og:title): 132.

## Verified (in team08-fresh-wpgroup-spanish.json)
1. "Spain Successful trading" — Online Earning, ES — https://chat.whatsapp.com/3XMpQsEPLE19V4pnnC80O1 (listing label was "Os Melhores 2018")
2. "Islam" — Islamic, International — https://chat.whatsapp.com/FRmhSaZKynH9JobDGtt6zc (listing label was "ᖇƗNǤᑌᕮ Ðᗩᔕ ƬᖇᕮƬᗩᔕ")

## Page health notes (for parent)
- This page is effectively DEAD as a source: 132/134 codes return HTTP 200 with EMPTY og:title (revoked/expired invites). Yield 1.5%.
- 132 pending items are weak-og:title (revoked) codes per task spec — they are NOT expected to revive; re-verification is low value.
- Content quality is poor: heavy Turkish off-topic contamination (betting, taxi, politics), Portuguese "amizade" spam clusters, and ~39 adult/profanity/junk entries dropped pre-verify (putaria/sacanagem/explicit-video titles, 🔞/🍆/💦 emoji titles, "GP COM VÍRUS" malicious name, profanity, meaningless "Zzz/ss/AAA/WWW").
- Data-integrity quirk: code JLthIFxsvOg4vilG3vXSzp appears TWICE on the page with different labels ("Spanish videos" and "Soy tu puta") — listing labels on this page are unreliable; og:title was used for verified names.
- Recommendation: mark wpgroup.in Spanish page EXHAUSTED; do not re-harvest until page shows a fresh update stamp.

## Name-only leads (no code extractable)
- None on this page — every listing carried an href code. (The "Join More Whatsapp Groups" cross-links at page top point to other wpgroup.in category pages — out of slice, not harvested.)

## Out-of-slice / not touched (for other teams or later waves)
- wpgroup.in other language/country pages (Portuguese "amizade" clusters suggest a PT page exists) — NOT scraped, out of this slice.
- Retired per task, untouched: wpgroup.in Kerala page, whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, elsabagh.com, techsslash.

## Pre-verify drops (39, not in either JSON — do not re-add without review)
Adult/sexual (26): VÍDEOS EXPLÍCITOS, Aqui pode putaria, Putaria liberada, Putaria💯Limites, ℒoucos por ℋentai, Seculo XXI #Perguntas (🔞), Contatinhos 10/10 ❤🔞, PRAZER 💯LIMITES, VIDEOS XX, Zap😜😂💦Zuera, Sacanagem Rola solta, Gulosas e tarados, Amigos con beneficios, 24/7 escupe traga un (🍆), •✮•ɠเƒร☠🔞૮σɳтσร•✮, Hentai, PUTARIA 24 HORAS, 100% PUTARIA, X VIĐ€ØŞ 3.0, x@x@x intenso, 100% señoras follando, FETICHExSEDUÇAOprCASAL, Ilha do ecchi hype, ORIGINALES (🔞), 100% PUTARIA (dup label).
Malicious/profanity/junk (13): GP COM VÍRUS, Su puta madre prros, fuck you, Huele pedo cara pis, EVLİCİFT TEK BAYAN GURBU (swingers-adjacent), whatsapp group link (generic), bawa g aaa pandi aaa (gibberish), Zzz, ss, SS, AAA, WWW, S.A.D, DAILY, que.
Union duplicates (9, already in groups.json/.existing_codes.json): Spanish Floppa, Real MADRID, ENGLISH GROUP, HYIP up to date, Investors Forum legit 2, İdda-yatırım-borsa, İstanbul Taksicileri 34, plus 2 more Turkish entries.

## Flags for parent (merge step)
1. Pending file = 132 revoked-code placeholders (weak og:title), NOT live groups. Merging them would add dead links; suggest excluding from any merge unless policy says otherwise.
2. The 2 verified items use og:title as name (per wave convention); "Spain Successful trading" may be a trading-signal group — review category fit (Online Earning) before merge.
3. No 429s hit; IP/UA not blocked by WhatsApp this run.
