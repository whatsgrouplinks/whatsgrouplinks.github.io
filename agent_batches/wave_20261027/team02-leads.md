# team02-fresh-tanzania — LEADS (name-only / Join-button, no invite recorded)

These groups appear on a fresh Tanzania teachers directory page, but no
invite code could be recorded for them in this run, so they are NOT in the
verified or pending JSON files. They need a live-browser Join-click pass.

## Join-button groups with no recorded invite
- Physics, Chemistry and Biology teachers — secondary teachers page; this
  Join button is shared by several labels on the same page (Competent
  teachers, Walimu wa CWT, Form four Teachers, Standard four Teachers).
  WhatsApp verification for that button was blocked in the text-fetch
  service and was not retried, so no invite is recorded here.
- Tuition teachers — listed on the teachers pages with no working link
  in the page HTML.
- Walimu Tanzania — listed on the teachers pages with no working link
  in the page HTML.
- All teachers tz — listed on the teachers pages with no working link
  in the page HTML.

## Notes
- Dedupe base: groups.json (38,051 groups) UNION .existing_codes.json
  = 73,170 codes; every verified/pending code above was checked against
  both and was not present, and no code is repeated within the outputs.
- Excluded on this run: all wave-20261026 / banned sources, and the
  explicit sexual-content directory found in search (no items taken
  from it, per the porn filter).
