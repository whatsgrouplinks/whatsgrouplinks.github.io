#!/usr/bin/env python3
"""Parent pass for wave 20261027: verify team-verified files, screen, merge.
Usage:
  python3 parent_verify_merge_20261027.py verify   # -> parent_verified.json, parent_dead.json, parent_flagged.json
  python3 parent_verify_merge_20261027.py merge    # merges parent_verified.json into groups.json (backup + dedupe sets)
Dedupe is against the UNION of groups.json codes AND .existing_codes.json (Oct 24 lesson).
Verification: curl invite, require HTTP success + non-empty og:title (Oct 23/24 convention).
Screens: hard-porn regex only blocks porn; adult-sexual emoji/signal items are FLAGGED for
manual review, not auto-merged (Oct 25/26 parent drops). Girls/friendship groups are KEPT.
"""
import json, re, os, sys, glob, shutil, time, pickle, subprocess

BASE = '/home/hatch/workspace/whatsapp-groups-site'
WAVE = os.path.join(BASE, 'agent_batches', 'wave_20261028')
GROUPS = os.path.join(BASE, 'groups.json')
CODES_JSON = os.path.join(BASE, '.existing_codes.json')
CODES_PKL = os.path.join(BASE, 'dedup_codes.pkl')

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)')
PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b', re.I)
ADULT_EMOJI_RE = re.compile(r'[🥵💦🔞🍆🍑😈👅💋🫦]')
VALID_CATS = {'Education','Jobs','Entertainment','Islamic','News','Sports','Technology',
              'Health','Business','Gaming','Friendship','Community & Social','Online Earning',
              'Crypto','Cooking','Poetry','Travel','Scholarship','Freelance','Real Estate','Buy & Sell'}
ALIASES = {'education':'Education','jobs':'Jobs','job':'Jobs','entertainment':'Entertainment',
    'fun':'Entertainment','islamic':'Islamic','islam':'Islamic','news':'News','sports':'Sports',
    'sport':'Sports','technology':'Technology','tech':'Technology','health':'Health',
    'business':'Business','gaming':'Gaming','games':'Gaming','friendship':'Friendship',
    'friends':'Friendship','community & social':'Community & Social','community':'Community & Social',
    'social':'Community & Social','online earning':'Online Earning','earning':'Online Earning',
    'crypto':'Crypto','cooking':'Cooking','food':'Cooking','poetry':'Poetry','shayari':'Poetry',
    'travel':'Travel','scholarship':'Scholarship','freelance':'Freelance','real estate':'Real Estate',
    'buy & sell':'Buy & Sell','buysell':'Buy & Sell','buy sell':'Buy & Sell','general':'Community & Social'}

def code_of(inv):
    m = CODE_RE.search(inv or '')
    return m.group(1) if m else None

def canon_cat(c):
    if not c: return 'Community & Social'
    c = str(c).strip()
    if c in VALID_CATS: return c
    return ALIASES.get(c.lower(), 'Community & Social')

def clean_name(n):
    return re.sub(r'\s+', ' ', (n or '').strip())[:120]

def existing_codes():
    groups = json.load(open(GROUPS))
    codes = set()
    for g in groups:
        c = code_of(g.get('invite',''))
        if c: codes.add(c)
    try:
        codes |= set(json.load(open(CODES_JSON)))
    except Exception as e:
        print('codes json read fail', e)
    return groups, codes

def team_verified_files():
    out = []
    for p in sorted(glob.glob(os.path.join(WAVE, 'team*.json'))):
        base = os.path.basename(p)
        if 'pending' in base or 'parent_' in base: continue
        out.append(p)
    return out

def check_live(invite):
    """curl -sL, require HTTP 2xx and non-empty og:title. Returns (live, title)."""
    try:
        r = subprocess.run(['curl','-sL','-m','20','-A',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '-w','\n%{http_code}', invite],
            capture_output=True, text=True, timeout=30)
        body, _, code = r.stdout.rpartition('\n')
        if code not in ('200','201','204','301','302'): return False, ''
        m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', body, re.I)
        if not m:
            m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']', body, re.I)
        title = (m.group(1).strip() if m else '')
        return bool(title), title
    except Exception:
        return False, ''

