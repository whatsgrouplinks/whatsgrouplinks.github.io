# Team29 — Entertainment + Health + News + Buy Sell — wave 20261027

## Counts
- Verified (in team29-cat-entertainment-health-news.json): 3
  - Buy Sell: 2 — Sasta Offers Deals 2.0, MS Shopping
  - Health: 1 — Oriflame Shopping (LK)
  - Entertainment: 0 verified, News: 0 verified
- Unverified-pending (in team29-unverified-pending.json): 43
  - Entertainment: 37, Buy Sell: 4, News: 1, Health: 1
  - All 43 returned HTTP 200 but an empty og:title on spaced curl, so per rule they are NOT verified. Do not import them as verified; re-check later.
- Dropped / excluded:
  - 2 porn-named candidates dropped by the porn filter: "Bangla vabi xxx video", "xxx video animal" (hubrecipes movies page).
  - 1 curl-verified code dropped as out-of-slice: GOYQuZGnwlYF66AcARZmWA — directory name "New Outfits" (Buy Sell), but live og:title is a religious group name, not a Buy Sell group. Not in either JSON file; do not import it as Buy Sell.
  - Girls/friendship/dating groups were NOT removed (per task, only hard porn is blocked); none are in the final files except as directory-listed entertainment/shopping items.

## Sources used (all NEW for this wave, none from the retired list)
- hubrecipes.com — movies page, news page, and active-groups page (Movie / Entertainment / News / Shopping sections). Main yield: most verified-candidate pool came from here.
- walinking.link — individual group pages: Oriflame Shopping (Health/Beauty/Fitness, Sri Lanka) and MPYA ONLINE (Health, Tanzania; pending, empty og:title).
- wahublink.com — entertainment, movies, news, online-shopping pages. Yield was mostly already in the existing set; 1 verified (MS Shopping).
- groupwa.link, whtspgrouplink.com, 77links.com — checked (homepages + category/weight-loss pages). Almost all their Entertainment/Health/News/Buy Sell codes were already in groups.json + .existing_codes.json (73,170 unique codes checked); only 1 new code surfaced and its directory name was unusable, so it was not used.
- Cloudflare-blocked via curl (not used for codes): whatgroups.com, whtsgrouplink.com. No codes were taken from them, and no chat link was fetched through the browser tool after a browser fetch of a chat link was rejected.

## Dedupe
- Full existing code set = groups.json (38,051 groups) UNION .existing_codes.json = 73,170 unique invite codes. Every candidate was checked against both before verification. No verified or pending code is in that set.

## Verification method
- Spaced curl (1.5 s between requests, browser User-Agent) to each chat.whatsapp.com invite. Verified ONLY on HTTP 200 + non-empty og:title. Verified items use the live og:title (cleaned) as name and the og:image pps.whatsapp.net URL where present. Pending items keep directory names, image "".
- Note: most hubrecipes movie groups returned HTTP 200 with og:title "" — per the task rule they are pending, not dead-confirmed. A re-check with a different method may recover some, but they must not be promoted without a non-empty og:title.

## Files
- team29-cat-entertainment-health-news.json — VERIFIED only (3 items)
- team29-unverified-pending.json — 43 items, HTTP 200 + empty og:title
- team29-leads.md — this file
- groups.json and any deploy output were NOT modified.
