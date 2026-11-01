# Team27 — Nepal + Sri Lanka truncated-code re-extraction (wave_20261029)

## Counts
- VERIFIED (team27-fresh-nepal-srilanka.json): **7** — NP 4, LK 3
- UNVERIFIED-PENDING: 0 (every candidate extracted verified on first pass; nothing junky left)
- Truncated leads resolved: 6 of 7 from wave_20261027/team08

## Verified breakdown (7)
- By country: NP 4, LK 3
- By category: Education 2, Sports 2, Finance 1, Gaming 1, Jobs 1
- Method: re-extracted FULL codes from YouTube video descriptions via the public Piped API (api.piped.private.coffee/streams/<id>); the JSON `description` field embeds the full href even when display text is truncated with "...". Direct YouTube HTML fetch was captcha-blocked from this egress. Then curl-verified (HTTP 200 + invite_link_type_v2 marker + meaningful og:title), 8s spacing, no 429s.

## Resolution of the 7 team08 truncated leads
1. ✅ H14LFi5Jp5R... → **H14LFi5Jp5RFedECQrAXz3** — "Nepal Next Official" (NP scholarship updates, Education) — verified
2. ✅ KsLZKwPvsFj... → **KsLZKwPvsFjDXJ9caCLMMH** — "Free Trading with Sandeep" (NEPSE watchlist, Finance) — verified
3. ✅ J4Tk0fR4mHq... → **J4Tk0fR4mHq6ck7cqa0abf** — "En CEE Warriors" (CEE 2083 entrance notes, Education) — verified
4. ✅ FR9CYaOF4Qh... → **FR9CYaOF4QhBOdUN3HZkBu** — "Royal Gaming Studio" (Nepali gaming, Gaming) — verified
5. ✅ IlrWDEsJgrG... → **IlrWDEsJgrGFqOM0I6Xr1P** — "ARV Loshan Sports 4" (Tamil cricket news, Sports) — verified
6. ✅ CkimXfurZTa... → **CkimXfurZTa4nRlJ42bYIz** — "ARV Loshan Sports 1" (Tamil sports, Sports) — verified
7. ❌ **JjpM0O1aALU... (LK government jobs group) — STILL UNRESOLVED.** The exact prefix finds no indexed video; multiple Sri Lanka vacancy videos fetched instead show different full codes. Needs a live-browser extractor (task instruction) or a re-scan of Sinhala-titled vacancy videos. NEVER complete it by guessing.

## Bonus (not from team08 leads)
- **IUbvckRyYgvJmfUSIQ19qo** — "Lanka Career 8" (LK jobs) — full code found in a search-result snippet of a LankaCareer YouTube Short; verified HTTP 200 + og:title. Dedupe: fresh.

## Dedupe
- All 7 codes checked against the union of groups.json (38,755 groups) + .existing_codes.json (73,874 codes): ALL NEW, 0 drops.
- Porn/xxx filters: nothing adult encountered in this slice's candidates.

## Leads / notes for future passes
- JjpM0O1aALU... (LK govt jobs, Sri Lanka government vacancies 2026 video description) — the one remaining truncated lead; needs live-browser extraction.
- hubrecipes.com Nepali-girls listicle and wagroup.in/tag/lanka-whatsapp-groups/ both timed out via curl (rc=28, twice each) and were NOT retried further; the hubrecipes page is adult-content heavy and should be skipped anyway (its clean entries, if any, need live-browser fetch).
- wagroup.in lanka feed contains a blocked "Escort service Sri Lanka Ladies only" entry — escort content, excluded per rules; do not ingest from that page without filtering.
- wagroupnest.com Sri Lanka page is RETIRED (per task) — not touched.
- Method note: api.piped.private.coffee is currently reachable from this egress and returns full YouTube descriptions (display hrefs included) — useful for any future truncated-code re-extraction. YouTube direct HTML is captcha-blocked; Invidious instances were dead; Lemnoslife API returned empty.
