# TEAM 36 — Health category discovery (wave_20261029)

## Fresh directories used (not retired)
- **grupbul.com** — WhatsApp group directory (Turkish, English listings). Health groups sit in "Other" category. Invite links are NOT in the page HTML; each group page has a `/redirect/<gid>/<n>` link which returns `refresh: 7; url=https://chat.whatsapp.com/invite/<code>` in the response headers (no-JS curl follow works via the header). CAUTION: page titles can be stale vs the live group og:title — "Atomy" page resolved to a live group titled "Freshzone", "Humble Motivation" page resolved to "Dubai Visa". Always trust the live og:title.
- **whtsagrouplinks.com** — "7900+ WhatsApp Group Links 2026", updated ~1 day ago. Health hits: "Healthy india & weight loss from Home", "Home Med Suppliers". Structure: `<li>NAME – <a href="chat link">Join</a></li>`. Sub-pages (all-whatsapp-group, other-whatsapp-group-links, indian-groups) had zero health hits.
- **whatzgrouplink.com/fitness-whatsapp-group-links/** — Fitness listicle, 8 named groups. (Only this site's jobs/Class12th pages are retired; fitness page is fine.)
- **77links.com** — Directory with 100+ groups per page; homepage + /pakistan-whatsapp-group-links/ yielded health hits ("Mental Health Support", "Skin Damage Problems", "GYM Bodybuilding", "Beauty of Love"). Structure: wp-block-columns with `<p>NAME: desc</p>` then a button column with the chat link.

## Name-only leads (not harvested — no direct invite or out of budget)
- "Navsari Health & Fitness" — listed on thewhatspgrouplinks.com Navsari page (individual code not extracted).
- "Smart Health and Fitness" — newgrouplinks.pk USA page (domain RETIRED, skip).
- "Meditation Experts Group", "Yoga Is Life", "Yoga Classes" — whatstele.com yoga page (domain RETIRED, skip).
- "HEALTH HARMONY - WEIGHT LOSS JOURNEY S4" — 21-day wellness program behind a Google Form (no direct invite).
- "Fitlife66" — paid diet/fitness coaching site, no public group link.
- "FOX Ladies Gym" — groupsgyani.org WhatsApp CHANNEL (channel, not group — out of schema).
- "TOI Health" — grupbul.com WhatsApp channel page (channel, not group — out of schema).

## Exhausted / dead ends
- grupbul.com site search (`/arama?q=...`) returns "no results" for health/fitness/gym/yoga/diet — site search is broken; web search (site:grupbul.com) is the working route.
- grupbul +18-chat / adults-chat categories — NEVER visited per rules.
- whtsagrouplinks.com sub-pages: all-whatsapp-group, other-whatsapp-group-links, indian-groups — 42 items each, no health matches.
- whatstele.com (yoga listicle), newgrouplinks.pk (USA health group) — both RETIRED, skipped.
- palify.io "Gujarati Diaspora Wellness Initiative" — article content only, no invite code.

## Notes
- 24 candidates harvested; 12 were already in the existing-codes union (other teams covered: IMA GROUP, Cairo Medics, Herbal Life Nutrition, Medical Info, Muslean Fitness, Aadil Shaikh Fitness, The Fitness Store, Fitness Mania, Health & Fitness groups, Fitness Boys, Premedical Group and Job, GYM Bodybuilding). Dedupe did its job.
- Verification: 12 codes checked at ~7s spacing, no HTTP 429. 8 verified (200 + non-empty meaningful og:title + invite_link_type_v2). 4 returned HTTP 200 + v2 marker but EMPTY og:title → staged as pending (Meditation And Life, Mental Health Support, Skin Damage Problems, Beauty of Love).
- og:image URLs captured were truncated HTML entities — staged as "" per schema.
- Freshzone is staged as "Buy Sell" and Dubai Visa as "Jobs" — both clearly mismatched with Health but verified and allowed as non-health categories.
- All names cleaned of emojis/symbols; no banned content; no source names/links in descriptions.
