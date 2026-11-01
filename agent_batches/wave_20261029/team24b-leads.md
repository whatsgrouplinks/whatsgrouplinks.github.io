# TEAM 24B — Los Angeles slice leads / notes (2026-10-29)

## Sources scraped
1. thewhatspgrouplinks.com/los-angeles-whatsapp-group-links/ — LA-dedicated listicle. 15 distinct invite codes extracted (table rows + bullet list). Names mapped 1:1 to codes.
2. whatgroups.com/whatsapp-group-links-usa/ — California table section parsed; 7 in-slice California codes (one already counted from source 1).
3. wahublink.com/usa-whatsapp-group-links/ — 52 code rows parsed; ALL USA-general (Islamic, girls, business, faith), no LA/California-specific rows. Out of slice, nothing taken.
4. wagroupshub.com/usa-whatsapp-group-links/ — same USA-general content as #3 (no LA/California rows). Out of slice, nothing taken.

## Dedupe result
- 21 distinct in-slice candidates extracted total.
- 15 of 21 already in groups.json / .existing_codes.json union (73,874 codes) — both directories heavily recycle the same codes across many names.
- 6 new codes sent to verification.

## Verification (curl, 7s spacing, no 429 encountered)
All 6 fresh codes returned HTTP 200 with `invite_link_type_v2` marker, BUT `og:title` was EMPTY on every page (WhatsApp serves a generic no-title invite shell — likely revoked/stale links). Per rules, empty og:title = NOT verified. All 6 went to `team24b-unverified-pending.json`. No fresh items.

## Name-only / dup leads (no action needed)
- "Los Angeles City Updates Group" — code JhfSEG02df01EL35xp30po reused for 3 different names on the same page (placeholder pattern) — code already existed; dropped as dupe.
- Meetup.com public snippets surfaced 3 LA groups (Kind Steps LA, Samba Los Angeles, Extremely Shy Sunday Hike LA) — all 3 codes (GAeWwpNo2TI1sSipfdXR7q, FiTOPFWk5bN3fpLllFfjcd, FjOx9EXXKTuAUhMeCdPyLJ) already in the existing union. No new harvest.
- techapkzone.com "Minecraft Los Angeles"/"Minecraft CA" — gaming listicle, codes not visible in snippets; out of slice as directory (gaming, no LA codes captured).
- techsslash.com "400+ Active American WhatsApp Group Links" — RETIRED domain, not touched. (Contains a "call girl" row anyway — would be banned.)

## Notes / flags
- HEAVY CODE RECYCLING: both LA directories map one code to many unrelated names and repeat the same 15 codes across the whole "870+ links" claim. Verified against WhatsApp directly: all fresh samples resolved to title-less shells. Treat un-curated "1000+ links" listicles for this slice as low-trust.
- No /sex/ /xxx/ /adult/ pages visited. No retired domains touched (whatsappgrouplink.org, wappgrouplinks.com, whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, elsabagh.com, techsslash).
- Remaining budget unused: no further LA-specific directories surfaced in 3 search rounds; recommend a future team try "hollywood", "beverly hills", "santa monica" micro-area directories, or Facebook/TG LA community posts.
