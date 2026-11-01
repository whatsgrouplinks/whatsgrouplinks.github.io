# Team12 leads — wave 20261026 (Portuguese / Brazil slice)

Name-only leads: codes are hidden behind a Join button / JS redirect on these
directories, so NO invite code is recorded here and nothing from these pages
was put in the verified or unverified JSON files.

- gruposbrasil.com.br — e.g. group page "Divulgação 👑" (Divulgação category,
  updated 12 Oct 2026). Join button redirects; no code visible in page text.
  Revisit only with a live browser that can follow the Join redirect.
- grupos-zap.com — group pages use numeric ids (e.g. grupo-2237, Memes e
  Zoeira, published 13 Oct 2026). Join button hides the code; name-only.
- gruposwhats.app — mentioned in wave_20261025 manifest as a page-level lead
  only, never scraped for invites by that team; its group pages use numeric
  ids and a Join button, so it is also name-only from text fetching. NOT
  used as an invite source by this team.

Notes for the merger: the 6 items in team12-unverified-pending.json come from
ongrupos.com, whose group-page URL slug is itself a 22-character invite-format
code (the same slug is used in its join-group redirect path). Those codes
were deduped against the full existing set (73,092 codes) and are all fresh,
but they still REQUIRE a curl check (HTTP success + non-empty og:title) before
any merge, because verification could not be completed in this session (see
final report: shell egress proxy CONNECT timeouts + text fetcher 403 on
chat.whatsapp.com).
