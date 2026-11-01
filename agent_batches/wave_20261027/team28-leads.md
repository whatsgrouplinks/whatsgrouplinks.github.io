# team28 — Islamic + Community — wave 20261027

## Counts
- Verified (team28-cat-islamic-community.json): **0**
- Unverified pending (team28-unverified-pending.json): **9**
  - Islamic: 6 — Islaaminfo A46, Quran Aur Sahih Hadees, Al Nahyan Islamic Group, Beautiful Islam, With Allah Comes Ease, Blessings Learn Arabic
  - Community & Social: 3 — Parents at Home (US), Community Groups London (GB), Deeper Connections (GB)
- Harvested before dedupe: 21 candidates; **12 dropped as already in the existing code set** (groups.json UNION .existing_codes.json, 73,169 codes checked).
- Porn filter: no hard-porn groups harvested or kept; none removed on that ground.

## Sources used (new for this wave; excluded sources avoided)
- meraonlineworld.com Islamic listing page (raw invite codes visible in page text)
- Meetup public community/event pages (Parents at Home, Community Groups London, Deeper Connections)
- Also checked, yielded no usable full codes: 77links.com Islamic page (links not exposed as text), whatgroups.com Islamic page (bot-check wall, no data), groupwa.link homepage (names only, no codes in snippet), groupda.com / grupbul.com / whatzgrouplink.com (all on the excluded list — not used)

## Verification gap — parent action needed
- **No invite was verified in this run, so the verified file is intentionally empty.**
- VM outbound curl timed out on every host (example.com and listing sites, 20–30s timeouts), so the required spaced-curl WhatsApp check could not run here.
- Fetching invite pages via the page-text tool returned HTTP 403 from WhatsApp, and per the runtime instruction those invite fetches were not retried or routed through another tool.
- The 9 pending items are therefore **unverified candidates only**: deduped and porn-screened, but NOT live-checked. A parent/eligible agent should run the spaced curl check (HTTP success + non-empty og:title) on the 9 pending invites before merging; dead/revoked/empty-title ones should stay in pending, not move to verified.

## Notes
- JSON items follow the exact schema; names/descriptions contain no source name, no source URL, and no personal info.
- groups.json, generate.py output and ~/workspace/wgl-deploy/ were not touched.
