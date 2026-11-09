import json, subprocess, re, html, time, os
BASE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
W8='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
GENERIC={'whatsapp group','join this group on whatsapp','whatsapp','join group on whatsapp'}

def code_of(u):
    return u.split('chat.whatsapp.com/')[-1].split('?')[0].split('#')[0].rstrip('/')

def check_once(code):
    try:
        p=subprocess.run(['curl','-s','-m','30','-A',UA,'-w','\nHTTP_CODE:%{http_code}',
                          'https://chat.whatsapp.com/'+code],
                         capture_output=True,text=True,timeout=40)
        out=p.stdout
        mcode=re.search(r'HTTP_CODE:(\d+)', out)
        http=int(mcode.group(1)) if mcode else 0
        body=out[:mcode.start()] if mcode else out
        mt=re.search(r'<meta property="og:title" content="([^"]*)"', body)
        title=html.unescape(mt.group(1)).strip() if mt else ''
        md=re.search(r'<meta property="og:description" content="([^"]*)"', body)
        desc=html.unescape(md.group(1)).strip() if md else ''
        return http, title, desc, ''
    except Exception as e:
        return 0, '', '', str(e)

pend=json.load(open(W8+'wave_20261108_pending_all.json'))
existing=set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
union=set(json.load(open(W8+'dedupe_union.json')))
todo=[]; skipped=[]
for p in pend:
    c=code_of(p['invite'])
    if c in existing or c in union:
        skipped.append({'code':c,'name':p.get('name'),'reason':'already-in-existing/union'})
    else:
        todo.append(p)
print(f'total={len(pend)} skipped-dup={len(skipped)} to-verify={len(todo)}', flush=True)
for s in skipped: print('SKIP-DUP', s, flush=True)

results={}
for i,p in enumerate(todo):
    c=code_of(p['invite'])
    status=None; title=''; desc=''; http=0; attempts=[]
    for att in range(3):
        http,title,desc,err=check_once(c)
        attempts.append({'attempt':att+1,'http':http,'title':title,'desc':desc[:200],'err':err})
        low=title.lower()
        if http==200 and title and low not in GENERIC:
            status='live'; break
        if http==200 and (not title or low in GENERIC):
            status='dead-empty'  # provisional; retry
            if att<2:
                time.sleep(12); continue
            status='dead'; break
        if http==404:
            status='dead-404'
            if att<2:
                time.sleep(12); continue
            break
        # transport / 429 / 5xx / other
        status='transport'
        if att<2:
            time.sleep(15); continue
    results[c]={'status':status,'http':http,'title':title,'desc':desc,'attempts':attempts,'orig':p}
    print(f"[{i+1}/{len(todo)}] {c} {status} http={http} title={title[:70]!r}", flush=True)
    json.dump({'results':results,'skipped':skipped}, open(BASE+'team15_verify_progress.json','w'), ensure_ascii=False, indent=1)
    time.sleep(3)
json.dump({'results':results,'skipped':skipped}, open(BASE+'team15_verify_progress.json','w'), ensure_ascii=False, indent=1)
from collections import Counter
print('COUNTS', Counter(v['status'] for v in results.values()), flush=True)
print('DONE', flush=True)
