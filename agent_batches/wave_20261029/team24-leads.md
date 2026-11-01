# TEAM 24 — Los Angeles slice leads (wave_20261029, 2026-10-29)

## Result summary
- Verified (fresh): **0** — no code passed the strict verification gate.
- Pending (unverified): **63** candidates in team24-unverified-pending.json.
- Fresh file: `team24-fresh-losangeles.json` is an empty array (honest zero).

## Why zero verified
- Verified 60 codes with curl (HTTP 200 on all, `invite_link_type_v2` marker present),
  but **og:title was empty** on 51 of 51 non-duplicate codes checked. Empty og:title on a
  200/V2 response = the invite link is expired or revoked (confirmed by re-fetching and
  inspecting the raw HTML — the meta tag is literally `content=""`).
- 13 further codes hit the 60-verification cap and were not checked at all.
- No HTTP 429 encountered; verification gate stopped purely on the og:title rule.
- Per the task rules these went to pending with `_verified: false` instead of fresh.
  **Recommendation for the merge step: treat pending items as likely-dead; consider
  dropping the 51 empty-og:title codes, or re-checking them once before publishing.**

## Sources harvested (directories scanned)
1. thewhatspgrouplinks.com/los-angeles-whatsapp-group-links/ — LA-specific table + listicle
   (12 codes extracted; 9 were already in the dedupe union, 3 were fresh but dead):
   - LA Events & Party Updates (dead)
   - Los Angeles Tourists & Visitors Chat (dead)
   - Los Angeles Jobs for Freshers (dead)
2. whatgroups.com/whatsapp-group-links-usa/ — USA + California listicles (150 name↔code pairs;
   61 fresh codes, all with empty og:title = dead; California rows were 100% dupes).
   Note: names here are generic-USA, not LA-specific; kept only because no USA team is
   present in this wave yet. A future USA-team sweep should take over this page.
3. Meetup/allevents search results — 4 LA event groups found
   (Kind Steps LA, Samba Los Angeles, LA Beach Volleyball, Set Underground LA),
   ALL 4 codes already in dedupe union. No harvest.

## Fresh name-only leads (codes already in dedupe — NOT re-submitted)
- Kind Steps LA Volunteer Community (LA volunteer/kindness community)
- Samba Los Angeles Batucada (Santa Monica rehearsal group)
- LA Beach Volleyball Learn and Play (Ocean Park)
- Set Underground LA Event Group (warehouse music events Q&A)
- California groups from whatgroups listicle (Fly to California, California hub,
  CHRISTIANS S.S., Free join California group, Dating California group,
  California Queen Videos, California groups, California News, Jobs Ideas) — all dupes.

## Exhausted pages (nothing more to squeeze)
- Both directories above: all visible name↔code pairs extracted.
- Meetup/allevents/dicotech/pvolve LA event pages: individual event invites, all dupes.
- Retired domains not touched (whatsappgrouplink.org, wappgrouplinks.com,
  whatsappgroupjoinlinks.com, grupodewhatsapp.com, wagroupnest.com, elsabagh.com, techsslash).

## Out-of-slice note
- whatgroups.com USA listicle contains many generic-USA groups (stock, business,
  girls/friendship, Islamic sections). If a dedicated USA slice exists in a later wave,
  re-harvest that page — links appear heavily rotated/recycled, so re-verification is essential.

## Dropped
- "Muslim kids quran academy" (BWhfWK1PkETCetdU0SXzcC) — school-age-sounding name, dropped per rules.
- "Roman Catholics" name cleaned from stylized unicode to plain text.
- No banned/adult content encountered in harvested set.

## Time used
- ~30 min of 35 budget. Verification (60 × ~7s spacing) was the dominant cost.
