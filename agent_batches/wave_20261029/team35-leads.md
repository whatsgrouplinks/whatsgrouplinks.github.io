# TEAM 35 — Gaming category discovery — 2026-10-29

Slice: GAMING. 6 fresh directory sources (none in retired list, no overlap with other teams' slices).

## Sources used
1. **whtsagrouplinks.com/pubg-whatsapp-group-links/** — PUBG store listicle. 14 links scraped, 9 already in .existing_codes.json, 5 new → ALL VERIFIED.
2. **77links.com/amazing-gaming-whatsapp-group-links/** — Top-100 gaming listicle. 81 unique codes scraped, 80 already existed, 1 new ("Gaming World") → pending (empty og:title).
3. **asiamediajournal.com/gaming-whatsapp-group-links/** — tablepress gaming listicle. 50 rows scraped, 25 new after dedupe → 3 verified (Flanky Gaming; PES HERO7; Youtube Video Sharing → Entertainment; Billionaire Community → Community & Social; Jaggii 99 → parked pending, name mismatch/category unclear), 22 pending (empty og:title).
4. **whtspgrouplink.com/** (homepage gaming sections) — 167 unique codes scraped; ALL already in existing set. Zero new.
5. **killarnation.com/free-fire-whatsapp-groups-link/** — Free Fire listicle, page claims Sept-2026 manual verification. 6 groups, 1 dup, 5 new → 4 verified, 1 pending (TaskPaisa × Free Fire, empty og:title).
6. **whatsonly.com/** — BGMI + Free Fire sections. 20 rows scraped, 14 dups, 6 new → all pending (empty og:title).

## Outcome
- Fresh verified: **13** (incl. 2 category re-homes: Youtube Video Sharing → Entertainment; Billionaire Community → Community & Social)
- Pending unverified: **29** (24 with http 2xx + v2 marker but empty og:title; 5 mismatched/unclear incl. Jaggii 99)
- HTTP 429: not hit. All 42 codes verified without rate-limit stops.

## Exhausted pages
- https://whtspgrouplink.com/ — 167 unique invite codes, all already in .existing_codes.json; nothing new.
- https://www.whtsagrouplinks.com/free-fire-whatsapp-groups-links/ and /bgmi-whatsapp-group-links/ — linked but not separately scraped (pubg page covered most; codes likely already in set). Future team may sweep them.
- https://www.techapkzone.com/free-fire-whatsapp-group-links — RETIRED per slice list; not touched.
- 77links.com gaming page — fully harvested (only 1 new code).
- asiamediajournal.com gaming page — fully harvested (tablepress, 50 rows).

## Out-of-slice fresh directories (NOT in retired list — suggested for other teams)
- **killarnation.com** — also has BGMI/esports listicles beyond the Free Fire page I used.
- **whatsonly.com** — big directory (jobs, entertainment, funny sections); I only took BGMI + Free Fire.

## Notes
- Dedupe: union of groups.json (38,750) + .existing_codes.json (73,873). ~150 scraped codes dropped as already-seen.
- Name source: verified og:title from WhatsApp (cleaned of decorative unicode) where available; listing name otherwise. Two mismatched titles re-homed to correct categories (Entertainment, Community & Social). "Jaggii 99" (listed as "Indian Gamers") parked in pending — real group, unclear category.
- og:image: none of the verified invites returned a usable og:image; image fields are "".
- No adult/suggestive content scraped; no /sex/ /xxx/ /adult/ pages visited. No personal info collected.
- Page HTML quirk: killarnation.com and whatsonly.com serve content twice — once as escaped JS blobs, once as real HTML; extractors matched the real HTML.
