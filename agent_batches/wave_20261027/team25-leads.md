# Team25 — Gaming — Wave 20261027

## Counts
- Verified: 0
- Unverified-pending: 2
- Leads / candidates examined with full codes: 10
- Dropped as duplicates (already in groups.json + .existing_codes.json union, 73,170 codes): 8

## Files
- team25-cat-gaming.json — verified only (empty this run)
- team25-unverified-pending.json — 2 items, both fresh codes

## Sources checked (non-banned, non-retired)
- Unstop BGMI / Brawl Stars tournament pages (plain-text invite codes in event text)
- DGL Sri Lanka PUBG Mobile tournament page (plain-text invite code)
- Star Husnain / HaasH / X-Trader gaming pages via search snippets (codes already in existing set — dropped)
- Directories inspected by name only: 77links.com gaming page, bgmi.in BGMI page, groupwa.link gaming section, whtspgrouplink.com gaming section, whatstele.com PUBG page — their "Join" links resolve to chat.whatsapp.com invites, but those invite URLs could not be harvested this run (see Gap below). No codes from those directories are included, and no code from any banned/retired source (asiamediajournal, joingroupslink, techapkzone, whtsagrouplinks, whatzgrouplink, grupbul, groupsnest, etc.) is included.

## Verification (spaced curl, browser User-Agent, 1-2s sleep)
- Both fresh candidates returned HTTP 200, but og:title was empty in the curl response.
- Per task rule, empty-title links go to unverified-pending, not verified. They are NOT claimed dead — the title was empty in this fetch, so a later re-check may verify them.
- No hard-porn groups were found among the candidates; none were removed on that filter.

## Gap / note for parent
- Direct curl egress timed out early in the run, then recovered for the two verification fetches above.
- One directory invite-link resolution attempt via the text-fetch tool was rejected (403) for a chat.whatsapp.com invite; that route was not retried, and that invite is excluded from all output. The parent / a live-browser-eligible agent would need to resolve the 77links / bgmi.in / groupwa.link / whatstele directory "Join" links to harvest the bulk of this slice.
- No files outside the team25 output dir were modified; groups.json and deploy dirs untouched.
