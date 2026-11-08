import json, subprocess, re, html, time
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
union=set(json.load(open(WAVE+'dedupe_union.json')))
raw=json.load(open(WAVE+'team01-linkado-raw.json'))
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
def check(code):
    for attempt in range(2):
        try:
            p=subprocess.run(['curl','-s','-m','30','-A',UA,'https://chat.whatsapp.com/'+code],
                             capture_output=True,text=True,timeout=40)
            m=re.search(r'<meta property="og:title" content="([^"]*)"',p.stdout)
            t=html.unescape(m.group(1)).strip() if m else ''
            if t and t.lower() not in ('whatsapp group','join this group on whatsapp','whatsapp'):
                return ('live',t)
            if attempt==0:
                time.sleep(10); continue
            return ('dead',t)
        except Exception:
            if attempt==0:
                time.sleep(10); continue
            return ('transport','')
    return ('dead','')
fresh={c:v for c,v in raw.items() if c not in union}
print('verifying',len(fresh),'linkado codes sequentially',flush=True)
results={}
for code,rec in fresh.items():
    st,title=check(code)
    results[code]={'status':st,'title':title,'rec':rec}
    print(code,st,'|',title[:70],flush=True)
    time.sleep(3)
json.dump(results,open(WAVE+'team01-linkado-verify.json','w'),ensure_ascii=False,indent=1)
print('DONE',flush=True)
