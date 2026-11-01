# team14 leads — wave 20261026 (codes NOT extracted, do not merge as groups)

## Name-only leads (invite codes hidden behind Join buttons / JS — need a live-browser pass; NO codes invented)

- grupbul.com (new Turkish/international directory, not in task ban list, not in scrape_log or prior waves):
  - "Yalnız Tərtibatçılar" — developers community, English/Azerbaijani — Technology
  - "Cairo Medics" — healthcare professionals and students community — Health
  - "Welcome To Our Group" — general friendship/social group — Friendship
  - Page text never exposes a chat.whatsapp.com code on any of the three pages checked; curl to the site times out from this sandbox.
- Warsaw 20s/30s international social meetup (Warsaw, PL) — event page says a WhatsApp groupchat link exists but the link itself is not exposed in page text — Community & Social / Friendship.
- Warsaw Global community (Warsaw, PL) — groups are behind a sign-up/verification form, no codes visible — Community & Social.

## Dead / no-link pages examined

- thediplomariot.com Morocco WhatsApp article — advice text only, contains zero group links.
- get.whtsgroupslinks.com — how-to guide article only, no group listings with codes in page text (also noted by teams 01/08 this wave).

## Abandoned (already harvested / claimed — NOT re-scraped)

- satyainpoland.com (Poland listing page) — harvested by team37 in wave 20261025 (8 codes exposed in full HTML, 5 kept); only 1 code visible in plain text, already known.
- dubai-forever.com GCC jobs page — fully harvested by team17 in wave 20261025, all codes already known.
- activewagroup.com — claimed by team04 in this wave (wave_20261026); also noted in wave 20261025 team09 candidates file. Not touched.
- groupjoin.link, whtspgrouplink.com, groupda.com, groupizo.com and all other task-banned domains — not touched.
- groupwa.link /sex/ and /xxx/ pages — not visited, per instruction.

## Blocker (affects verification, not candidate extraction)

- Sandbox curl egress is dead this run: curl returns 000 even for example.com and google.com, and for chat.whatsapp.com. Page-text fetching works, but WhatsApp invite pages deny text fetch (403) and that denial was not retried. Therefore NO item in this team's batch could be curl-verified here, so the verified file is empty and all 11 fresh candidates went to team14-unverified-pending.json for the parent's re-verification pass.
