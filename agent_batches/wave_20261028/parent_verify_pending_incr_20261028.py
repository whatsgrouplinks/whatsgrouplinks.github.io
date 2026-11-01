#!/usr/bin/env python3
"""Incremental pending verification for wave 20261028 (resume-safe).
Writes parent_pending_verified_incr.json / parent_pending_dead_incr.json /
parent_pending_flagged_incr.json after every 25 checks, so a kill loses at most 25.
"""
import json, re, os, glob, subprocess, time
BASE='/home/hatch/workspace/whatsapp-groups-site'
WAVE=os.path.join(BASE,'agent_batches','wave_20261028')
CODE_RE=re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)')
PORN_RE=re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b', re.I)
ADULT_EMOJI_RE=re.compile(r'[🥵💦🔞🍆🍑😈👅💋🫦]')
def code_of(inv):
    m=CODE_RE.search(inv or ''); return m.group(1) if m else None
def og_title(url):
    try:
        r=subprocess.run(['curl','-sL','-m','20','-A','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36','-w','\n%{http_code}',url],capture_output=True,text=True,timeout=30)
        body,_,code=r.stdout.rpartition('\n')
        if code not in ('200','201','204'): return ''
        m=re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',body,re.I)
        if not m: m=re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']',body,re.I)
        return (m.group(1).strip() if m else '')
    except Exception: return ''
def load(p):
    try: return json.load(open(p))
    except Exception: return []
def save(p,d): json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
def main():
    groups=json.load(open(os.path.join(BASE,'groups.json')))
    known=set()
    for g in groups:
        c=code_of(g.get('invite',''))
        if c: known.add(c)
    try: known|=set(json.load(open(os.path.join(BASE,'.existing_codes.json'))))
    except Exception: pass
    live=load(os.path.join(WAVE,'parent_pending_verified_incr.json'))
    dead=load(os.path.join(WAVE,'parent_pending_dead_incr.json'))
    flagged=load(os.path.join(WAVE,'parent_pending_flagged_incr.json'))
    done={code_of(g.get('invite','')) for g in live+dead+flagged}
    seen=set(); cand=[]; porn=0; bad=0
    for fp in sorted(glob.glob(os.path.join(WAVE,'team*-unverified-pending.json'))):
        for g in json.load(open(fp)):
            name=re.sub(r'\s+',' ',(g.get('name') or '').strip())[:120]
            code=code_of(g.get('invite',''))
            if not name or not code: bad+=1; continue
            if code in known or code in seen or code in done: continue
            text=f"{name} {g.get('description','')} {g.get('category','')}"
            if PORN_RE.search(text): porn+=1; continue
            if ADULT_EMOJI_RE.search(name): flagged.append(g); seen.add(code); continue
            seen.add(code); cand.append(g)
    print(f'to-check={len(cand)} already-done={len(done)} porn={porn} bad={bad} flagged-total={len(flagged)}',flush=True)
    for i,g in enumerate(cand):
        title=og_title(g['invite'])
        if not title and '/invite/' in g['invite']:
            title=og_title(f"https://chat.whatsapp.com/{code_of(g['invite'])}")
        (live if title else dead).append(g)
        if (i+1)%25==0 or i+1==len(cand):
            save(os.path.join(WAVE,'parent_pending_verified_incr.json'),live)
            save(os.path.join(WAVE,'parent_pending_dead_incr.json'),dead)
            save(os.path.join(WAVE,'parent_pending_flagged_incr.json'),flagged)
            print(f'  checked {i+1}/{len(cand)} live={len(live)} dead={len(dead)}',flush=True)
        time.sleep(0.4)
    print(f'PENDING-INCR live={len(live)} dead={len(dead)} flagged={len(flagged)}')
if __name__=='__main__': main()
