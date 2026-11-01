# Team05 wave 20261027 — Morocco + North Africa (MA, DZ, TN, LY)

## Counts
- Verified (team05-fresh-morocco-northafrica.json): 0
- Unverified-pending (team05-unverified-pending.json): 1
  - Human Unity - Rabat (MA, Community & Social) — code NOT in the full dedupe union, but shell curl verification returned HTTP 000 (see below), so it is pending, not verified. Re-run curl verification (HTTP success + non-empty og:title) before any merge.
- Name-only leads in this file: 12 (Libya, no codes — see below)
- Dedupe-dropped: 1 — a Tunis community group code was already in the full union (groups.json codes + .existing_codes.json) and was dropped, not included in either JSON file.
- Porn-blocked: 0. Girls/friendship/dating groups were not removed (none surfaced with codes in this slice).

## Dedupe basis (checked)
- groups.json: 38,051 groups, 38,017 invite codes extracted
- .existing_codes.json: 73,169 codes
- Union checked: 73,170 codes. The 1 pending code and the 1 dropped code were both checked against this full union.

## Verification caveat — shell curl egress dead this run
- Spaced curl (1-2 s, browser User-Agent) to the pending invite returned HTTP 000, with no file/title.
- The same shell curl also returned HTTP 000 for example.com and google.com in a control check, so 000 here does NOT prove the invite is dead — it proves shell egress was dead at verification time.
- Parent action: re-run the curl verification for the 1 pending item when egress recovers; promote only on HTTP success + non-empty og:title.

## New directory checked (not a wave-20261026 source, not on the retired list)
- A country-page directory listing Libya groups (Libya page reached via its own related-groups links from its Belize page). Its Libya page lists group names only in text fetch; its Join links resolve to chat.whatsapp.com invites that text fetch does not expose.
- One Join-link resolution attempt via text fetch was blocked with HTTP 403; that attempt was NOT repeated, and no code from that blocked attempt is included anywhere in this batch. All other Join links on that Libya page were therefore left unresolved — hence the name-only list below, for a live-browser Join-click pass.
- Deliberately NOT used: groupjoin.link, groupwa.link, whatsagroupslinks.com, whtspgrouplink.com, whtsgrouplink.com, thewhatspgrouplinks.com variants already noted in wave-20261026 leads, and every domain on the task retired list. The diplomariot Morocco article was already noted in wave-20261026 as advice-only with zero group links and was not re-scraped.

## Name-only Libya leads (NO codes — do NOT guess codes, live-browser Join-click pass only, then dedupe + curl-verify)
All country LY:
- Benghazi group for Jobs News — Jobs
- North Africa News — News
- Libya Politics & Economy — News
- Tripoli Job Seekers — Jobs
- Libya Trade Market — Buy Sell
- Tripoli University Notes group — Education
- Scholarship Updates Libya — Education
- Discover Tripoli group — Community & Social
- Benghazi Tourism Friends — Community & Social
- Libya History & Culture — Community & Social
- Libya Study Friends Chat — Education
- Libya Youth Chat — Community & Social

## Slice gaps
- Algeria (DZ): no new extractable codes found in this run — searches surfaced only the already-avoided directories and advice/news pages with no invites.
- Morocco (MA): only the 1 pending Rabat item above; no other new extractable MA codes found.
- Tunisia (TN): only the dedupe-dropped Tunis item; no other new extractable TN codes found.
- Libya (LY): 12 name-only leads above; no codes extracted (see Join-link block above).
- No groups.json, generate.py output, or deploy files were modified.
