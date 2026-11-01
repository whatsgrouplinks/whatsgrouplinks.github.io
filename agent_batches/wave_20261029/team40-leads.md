# TEAM 40 — Business category discovery (wave_20261029, 2026-10-29)

## Summary
- Fresh sources found and scraped: 4 (groupsinvite.link, thinkingoutsidethesandbox.ca, groupsnest.com, whatzgrouplink.com) + hubrecipes.com business listicle checked.
- Dedupe base: 73,874 existing codes (groups.json + .existing_codes.json union).
- Verified & fresh: **1** (team40-fresh-cat-business.json).
- Pending (codes not verified — invite pages returned HTTP 200 + invite_link_type_v2 marker but EMPTY og:title, i.e. likely expired/revoked): **10** (team40-unverified-pending.json).
- HTTP 429: never hit; verification loop ran cleanly with 7s spacing.

## Name-only leads (groupsinvite.link business directory — codes hidden behind JS join button)
https://groupsinvite.link/group/business/ lists 43 business groups, but the "Join Group" button's chat.whatsapp.com code is resolved client-side via obfuscated LiteSpeed JS — no direct codes in HTML. Needs a live-browser click to harvest. Names:
- Buy and sell (buy-sell marketplace), KMPOFFICIAL / KMPOFFICIAL 2 / 3 / 4 (Business, Entertainment, Social Issues), KMPofficial (Karachi Market Place), Exclusive investment group, Online Business Guidelines, Fast Delivery Data Bundles, HESTY AURA PERFUMERY - SKINCARE AND WELLNESS, Launching Soon, Tenshi Sky Community, EVOLUTION TRADE, TURKISHEXPORTER VETEMENTS, WHATSAPP GROUP SALE & BUY TEAM 1, Asim Digital Hub, SHIVAM INTERLOCKING BRICKS&WORS 2019, Gold XAUUSD Scalping Blueprint, USA KYC & Business Hub, Connexion Gratuite Netflix IA Produits digitaux (French, digital products), Digital business hub, Diya Agency's - 9, Online business and side hustle ideas, Shivan Creation, وجع الشركات | الحل عندنا (Arabic, business services), امیران سیر ترابر (Persian, international transport company), Earn with me, DELHI NCR SME Forum, GlobalBridge Imports, Shree Sai Traders Nashik, DuoEcom Digital, RSK Saree Resellers Grp, Fragrance - Buyer/Seller, ALL INDIA RESELLERS 46, Cosmetic Reseller, RSK Kurtis Resellers grp1, Reseller, Jobs update and business, Curyus, Mlm software develop, Bangalore Startup's, Bangalore First Business Meet, REpro BC Bangalore
- Related SEO article page (groupsinvite.link/business-whatsapp-group/) yielded exactly 1 extractable code: the verified Shivan Creation item above.

## Out-of-slice fresh directories (for other teams)
- https://whatzgrouplink.com — 111 NEW (non-dupe) codes found on homepage across Sports/Gaming/Entertainment/Islamic/News/Funny/YouTube/Dating/Work-from-home/Earning sections; only the business-flavored ones were checked by this team. Rich harvest for sports/gaming/entertainment teams.
- https://groupsnest.com/ — 28 codes on homepage; 23 already existing. New ones found: 5 (all dead — see pending).

## Exhausted / zero-yield pages
- thinkingoutsidethesandbox.ca/135-best-business-whatsapp-group-links/ — 53 business codes extracted, but 53/53 already in existing set (dedupe 0 new). Last verified Sep 1, 2026.
- hubrecipes.com/active-business-whatsapp-group-links/ — 57 codes; 55 already existing; 2 new codes had only generic page labels ("WhatsApp group India", "Lahore WhatsApp group link") and dead invites — dropped as unusable.
- groupsnest.com Business-ish new codes (4 of 5) all returned empty og:title → likely expired.

## Notes
- WhatsApp invite HTML: empty og:title + absent group-name JSON blob = reliably distinguishable from live invites (live ones carry og:title + embedded group name). Method validated against the one verified item.
- No adult/18+ pages visited; no source names/links or personal info included in items.
