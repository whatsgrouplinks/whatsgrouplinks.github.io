# TEAM 09 — groupio.app German slice — leads & notes (2026-10-29)

## Summary
- Fetched all 52 German group pages linked from https://groupio.app/ homepage (skipping 3 adult-sex pages, never visited).
- 45 of the 52 invite codes were ALREADY in the dedupe union → site is largely harvested.
- 7 genuinely new codes extracted → 5 VERIFIED (HTTP 200 + og:title + invite_link_type_v2 + real WhatsApp CDN profile image), 2 pending (empty og:title).
- No HTTP 429 hit during verification.

## Name-only leads (not fetched this run)
- groupio.app category listing pages hold MORE German group pages than the 52 on the homepage. Out-of-slice fresh directory set:
  /groups/freundschaften, /groups/gaming, /groups/fan-gruppen, /groups/musik,
  /groups/Finanzen, /groups/Marktplatz, /groups/allgemein, /groups/selbsthilfe,
  /groups/serien-filme, /groups/best, /groups/tag/deutschlandweit, /groups/tag/neu,
  /groups/Anime-Manga, /groups/tag/chatten, /groups/tag/freunde
  → recommend a follow-up team crawl each listing and extract /group/join/ slugs beyond the homepage set.
- Pending re-check candidates: "Bi-Les-Date-Paradise" (DSi2HCdC2czLqNpWxXx9Jj) and "no vibe, no life" (CjUnJpGLLWG9FTg7Lt9lss) — live links with empty og:title; re-verify in 1-2 waves.

## Exhausted pages (all 52 homepage /group/join/ slugs; 3 never visited per adult rule)
Visited: All-about-Rp, Anime, Anime-Japan-Day, B-R, BI-amp-GAY-Boy's-ab-18, Beste-Vorgruppe,
Bi-Les-Date-Paradise, Brawlstars, Crypto-Experts, Deutschrap-LEAKS, Discord-Zocken, Einsamkeit,
FRIEDHOF-DER-VERNUNFT, Flohmarkt-fuer-Alles, Freunde, Gaming, Gay-Boys-18-38,
Gay-Maenner-in-Damenwaesche-AB18 (dropped: suggestive emoji in title), Gays-ab-18,
Geld-verdienen-Gruppe, Herr-der-Ringe-Hobbit, ImmoInvest, Kauf-amp-Verkauf-Gruppe,
Liebeslieder, Manga-Projekte, MusicLegends, OG-Business, OG-filme, PsychCommunity-Vorgruppe,
Schwulen-und-bi-Gruppe, Singles, Starter-Squad, Sticker-Anime, Suche-Freundin, Switch-Gruppe,
The-ugly-childrenV-V, Tiktok, Tonie-Gruppe-1, Top-Deals-Vorgruppe-1, Vorgruppe,
Walczak-Gang-Warsaw-Ghetto, Weirdooos, Yugioh-Fangruppe-Deutschland, Zone,
lxwdrip-fanatics-latestnews, no-vibe-no-life, whatsapp-group-54751/55062/56776.
Never visited (adult rule): Apex-hentai-3028, Private-Livecams-gratis-36,
VORGRUPPE-FKK-Club-ab-18-54016, and the whole /groups/adult category.

## Notes / flags
- Dedupe union used: groups.json (38,755 groups, 38,721 codes) + .existing_codes.json (73,873) = 73,874 codes. Each candidate checked against the union and within-batch.
- "Walczak Gang (Warsaw Ghetto)" name has a Holocaust-adjacent meme tone; kept as International community since it doesn't match the banned regex — parent may want to review before merging.
- All items: country DE except Walczak (International); no source names, no personal info, English descriptions.
- Retired sources were not touched (per slice instructions).
