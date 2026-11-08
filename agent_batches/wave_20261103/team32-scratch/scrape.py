import re, json, time, subprocess

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/'
union=set(json.load(open(WAVE+'dedupe_union.json')))

def fetch(url):
    for _ in range(2):
        p=subprocess.run(['curl','-sL','-A',UA,'--max-time','40',url],
                         capture_output=True, timeout=60)
        if p.returncode==0 and len(p.stdout)>10000:
            return p.stdout.decode('utf-8','ignore')
        time.sleep(2)
    return ''

def records(t):
    s=t.replace('\\\\"','"').replace('\\\\n',' ').replace('\\n',' ')
    for _ in range(3):
        s2=s.replace('\\"','"')
        if s2==s: break
        s=s2
    s=re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1),16)), s)
    recs=[]
    for m in re.finditer(r'"group_title":"(.*?)"(.*?)https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', s):
        title=m.group(1); mid=m.group(2); code=m.group(3)
        desc=re.search(r'"group_desc":"(.*?)"', mid)
        win=s[max(0,m.start()-600):m.start()+2000]
        cslug=re.search(r'"category_slug":"(.*?)"', win)
        cname=re.search(r'"category_name":"(.*?)"', win)
        created=re.search(r'"created_at":"(.*?)"', mid) or re.search(r'"created_at":"(.*?)"', s[m.start():m.start()+1500])
        recs.append({'code':code,'title':title,
                     'desc':desc.group(1) if desc else '',
                     'category_name':cname.group(1) if cname else '',
                     'category_slug':cslug.group(1) if cslug else '',
                     'created_at':created.group(1) if created else ''})
    return recs

all_recs={}
pages=0
for p in range(1, 31):
    url=f'https://www.groupjoin.link/country/nigeria?page={p}&limit=20&safeSearch=strict'
    t=fetch(url)
    if not t:
        print('page',p,'FETCH FAIL'); break
    recs=records(t)
    pages=p
    if not recs:
        print('page',p,'no records - stop'); break
    new_here=0
    for r in recs:
        if r['code'] not in union and r['code'] not in all_recs:
            all_recs[r['code']]=r; new_here+=1
    print('page',p,'records',len(recs),'new',new_here, flush=True)
    time.sleep(1)

json.dump(list(all_recs.values()), open(WAVE+'team32-scratch/candidates.json','w'), indent=1)
print('PAGES:',pages,'NEW CANDIDATES:',len(all_recs))
