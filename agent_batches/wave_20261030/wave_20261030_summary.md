# Wave 20261030 — summary (Oct 30, 2026)

## Totals (verified from files on disk, not team claims)
- **518** verified-fresh items across 36 team files
- **296** unverified-pending codes
- **3,496** leads
- **Net for merge: 492** (518 − 13 pre-existing slips − 4 cross-team extra copies − 9 channel-format items)

## Top contributors (fresh)
1. team18 cricket/sports — 211 (net 209 after 2 pre-existing slips)
2. team24 deep-search newdirs — 50
3. team36 gaming — 37 (9 are channel-format `/invite/` links — see flag below)
4. team23 scholarship — 22 (net 13 after 9 pre-existing slips)
5. team35 freelance/study — 22 | team29 EU/UK classifieds — 19
6. team19 crypto/earning — 15 | team15 DE/NL universities — 14
7. team10 Ecuador/Uruguay/Paraguay — 13 | team33 Portuguese — 10 | team31 Arabic EG/MA/DZ — 10 | team26 South Asia org/NGO — 10 | team21 health/cooking — 10

## New domain discoveries (harvest targets for next waves)
- **groupor.link** (team34) — NEW global directory, 28 categories, 180+ countries, codes in `/group/invite/whatsapp/<code>`; richest new vein. Skip its Adult/18+ category.
- whatsgroupjoinlinks.com (team24, 29 live), whatsonly.com, groupsinvite.link (team24)
- whtsagrouplinks.com, whatgroups.com, groupsnest.com, groupwa.link, whatspgroupslink.com, whatgrouplinks.org (team25; JS-gated, browser needed)
- thewhatspgrouplinks.com (team34; high dead rate)
- tikane10.com, mstaml.com, anyquizi.com (team32, Arabic Gulf)
- appgrouplink.com/scholarship-whatsapp-group-links, scholarhunter.com (team23)
- englishums.com, vocabineer.com, mrmrsenglish.com (team35, 2026 education pages)
- groups1.com (team18, 185/231 live — healthy)
Caution: groupwa.link self-describes as "SexGroup links" — apply porn filter per group. whatgroups.com listicles ~99% dead.

## New retirements / exhaustions (add to the retired list)
- groupjoin.link Kenya tag pp.3-4: 404 (single 20-result page)
- groupjoin.link USA tag ?page=3 empty; UK tag ?page=2 empty; Nigeria tag 8 pages fully covered
- groupjoin.link Indonesia city tags (surabaya/medan/semarang/makassar/yogyakarta/palembang/denpasar): all 0 groups
- groupjoin.link EU country tags: porn-saturated, skip
- groupjoin.link Balkan tags: fuzzy junk, useless; no AL/BA/XK/ME directory pages exist on whtspgrouplink
- groupjoin.link gaming tag: ~1,172 groups, only pp.1–12 covered — **pp.13+ is the follow-up vein**
- grouplinkshare.com Bangladesh: exactly one page exists, all dead/dupes
- whtspgrouplink SG/MY: only 3 pages (MY all dupes, SG dead); Mekong: no VN/MM pages; LA/KH all dead
- grouplink.com.in Malayalam pages: all dead/dupes; Malayalam Islamic live codes were pre-existing dupes
- whtspgrouplink Europe Jobs page: fully stale (its "manually verified Jan 2026" claim is false); uclm.es PDF fully stale
- whts.club static listings: all dead; wagroupslink freelance listicles all dead; groupjoin.link Uganda/Ghana tags hide codes behind JS Join buttons
- whatsgroulinks.com poetry page (Aug 2026): 0/10 live; Sweden has no public WhatsApp invites (Discord/Facebook); Japan/Taiwan expats use KakaoTalk/LINE
- Angola: almost no public group invites (channels instead)

## Method findings
- groupjoin.link paginates via `?page=N` query params, NOT `/page/N/` paths (404)
- Verification (HTTP 200 + meaningful og:title) works from most sandboxes but is **egress-IP-dependent**: some sandboxes get JS-gated/403/timeout for ALL codes (teams 3, 4, 8, 16, 17, 32). Teams there correctly banked to pending/leads instead of guessing.
- Egress workarounds that worked: curl `--resolve` via DoH (team20), `--tlsv1.2` (team26), explicit `-x "$https_proxy"` (team21), r.jina.ai reader proxy (team22), search-backend text crawl (team30)
- Rule validation: fake codes return HTTP 200 + empty og:title; live codes return the group name — the gate is sound where egress allows it

## ⚠️ Merge-time flags (for parent_verify_merge)
1. **Drops (13 pre-existing in groups.json):** team23 ×9, team22 ×2, team18 ×2 — those teams' dedupe reads were stale; their other items are fine.
2. **Cross-team extra copies (4):** `Hx5F66PdTFW5KyuA2ATODg` (01+02), `CljXPE6aLOvCTIUooUzLd4` (05+19), `DJbjdFvzNjOGx7ksEYOT1J` (05+19), `HW4VpGfWp8aFeTRJOBU8Ow` (18+24) — keep one each.
3. **team36 channel-format (9 items):** `https://chat.whatsapp.com/invite/<16-char>` — these are WhatsApp **channel** links, not group invites; they fail the 22-char schema. Exclude unless the parent decides channels belong on the site.
4. **RESCUE (3 verified-live codes in no fresh file):** team22 verified these but excluded them as non-poetry — all NEW vs the union: `JbU2xvAO72JB0seQKPCam0` (Islamic Status, Islamic), `ITE018KuLvO8ticFwczRbX` (Islam forever, Islamic), `JRPGdICdSdEDNSpdOrxwi1` (اصلاح خواتین women's guidance, Community & Social). Add them to the merge.
5. **Re-verify watch:** team12's 24 items used a weaker criterion (HTTP 200 + invite-app shell, no og:title) because their sandbox gated everything — re-verify before merge.
6. **Collision watch:** team29 excluded 5 French carpool codes as "claimed by another team" — no completed team reported them; check they aren't lost.
7. **Pending-file semantics differ:** team05's 194, team11's 23, team02's 85, team24's 864 (team24_work/), team06's 10, team07's 16 pending entries are **dead-code logs**, not candidates — add them to the union/dead list to skip re-checks, don't re-verify as candidates.
8. Mid-run appends to `dedupe_union_codes.txt` by individual teams caused lost-yield confusion (teams 13, 29 dropped verified items assuming sibling claims). Recommend: freeze the union during the wave and make merge-time dedupe the single authority.

## Big lead pools for browser/egress-capable follow-ups
- team04: 2,406 Indonesia leads (pp.31–220) — needs curl liveness pass
- team25: 662 listicle leads across 6 new domains — needs live browser (JS join buttons)
- team32: 67 Arabic Gulf codes — needs curl verification pass
- team28: 33 groupjoin UG/GH detail URLs — needs live browser
- team22/27/31/11/35: YouTube-truncated and JS-gated codes (~50 total)
- team36 note: `groupwa.link` gallery and `whtsa-gaming` page still unmined (Cloudflare)
