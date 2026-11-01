# TEAM 19 leads — whtspgrouplink.com SEA country pages (2026-10-29)

## Result: ZERO fresh codes — slice fully covered already
- Scraped all 5 country pages in slice: Singapore (investment + jobs), Malaysia, Laos, Cambodia.
- Extracted 76 unique chat.whatsapp.com invite codes (86 raw rows incl. dupes).
- Dedupe vs groups.json (38,755) + .existing_codes.json (73,873) union (73,874): ALL 76 codes already present → 0 fresh, 0 pending, no verification curls needed.

## Pages scraped (all HTTP 200)
- https://whtspgrouplink.com/singapore-investment-whatsapp-group-links/ (15 groups, table layout)
- https://whtspgrouplink.com/singapore-jobs-whatsapp-group-links/ (17 groups, list layout)
- https://whtspgrouplink.com/malaysia-whatsapp-group-links/ (26 groups, list layout)
- https://whtspgrouplink.com/laos-whatsapp-group-links/ (33 groups, list layout)
- https://whtspgrouplink.com/cambodia-whatsapp-group-links/ (10 groups, list layout)

## Coverage gaps (no pages exist on this site)
- **Vietnam**: NO country page on whtspgrouplink.com (checked full post-sitemap.xml, 503 URLs; also tried viet/saigon/hanoi variants).
- **Myanmar**: NO country page (checked myanmar/burma/yangon variants).
- Site has NO general "singapore-whatsapp-group-links" page — only the investment + jobs variants above.

## Out-of-slice fresh directories on same site (for other teams)
- https://whtspgrouplink.com/thailand-whatsapp-group-links/
- https://whtspgrouplink.com/philippines-whatsapp-group-links/
- Category index: https://whtspgrouplink.com/category/international-whatsapp-group-links/ (lists country posts incl. Belize etc.)

## Notes / flags
- Site serves two URL forms: chat.whatsapp.com/<code> and chat.whatsapp.com/invite/<code> — both handled.
- Site recycles the SAME invite code under DIFFERENT group names on the Singapore jobs page (e.g. code E6ausk1jN4K8L75HC0std9 listed as both "NHS Interview Insight" and "Retail & Cashier Openings"; G6ojkp9m1Dy2y2wdrBHAh4 as "BCA GLOBAL AGENCY" and "Freelance & Tutor Gigs"; DmVXKkCq6JhH3BIFAD2Ykz as "Singapore part time jobs indian" and "Clinic Assistants Singapore"). Deduped by code, first name kept. These look like stale/recycled listings — parent may want to flag the site as low-trust for this page.
- Page fetches were flaky (2 pages returned HTTP 000 / truncated 15KB on first attempt); retries with --retry 2 succeeded. Allow generous timeouts for this host.
- Never visited any /sex/ /xxx/ /adult/ pages (none encountered in slice).
- No banned-content titles found in the 76 extracted names; content filter found nothing to drop (all were dupes anyway).
