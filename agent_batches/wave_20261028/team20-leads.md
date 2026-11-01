# team20 — wave 20261028 — groupjoin.link NON-ASIA country tags

## Sources / pages scraped
- groupjoin.link country pages, page 1, `?safeSearch=off` (20 countries):
  Kenya, Ghana, Nigeria, Ethiopia, Egypt, Morocco, South Africa, USA
  (united-states), UK (united-kingdom), Canada, Australia, Brazil, Mexico,
  Colombia, Argentina, Spain, France, Germany, Italy, Turkey.
- Same country pages, page 2 (6 thinnest / follow-up countries):
  Kenya, Nigeria, Canada, Australia, Argentina, France.
- Exploration only (no groups harvested from them): groupjoin.link
  tag/Kenya page 2 and tag/ghana page 1 — tag pages returned almost no
  group cards, while the country pages returned full group records, so
  country pages were used as the productive source for the same countries.
- NOT re-scraped: any wave 20261027 source (manifest at
  agent_batches/wave_20261027/manifest.txt), in particular no Uganda tag
  page and no Indonesia tag pages; no Asia tags and no Indonesia tags at
  all. No retired sources used. No groups.json / generate.py output /
  ~/workspace/wgl-deploy/ touched — only the three team20 files in this
  wave directory were written.

## Counts
- Parsed from pages: 489 group records (377 from page 1 + 112 from page 2).
- Candidates after dedupe + filters: 98.
- Verified (fresh file): 39 — HTTP 200 on chat.whatsapp.com AND a
  non-empty, meaningful og:title, used as the group name.
- Pending (unverified file): 58 — all returned HTTP 200 but WhatsApp
  returned no og:title in the fetched page, so they could not be verified
  under the rule (never staged as verified).
- Post-verification drop: 1 — a France group whose og:title was a
  spaced-out "Naughty boy" (sexual-suggestive); dropped entirely, in
  neither file.

## Dedupe drops: 71
- Against dedupe_union_codes.txt (73,684 existing codes) + within own
  output: 33 on page 1, 38 on page 2 (page-2 figure includes overlap with
  page-1 candidates as well as the union).

## Content-filter drops: 320 (pre-verification) + 1 post-verification
- Site Adult-category drops: 291 (232 page 1 + 59 page 2). The country
  pages are sorted by views and page 1 is dominated by Adult-category
  groups; the whole Adult category was dropped rather than trying to
  salvage individual titles, because most Adult titles/descriptions on
  this site are sexual content even when the title alone looks vague
  (e.g. "Videos", "Hot", "Mega links").
- Explicit porn-term drops (title, incl. leet variants like s£x, and
  porn emojis): 3 on page 1, 0 on page 2.
- Symbol-only / meaningless titles: 23 (20 page 1 + 3 page 2).
- Extra risky drops: 3 — an Egypt "18+ 💦" group, a Mexico "Only for
  14 + boys" group, and a UK 18+ ad-chat group whose description
  mentioned nudes.
- Girls / friendship / dating / social groups were NOT dropped; they
  appear in both files under Friendship where applicable.

## Verified breakdown (39)
GH 2, NG 2, ET 1, MA 1, ZA 3, US 3, CA 1, BR 2, MX 3, CO 3, AR 2, ES 5,
FR 4 (after the 1 post-verify drop), DE 3, IT 3, TR 1. Kenya, Egypt,
UK, Australia had 0 verified this pass (their clean candidates all
landed in pending with empty og:title).

## Notes / caveats
- Verification quirk: many WhatsApp invite pages return HTTP 200 but no
  og:title at all in the curl-fetched HTML (58 of 98). Those are pending,
  not dead — a re-check may surface titles for some of them.
- Two verified names differ from the source listing title (group renamed
  since listing, e.g. a Brazil group whose og:title is "Conta Roubada");
  the og:title was used, per the rule.
- Category mapping: source categories were mapped to the allowed list;
  betting groups go to Sports, forex/crypto/trading to Finance, Love /
  Flirting to Friendship, Spiritual non-Islamic to Community & Social.

## Next-pass leads (same slice only)
- Country pages page 3+ for the large totals: USA (1,308 groups),
  Nigeria (566), UK (486), Canada (247), Australia (240), Ghana (148),
  South Africa (149), Egypt (116), Morocco (120), Argentina (90),
  Germany (61), Italy (37), France (33), Turkey (31).
- Kenya pages 3–4 (64 total; pages 1–2 yielded no clean verified group).
- Re-check the 58 pending codes for og:title surfacing.
- Other non-Asia country pages on groupjoin.link not covered this pass
  (e.g. Algeria and other African / Latin American / European country
  pages) — same country-page method, same Adult-category drop.
- Do NOT revisit: Asia tags, Indonesia tags, Uganda tag page
  (wave 20261027), or any retired source.
