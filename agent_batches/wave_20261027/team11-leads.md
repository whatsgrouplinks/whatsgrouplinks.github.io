# Team11 — Vietnam + Thailand — wave 20261027

## Counts
- Verified: 0
- Unverified-pending: 11 (5 VN, 6 TH)
- Dedupe pool checked: 73,170 codes (groups.json 38,051 groups UNION .existing_codes.json)
- Candidates dropped as already existing: 5

## Verification status — IMPORTANT
Spaced curl checks from this VM returned HTTP 000 with empty body for EVERY
invite tested, and the same curl test also returned nothing for a plain
example.com check. This is a VM network block on direct curl, NOT proof that
any invite is dead or revoked. Per the task rule (verified only on HTTP
success + non-empty og:title), verified is therefore 0 and all 11 fresh
candidates are in unverified-pending for re-verification from a host where
chat.whatsapp.com is reachable. Do NOT treat pending as dead.

## Sources consulted (new, not retired, not wave-20261026 team06 meetup pages)
- Public web search for Vietnam and Thailand WhatsApp groups, Hanoi/Ho Chi
  Minh City/Da Nang/Hoi An and Bangkok/Pattaya/Phuket community listings.
- A Bangkok directory listing page: its invite links could not be extracted
  here — one invite fetch was blocked (403) and that page was not pursued
  further, so none of its groups are claimed in this batch.
- Non-meetup public listings: a Hanoi dance/fitness studio listing, a
  Hoi An meditation event listing, a Hanoi coffee course page, a Ho Chi
  Minh City design community page, a Thailand news community page, a
  Bangkok school booster news page, and a Bangkok triathlon club page.
- Excluded by design: all meetup.com pages, all retired sources named in
  the task, and any candidate already in the 73,170-code dedupe set.

## Porn filter
No hard-porn groups included. No candidate was removed under the porn
filter; girls/friendship/social groups were not targeted for removal.

## Files
- team11-fresh-vietnam-thailand.json — verified only (empty this wave, see above)
- team11-unverified-pending.json — 11 candidates, same schema, for re-verification
- team11-leads.md — this file

No changes were made to groups.json, generate.py output, or wgl-deploy.
