import json, re, random, subprocess, time, html, os
from concurrent.futures import ThreadPoolExecutor

UAS=[
 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
]
def check(code, ua_idx=0):
    url=f'https://chat.whatsapp.com/{code}'
    try:
        r=subprocess.run(['curl','-s','--max-time','25','-A',UAS[ua_idx%len(UAS)],url],
                         capture_output=True,text=True,timeout=30)
        body=r.stdout or ''
        m=re.search(r'<meta property="og:title" content="([^"]*)"',body)
        title=html.unescape(m.group(1)).strip() if m else ''
        m2=re.search(r'<meta property="og:description" content="([^"]*)"',body)
        desc=html.unescape(m2.group(1)).strip() if m2 else ''
        return {'http':200 if body else 0,'title':title,'desc':desc}
    except Exception as e:
        return {'http':0,'title':'','desc':'','err':str(e)}

def verify_one(job):
    code=job['code']
    a=check(code,0)
    if a['http']==0 or a['title']=='':
        time.sleep(15)
        b=check(code,1)
        # keep the better attempt
        if b['title']: a=b
        elif b['http']!=0: a={'http':b['http'],'title':'','desc':b.get('desc',''),'attempts':2}
        else: a={**a,'attempts':2}
    return {**job,'result':a}

jobs=[]
# A: team13 all 97
t13=json.load(open('team13-candidates.json'))
for it in t13:
    code=it['invite'].split('/')[-1]
    jobs.append({'set':'team13','code':code,'name':it['name'],'category':it['category'],'country':it['country'],'description':it['description']})
# B: transport-pending (with codes only; drop adult D914 pending)
pend_sources={'team15':2,'team22':5,'team06':2,'team08':4,'team09':6,'team12':5,'team24':1,'team07':1,'team04':1}
DROP={'D914yMtMMzH57FwW1wPK9E'}
for n in [15,22,6,8,9,12,24,7,4]:
    items=json.load(open(f'team{n:02d}-pending.json'))
    for it in items:
        code=it.get('code') or (it.get('invite','').split('/')[-1] if it.get('invite') else '')
        if not code or code in DROP: continue
        jobs.append({'set':f'pending-t{n:02d}','code':code,'name':it.get('name',''),'category':it.get('category',''),'country':it.get('country',''),'description':it.get('description',''),'ctx':it.get('ctx','')[:200]})
# C: 30 random team17 pending
t17=json.load(open('team17-pending.json'))
random.seed(20261109)
for it in random.sample(t17,30):
    jobs.append({'set':'team17-sample','code':it['code'],'name':it.get('listing_name',''),'category_hint':it.get('category_hint','')})
# D: 35 random prelim-clean codes (excluding team13)
clean=json.load(open('wave_20261109_verified_clean_prelim.json'))
t13codes={it['invite'].split('/')[-1] for it in t13}
pool=[c for c in clean if c['invite'].split('/')[-1] not in t13codes]
for it in random.sample(pool,35):
    jobs.append({'set':'clean-spot','code':it['invite'].split('/')[-1],'name':it['name'],'category':it['category'],'country':it['country']})
print('total jobs:',len(jobs))
json.dump(jobs,open('parent_verify_jobs.json','w'),indent=1)

state={}
if os.path.exists('parent_verify_state.json'):
    state=json.load(open('parent_verify_state.json'))
done=set(state.keys())
todo=[j for j in jobs if j['code'] not in done]
print('remaining:',len(todo))
results=[]
def run(j):
    time.sleep(0.7)
    r=verify_one(j)
    state[r['code']]=r
    return r
with ThreadPoolExecutor(max_workers=3) as ex:
    for i,r in enumerate(ex.map(run,todo)):
        if i%20==0:
            json.dump(state,open('parent_verify_state.json','w'),indent=1)
            print(f'{i}/{len(todo)} done',flush=True)
json.dump(state,open('parent_verify_state.json','w'),indent=1)
from collections import Counter
print(Counter((v['set'], bool(v['result'].get('title'))) for v in state.values()))
