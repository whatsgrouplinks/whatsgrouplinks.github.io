import json, subprocess, re, html, time, os, threading
from concurrent.futures import ThreadPoolExecutor
LOCK=threading.Lock()
BASE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'
W8='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
GENERIC={'whatsapp group','join this group on whatsapp','whatsapp','join group on whatsapp'}

def code_of(u):
    return u.split('chat.whatsapp.com/')[-1].split('?')[0].split('#')[0].rstrip('/')

def check_once(code):
    try:
        p=subprocess.run(['curl','-s','-m','20','-A',UA,'-w','\nHTTP_CODE:%{http_code}',
                          'https://chat.whatsapp.com/'+code],
                         capture_output=True,text=True,timeout=30)
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

def verify(p):
    c=code_of(p['invite'])
    status=None; title=''; desc=''; http=0; attempts=[]
    for att in range(3):
        http,title,desc,err=check_once(c)
        attempts.append({'attempt':att+1,'http':http,'title':title,'desc':desc[:200],'err':err})
        low=title.lower()
        if http==200 and title and low not in GENERIC:
            status='live'; break
        if http==200 and (not title or low in GENERIC):
            status='dead'
            if att<2:
                time.sleep(10); continue
            break
        if http==404:
            status='dead-404'
            if att<2:
                time.sleep(10); continue
            break
        status='transport'
        if att<2:
            time.sleep(12); continue
    return c, {'status':status,'http':http,'title':title,'desc':desc,'attempts':attempts,'orig':p}

prog=json.load(open(BASE+'team15_verify_progress.json'))
results=prog['results']; skipped=prog['skipped']
pend=json.load(open(W8+'wave_20261108_pending_all.json'))
done=set(results.keys()) | {s['code'] for s in skipped}
todo=[p for p in pend if code_of(p['invite']) not in done]
print(f'resuming: done={len(done)} remaining={len(todo)}', flush=True)
idx=[0]
def save():
    with LOCK:
        snap={'results':dict(results),'skipped':skipped}
    json.dump(snap, open(BASE+'team15_verify_progress.json','w'), ensure_ascii=False, indent=1)

def run(p):
    c,res=verify(p)
    with LOCK:
        results[c]=res
        idx[0]+=1
        n=idx[0]
    print(f"[{n}/{len(todo)}] {c} {res['status']} http={res['http']} title={res['title'][:70]!r}", flush=True)
    save()
    return c
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(run, todo))
save()
from collections import Counter
print('COUNTS', Counter(v['status'] for v in results.values()), flush=True)
print('DONE', flush=True)
