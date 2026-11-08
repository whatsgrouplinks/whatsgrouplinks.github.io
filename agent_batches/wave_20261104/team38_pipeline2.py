import requests, re, time, html as H, json, sys
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36'
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104'
def log(*a): print(*a, file=sys.stderr, flush=True)
def fetch(url, minlen=20000):
    for i in range(12):
        try:
            s=requests.Session(); s.headers.update({'User-Agent':UA})
            t=s.get(url,timeout=60).text
            if len(t)>=minlen: return t
            log(f'fetch try{i} SHORT {len(t)}')
        except Exception as e:
            log(f'fetch try{i} {type(e).__name__}')
        time.sleep(4+i*2)
    return None
h=fetch('https://instantgrouplink.com/')
if not h: log('FETCH FAILED'); sys.exit(1)
log('LEN',len(h))
WANT={'make money online whatsapp group':'Finance','share market whatsapp group':'Finance',
      'cryptocurrency whatsapp group':'Crypto','trading whatsapp groups':'Crypto',
      'forex trading whatsapp group':'Crypto'}
# split by headings
parts=re.split(r'(<h[23][^>]*>.*?</h[23]>)', h, flags=re.S)
cur=None; rows=[]
for p in parts:
    m=re.match(r'<h[23][^>]*>(.*?)</h[23]>', p, re.S)
    if m:
        cur=H.unescape(re.sub('<[^>]+>','',m.group(1))).strip().lower()
        continue
    if cur and cur in WANT:
        for t in re.findall(r'<tr[^>]*>(.*?)</tr>', p, re.S):
            cm=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', t)
            if not cm: continue
            nm=H.unescape(re.sub(r'<[^>]+>',' ',t)); nm=re.sub(r'\s+',' ',nm).strip()
            nm=re.sub(r'\s*(Click Here|Join|Link)\s*$','',nm).strip()
            if nm: rows.append((nm,cm.group(1),cur,WANT[cur]))
log('section rows',len(rows))
SCAM_PAT=re.compile(r'100%\s*profit|double.{0,5}money|hyip|usdt\s*flash|flash\s*usdt|investment\s*doubler|guaranteed\s*(profit|income|return)', re.I)
scam=[]; ok=[]
for r in rows:
    (scam if SCAM_PAT.search(r[0]) else ok).append(r)
log('scam drops:',len(scam),[s[0] for s in scam])
seen={}; uniq=[]
for nm,code,sec,cat in ok:
    if code in seen: continue
    seen[code]=(nm,sec); uniq.append((nm,code,sec,cat))
log('uniq',len(uniq))
union=set(json.load(open(WAVE+'/dedupe_union.json')))
fresh=[c for c in uniq if c[1] not in union]
log('fresh:',len(fresh),'| in union:',len(uniq)-len(fresh))
vs=requests.Session(); vs.headers.update({'User-Agent':UA})
verified=[]; pending=[]; dead=0
for i,(nm,code,sec,cat) in enumerate(fresh):
    title=''; terr=None
    for att in range(3):
        try:
            r=vs.get('https://chat.whatsapp.com/'+code, timeout=50)
            if r.status_code==429: terr='rate-limited'; break
            m=re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
            title=H.unescape(m.group(1)).strip() if m else ''
            break
        except Exception as e:
            terr=type(e).__name__; time.sleep(2+att*2)
    if terr=='rate-limited':
        pending.append([nm,code,sec,'rate-limited'])
        for x in fresh[i+1:]: pending.append([x[0],x[1],x[2],'rate-limited (batch stop)'])
        log('RATE LIMITED at',i); break
    if title: verified.append([nm,code,title,sec,cat])
    elif terr: pending.append([nm,code,sec,'transport failure: '+terr])
    else: dead+=1
    if i%25==0: log(f'progress {i}/{len(fresh)} v={len(verified)} p={len(pending)} d={dead}')
log(f'DONE v={len(verified)} p={len(pending)} d={dead}')
json.dump({'verified':verified,'pending':pending,'dead':dead,
           'scam':[[s[0],s[1]] for s in scam]}, sys.stdout)
