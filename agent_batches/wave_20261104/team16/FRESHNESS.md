# team16 groupwhat.com freshness report — wave 20261104 (crawled 2026-11-04 ~12:00-12:30 PKT)

All 11 category listing pages fetched (raw HTML via python requests; curl returns empty 200 - bot-gated).
Listing embeds full group JSON in Next.js flight data: name, invite_link, image_url, description,
created_at, updated_at, category, country, language. 10 latest groups per category, page order = recency.

## Per-category latest group (updated_at from site)
| category | groups | latest updated_at (UTC) | latest group name |
|---|---|---|---|
| animation | 10 | 2026-10-28T23:35:54 | Filtro • Freak Union |
| business | 10 | 2026-10-30T19:48:22 | KMPofficial ( Karachi Market Place ) |
| cryptocurrency | 10 | 2026-11-02T10:44:01 | Launching Soon |
| earning | 10 | 2026-11-02T10:42:37 | Mahar Muzamil Airdrops |
| education | 10 | 2026-10-30T21:31:03 | Upon Resources |
| finance | 10 | 2026-11-03T20:19:21 | USA Trading Pro Signals (Forex/Crypto) |
| football | 10 | 2026-11-02T00:04:30 | SPORTY HERO |
| friendship | 10 | 2026-10-30T21:41:27 | Freak Union |
| gaming | 10 | 2026-10-29T15:09:15 | Filtro • Freak Union |
| movies | 10 | 2026-10-27T14:14:41 | Arabs Wizarding World |
| uncategorized | 10 | 2026-09-24T20:08:38 | J C B GROUP |

## Verdict
110 records total: 104 chat.whatsapp.com codes (ALL already in dedupe_union.json),
6 whatsapp.com/channel links (excluded). 0 new codes.
NO category has new listings since Nov 3 — every 10-latest set is fully banked already.
Note: finance's latest item (updated Nov 3 20:19 UTC / Nov 4 01:19 PKT) is already in the union,
so even the freshest listing addition was captured by an earlier wave.