def do_verify():
    groups, known = existing_codes()
    print(f'groups.json={len(groups)} known_codes={len(known)}')
    seen, cand, porn, bad, flagged = set(), [], 0, 0, []
    for fp in team_verified_files():
        try: items = json.load(open(fp))
        except Exception as e: print('skip', fp, e); continue
        for g in items:
            name = clean_name(g.get('name'))
            code = code_of(g.get('invite',''))
            if not name or not code: bad += 1; continue
            if code in known or code in seen: continue
            text = f"{name} {g.get('description','')} {g.get('category','')}"
            if PORN_RE.search(text): porn += 1; continue
            if ADULT_EMOJI_RE.search(name) or ADULT_EMOJI_RE.search(g.get('description','')):
                flagged.append(g); continue
            if 'http' in (g.get('description','') or '') or 'www.' in (g.get('description','') or ''):
                g = dict(g); g['description'] = ''
            seen.add(code); cand.append(g)
    print(f'candidates={len(cand)} porn_dropped={porn} bad={bad} adult_flagged={len(flagged)}')
    live, dead = [], []
    for i, g in enumerate(cand):
        ok, title = check_live(g['invite'])
        if ok: live.append(g)
        else: dead.append(g)
        if (i+1) % 25 == 0: print(f'  checked {i+1}/{len(cand)} live={len(live)} dead={len(dead)}', flush=True)
        time.sleep(0.4)
    json.dump(live, open(os.path.join(WAVE,'parent_verified.json'),'w'), ensure_ascii=False, indent=1)
    json.dump(dead, open(os.path.join(WAVE,'parent_dead.json'),'w'), ensure_ascii=False, indent=1)
    json.dump(flagged, open(os.path.join(WAVE,'parent_flagged.json'),'w'), ensure_ascii=False, indent=1)
    print(f'VERIFIED live={len(live)} dead={len(dead)} flagged={len(flagged)}')

def do_merge():
    groups, known = existing_codes()
    items = json.load(open(os.path.join(WAVE,'parent_verified.json')))
    old = len(groups); new_groups, batch, stats = [], set(), {'dup':0,'porn':0,'bad':0}
    for g in items:
        name = clean_name(g.get('name')); code = code_of(g.get('invite',''))
        if not name or not code: stats['bad'] += 1; continue
        if code in known or code in batch: stats['dup'] += 1; continue
        text = f"{name} {g.get('description','')} {g.get('category','')}"
        if PORN_RE.search(text): stats['porn'] += 1; continue
        cat = canon_cat(g.get('category'))
        desc = re.sub(r'\s+',' ', (g.get('description') or '').strip())[:300]
        if not desc or 'http' in desc or 'www.' in desc:
            desc = f"Join {name}, a WhatsApp group listed under {cat}."
        new_groups.append({'name':name,'category':cat,'description':desc,
            'image':(g.get('image') or '').strip(),'invite':f'https://chat.whatsapp.com/{code}',
            'country':(g.get('country') or '').strip()})
        batch.add(code)
    if not new_groups:
        print('No new groups to merge.', stats); return
    backup = GROUPS + f".backup-merge-20261028-{time.strftime('%H%M')}"
    shutil.copy2(GROUPS, backup)
    groups.extend(new_groups)
    json.dump(groups, open(GROUPS,'w'), ensure_ascii=False)
    known |= batch
    json.dump(sorted(known), open(CODES_JSON,'w'))
    try:
        pickle.dump(known, open(CODES_PKL,'wb'))
    except Exception as e: print('pickle fail', e)
    print(f"MERGED: {old} -> {len(groups)} (+{len(new_groups)}) stats={stats} backup={backup}")

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ('verify','merge'):
        print('usage: verify|merge'); sys.exit(1)
    (do_verify if sys.argv[1]=='verify' else do_merge)()
