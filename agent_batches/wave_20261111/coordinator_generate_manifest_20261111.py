#!/usr/bin/env python3
"""Generate wave_20261111 manifest.txt + wave_20261111_summary.md from files on disk."""
import json, os
from collections import Counter

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111'
BASELINE_GROUPS = 73370
UNION = 108992

SPECS = [
    (1, 'leads slice 1', 'team01-leads-slice1'),
    (2, 'leads slice 2', 'team02-leads-slice2'),
    (3, 'leads slice 3', 'team03-leads-slice3'),
    (4, 'leads slice 4', 'team04-leads-slice4'),
    (5, 'leads slice 5', 'team05-leads-slice5'),
    (6, 'leads slice 6', 'team06-leads-slice6'),
    (7, 'leads slice 7', 'team07-leads-slice7'),
    (8, 'leads slice 8', 'team08-leads-slice8'),
    (9, 'pending recheck', 'team09-pending-recheck'),
    (10, 'linkado sitemap 2300-2699', 'team10-linkado-2300'),
    (11, 'linkado sitemap 2700-3099', 'team11-linkado-2700'),
    (12, 'linkado sitemap 0-1499', 'team12-linkado-0-1499'),
    (13, 'groupjoin new', 'team13-groupjoin'),
    (14, '77links', 'team14-77links'),
    (15, 'tugrupo', 'team15-tugrupo'),
    (16, 'grupbul', 'team16-grupbul'),
    (17, 'groupssor', 'team17-groupssor'),
    (18, 'grouplinksforyou', 'team18-grouplinksforyou'),
    (19, 'groupsnest', 'team19-groupsnest'),
    (20, 'wglfinder', 'team20-wglfinder'),
    (21, 'freewagroup', 'team21-freewagroup'),
    (22, 'walink', 'team22-walink'),
    (23, 'groupsinvite', 'team23-groupsinvite'),
    (24, 'whtspgrouplink', 'team24-whtspgrouplink'),
    (25, 'new dirs South Asia', 'team25-newdirs-southasia'),
    (26, 'new dirs Africa/Mideast', 'team26-newdirs-africa-mideast'),
    (27, 'new dirs SE Asia', 'team27-newdirs-seasia'),
    (28, 'new dirs LatAm/Gulf', 'team28-newdirs-latam-gulf'),
    (29, 'listicles edu/jobs', 'team29-listicles-edu-jobs'),
    (30, 'listicles mixed', 'team30-listicles-mixed'),
    (31, 'tglinkhub verify2', 'team31-tglinkhub-verify2'),
    (32, 'igrupos geogated', 'team32-igrupos-geogated'),
]

def load(p):
    try:
        return json.load(open(os.path.join(WAVE_DIR, p)))
    except Exception:
        return None

clean = load('wave_20261111_clean.json')
teams = load('wave_20261111_clean_teams.json')
pend_all = load('wave_20261111_pending_all.json')
leads_all = load('wave_20261111_leads_all.json')
exc = load('wave_20261111_excluded.json')
dups = load('wave_20261111_cross_dups.json')
leaks = load('wave_20261111_union_leaks.json')
errs = load('wave_20261111_schema_err.json')
state = load('coordinator_verify_state_20261111.json')
kept = Counter(teams.values())

rows = []
raw_total = 0
for n, label, base in SPECS:
    v = load(base + '.json') or []
    p = load(base + '-pending.json') or []
    l = load(base + '-leads.json') or []
    s = load(base + '-summary.json') or {}
    raw_total += len(v)
    rows.append((n, label, len(v), kept.get(n, 0), len(p), len(l), s))

