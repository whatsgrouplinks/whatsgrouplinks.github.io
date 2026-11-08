#!/usr/bin/env python3
"""Leg-1 assembly fix-up for wave 20261105 (run 2026-11-06).
Run AFTER parent_reverify_dead_20261105.py finishes (it rewrites parent_verified.json).
1. Re-audits the FINAL parent_reverify_state.json: any 'live' code whose og:title
   trips the run's own adult screen (PORN_RE / PORN_URDU_RE / ADULT_EMOJI) is dropped
   from parent_verified.json — the reverify script only screened the team name,
   so og-title-only signals slipped through (13 found in the first 6,800).
2. Appends the transport code Fu6LZ0jYpCLGmAQKV9UWrD ('Clash Royale libre',
   verified live by parent curl 2026-11-06, record from team03-igrupos.json).
3. Belt-and-braces: re-screens every parent_verified.json item name+description
   with the same screen; drops any hit.
4. EXCLUDES L0JS1dP9m2M3jjoOxfKK0z (SOCRATES COMMUNITY invite, not a group).
Prints final count + drop list. Writes parent_verified.json (backup .pre-fixup).
"""
import json, re, os, shutil, html

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261105')
PV = os.path.join(WAVE, 'parent_verified.json')
S2 = os.path.join(WAVE, 'parent_reverify_state.json')

PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal|bokep)\b', re.I)
PORN_URDU_RE = re.compile(r'مزا\s?دینے|مزہ\s?دینے', re.I)
ADULT_EMOJI = set('🥵🍆🍑🔞💦👅👄💋')
EXCLUDE_CODES = {'L0JS1dP9m2M3jjoOxfKK0z'}
TRANSPORT_OG = {  # pending-transport codes verified LIVE by parent curl 2026-11-06
    'Fu6LZ0jYpCLGmAQKV9UWrD': 'Clash Royale libre',
    'IpAK8w9UKE75g2OxhtI6gx': '&#x1d648;&#x1d64e; &#x1d64e;&#x1d66a;&#x1d658;&#x1d658;&#x1d65a;&#x1d668;&#x1d668;&#x2708;&#xfe0f;',
    'IpWiY65r0ELHi0xOWFGtb5': '&#x1f6a9;&#x2694;&#xfe0f;&#x939;&#x93f;&#x928;&#x94d;&#x926;&#x942; &#x927;&#x930;&#x94d;&#x92e;&#x2694;&#xfe0f;&#x1f6a9;',
    'Ir1CTq4RIpA9I2X00ESIzh': 'link sharing and referral &#x1f525;',
    'It9jB4ZgiYn2z0SWY4sMrE': 'Tiktok follow to follow back',
    'HnKWHHsyvZQ6jPlRSCJtZW': 'A B M TEX',
    'FZL3UILw4mSLKKFxyoRlKu': 'Prem ka Sager ',
    'BRiKRs0tKhdJX3L0WPiAdq': 'Factory outlet.OG &#x2122;&#xfe0f;&#x1f6d2;&#x1f6cd;&#xfe0f;',
    'CD48glhJjO8ABl8jId26RL': 'Social Media Services',
    'Cbkl5BB6Xqk7x73EysjxDP': 'Masti',
    'Cit0Ehi0yViJ59hCgbWlQ5': 'Learn Free English Online',
    'DNNpOzFAXEP8YPBlodj82W': 'Chuza Creatives',
    'HRYwREZFa1o8Vv2AOOQtEk': '&#x2728;&#x1f432;&#x110;&#x24d;&#x23a;&#x1e5;&#xf8;&#x301;n &#x243;&#x23a;&#x142;&#x142;&#x1f432;&#x1f250;&#xc4;&#x144;&#xef;m&#xeb;s&#x1f250; &#x1f47e;J&#x16b;&#xea;g&#xf8;s&#x1f47e;&#x2728;',
}

def code_of(invite):
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', invite or '')
    return m.group(1) if m else None

def flagged(text):
    t = text or ''
    return bool(PORN_RE.search(t) or PORN_URDU_RE.search(t) or any(e in t for e in ADULT_EMOJI))

def main():
    s2 = json.load(open(S2))
    og_flagged = set()
    for c, v in s2.items():
        if isinstance(v, list) and v[0] == 'live' and len(v) > 1 and flagged(v[1]):
            og_flagged.add(c)
    print('og-title-flagged live codes in final state2:', len(og_flagged), flush=True)

    items = json.load(open(PV))
    print('parent_verified.json before fix-up:', len(items), flush=True)
    shutil.copy2(PV, PV + '.pre-fixup')

    dropped = []
    kept = []
    for it in items:
        c = code_of(it.get('invite'))
        if c in EXCLUDE_CODES:
            dropped.append((c, 'excluded-community-invite'))
            continue
        if c in og_flagged:
            dropped.append((c, 'og-title-adult-screen:' + (it.get('name') or '')[:60]))
            continue
        if flagged((it.get('name') or '') + ' ' + (it.get('description') or '')):
            dropped.append((c, 'name-desc-adult-screen'))
            continue
        kept.append(it)

    # append transport codes (verified live by parent curl)
    kept_codes = {code_of(it.get('invite')) for it in kept}
    # team records indexed by code (manifest-canonical files)
    teamrec = {}
    for _l in open(os.path.join(WAVE, 'manifest.txt')):
        _m = re.search(r'(team\d+-[\w\-\.]+\.json): count=(\d+)', _l)
        if not _m:
            continue
        try:
            items = json.load(open(os.path.join(WAVE, _m.group(1))))
        except Exception:
            continue
        for it in items:
            if isinstance(it, dict):
                c = code_of(it.get('invite'))
                if c and c not in teamrec:
                    teamrec[c] = it
    for tcode, og_raw in TRANSPORT_OG.items():
        og = html.unescape(og_raw).strip()
        if tcode in kept_codes:
            print('transport code already present:', tcode, flush=True)
            continue
        rec = teamrec.get(tcode)
        if not rec:
            print('transport code record NOT FOUND:', tcode, flush=True)
            continue
        if flagged((rec.get('name') or '') + ' ' + (rec.get('description') or '')) or flagged(og):
            print('transport code FAILED adult screen, NOT appended:', tcode, flush=True)
            continue
        name = (rec.get('name') or '') or og
        if og and len(og) > len(name):
            name = og
        kept.append({'name': name[:120],
                     'category': rec.get('category') or 'Community & Social',
                     'country': rec.get('country') or 'International',
                     'description': rec.get('description') or '',
                     'invite': rec.get('invite'), 'image': rec.get('image') or ''})
        print('transport code appended:', tcode, flush=True)

    json.dump(kept, open(PV, 'w'), ensure_ascii=False)
    print('DROPPED:', len(dropped), flush=True)
    for c, why in dropped:
        print('  ', c, why, flush=True)
    print('parent_verified.json after fix-up:', len(kept), flush=True)

if __name__ == '__main__':
    main()
