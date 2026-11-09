import json, os, re, subprocess, sys, time, html as htmllib

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
WORK="team06_raw/verify"
os.makedirs(WORK, exist_ok=True)
RESULTS="team06_raw/verify_results.jsonl"
TITLE_RE=re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)

def load_results():
    res={}
    if os.path.exists(RESULTS):
        for ln in open(RESULTS, encoding='utf-8'):
            try:
                r=json.loads(ln); res.setdefault(r['code'],[]).append(r)
            except Exception: pass
    return res

def status_of(code, res):
    """return ('live',title) | ('ambig',) | ('dead',) | ('pending',reason) | None"""
    atts=res.get(code,[])
    if not atts: return None
    last=atts[-1]
    return last.get('final')

def run_chunk(codes, attempt):
    """Run one curl --parallel chunk. Returns dict code -> (http, title or None, ok)"""
    out={}
    cmd=["curl","-s","--parallel","--parallel-max","2","--http2","--compressed",
         "--rate","2/s","--retry","1","--retry-delay","3","--max-time","25","-A",UA,
         "-w", "RES %{url_effective} %{http_code} %{time_total}\n"]
    for c in codes:
        cmd+=["-o", f"{WORK}/{c}.html", f"https://chat.whatsapp.com/{c}"]
    t0=time.time()
    p=subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    for ln in (p.stdout or "").splitlines():
        m=re.match(r'RES https://chat\.whatsapp\.com/(\S+) (\d{3}) ([\d.]+)', ln.strip())
        if m:
            out[m.group(1)]=(int(m.group(2)), float(m.group(3)))
    # parse titles, delete html
    res={}
    for c in codes:
        f=f"{WORK}/{c}.html"
        http, tt = out.get(c, (0, 0.0))
        title=None
        if os.path.exists(f):
            try:
                txt=open(f, encoding='utf-8', errors='ignore').read()
                m=TITLE_RE.search(txt)
                if m: title=htmllib.unescape(m.group(1)).strip()
            except Exception: pass
            try: os.remove(f)
            except Exception: pass
        res[c]=(http, title)
    return res, time.time()-t0

def main():
    attempt=int(sys.argv[1]) if len(sys.argv)>1 else 1
    codes=json.load(open('team06_raw/newcodes.json'))
    res=load_results()
    if attempt==1:
        todo=[c for c in codes if c not in res]
    else:
        # retry only ambiguous (200 + empty title after previous attempts), max 2 retries
        todo=[]
        for c in codes:
            atts=res.get(c,[])
            if not atts: todo.append(c); continue
            last=atts[-1]
            if last.get('final') in ('ambig','pending') and last.get('attempt',0)<3:
                todo.append(c)
    print(f"attempt {attempt}: {len(todo)} codes to check", flush=True)
    done=0; live=0; amb=0; pend=0; badstreak=0
    CH=45
    with open(RESULTS,'a',encoding='utf-8') as fh:
        for s in range(0,len(todo),CH):
            chunk=todo[s:s+CH]
            try:
                r,dt=run_chunk(chunk, attempt)
            except Exception as e:
                print("chunk error", e, flush=True)
                r={c:(0,None) for c in chunk}
            for c in chunk:
                http,title=r.get(c,(0,None))
                if http==200 and title:
                    final='live'; live+=1; badstreak=0
                elif http==200 and not title:
                    final='ambig'; amb+=1; badstreak=0
                elif http in (429,403):
                    final='pending'; pend+=1; badstreak+=1
                elif http==0:
                    final='pending'; pend+=1; badstreak+=1
                else:
                    final='dead'; badstreak=0
                rec={'code':c,'attempt':attempt,'http':http,'title':title,'final':final,
                     'ts':time.strftime('%Y-%m-%dT%H:%M:%S')}
                fh.write(json.dumps(rec,ensure_ascii=False)+"\n"); fh.flush()
                done+=1
            print(f"  {done}/{len(todo)} chunk {dt:.1f}s live={live} ambig={amb} pend={pend}", flush=True)
            if badstreak>=9:
                print("PAUSE: 9 consecutive transport failures - sleeping 30s", flush=True)
                time.sleep(30)
                badstreak=0
            time.sleep(0.6)
    print(f"attempt {attempt} done: live={live} ambig={amb} pend={pend}", flush=True)

if __name__=='__main__':
    main()