lines = []
lines.append('# WhatsGroupLinks wave 20261111 — coordinator manifest')
lines.append('# Run: Wed 2026-11-11. Coordinator spawned 32 teams, consolidated their')
lines.append('# final files on disk (coordinator_build_clean_20261111.py + repair + finalize).')
lines.append(f'# groups.json baseline: {BASELINE_GROUPS} groups.')
lines.append(f'# Dedupe union: {UNION} codes (.existing_codes.json; groups.json codes are a subset).')
lines.append('# Coordinator validation: 0 union leaks, 0 schema errors (after repair), 0 dup codes in clean.')
lines.append('# Coordinator spot re-check: 35/35 sampled clean codes confirmed live')
lines.append('# (sequential curl-equivalent, persistent session, non-empty og:title) + controls OK')
lines.append('# (known-live groups.json code live, fabricated code dead) — see')
lines.append('# coordinator_verify_state_20261111.json.')
lines.append('#')
lines.append('# TOTALS')
lines.append(f'#   raw team items:                    {raw_total}')
lines.append(f'#   cross-team dups (first-team-wins):  {len(dups)}')
lines.append(f'#   union leaks:                         {len(leaks)}')
lines.append(f'#   schema errors:                       {len(errs)}')
lines.append(f'#   screen-excluded (coordinator):       {len(exc)}')
lines.append(f'#   coordinator false-positive restores: 22  (prohibition sentences / sexta-Friday / chuta-verb / 18+ age gates)')
lines.append(f'#   coordinator spot-verify drops:        2  (AI-trading daily-profits scam, team28 flag; sports-betting recruitment group)')
lines.append(f'#   schema-error names recovered:         5  (team09 empty names, og:title used)')
lines.append(f'#   verified unique (clean file):      {len(clean)}  (wave_20261111_clean.json)')
lines.append(f'#   groups.json would become:          {BASELINE_GROUPS} -> {BASELINE_GROUPS + len(clean)} (parent merges)')
lines.append(f'#   pending (transport failures):      {len(pend_all)}  (wave_20261111_pending_all.json)')
lines.append(f'#   leads (unique URLs + codes):      {len(leads_all)}  (wave_20261111_leads_all.json; '
            f'{sum(1 for s in leads_all if str(s).startswith("http"))} URLs + '
            f'{sum(1 for s in leads_all if not str(s).startswith("http"))} unverified code strings)')
lines.append(f'#   excluded (coordinator screen):       {len(exc)}  (wave_20261111_excluded.json)')
lines.append('#')
lines.append('# PER-TEAM TABLE: team | slice | verified raw | kept in clean* | pending | leads')
for n, label, vr, kp, pd, ld, s in rows:
    lines.append(f'#   {n:02d} | {label:26s} | {vr:4d} | {kp:4d} | {pd:4d} | {ld:5d}')
