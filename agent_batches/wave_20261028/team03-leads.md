# Team03 — grouplinkshare.com slice (wave 20261028)

## Results
- VERIFIED: 124 items in `team03-fresh-grouplinkshare.json`
- UNVERIFIED-PENDING: 220 items in `team03-unverified-pending.json`
- Candidates found: 344 (all with invite codes in page HTML)
- Dedupe drops: 0 — all 344 codes were fresh against the 73,684-code
  `dedupe_union_codes.txt` union, and 0 cross-page duplicates within this slice.
- Porn drops: 0 — no hard-porn/xxx titles found (titles scanned for porn/xxx
  terms and porn emojis). Girls/friendship/chat groups were kept, as instructed.
- Meaningless/symbol-only drops: 0 (all directory labels had real names).

## Sources / pages scraped (grouplinkshare.com only; Bangladesh page EXCLUDED)
Homepage link discovery found 14 listing slugs; the Bangladesh slug was
deliberately NOT scraped (wave 20261027 slice). The 13 pages scraped:
- pakistani-whatsapp-groups-links (30 cards)
- indian-whatsapp-groups (90 cards)
- world-wide-whatsapp-group-links (54 cards: Sri Lanka, Thailand, Indonesia,
  Philippines, Malaysia, Vietnam — 9 each)
- nepal-whatsapp-group-links (15 cards)
- uae-whatsapp-group-links (15 cards)
- girls-whatsapp-group (50 cards)
- girls-chat-whatsapp-group-links (30 cards)
- business-whatsapp-group-links (10 cards)
- chat-whatsapp-group-links (10 cards)
- entertainment-whatsapp-group-links (10 cards)
- jobs-whatsapp-group-links (10 cards)
- online-earning-whatsapp-groups (10 cards)
- study-whatsapp-group-links (10 cards)

Note: the task brief's examples (Nigeria, Kenya, USA, UK, Philippines country
pages) do not exist on this site — its only country pages are Pakistan,
India, Bangladesh (excluded), Nepal, UAE and Worldwide. No other grouplinkshare
pages were found via homepage/category navigation, so the slice is exhausted.

## Verification method
- Spaced curl (1.2s sleep, browser-like User-Agent) of each
  https://chat.whatsapp.com/<code>.
- VERIFIED = HTTP 200 AND a non-empty, meaningful og:title; the og:title is
  used verbatim as the group name (whitespace collapsed only).
- PENDING = HTTP 200 but EMPTY og:title (all 220 pending items; no HTTP
  failures occurred — all 344 returned HTTP 200). No item had the bare generic
  "WhatsApp Group Invite" title.
- Verified names, categories (allowed list only) and countries were mapped
  from the og:title plus the directory card's category/country context;
  pending names are cleaned directory labels (emoji/member-count/tags stripped)
  and are provisional until a live-browser recheck supplies a real og:title.

## Verified / pending by page
| Page | Total | Verified | Pending |
|---|---|---|---|
| Pakistan | 30 | 30 | 0 |
| India | 90 | 6 | 84 |
| Worldwide | 54 | 31 | 23 |
| Nepal | 15 | 5 | 10 |
| UAE | 15 | 1 | 14 |
| Girls (Indian) | 50 | 17 | 33 |
| Girls chat | 30 | 25 | 5 |
| Business | 10 | 0 | 10 |
| Chat | 10 | 0 | 10 |
| Entertainment | 10 | 0 | 10 |
| Jobs | 10 | 0 | 10 |
| Online earning | 10 | 9 | 1 |
| Study | 10 | 0 | 10 |

Verified countries: PK 30, International 35, IN 22, LK 9, ID 7, VN 6,
NP 5, TH 5, PH 4, AE 1.

## Observations
- Pakistan's page verified 30/30; Worldwide verified 31/54 (Sri Lanka 9/9,
  Thailand 5/9, Indonesia 7/9, Philippines 4/9, Vietnam 6/9, Malaysia 0/9).
- The five generic category pages (business, chat, entertainment, jobs,
  study) verified 0/50 — their links return HTTP 200 with an empty og:title,
  which looks like placeholder/dead links rather than live groups.
- India's page verified only 6/90 despite specific-looking card names; most
  of its links likewise return an empty og:title.

## Next-pass leads
- Recheck the 220 pending items in a live browser: if a real og:title
  appears, they can be promoted to verified with no further dedupe needed
  (already deduped against the union). Highest-value pending sets: India
  (84), Girls (33), Worldwide Malaysia (9, all pending), UAE (14).
- No further grouplinkshare pages to scrape in a next pass — all 13
  non-Bangladesh listing pages were harvested. Any new grouplinkshare page
  (e.g. a future country/category slug) would be a fresh source.
- groups.json, generate.py output and ~/workspace/wgl-deploy/ were NOT touched.
