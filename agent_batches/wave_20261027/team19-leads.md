# Team19 — USA regional — wave 20261027

## Counts
- Verified (team19-fresh-usa.json): 3
- Unverified-pending (team19-unverified-pending.json): 3
- Dropped as already in the existing catalogue (dedupe): 8
- Total fresh candidates checked: 14

## Dedupe
Checked every candidate code against BOTH
`~/workspace/whatsapp-groups-site/groups.json` (38,051 groups) and
`~/workspace/whatsapp-groups-site/.existing_codes.json` (73,169 codes, union covers the groups file).
Dropped as duplicates: SET Underground Los Angeles, Pvolve Challenge Chat,
New York SBKZ Congress Community, Full Moon Drum Circle Miami Beach,
Feel Good Fridays Austin, and all three directory codes from the USA page
(USA United, USA Muslim Network, College Gals USA).

## Verification method and caveat
- Spaced curl with a browser User-Agent, as specified. First pass with a
  10 s timeout returned HTTP 000 for all six fresh candidates (VM egress
  was slow, not a WhatsApp block); a retry pass at 25 s returned HTTP 200
  for all six. Verified = HTTP 200 AND non-empty og:title.
- Verified titles: "Ask Jackie" (Los Angeles Relationships Chat),
  "Spirit Embassy Illinois", "Meet Me at the Tee".
- Pending reason: HTTP 200 but EMPTY og:title on two attempts each
  (Weill Cornell Student Community, UChicago GPHAP Social Group,
  Miami Crypto Chamber of Commerce) — treated as dead/empty per the rules,
  not as verified.
- NOTE on one pending invite: the UChicago group was published in
  /invite/ form, so its pending invite is kept as
  https://chat.whatsapp.com/invite/BYMEUqshxH1K6xpID5OmAk rather than the
  plain form, to preserve the exact published link. Convert only after a
  successful re-check of the plain form.
- Images in the verified file are the groups' own pps.whatsapp.net
  og:image values. No source names, source URLs or personal info appear
  in any name or description. No hard-porn groups were kept; the
  girls/friendship/dating groups found were kept in scope (one verified).

## Sources actually used (all NEW, none from the banned/retired lists)
- Search-snippet raw invite URLs from: a Los Angeles relationships podcast
  page, a Chicago church cell-group post, a University of Chicago graduate
  programme newsletter, a Miami golf-community interview, and a Miami
  crypto chamber listing.
- Directory page read in full (names only, codes hidden behind Join
  buttons): the USA page on wagroupshub.com — its three extractable codes
  were all duplicates, so nothing from it survived.

## Excluded on purpose
- meetup.com US pages (slice ban) — all meetup-sourced codes dropped,
  including Death Valley, Seattle tea/philosophy/climbing, Miami dance
  and Central Florida adventure codes.
- docs.google.com SAS Alumni city clubs (slice ban) — Boston, Chicago,
  Dallas-Fort Worth, New York, San Francisco Bay Area, Washington DC codes.
- pickupultimate.com (slice ban).
- School-internal / minor-adjacent groups — LaGuardia (NYC) tech and
  IEP/504 parent chats, Miami Beach Senior High PTSA grade chats,
  Saranac Lake camp parent updates, UTEP class chat, Seattle school
  rapid-response groups. Not listed anywhere in the outputs.
- Truncated codes from video descriptions (incomplete, unusable).

## Leads for a follow-up pass (codes NOT extracted — need a live-browser pass)
These directory pages list promising USA city groups but hide the invite
code behind a "Join" button, so no code could be taken from text alone:
- Chicago page on whtspgrouplink.com — Private job in Chicago, Illinois
  Friends Zone, Trip to Chicago, people of Chicago, Chicago Broadcast,
  Chicago Gaming Group, I need some friends in Chicago, and more.
- Los Angeles page on thewhatspgrouplinks.com — Los Angeles Friends Chat,
  California Jobs Updates, Los Angeles Business Networking, LA College
  Students Network, LA Events and Party Updates, Los Angeles Foodies, and
  about 30 more LA/California groups.
- USA page on wagroupshub.com — USA Universities, USA Women, Truck Driver
  in New York, Amazon USA and ISKCON USA sections (further codes beyond
  the three already deduped above).
- Friendship page on whatgroups.com — "Meet new friends in Alabama /
  Connecticut / Florida / Hawaii" and "US Citizen" groups.
- Girlfriend page on techsslash.com — city-named groups for Indianapolis,
  Charlotte, Texas, Florida, New York, Denver, Washington and Boston.
- A jotform community form (code HoNmJy8x2WkHIlXRJDgtBr) surfaced in a
  New York search but with no confirmed US location, so it was not used.
