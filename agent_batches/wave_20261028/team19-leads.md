# Team19 — wave 20261028 — University / club / community

## Counts
- Candidates found via web search: 63
- Verified (fresh file): 19
- Pending (unverified file): 5
- Dedupe drops (code already in dedupe_union_codes.txt): 39
- Porn drops: 0 (no hard-porn titles found; no girls/friendship groups dropped)
- Total accounted: 63 = 19 + 5 + 39

## Sources / pages scraped (search results, NOT wave 20261027 sources)
- UK student-union society pages: Sheffield (Pharmacy, Radical Youth, Rugby League, Irish Dance, Cycling), UCL (Red Star, Football, Volleyball, Amnesty, RUMS Hockey, Boxing), LSE (PPE, Hedge Fund, Poker), QMUL (Hockey, Salsa, Music), Bristol (Arab, Hindu, Sailing), Cardiff Clay Pigeon, Kent Cricket, Southampton (Surgical, Riding, Darts), Warwick Darts, UWE Archery, UWL Football, Leeds Boat Club, Edinburgh Cycling, Surrey Kannada, Aston Computer Science, Royal Holloway Indian Society
- Community / church / mosque pages: Lighthouse campaign archive, Kingdom Vineyard St Andrews students, Nairobi Chapel GriefShare, School of Life volunteer page, Katong Presbyterian bulletins, Exeter Mosque, Salafi Centre Manchester, Madina Mosque Oldham, Masjid-e-Ali Luton
- Club / hobby pages: University of London Mountaineering, TU Dresden BDF group, Shinfield CC, Harold Wood CC, Tramway FC (South Africa), Auckland Women's Football, Founders Running Club Kyiv, UpGrade Chess Club Baku
- India university / event pages: NIT Jalandhar Mechanical Engineers, ISTE GCE Kannur, BMN College IntelliNova, HNBGU course notices, National Youth Parliament brochure
- NOT re-scraped: wave 20261027 manifest sources (Kenyan universities, KCA, Kenyatta Energy Eng Club, Oviedo, ESI/UCLM, Lisbon PDF, Bogota pages, Cluj-Napoca, Karadeniz, UChicago, Chicago church, Miami listings) and all retired directories listed in the task.

## Verification notes
- Method: spaced curl (1.5s, browser User-Agent) of https://chat.whatsapp.com/<code>; verified only on HTTP 200 + non-empty meaningful og:title, with og:title used as the group name.
- First pass was intermittent (HTTP 000 on 5 codes, empty og:title on 4). A spaced re-check recovered 4: the Lighthouse-archive code's og:title is "Classmates of Orthodox Theology and Methodology" (used as name, country set to International as no country was evidenced on that page), "RY Sheffield", "RY Sheffield Freshers", and "UOLBC 2026/27".
- Pending (5) — og:title empty on both passes, so names below are source-context names only, NOT og:titles; re-check before any merge:
  - QMUL Salsa Society (C9cYGDkvlHO38YqOPl65rN)
  - Founders Running Club Kyiv (JGkMxRcPtpBIkKGNO3kjSX)
  - Southampton Darts Club (KatlupYbHTRG4UDp3nYd2K)
  - ISTE GCE Kannur (KbRUie0DzAREWsEZ6vfCno)
  - BMN College IntelliNova (GRbmCLXso6HFPLDca1lUF2)
- Note: the Warwick Darts code appeared with a space in the search snippet; the joined 22-char code verified as "Warwick Darts 2026/27".
- Note: many UK student-union codes were already in the dedupe union (39 drops) — that source family is largely exhausted for fresh codes.

## Next-pass leads
- Sheffield SU, UCL SU, LSE SU, Bristol SU, Southampton SU society indexes still list many societies, but most published codes already dedupe out; try less-indexed unions (e.g. Manchester, Leeds, Glasgow, Nottingham, Birmingham city-university pages) and non-UK unions (Australia, South Africa, India state universities).
- Church/mosque notice PDFs and parish newsletters: several published codes, but many are channels (whatsapp.com/channel) not groups — filter those out.
- Local sports-club sites (cricket, rowing, running) outside the UK SU system had the best fresh hit rate in this pass.
