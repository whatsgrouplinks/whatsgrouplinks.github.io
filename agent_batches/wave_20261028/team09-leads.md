# team09 — Europe regional (wave 20261028)

## Slice
NEW Netherlands, Belgium, Nordics, Balkans and Eastern Europe pages NOT covered in wave 20261027. No Spain/Portugal, Italy, or France/Germany/Poland sources from wave 20261027 were reused. No retired sources were used. groups.json, generate.py output and ~/workspace/wgl-deploy/ were NOT touched.

## Sources / pages scraped
- Netherlands housing list (city-by-city housing groups: Amsterdam, Rotterdam, Utrecht, The Hague, Groningen, Eindhoven, Leiden, Delft, Amstelveen, Almere, Arnhem, Nijmegen, Breda, Maastricht, Tilburg, Enschede, Haarlem, Zwolle, Wageningen, Leeuwarden, Heerlen)
- Netherlands student/community pages: IHE Delft MSc page, UTwente EST pages, Indian Student Association Delft page, C.O.R.E. Utrecht/Amsterdam/Leiden page, Primal Play Utrecht/Amsterdam pages, Rotterdam Rocks page, Outdoors in Utrecht page, Expat Cinema Rotterdam page
- Belgium: EuroMeet Brussels Meetup page
- Nordics: Nordic Society Stockholm Meetup page, Northern Sweden Meet-ups Meetup page, Stockholm/Oslo/Copenhagen/Helsinki expat and Meetup searches
- Balkans / Eastern Europe: Macedonia directory page (see gap below), Croatia/Serbia/Bulgaria/Albania/Montenegro/Macedonia searches, Prague/Budapest/Zagreb/Belgrade/Bratislava/Vilnius/Tallinn searches — no extractable new codes beyond the Macedonia page
- General directory searches for Netherlands/Belgium/Sweden/Croatia/Serbia pages (no additional extractable codes)

## Candidates found
- 42 candidates collected in total (28 Netherlands housing + 5 other Netherlands community/student + 5 Netherlands student + 1 Belgium + 2 Nordics + 1 other, as counted in the working list; 42 unique codes).

## Verification
- Spaced curl (1–2 s, browser-like User-Agent) of https://chat.whatsapp.com/<code>, checking HTTP status and og:title.
- Only 1 code had a non-empty, meaningful og:title: "Northern Sweden Meet-Ups" (SE).
- The other 8 codes not already in the union returned HTTP 200 with an empty og:title (generic "WhatsApp Group Invite" page) or an empty curl response, so they were staged as pending, never as verified.

## Counts
- Verified: 1 (team09-fresh-europe.json)
- Pending: 8 (team09-unverified-pending.json)
- Dedupe drops: 33 — codes already present in dedupe_union_codes.txt (73,684-code file; 33 of the 42 candidates, including most Netherlands housing codes, the Brussels EuroMeet code, the Nordic Society Stockholm code, and several Netherlands community codes).
- Porn drops: 0 (no hard-porn titles encountered; the one explicit-titled directory result in a general search was not a candidate in this slice and was not staged).
- Within-output duplicates: 0.

## Gap / not completed
- Macedonia directory page: its six "Join" links could not be opened through the text reader (HTTP 403 on the invite URLs). Those links were NOT repeated through another tool and were NOT staged in either file, per the access-denial handling. The Macedonia country page itself is therefore a next-pass lead only, to be re-checked by a live-browser pass if the parent wants it.
- Amsterdam "20s 30s Global Socializing" Meetup page mentions a WhatsApp groupchat link but the code was not exposed in the search snippet — live-browser lead.
- Balkans/Eastern Europe (Croatia, Serbia, Bosnia, Bulgaria, Albania, Czechia, Hungary, Slovakia, Baltics) yielded almost no publicly indexed invite codes in this pass; most community links there are gated behind Meetup/Facebook membership or QR codes.

## Next-pass leads
- Re-check the Macedonia directory page via live browser; re-check the 8 pending codes later (empty og:title may mean revoked/expired, but a re-check costs little).
- Amsterdam 20s/30s socialising, Social Oslo, Copenhagen Global Hangout and Gothenburg Internationals Meetup pages (codes hidden behind membership/event pages).
- University pages in Prague, Budapest, Zagreb, Belgrade, Vilnius and Tallinn (student WhatsApp links are often in PDFs or QR codes, not indexed text).
