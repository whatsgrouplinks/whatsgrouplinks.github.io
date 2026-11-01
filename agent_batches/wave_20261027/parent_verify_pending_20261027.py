#!/usr/bin/env python3
"""Parent pass over wave 20261027 pending files: spaced curl + og:title check.
Promotes live items to parent_pending_verified.json; dead to parent_pending_dead.json.
Rules: plain-form re-check for /invite/ links; truncated/garbled codes fail naturally
(empty og:title or non-200 -> dead). Extra keys stripped at merge time, not here.
Dedupe vs union of groups.json codes + .existing_codes.json + parent_verified codes.
"""
import json, re, os, glob, subprocess, time

BASE = '/home/hatch/workspace/whatsapp-groups-site'
WAVE = os.path.join(BASE, 'agent_batches', 'wave_20261027')
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)')
PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b', re.I)
ADULT_EMOJI_RE = re.compile(r'[🥵💦🔞🍆🍑😈👅💋🫦]')

def code_of(inv):
    m = CODE_RE.search(inv or '')
    return m.group(1) if m else None

def og_title(url):
    try:
        r = subprocess.run(['curl','-sL','-m','20','-A',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '-w','\n%{http_code}', url], capture_output=True, text=True, timeout=30)
        body, _, code = r.stdout.rpartition('\n')
        if code not in ('200','201','204'): return ''
        m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', body, re.I)
        if not m:
            m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']', body, re.I)
        return (m.group(1).strip() if m else '')
    except Exception:
        return ''

def main():
    groups = json.load(open(os.path.join(BASE,'groups.json')))
    known = set()
    for g in groups:
        c = code_of(g.get('invite',''))
        if c: known.add(c)
    try: known |= set(json.load(open(os.path.join(BASE,'.existing_codes.json'))))
    except Exception: pass
    try:
        for g in json.load(open(os.path.join(WAVE,'parent_verified.json'))):
            c = code_of(g.get('invite',''))
            if c: known.add(c)
    except Exception: pass
    seen, cand, porn, flagged, bad = set(), [], 0, [], 0
    for fp in sorted(glob.glob(os.path.join(WAVE,'team*-unverified-pending.json'))):
        for g in json.load(open(fp)):
            name = re.sub(r'\s+',' ', (g.get('name') or '').strip())[:120]
            code = code_of(g.get('invite',''))
            if not name or not code: bad += 1; continue
            if code in known or code in seen: continue
            text = f"{name} {g.get('description','')} {g.get('category','')}"
            if PORN_RE.search(text): porn += 1; continue
            if ADULT_EMOJI_RE.search(name):
                flagged.append(g); continue
            seen.add(code); cand.append(g)
    print(f'pending candidates={len(cand)} porn={porn} flagged={len(flagged)} bad={bad}')
    live, dead = [], []
    for i, g in enumerate(cand):
        title = og_title(g['invite'])
        if not title and '/invite/' in g['invite']:
            title = og_title(f"https://chat.whatsapp.com/{code_of(g['invite'])}")
        if title: live.append(g)
        else: dead.append(g)
        if (i+1) % 50 == 0: print(f'  checked {i+1}/{len(cand)} live={len(live)} dead={len(dead)}', flush=True)
        time.sleep(0.4)
    json.dump(live, open(os.path.join(WAVE,'parent_pending_verified.json'),'w'), ensure_ascii=False, indent=1)
    json.dump(dead, open(os.path.join(WAVE,'parent_pending_dead.json'),'w'), ensure_ascii=False, indent=1)
    json.dump(flagged, open(os.path.join(WAVE,'parent_pending_flagged.json'),'w'), ensure_ascii=False, indent=1)
    print(f'PENDING-VERIFIED live={len(live)} dead={len(dead)} flagged={len(flagged)}')

if __name__ == '__main__':
    main()
