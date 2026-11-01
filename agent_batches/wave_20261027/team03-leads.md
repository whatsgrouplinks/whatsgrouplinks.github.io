# team03 (wave 20261027, Ghana + West Africa: GH, CI, SN, CM)

## Counts
- Verified (fresh, deduped, curl HTTP 200 + non-empty og:title): 6
- Unverified-pending: 1
- Dropped as already in existing set (groups.json UNION .existing_codes.json, 73,170 codes): 2

## Verified (in team03-fresh-ghana-westafrica.json)
- GH, Education: Elican School All Alumni Group — og:title "ELI SCH ALL ALUMNI GROUP"
- GH, Education: NextDeadlines Group10 — og:title "NextDeadlines Group10"
- CM, Community & Social: CAMEROON DIASPORA YOUTHS — og:title "CAMEROON DIASPORA YOUTHS"
- CM, Entertainment: Know IT- (Dr Roy ft BP Conceptz) — og:title "Know IT- (Dr Roy ft BP Conceptz)"
- SN, Entertainment: PENCHMI VILLAGE — og:title "PENCHMI VILLAGE"
- CI, Technology: Max it Assistance — og:title "Max it assistance"

## Unverified-pending (in team03-unverified-pending.json)
- GH, Community & Social: Mercy Heart Global — curl HTTP 200 but EMPTY og:title on the retry pass (first pass: connection failure). Per task rule it is pending, not verified. Do not merge until a live check returns a non-empty title.

## Dedupe drops (already in existing set, not in any output file)
- Uncle Ne Cameroon jobs group (CM) and the YALI West Africa agribusiness group — both invite codes already present in groups.json / .existing_codes.json.

## Sources used (individual group pages found via web search, NOT directory re-scrapes)
- A school homepage in Accra (GH), a scholarship-guide page for a University of Ghana programme (GH), a Cameroon diaspora youth membership form (CM), a Cameroon music-event listing (CM), a Senegalese drum-and-dance event page (SN), and an app-store review reply from the Côte d'Ivoire operator (CI).
- Deliberately NOT used: schoolandcollegelistings.com (any country), human-unity.org, steemit / findglocal singletons, groupjoin.link, whtspgrouplink.com, thewhatspgrouplinks.com, whatsagroupslinks.com, webnews21.com, and all other retired / wave-20261026 sources listed in the task. No source name or URL appears in any JSON name/description.
- No porn/xxx groups encountered; no groups removed on that filter.

## Leads for a live-browser pass (no codes, NOT in JSON files)
- GhanaInfo.net Ghana category groups (Intercessors, houses/cars for sale) and the Senegal page on whatsagroupslinks.com: codes hidden behind Join buttons — already noted in wave-20261026 team10 leads; not re-chased here.
- Côte d'Ivoire pan-Africa museum-education groups (CECA Africa report): Africa-wide, not CI-specific, so not claimed as CI groups.
- No CI-specific directory with exposed codes was found this wave; CI coverage rests on the single verified Max it Assistance group above.

## Verification notes
- First curl pass (1.5s spacing, browser User-Agent) returned HTTP 000 for 5 candidates and 200 + real titles for 2; a second spaced pass (2s spacing) then returned HTTP 200 for all 5, with 4 real titles and 1 empty title. The 000s are treated as transient connection failures, not as dead links — the retry titles are the basis for the verified/pending split above.
- groups.json and .existing_codes.json were NOT modified; no files under ~/workspace/wgl-deploy/ were touched.