lines.append('#   * kept-in-clean counts are after cross-team first-team-wins dedupe (team-number')
lines.append('#     order), coordinator screening, the 22 false-positive restores, the 5')
lines.append('#     schema-error name recoveries, and the 2 coordinator spot-verify drops.')
lines.append('#     team06 won 64 linkado dups (teams 10/11 mined the same grupo pages as')
lines.append('#     leads slice 6); team10 lost 38, team11 lost 27, team12 lost 4 to slices.')
lines.append('#     team13 lost both Adult-category codes to the coordinator Adult exclusion;')
lines.append('#     team17 lost its 1 code to the coordinator 18+ screen, then had it restored.')
lines.append('#     team20 lost 1 to team06 (dup) and 1 is the betting group dropped on spot-verify.')
lines.append('#')
lines.append('# COORDINATOR SCREEN (41 initial drops -> 22 restored -> 19 kept + 2 spot-verify drops = 21)')
lines.append('#   Restored (false positives — see coordinator_repair_20261111.py):')
lines.append('#     - 13 prohibition sentences the strip missed (Portuguese Proibido/Sem/Não pode')
lines.append('#       pornografia, 🚫 Nudez, PROIBIDO 🔞, pode tudo menos 18+, foto 18+ é banido).')
lines.append('#     - 1 sexta-feira (Friday) — substring "sex" inside "sexta".')
lines.append('#     - 1 "chuta" verb — substring "chut" inside Portuguese "chutar" (to kick).')
lines.append('#     - 4 18+/🔞 age gates on non-porn groups: hookah (tobacco), LGBTQ social group,')
lines.append('#       friendship/chat group (team17 judgement), "Compra e venda e rolo" (team10 confirmed).')
lines.append('#     - 3 more prohibition-sentence cases (pet adoption "sem porno", sticker "SÓ NÃO PODE')
lines.append('#       FIGURINHAS DE PORNOGRAFIA", "PROIBIDO PORNO").')
lines.append('#   Kept excluded (19): hard porn/xxx names (SEXUAL HOME, call-girl x2, Desi bhabhi x2,')
lines.append('#     Brazzers, No Sigilo hookup, 18+ sticker groups, Jampaflix 18+ streaming,')
lines.append('#     Adults 18+ Aunty, Only girls 18+, hentai), 2 groupjoin Adult-category codes,')
lines.append('#     3 re-labelled scams (VENDA DE XIT cheat sales = paid hack; 2 betting-platform promos).')
lines.append('#   Spot-verify drops (2): KkKQsWHSNibIMTA1wPN3h8 AI-trading daily-profits scam (team28 flag);')
lines.append('#     BTK6Vvs3TEu6oW7joHtiY9 sports-betting recruitment (og:title BETS1GREEN APOSTA).')
lines.append('#   Spot-verify kept (judgement calls, og:title checked live and clean): GLOBAL WEB 3')
lines.append('#     (Crypto, KYC bullet is one service among six, not a scam name); Weltrade/Deriv signal')
lines.append('#     trials (trading signals, not a named scam); Teen Patti blue (card game); "." degenerate')
lines.append('#     name (live, kept); تداول أموال money-trading, earn-money-daily pitch, Adfly (generic')
lines.append('#     earning pitches, not named scams); "Divulgo suas plataforma" (platform promotion, no')
lines.append('#     betting terms).')
lines.append('#')
lines.append('# PARENT FLAG — NOV-10 SCAM CODES NOW IN groups.json (team18 finding, verify before merge):')
lines.append('#   KD408PRv4Kh1j81OBGMB6O ("FREE AIRDROP ALPHA"), FQAEuMQvBZJKtOlCrsnmac ("Binary Option')
lines.append('#   Investment"), KkdRrp9oFNxLY9Q6eAwpGR ("Airdrop 3"), EghZlHeOTD406TCI21NChX ("TON-AIRDROP").')
lines.append('#   All 4 have airdrop/scam og:titles; the source site has since removed all 4 from its posts.')
lines.append('#   The parent may want to purge these 4 codes from groups.json + the union.')
lines.append('#')
lines.append('# COORDINATOR SPOT-VERIFY (35 clean-sample codes + 2 controls + 5 schema codes):')
lines.append(f"#   {state['live']}/35 live, {state['dead']} dead, {state['pending']} pending. "
            f"Control-live {state['controls'][0]['status']}, control-fake {state['controls'][1]['status']}.")
lines.append('#   All 5 schema-error codes live with clean og:titles — restored with og:title as name.')
lines.append('#   No og:title scam/porn signal found in the 35-code sample except the betting group above.')
lines.append('#   Residual risk (as Nov 10): og:title-vs-banked-name mismatches can only be caught by')
lines.append('#   sampling; full re-verification of all 3,078 was not feasible at ~25s/check from this VM.')
lines.append('#')
lines.append('# ENVIRONMENT NOTES (for the next wave):')
lines.append('#   - VM egress charges ~25-30s per FRESH TLS connection (all hosts, not just WhatsApp);')
lines.append('#     a persistent keep-alive session makes warm requests ~1s. Curl with 15-20s timeouts')
lines.append('#     produced false transport failures mid-wave (team30 read it as a VM-wide outage).')
lines.append('#     Use 60-90s timeouts + keep-alive sessions for all verification.')
lines.append('#   - Two VM reboots (~08:00 and ~10:00 UTC) killed background jobs mid-run; checkpoint')
lines.append('#     files in the wave dir saved all work. team31 verify2 checker died at ~07:58 UTC.')
lines.append('#   - WhatsApp throttles this host under concurrent load (team20 pass 3: 75/75 timeouts).')
lines.append('#     Pending codes are worth one re-check in a quiet window, not during the wave storm.')
lines.append('#')
lines.append('# RESUME POINTS (from team summaries):')
for n, label, vr, kp, pd, ld, s in rows:
    r = s.get('resume') if isinstance(s, dict) else None
    if r:
        lines.append(f'#   team{n:02d} {label}: {r}')
    else:
        lines.append(f'#   team{n:02d} {label}: (no resume point in summary)')
