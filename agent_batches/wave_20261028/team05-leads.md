# team05 — wave 20261028 — Fresh new directories, N–Z

Slice: fresh WhatsApp-group directory sites whose names start with N–Z, not
covered in wave 20261027 and not retired. Checked against
`wave_20261027/manifest.txt` before scraping: none of the sources below
appear in that manifest. Did NOT touch groupjoin.link, grouplinkshare.com,
whatgroups.com, wahublink.com, whatsshare.com, groupchatlink.com,
77links.com, whatsgrouply.com, mdecommunity.com, any A–M directory, or any
retired source. Did NOT modify groups.json, generate.py output, or
~/workspace/wgl-deploy/.

## Sources / pages scraped
- https://whatasgrouplink.com/ (homepage, W) — 305 unique invite codes found
  in the page HTML (including links carrying query strings, e.g.
  `?s=cl&p=a&ilr=4`, which a naive quote-terminated regex misses).
- https://whatsgroulink.com/ (homepage, W) — 179 unique invite codes found.
- Attempted, 0 codes extracted (see Next-pass leads):
  - https://whatzgrouplink.com — curl returned an empty reply / timed out;
    browser text fetch worked but does not expose the invite codes.
  - https://www.whtsagrouplinks.com/ — Cloudflare challenge page in the
    browser fetch; curl returned IncompleteRead (0 bytes).
  - https://whatsgroupslinkz.com/2024/12/25/drama-whatsapp-group-link/ —
    curl returned a 16-byte empty response.

## Counts
- Candidates examined: 478 unique codes across the two scraped homepages
  (305 + 179, 6 overlapping between the two sites).
- Dedupe drops: 432 codes already in
  `wave_20261028/dedupe_union_codes.txt` (73,684-code union).
- New candidates (not in the union): 46.
- Verified: 11 — HTTP success + non-empty, meaningful og:title, used
  verbatim as the group name, in team05-fresh-newdirs-nz.json.
- Pending: 35 — HTTP 200 but empty og:title under the spaced-curl check,
  so per the task rule they are NOT in the fresh file; names in
  team05-unverified-pending.json are the source listing names, to be
  re-checked before any merge. (One pending code, CcJWspzY08aApIKkUFVprU,
  returned a valid-looking invite page but with an empty og:title, so it
  stays pending under the rule.)
- Internal duplicates within outputs: 0. Verified-vs-pending overlap: 0.
- Verified-vs-dedupe-union overlap: 0 (asserted in script).
- Porn drops: 0. No candidate carried an explicit porn term or porn emoji
  in its verified og:title. Girls/friendship/dating groups were NOT dropped.
- Meaningless/symbol-only titles: none among the verified set; pending
  items are pending for empty og:title, not for title content.

## Verification method
Spaced curl (1.5 s between checks, browser-like User-Agent) of
https://chat.whatsapp.com/<code>, og:title extracted from the response.
A bare generic "WhatsApp Group Invite" title would have gone to pending;
none of the verified titles was generic. One verified title contained
HTML entities (stylised text) and was decoded to plain text
("KHALID DRY FRUITS MUNDA") before staging.

## Verified list (11)
Boss Level Profits, Programming skills, News Temple -17, Blogs group,
TikTok Ads Agency, SHOPIFY KING, KHALID DRY FRUITS MUNDA, SURAT JOB,
Kohinoor, amazprime.com 12, kingpain.official surat.

Note on "amazprime.com 12": that is the group's og:title verbatim, kept
as the name; the description contains no URL or source name.

## Next-pass leads
- whatzgrouplink.com: retry with a live-browser pass — its homepage lists
  hundreds of groups (Work from Home, Movies, Islamic, Gaming, Funny,
  Dating, USA, Education, News, Girls sections) but curl from this VM gets
  an empty reply.
- whtsagrouplinks.com: retry once the Cloudflare challenge clears; its
  Lahore and category pages looked rich in search snippets.
- whatsgroupslinkz.com drama page: retry; the 16-byte response suggests
  blocking rather than an empty page.
- whatasgrouplink.com category pages beyond the homepage (Girls, Jobs,
  Trading, etc.) may hold further codes not on the homepage.
- Re-check the 35 pending codes later: several may gain an og:title if
  WhatsApp's invite page renders differently on retry.
