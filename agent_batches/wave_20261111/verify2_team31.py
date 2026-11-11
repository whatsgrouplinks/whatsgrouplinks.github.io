import json, subprocess, re, time, threading, html as H
from concurrent.futures import ThreadPoolExecutor
# TEAM 31 — wave 20261111, tglinkhub verify2 resume
# Reads Nov-10 raw dir; writes NEW results to wave_20261111 dir only.
RAW='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team32_raw/'
OUT='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/'
fresh=json.load(open(f'{RAW}tg_fresh_codes.json'))
recs=json.load(open(f'{RAW}tg_code_recs.json'))
dates=json.load(open(f'{RAW}tg_dates.json'))
excl=json.load(open(f'{RAW}tg_name_exclusions.json'))
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
keep=[c for c in fresh if c not in excl]
MINED_NOV9={'whatsapp-group-links','kerala-group','malayalam-whatsapp'}
def sortkey(c):
    r=recs.get(c,{})
    slug=r.get('slug','') if r else ''
    mined=1 if slug in MINED_NOV9 else 0
    return (mined, slug)
keep.sort(key=sortkey)
print("to verify:",len(keep),flush=True)
print("first 5 slugs:",[recs.get(c,{}).get('slug') for c in keep[:5]],flush=True)
done={}
for path in (f'{RAW}verify2_results.jsonl', f'{OUT}verify2_results_20261111.jsonl'):
    try:
        for line in open(path):
            d=json.loads(line); done[d['code']]=d
    except FileNotFoundError:
        pass
todo=[c for c in keep if c not in done]
print("already done (Nov10 + this run):",len(done),"todo:",len(todo),flush=True)
ogpat=re.compile(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)',re.I)
ogpat2=re.compile(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']',re.I)
def fetch(code):
    url=f'https://chat.whatsapp.com/{code}'
    try:
        p=subprocess.run(['curl','-sS','-A',UA,'--max-time','30','-w','\n__HTTP__%{http_code}','-L',url],
                         capture_output=True,text=True,timeout=35)
        out=p.stdout
        m=re.search(r'__HTTP__(\d+)\s*$',out)
        http=int(m.group(1)) if m else 0
        body=out[:m.start()] if m else out
        return http,body,p.returncode,p.stderr.strip()[:120]
    except Exception as e:
        return 0,'',-1,str(e)[:120]
def check(code):
    last_err=''
    for attempt in range(3):
        http,body,rc,err=fetch(code)
        if http==0 or not body.strip():
            last_err=f'transport: rc={rc} {err}'
            if attempt<1:
                time.sleep(2); continue
            return {'code':code,'status':'pending','http':0,'og_title':'','reason':last_err}
        og=ogpat.search(body) or ogpat2.search(body)
        ogtitle=H.unescape(og.group(1)).strip() if og else ''
        if http==200 and ogtitle:
            return {'code':code,'status':'live','http':http,'og_title':ogtitle}
        if http==200 and not ogtitle:
            if attempt<2:
                time.sleep(2); continue
            return {'code':code,'status':'dead','http':http,'og_title':'','reason':'empty og:title after 3 attempts'}
        return {'code':code,'status':'dead','http':http,'og_title':ogtitle,'reason':f'http {http}'}
    return {'code':code,'status':'pending','http':0,'og_title':'','reason':last_err or 'transport failure'}
lock=threading.Lock(); fout=open(f'{OUT}verify2_results_20261111.jsonl','a')
n=[0]; t0=time.time()
def work(code):
    r=check(code)
    with lock:
        fout.write(json.dumps(r,ensure_ascii=False)+'\n'); fout.flush()
        n[0]+=1
        if n[0]%100==0:
            print(f"{n[0]}/{len(todo)} elapsed {time.time()-t0:.0f}s",flush=True)
    time.sleep(0.5)
with ThreadPoolExecutor(max_workers=6) as ex:
    list(ex.map(work,todo))
fout.close()
print("DONE",n[0],"elapsed",time.time()-t0,flush=True)