lines.append('#   team01 stream verifier STILL RUNNING at finalize (pid 1757, team01_verify_stream.py);')
lines.append('#     re-run team01_finalize.py after it finishes to fold in remaining results (1,171')
lines.append('#     candidates in team01-merged-candidates.json, also banked as code-string leads).')
lines.append('#   team31 verify2 checker DEAD (reboot ~07:58 UTC); 11,587 codes still unverified —')
lines.append('#     re-run verify2_team31.py then bank_team31.py to continue (637 lines banked so far).')
lines.append('#   team02: 2,160 mined candidates await verification (team02-awaiting-verification.json,')
lines.append('#     also banked as code-string leads); re-run team02_mine2.py then team02_build.py.')
lines.append('#   team30: run team30_scratch/retry_pass.py FIRST next wave (163 pending + 13 dead re-check)')
lines.append('#     after a curl control test on a known-live code.')
lines.append('#   team04: slice 4 resume at index 1100 of leads_slice4.json')
lines.append('#     (https://linkado.app/grupo/650d75096f3f15eab134f2b1); re-run team04_mine.py + finalize.')
lines.append('#   linkado: team10 next index 2700 (https://linkado.app/grupo/69baf82349dbc7627d73499f,')
lines.append('#     lastmod 2026-03-19); team11 next index 3100 (https://linkado.app/grupo/695af8fcdee39681ec9e0ac1,')
lines.append('#     lastmod 2026-01-04); team12 sweep 0-1499 COMPLETE. New: team32 igrupos gids 526723-526885')
lines.append('#     still uncovered (resume downward from 526886); linktogroups.com (team26 find) needs a')
lines.append('#     browser leg for its click API; team03/team04 linkado JS-gated leads need browser clicks.')
lines.append('#   Sources exhausted/closed: tugrupo.com (dead; moved to tugrupo.online), walink.pk (clean'),
lines.append('#     groups exhausted, 2 waves running), groupsnest (unchanged), freewagroup (unchanged since')
lines.append('#     Nov 8), grouplinksforyou (39 posts, all mined), groupsinvite catalog closed Nov 9')
lines.append('#     (new entries only, via sitemap+homepage diff).')
lines.append('#')
lines.append('# FILES (all in ~/workspace/whatsapp-groups-site/agent_batches/wave_20261111/):')
for f in ['wave_20261111_clean.json', 'wave_20261111_clean_teams.json',
          'wave_20261111_pending_all.json', 'wave_20261111_leads_all.json',
          'wave_20261111_excluded.json', 'wave_20261111_cross_dups.json',
          'wave_20261111_union_leaks.json', 'wave_20261111_schema_err.json',
          'coordinator_verify_state_20261111.json', 'manifest.txt',
          'wave_20261111_summary.md', 'coordinator_build_clean_20261111.py',
          'coordinator_repair_20261111.py', 'coordinator_verify_20261111.py',
          'coordinator_finalize_20261111.py', 'coordinator_generate_manifest_20261111.py']:
    p = os.path.join(WAVE_DIR, f)
    lines.append(f'#   {f} ({os.path.getsize(p)} bytes)' if os.path.exists(p) else f'#   {f} (MISSING)')
lines.append('# Per-team final files: teamNN-<slice>.json / -pending.json / -leads.json / -summary.json')
lines.append('# (32 teams x 4 files, plus team checkpoints/scripts in the same dir).')

open(os.path.join(WAVE_DIR, 'manifest.txt'), 'w').write('\n'.join(lines) + '\n')
print('wrote manifest.txt')

