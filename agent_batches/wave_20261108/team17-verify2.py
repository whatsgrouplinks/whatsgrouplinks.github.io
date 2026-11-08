import subprocess, re, json, time, threading, sys
from concurrent.futures import ThreadPoolExecutor
from html import unescape
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
GENERIC={'whatsapp group','join this group on whatsapp','whatsapp','join group on whatsapp'}
ADULT_EMOJI=set('🥵🍆🍑🔞💦👅👄💋')
BAD_WORDS=re.compile(r'\b(xxx|porn|porno|sex|nude|call\s*girl|escort)\b',re.I)
def fetch(code):
    try:
        p=subprocess.run(['curl','-s','--max-time','25','-A',UA,f'https://chat.whatsapp.com/{code}'],
            capture_output=True,text=True,timeout=35)
        return p.stdout if p.returncode==0 and p.stdout else None
    except Exception:
        return None
def verify(code, retries=1, pause=15):
    for attempt in range(retries+1):
        time.sleep(1.0)
        html=fetch(code)
        if html is None:
            if attempt<retries: time.sleep(5); continue
            return ('pending','transport')
        m=re.search(r'<meta property="og:title" content="([^"]*)"',html)
        title=unescape(m.group(1)).strip() if m else ''
        if not title:
            if attempt<retries: time.sleep(pause); continue
            return ('dead','200-empty-title-after-retry')
        low=title.lower()
        if low in GENERIC: return ('dead','generic-title:'+title)
        if any(e in title for e in ADULT_EMOJI) or BAD_WORDS.search(title): return ('dead','adult-title:'+title)
        if 'channel' in low and 'group' not in low: return ('dead','channel-title:'+title)
        return ('live',title)
    return ('dead','unknown')
mode=sys.argv[1] if len(sys.argv)>1 else 'pass1'
cands=json.load(open(WAVE+'team17-scratch-cands.json'))
prog=json.load(open(WAVE+'team17-verify-progress.json'))
done_codes=set(prog.keys())
live_codes={k for k,v in prog.items() if v['res'][1]=='live'}
if mode=='pass1':
    todo=[c for c in cands if c not in done_codes]
elif mode=='pass2':
    prev=json.load(open(WAVE+'team17-verify2-pass1.json'))
    todo=[c for c,v in prev.items() if v['res'][1] in ('dead','pending') and 'empty-title' in v['res'][2] or v['res'][1]=='pending']
    live_codes |= {k for k,v in prev.items() if v['res'][1]=='live'}
    prev_results=prev
else:
    raise SystemExit('bad mode')
print(f'{mode}: todo={len(todo)} already-live={len(live_codes)}',flush=True)
results={}
lock=threading.Lock(); n=[0]
def work(code):
    r=verify(code, retries=1, pause=15)
    with lock:
        results[code]={'cand':cands[code],'res':r}
        n[0]+=1
        if n[0]%25==0:
            print(f"{n[0]}/{len(todo)} live={sum(1 for v in results.values() if v['res'][1]=='live')} pend={sum(1 for v in results.values() if v['res'][1]=='pending')}",flush=True)
            json.dump(results, open(WAVE+f'team17-verify2-{mode}.json','w'), ensure_ascii=False)
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, todo))
json.dump(results, open(WAVE+f'team17-verify2-{mode}.json','w'), ensure_ascii=False)
from collections import Counter
print(mode,'DONE live',sum(1 for v in results.values() if v['res'][1]=='live'),
      'pending',sum(1 for v in results.values() if v['res'][1]=='pending'),
      'dead',sum(1 for v in results.values() if v['res'][1]=='dead'),flush=True)
print(Counter(v['res'][2].split(':')[0] for v in results.values() if v['res'][1]=='dead'))
