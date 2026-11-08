import requests, re, json, time, threading
from html import unescape
from concurrent.futures import ThreadPoolExecutor
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
cands=json.load(open(WAVE+'team17-scratch-cands.json'))
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
GENERIC={'whatsapp group','join this group on whatsapp','whatsapp','join group on whatsapp'}
ADULT_EMOJI=set('🥵🍆🍑🔞💦👅👄💋')
BAD_WORDS=re.compile(r'\b(xxx|porn|porno|sex|nude|call\s*girl|escort|randi)\b',re.I)
# pre-filter junk names
items=[]
dropped_junk=0
for code,v in cands.items():
    name=v['name']
    stripped=re.sub(r'[^\w\s]','',name,flags=re.UNICODE).strip()
    if len(stripped)<2:
        dropped_junk+=1; continue
    if any(e in name for e in ADULT_EMOJI) or BAD_WORDS.search(name):
        dropped_junk+=1; continue
    items.append((code,v))
print('to verify:',len(items),'pre-dropped junk:',dropped_junk)
def check(code):
    url=f'https://chat.whatsapp.com/{code}'
    for attempt in range(2):
        try:
            time.sleep(0.6)
            r=requests.get(url,headers=UA,timeout=20)
            if r.status_code!=200:
                return (code,'dead',f'http{r.status_code}')
            m=re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', r.text)
            if not m:
                m=re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:title"', r.text)
            title=unescape(m.group(1)).strip() if m else ''
            if not title:
                if attempt==0:
                    time.sleep(8); continue
                return (code,'dead','200-empty-title-after-retry')
            low=title.lower().strip()
            if low in GENERIC:
                return (code,'dead','generic-title:'+title)
            if any(e in title for e in ADULT_EMOJI) or BAD_WORDS.search(title):
                return (code,'dead','adult-title:'+title)
            if 'channel' in low and 'group' not in low:
                return (code,'dead','channel-title:'+title)
            return (code,'live',title)
        except Exception as e:
            if attempt==0:
                time.sleep(5); continue
            return (code,'pending',f'transport:{type(e).__name__}')
    return (code,'dead','unknown')
results={}
lock=threading.Lock(); done=[0]
def work(item):
    code,v=item
    res=check(code)
    with lock:
        results[code]=(v,res)
        done[0]+=1
        if done[0]%50==0:
            print(f'{done[0]}/{len(items)} live={sum(1 for _,r in results.values() if r[1]=="live")} pending={sum(1 for _,r in results.values() if r[1]=="pending")}',flush=True)
            json.dump({k:{'cand':v,'res':r} for k,(v,r) in results.items()}, open(WAVE+'team17-verify-progress.json','w'), ensure_ascii=False)
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, items))
live={k:v for k,(v,r) in results.items() if r[1]=='live'}
pend={k:v for k,(v,r) in results.items() if r[1]=='pending'}
dead={k:v for k,(v,r) in results.items() if r[1]=='dead'}
print('LIVE',len(live),'PENDING',len(pend),'DEAD',len(dead))
json.dump({k:{'cand':v,'res':r} for k,(v,r) in results.items()}, open(WAVE+'team17-verify-results.json','w'), ensure_ascii=False)
from collections import Counter
print(Counter(r[2].split(':')[0] for _,r in dead.values()))