# --- summary.md ---
kept = Counter(teams.values())
cat = Counter(c['category'] for c in clean)
ctry = Counter(c['country'] for c in clean)
md = []
md.append('# Wave 20261111 — Summary')
md.append('')
md.append(f'**Date:** Wed 2026-11-11. **Coordinator outputs on disk** (unlike Nov 10, when they went missing).')
md.append('')
md.append('## Result')
md.append('')
md.append(f'- **Verified new groups ready to merge: {len(clean)}**')
md.append(f'- **Total would become: {BASELINE_GROUPS} → {BASELINE_GROUPS + len(clean)} groups** (parent merges; coordinator does not merge/deploy)')
md.append(f'- **Dedupe union: {UNION} codes** (groups.json codes are a subset)')
md.append(f'- **Pending (transport failures, NOT merged): {len(pend_all)}** — banked in wave_20261111_pending_all.json')
md.append(f'- **Leads (unique URLs + unverified codes): {len(leads_all)}** — banked in wave_20261111_leads_all.json')
md.append(f'- **Excluded (coordinator screen): {len(exc)}** — banked in wave_20261111_excluded.json')
md.append('')
md.append('## Consolidation')
md.append('')
md.append(f'- Raw team items: {raw_total} across 32 team files (21 teams verified >0).')
md.append(f'- Cross-team dups removed: {len(dups)} (first-team-wins, team-number order; team06 won 64 linkado dups).')
md.append(f'- Union leaks: {len(leaks)}. Schema errors: {len(errs)} (5 team09 empty names recovered via og:title).')
md.append('- Coordinator screen drops: 41 initial → 22 false positives restored → 19 kept excluded, plus 2 spot-verify drops.')
md.append('- Coordinator spot re-check: 35/35 sampled clean codes live; controls OK (known-live live, fabricated dead).')
md.append('- False-positive restores: 22 (13 Portuguese prohibition sentences, sexta-Friday, chuta-verb, 4 18+/🔞 age gates, 3 more prohibition cases).')
md.append('- Spot-verify drops: 2 (AI-trading daily-profits scam, team28 flag; sports-betting recruitment group).')
md.append('- Schema-error name recoveries: 5 (team09 empty names → og:title names, all live and clean).')
md.append('')
md.append('## Per-team kept counts')
md.append('')
md.append(', '.join(f'team{n:02d} {kept.get(n, 0)}' for n, _, _ in SPECS) + '.')
md.append('Zero: teams 15, 16, 18, 19, 21, 22, 30, 32 (team32 leads-only by design).')
md.append('')
md.append('## Categories / countries (clean file)')
md.append('')
md.append(', '.join(f'{k} {v}' for k, v in cat.most_common()) + '.')
md.append('Countries: ' + ', '.join(f'{k or "(blank)"} {v}' for k, v in ctry.most_common(10)) + '.')
md.append('')
md.append('## Files')
md.append('')
for f in ['manifest.txt', 'wave_20261111_clean.json', 'wave_20261111_clean_teams.json',
          'wave_20261111_pending_all.json', 'wave_20261111_leads_all.json',
          'wave_20261111_excluded.json', 'wave_20261111_cross_dups.json',
          'wave_20261111_union_leaks.json', 'wave_20261111_schema_err.json',
          'coordinator_verify_state_20261111.json',
          'coordinator_build_clean_20261111.py', 'coordinator_repair_20261111.py',
          'coordinator_verify_20261111.py', 'coordinator_finalize_20261111.py',
          'coordinator_generate_manifest_20261111.py']:
    md.append(f'- {f}')
md.append('')
md.append('## Notes / residual risks')
md.append('')
md.append('- **Parent flag — Nov-10 scam codes in groups.json (team18):** KD408PRv4Kh1j81OBGMB6O,')
md.append('  FQAEuMQvBZJKtOlCrsnmac, KkdRrp9oFNxLY9Q6eAwpGR, EghZlHeOTD406TCI21NChX — all 4 have')
md.append('  airdrop/scam og:titles; the source site has since removed them. Consider purging from groups.json.')
md.append('- og:title-vs-banked-name mismatches can only be caught by sampling: 1 of 35 sampled codes')
md.append('  was a betting group (dropped). Full re-verification of all 3,078 was not feasible at ~25s/check.')
md.append('- team31 (tglinkhub) names come from directory listing titles + og:title — same mismatch risk')
md.append('  class as the Nov-10 HOLIVERSE case; its own exclusions already dropped ~500 scam/adult codes.')
md.append('- team01 stream verifier still running at finalize; team31 checker dead (reboot); team02 has')
md.append('  2,160 candidates awaiting verification — all banked as leads for the next wave.')
md.append('- Egress lesson: use 60-90s timeouts + keep-alive sessions; short-timeout curls produced false')
md.append('  transport failures mid-wave (read as a VM-wide outage by team30).')
md.append('- Search Console indexing NOT attempted (balochaiza47 sign-in is device-gated) — parent handles.')
md.append('')
open(os.path.join(WAVE_DIR, 'wave_20261111_summary.md'), 'w').write('\n'.join(md))
print('wrote wave_20261111_summary.md')
