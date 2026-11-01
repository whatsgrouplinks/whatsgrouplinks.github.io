# TEAM 16 — Meetup.com Amsterdam 20s/30s — leads.md (2026-10-29)

## Summary
- Verified fresh: 1 (Language Corner Amsterdam Improv Masterclass, code EwfxPHy3AuE6WQ4rjOkstO, HTTP 200, og:title "'Improv' your English masterclass", v2 marker present)
- Unverified pending: 2 (both "20s 30s Global Socializing in Amsterdam"; current live link BwiHcaLy6FS3Z3FBwY73WB from group page HTML + older event-page link Dt7YTnGWgXIAXEoIjX6xNW; both HTTP 200 + v2 marker but EMPTY og:title, so per rules -> pending)
- No HTTP 429 hit; verifications run with 7s spacing (well under 60-code cap).

## Name-only leads (Amsterdam Meetup groups with NO public chat.whatsapp.com link found)
These groups exist on meetup.com but keep WhatsApp access behind sign-in, private message, or phone-number request:
- Amsterdam Parties (after-work drinks, ages ~25-45) — no public WhatsApp link; worth a re-check later
- WeMeet 20s-40s Socials Amsterdam (English) (amsterdam-young-professionals-meetup-group) — links only Instagram/LinkedIn/TikTok
- Singles in Amsterdam! 20-39 years — no public WhatsApp link
- Amsterdam Age 35+ Social Group — no public WhatsApp link
- Amsterdam Social Meetup Group (daily locals/expats/travelers meetups) — no public WhatsApp link
- Joyala Amsterdam: Game Nights, Adventures & Play — no public WhatsApp link in page text
- Amsterdam Board Gaming Meetup Group — no public WhatsApp link
- Amsterdam International Community for expats (AIC) — uses a wa.me assistant ("Klickie"), not a chat.whatsapp.com group link
- The Amsterdam Expat Meetup Group (amsterdam-expat) — join via phone number message only, no public invite link
- Amsterdam Dance, Dine & Socialites (30 & above) — WhatsApp is members-only; their public link FXwifLI3yAkBgbO9NZLrPR is ALREADY in DB

## Codes found but DROPPED (already in DB)
- FEYVSvlUYsZJkF60I5zIhI — International Expats Adventure Guild Amsterdam (in DB)
- C0ywEOnB7aB8EmwFM9jtuJ — VTAG Volleyball training Amsterdam (in DB)
- GfrmmUbkMUsDFLEcq1rSZC — Language Corner Amsterdam conversation session (in DB)
- BfXSl8fOsCMK8eFwV4ZkcF — Just For Fun Amsterdam (in DB)
- FXwifLI3yAkBgbO9NZLrPR — Amsterdam Dance, Dine & Socialites (in DB)

## Out-of-slice (not Amsterdam / not NL — for other teams)
- F30mGDv7j64EfqzmNyB8PS — Nordic Society, STOCKHOLM event (in DB already)
- ITesisMThOFAyNRUJ6uECN — Socializus Erasmus/expats event, PARIS Bastille (in DB already)
- FBwhQ6OWb5x1EpTVuGRjAL — Weekly 90s-00s Singles Dinner, HONG KONG group (averagerichcantonese; in DB already) — HK slice note

## Notes
- Meetup.com event pages rotate their WhatsApp links: the 20s-30s group shows an older code (Dt7YTnGWgXIAXEoIjX6xNW) on the Sep-2025 event crawl but a NEWER code (BwiHcaLy6FS3Z3FBwY73WB) in the live group-page HTML. Both returned HTTP 200 + invite_link_type_v2 but empty og:title. Possible the link rotation broke the invite-page metadata — re-curl in a later wave to see if og:title recovers.
- meetup.com HTML fetches via curl are slow (~15s/page); search-snippet harvesting + one targeted curl per group page was the efficient route.
- No /sex/ /xxx/ /adult/ pages visited; no banned-title items kept.
