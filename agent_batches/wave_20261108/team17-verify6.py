import subprocess, re, json, time, threading
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
def verify(code):
    for attempt in range(2):
        time.sleep(1.0)
        html=fetch(code)
        if html is None:
            if attempt==0: time.sleep(5); continue
            return ('pending','transport')
        m=re.search(r'<meta property="og:title" content="([^"]*)"',html)
        title=unescape(m.group(1)).strip() if m else ''
        if not title:
            if attempt==0: time.sleep(20); continue
            return ('dead','200-empty-title-after-retry')
        low=title.lower()
        if low in GENERIC: return ('dead','generic-title:'+title)
        if any(e in title for e in ADULT_EMOJI) or BAD_WORDS.search(title): return ('dead','adult-title:'+title)
        if 'channel' in low and 'group' not in low: return ('dead','channel-title:'+title)
        return ('live',title)
    return ('dead','unknown')
cands=json.load(open(WAVE+'team17-scratch-cands.json'))
results=json.load(open(WAVE+'team17-verify5.json'))
results={k:{'cand':v['cand'],'res':tuple(v['res'])} for k,v in results.items()}
todo=[c for c in cands if c not in results or results[c]['res'][0]=='pending']
for c in [c for c in list(results) if results[c]['res'][0]=='pending']:
    del results[c]
print(f'verify6: base-done={len(results)} todo={len(todo)} live-so-far={sum(1 for v in results.values() if v["res"][0]=="live")}',flush=True)
lock=threading.Lock(); n=[0]
def work(code):
    r=verify(code)
    with lock:
        results[code]={'cand':cands[code],'res':r}
        n[0]+=1
        if n[0]%25==0:
            print(f"{n[0]}/{len(todo)} live={sum(1 for v in results.values() if v['res'][0]=='live')} pend={sum(1 for v in results.values() if v['res'][0]=='pending')}",flush=True)
            json.dump({k:{'cand':v['cand'],'res':list(v['res'])} for k,v in results.items()}, open(WAVE+'team17-verify6.json','w'), ensure_ascii=False)
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, todo))
json.dump({k:{'cand':v['cand'],'res':list(v['res'])} for k,v in results.items()}, open(WAVE+'team17-verify6.json','w'), ensure_ascii=False)
from collections import Counter
print('DONE live',sum(1 for v in results.values() if v['res'][0]=='live'),
      'pending',sum(1 for v in results.values() if v['res'][0]=='pending'),
      'dead',sum(1 for v in results.values() if v['res'][0]=='dead'),flush=True)
print(Counter(v['res'][1].split(':')[0] for v in results.values() if v['res'][0]=='dead'))
