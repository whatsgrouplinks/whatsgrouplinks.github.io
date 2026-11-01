# TEAM 02 — groupjoin.link USA pages 3–30 — leads & notes (2026-10-29)

## Coverage
- Walked `https://www.groupjoin.link/country/united-states?safeSearch=blur&page=N` for **pages 3–30** (20 groups/page, 560 group objects parsed).
- Pages 1–2 were already harvested by another team (out of slice, skipped).
- Pages 31+ (~66 pages total per the site's "1,309 local communities" count) NOT walked — time budget reached. No 404/empty page hit; pagination continues past p30.

## Yield
- **Fresh (verified): 5** → `team02-fresh-groupjoin-usa.json`
- **Pending (unverified): 6** → `team02-unverified-pending.json`
- 1 candidate dropped as duplicate of existing union (`B99CC9khOiuKCSD4Bcjrn6` "Canada,Jamaican and United States Business Center" — already in groups.json).

## Key findings
1. **USA pages 3+ are ~90% adult/explicit spam** (site category "Adult": VIP/leak/teen/"content seller" groups, suggestive-emoji titles). All dropped per content rules. SafeSearch=strict does NOT change server-side listing (only client blur) — verified by fetching p3 with `safeSearch=strict`, identical 20 groups.
2. **Heavy "Moviesdark" piracy spam** across Entertainment (same title+desc reposted under many codes: "The Unholy Trinity", "Man with No Past", "Alien: Romulus", "M3GAN 2.0", "Gladiator II", "Sarzameen", "Hallow Road", "Death of a Unicorn", "Until Dawn", "Hell of a Summer", "Thunderbolts*", "Sitaare Zameen Par", "Control Room", "Jurassic World Dominion", "A Normal Woman"). All dropped as automated spam reposts.
3. **Listing data is stale for some codes** — verified og:title on the live invite differed from groupjoin.link's stored title:
   - `BFPAM00IyqFIxrFrPYfdQh`: listed as "Stuffs For Sell At Aforable Prices", actually "Love 💕💕 friend... Hook ♀️♀️" (hookup-seeking) → DROPPED.
   - `BYP5odTy101KqXJ9HernNW`: listed as "Make money 🤖 💰🧮" (forex), actually "TS Academy | New Members Hub" → KEPT under real name (Community & Social).
   - `InhnQNPIhJCGUOGvPSrqWC`: listed as "Meet new friends to jazz with", actually "Real state" → DROPPED (vague, listing wrong).
4. **Fraud-adjacent drops**: "Gift Card Redeem Plug" (gift-card redeeming), "ALL COUNTRIES KYC BUYER HACKSMITH HUD" (KYC-account buying), "Usa kyc instant pay" (buy/sell accounts tag) → all DROPPED.
5. Pending items returned HTTP 200 + invite_link_type_v2 but **empty og:title** and generic placeholder og:image — likely dead/revoked invites; kept in pending per spec, not fresh.

## Name-only leads (dropped, for reference — do NOT add without re-verification)
- "Usa kyc instant pay" (fraud-adjacent, p18) · "Gift Card Redeem Plug" (p8) · "General" (vague title, p20) · "Real state" (vague, p23) · "HIP/HOP UNIVERSE" (symbol-jumbled title, p22) · "this group is no longer on whatsapp BEELZUBUB'fans" (dead-group notice, p5).

## Out-of-slice directories found
- None — stayed strictly on the USA country listing. (groupjoin.link also exposes /category/*, /city/*, /tag/* pages; not touched.)

## Technical note for future runs
- groupjoin.link is a Next.js app; group data lives in `self.__next_f.push([1,"…"])` flight chunks, **split mid-string across chunks**. Parse by extracting + JS-decoding + concatenating all stream-1 payloads first, then brace-matching `"group":{…}` objects. Naive regex on raw HTML misattributes titles (verified by cross-check).
- Invite links in `link` fields sometimes carry tracking suffixes (`?mode=gi_t`, `?s=cl…`); strip at `?` for the code.
- Never visited any /sex/, /xxx/, /adult/ pages (only the country listing pages).
