# team15 — Islamic + Community & Social — wave 20261028

## Sources / pages scraped (all NEW for this slice, none from wave 20261027)
- grouplink.com.in Malayalam Islamic page (Oct 2026 update) — names listed, join buttons hide codes; 1 code surfaced (already in dedupe set, dropped)
- wpgroup.in Kerala WhatsApp group page — raw /invite/ codes in page text (Kerala community + Voice of Islam Admission)
- schoolandcollegelistings.com Al-Huda Institute Karachi listing — full raw code in post text
- hillsislamicassociation.org.au (Hills Islamic Association, AU) — raw mosque-community code on homepage
- rips kit / Exeter Mosque / Madina Mosque Oldham / Masjid Muhammad / Idriss Mosque Seattle listings — raw codes, all already in dedupe set
- shenstone-staffs.gov.uk Shenstone Neighbourhood Watch page — raw code
- taranhw.co.za Tara Neighbourhood Watch FAQ — raw code
- tengesai.com Zimbabwe community articles — raw codes (Masvingo, Kadoma, Beitbridge, Harare, Chitungwiza, Marondera)
- docs.google.com Ward 89 resident-info form — raw code
- you.38degrees.org.uk West Thamesmead petition page — raw code
- fishpoolstreet.org newsletter, orchardvillagewaterways.co.za report, compton-surrey.co.uk village page — raw community codes
- Search-snippet raw codes (YouTube Islamic descriptions, mosque pages) — several already in dedupe set

NOT re-scraped: meraonlineworld.com Islamic page, Meetup London community pages (wave 20261027 team28), or any retired source (whatslinkhub, elsabagh, whatsappgrouplink.org, wappgrouplinks, whatsappgroupjoinlinks, grupodewhatsapp, wagroupnest, groupda, groupizo sitemaps). groups.json, generate.py output and ~/workspace/wgl-deploy/ were NOT touched.

## Counts
- Candidates found: 42 (39 first batch + 3 second batch)
- Dedupe drops (code already in dedupe_union_codes.txt, 73,684 codes): 28
  - Includes the grouplink Malayalam Quran 2 code, most wpgroup.in Kerala codes, all rips kit / Exeter / Madina / Masjid Muhammad / Idriss mosque codes, Marondera (ZW), Fishpool Street (GB), and the truncated-snippet-adjacent codes were never counted (see below).
- Verified (spaced curl, HTTP 200 + meaningful non-generic og:title, title used as name): 6
  - Upcoming Courses at DHA Institute (Islamic, PK), HIA - Baulkham Hills Mussallah (Islamic, AU), DA WARD 89 JHB POLITICAL NEWS AND INFO (Community & Social, ZA), West Thamesmead Community Group (Community & Social, GB), Friends of Orchard Village Waterways (Community & Social, ZA), Compton Club Members (Community & Social, GB)
- Pending (HTTP 200 but EMPTY og:title on re-check — code-bearing, never in fresh file): 8
  - Shenstone Neighbourhood Watch Alerts (GB), Tara Caring Neighbor (ZA), Masvingo / Kadoma / Beitbridge / Harare / Chitungwiza community groups (ZW), Aiwa Kerala Community (IN)
- Porn drops: 0 (no hard-porn titles encountered; no candidates dropped on content grounds)
- Out-of-slice / unusable, excluded from both files: wpgroup.in Retail FMCG Jobs Network and GCC News Dubai (Jobs/News, not this slice); grupbul.com group pages (names only, join button hides the code); grouplink.com.in table rows beyond the one surfaced code (buttons hide codes).

## Verification notes
- Spaced curl (~1.5 s between checks, browser-like User-Agent) to https://chat.whatsapp.com/<code>.
- Empty og:title pages return full-size HTML (HTTP 200, ~224 KB) with `og:title" content=""` — treated as unverified, not as dead links; a later re-check may restore titles for the 8 pending items.
- No generic "WhatsApp Group Invite" titles were seen in this batch.

## Next-pass leads (for a live-browser pass — codes hidden behind buttons/QR, not fetchable here)
- grouplink.com.in Malayalam Islamic page: 35 named groups (Malayalam Quran 3/4/7/18, Iqraa Daily, Islamic Speech Live, ISM/MSI/J Media, Voice of Rahmaniyya, Straight Path, Daily Islam 1/2, Islamic Q&A, Voice of Islam, Proudly Muslim, Live Islam, Ashiq E Raza, Deen-e-Mustafa, Allah Ke Bande) — join buttons hide codes.
- grouplink.com.in Tamil Devotional page: Islamic Knowledge + Tajweed Course Tamil rows (same button pattern).
- grupbul.com Islamic group pages (e.g. Islamic Ummah -1, Quran Sunnah True Jannah, Full.Quran) — join button hides the code.
- wpgroup.in Kerala page top table (Bad boys, Best friends, Islam means peace, etc.) — codes hidden behind Link buttons.
- Truncated search-snippet codes (NOT staged, need full code from the source page): Learn from Scholars / Ask Islamic Scholars groups, Darulifta Ahlesunnat group (BaOeONWmGSv...), Chadwick End parish community (GIja...).
- Dedupe note for coordinator: the wave 20261028 dedupe union already contains many codes from these very pages (27 of the first 39 candidates), so re-scraping them yields little; fresh value is likelier from mosque/parish/council sites publishing raw codes, as in this batch's 6 verified.
