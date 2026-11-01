# TEAM 34 — Sports category discovery leads (2026-10-29)

## Counts
- Fresh (verified): 0
- Pending (unverified): 16 (11 Sports, 5 Gaming)

## Fresh directories harvested (new, not in retired list)
- whtsagrouplinks.com sports page — 36 invite codes extracted, 33 already in dedupe union, 3 fresh (1 live, 2 dead)
- wahublink.com sports page — 47 invite codes extracted, ALL 47 already in dedupe union (exhausted, do not re-harvest)
- whatsonly.com homepage — 255 invite codes extracted, 69 fresh; sports/IPL sections kept (4 Sports + 5 Gaming), rest out of slice
- whatgroups.com cricket page — 97 invite codes extracted, 4 fresh, all Sports

## Out-of-slice fresh directories (for parent/other teams)
- whatsonly.com has large fresh sections: YouTube/sub4sub (~10 codes), online shopping Pakistan (~15 codes), online earning (~6 codes), friendship/girls (~5 codes), crypto/trading signals (~2 codes). Codes with names recorded in /tmp/team34/whatsonly_rows.json if parent wants them.
- whatgroups.com cricket page name overlap: code EoWKGzpzKYI4cOcumfzx62 appears on whatgroups as "CRICKET ICC" and on whatsonly as "Active Sub4Sub" — recycled/renamed group, staged under cricket name.

## Verification notes
- 15 of 16 candidates: HTTP 200 BUT og:title empty + invite_link_type_v2 content empty = WhatsApp dead-link template (expired/revoked invites). Re-checked 2 of them — still empty. Sent to pending.
- 1 candidate (J9ISIE2dN9WKSGHfADc3AB, listed as "ONLY CRICKET SCORE GURUP"): live group but og:title = "Self drive cars available" — name mismatch / group repurposed as car-rental chat. Sent to pending with flag.
- No HTTP 429 encountered; verification completed fully (16/16 codes, no stop needed).

## Name-only leads (not staged, out of slice or duplicates)
- wahublink.com sports: full table already in union — skip future runs.
- whatsonly.com: ~186 fresh codes in other categories (YouTube, shopping, earning, friendship) available for other teams; same-domain pages (telugu/malayalam/islamic sections) may overlap teams 10/11/20.
- whtsagrouplinks.com also has cricket-football-kabaddi related pages (cricket-whatsapp-group-links) — partially harvested.

## Flags
- High dead-link rate on these listicles (esp. whatsonly/whatsappgrouplink-style pages) — listings are stale; prefer recency-dated pages next wave.
