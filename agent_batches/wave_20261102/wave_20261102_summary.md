# Wave 20261102 summary — 37 teams (36 + 1 replacement), all complete

- **Verified banked:** 2,624 items (2,620 merge-ready after consolidation dedupe: 1 cross-team dup dropped — team07 code already in team01's batch; 3 union-dups dropped from team24's batch)
- **Pending (next-wave retry):** 14 items (team01×12 transport failures, team06×1, team28×1 redacted-title)
- **Leads banked:** 190 (all in per-team `teamNN-leads.json`)
- **Porn drops (hard-blocked, never written):** ~694 (top: team06 419, team01 184)
- **Merge files:** per-team `teamNN-<desc>.json` in this dir + `coordinator_pickups_verified.json` (2 self-verified handoff codes). DO NOT merge `*-unverified-pending.json` or `*-leads.json`. Manifest: `manifest.txt`.

## Top contributors
1. team01 groupda WP-API categories — 1,271 (all 33 categories paginated to completion; slice fully exhausted)
2. team30 Mexico/Central America — 425 (new directory igrupos.com, 47% live rate)
3. team06 groupjoin.link Indonesia pp.175–220 + 9 gap pages — 273
4. team28 Canada/Australia/NZ — 126 (117 AU trade job-alert groups)
5. team22 Italy — 120 (112 UNICAS/Ferrara university study groups)
6. team03 groupjoin.link deeper categories — 91 (gaming pp.41–202 fully swept)
7. team08b alatekno/carakami Indonesian banked codes — 55 (~10% hit rate, rest expired)
8. team07 new-dir listicles — 36 (wglfinder.com fully server-rendered, money source)
9. team29 Brazil non-porn — 34 (28 regional Vendas groups)
10. team20 Colombia/Ecuador — 26 (elyex.com)

## Review flags for parent (merge decision)
1. team09 item "BITFINEXINVESTS.LTD email address passcode clave gmail zoom meeting Esuela" (code ElxeXs91Xl9Ap9upNObZRD, CM, Crypto) — phishing-flavored keyword-stuffed title, mechanically verified live. Consider dropping.
2. team07 item "PayPal Receiver and Loader" (code H590csE0EGA4SsUF2E2WnD, KE, Finance) — money-mule fraud flavor. Consider dropping.
3. team27 surfaced (dead, dropped) a counterfeit-currency/SSD-chemical scam listing on groupjoin.link USA tag — brief only mandates porn drops; a scam-group policy may be needed for future waves.
4. team21 out-of-slice code verified live: "ANGOLANA" (Iv5kzGuVO9L5wWRZNUzhEr) — self-verified this wave, banked in `coordinator_pickups_verified.json` as AO/Friendship.
5. team31 Gaming handoff code verified live: "Vibe FF ID Selling" (GVRBbh6CPp80EHGg3rRqdI) — self-verified this wave, banked in `coordinator_pickups_verified.json` as International/Buy-Sell.

## Policy questions raised (no mid-wave rule changes made)
- team04/team06: groupjoin.link renders record links as `chat.whatsapp.com/invite/<code>` but the codes are VALID PLAIN group codes (plain URL returns real og:title for live groups; one record pasted a direct-format code identical to its own `/invite/` code). The brief's blanket `/invite/`-exclusion may be overbroad for groupjoin.link specifically. Team06 salvaged these by testing the plain form; team04 excluded 42 Oceania records under the current rule.
- team06: the site sets contentRating=18 + nsfw=1 on ALL records (safeSearch=blur artifact) — correctly NOT used as an adult signal; only category_slug='adult' + keyword/emoji block used.

## Retirement / exhaustion findings (new this wave)
- whtsagrouplinks.com sitemap URLs (team05): all 627 URLs processed — near-100% union overlap, 63/74 fresh candidates dead. Slice DONE; add to retired unless the site rotates fresh links.
- groupda.com WP-API categories (team01): all 33 categories paginated to completion. Next wave: only retry 12 pending + new posts.
- groupjoin.link Indonesia tag (team06): nothing exists beyond page 220 (pp.221/222/225 return 0 records). DONE.
- Central Asia (team10), Mongolia/Caucasus (team16), Myanmar/Khmer/Lao (team19), Philippines (team17), USA regional (team27), Caribbean JM/BB (team13), Baltics (team12): structurally exhausted for curl-based scraping this wave.
- team08's premise was void: "594 banked Arabic-Gulf codes" were Indonesian (alatekno/carakami). team08b verified them instead (55 live). Genuine Gulf-code source still missing.
- groupjoin.link EU/UK/US old routes and country pages remain effectively unreachable from this VM (DNS/read timeouts); tags polluted with porn + channel records.

## Infra notes (for next wave)
- Raw `curl` from the sandbox is unreliable through the egress proxy (CONNECT timeouts even to example.com for several teams); python `requests`/`urllib` through the proxy works. Teams adapted individually. Consider standardizing verification on python requests.
- browser.open returns HTTP 403 on chat.whatsapp.com — verification must stay on direct HTTP clients.
- Egress proxy breaks keep-alive reuse (requests Session fails on 2nd request) — use fresh connections per request.
- Recurring yield wall: JS-gated join buttons (grupbul.com, GroupsWP, groupmaster deeper pages, everygroup.me, linkado categories, whatsshare.com, wahublink LK tag, grups on Francophonie/JP university sites) — the largest remaining untapped inventory needs a live-browser wave. Banked in leads files.
- Resumable pipelines saved in this dir: team03_scrape.py + team03-state.json (groupjoin.link categories), team30-scrape.py + team30-finalize.py + team30-progress.json (igrupos.com), team36_pipeline.py / phase2-4 (listicles).

## Resume point (next wave)
- team03: online-shopping pp.40–114, sports-and-fitness pp.15–191, Entertainment pp.47–1 on groupjoin.link.
- team30: raise MAX_PAGES/DETAIL_PER_CITY on igrupos.com; add queretaro/merida/oaxaca/toluca/hermosillo/acapulco slugs.
- team01: retry 12 pending codes; scrape posts published after 2026-11-02.
- team28: 1 pending (redacted og:title "Xxxxxxxxx xxxxxxxxx") — retry for real name.
- team06: 1 pending transport-failure code.
- 190 leads in teamNN-leads.json, heaviest JS-gated: grupbul.com (team25/team16/team18), GroupsWP.com, groupmaster.app /de/groups pp.2–3+, everygroup.me, whatsshare.com.
- Fresh directories proven server-rendered and worth re-scraping: wglfinder.com (13 country pages were placeholder shells — recheck), groupwhat.com, newgrouplinks.pk, igrupos.com, groupmaster.app, livinintheuk.com, linkado.app (more PT queries), elyex.com tag archives.
