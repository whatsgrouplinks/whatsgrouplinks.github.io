import json, re, subprocess, time, html, os, sys
from concurrent.futures import ThreadPoolExecutor
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
TITLE_RE=re.compile(r'<meta property="og:title" content="([^"]*)"', re.S)

def fetch(code):
    url=f"https://chat.whatsapp.com/{code}"
    try:
        p=subprocess.run(["curl","-s","-L","--max-time","90","-A",UA,"-o","-","-w","\n%{http_code}",url],
                         capture_output=True,text=True,timeout=100)
        out=p.stdout
        lines=out.rsplit("\n",1)
        http=lines[1].strip() if len(lines)==2 else "000"
        body=lines[0] if len(lines)==2 else out
        if http=="429":
            return {"code":code,"status":"http429","title":""}
        if http=="000" or p.returncode!=0 or not body:
            return {"code":code,"status":"transport","title":"","http":http}
        m=TITLE_RE.search(body)
        title=html.unescape(m.group(1)).strip() if m else ""
        # NOTE: og:description is generic on live AND dead; never a live signal.
        return {"code":code,"status":"live" if title else "dead","title":title,"http":http}
    except Exception as e:
        return {"code":code,"status":"transport","title":"","error":str(e)}

def main():
    fresh=json.load(open(f"{WD}/team20_fresh_77.json"))
    pend=json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team20-77links-pending.json"))
    todo=[]
    for code,v in fresh.items():
        todo.append({"code":code,"src":"77links","page":v["page"],"label":v.get("label",""),"country":v.get("country","PK")})
    for p in pend:
        code=p["invite"].split("/")[-1]
        todo.append({"code":code,"src":"pending-retry","page":p.get("category",""),"label":p.get("name",""),"country":p.get("country","PK"),"prev":p})
    todo.append({"code":"LvkywXnuMqP16t35FhH4gZ","src":"linktogroups","page":"whatsapp-groups","label":"DVoice Media","country":"NG"})
    print("TODO:",len(todo),flush=True)
    ckpt_path=f"{WD}/team20_verify_ckpt.jsonl"
    done={}
    if os.path.exists(ckpt_path):
        for line in open(ckpt_path,encoding='utf-8'):
            try:
                r=json.loads(line); done[r["code"]]=r
            except Exception: pass
    print("already done in ckpt:",len(done),flush=True)
    todo=[t for t in todo if t["code"] not in done]
    print("remaining:",len(todo),flush=True)
    ckpt=open(ckpt_path,'a',encoding='utf-8')
    meta={t["code"]:t for t in todo}
    # keep meta for all codes for later finalize
    allmeta={}
    for code,v in fresh.items(): allmeta[code]={"src":"77links","page":v["page"],"label":v.get("label",""),"country":v.get("country","PK")}
    for p in pend:
        code=p["invite"].split("/")[-1]
        allmeta[code]={"src":"pending-retry","page":p.get("category",""),"label":p.get("name",""),"country":p.get("country","PK"),"prev":p}
    allmeta["LvkywXnuMqP16t35FhH4gZ"]={"src":"linktogroups","page":"whatsapp-groups","label":"DVoice Media","country":"NG"}
    json.dump(allmeta, open(f"{WD}/team20_verify_meta.json",'w'), ensure_ascii=False, indent=1)
    n=0
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(fetch, [t["code"] for t in todo]):
            res["pass"]=1
            done[res["code"]]=res
            ckpt.write(json.dumps(res,ensure_ascii=False)+"\n"); ckpt.flush()
            n+=1
            if n%25==0: print(f"pass1 {n}/{len(todo)}",flush=True)
    ckpt.close()
    # spaced retry for dead + 429 + transport
    need=[c for c,r in done.items() if r["status"] in ("dead","http429","transport")]
    print("pass1 summary:", {s:sum(1 for r in done.values() if r["status"]==s) for s in ("live","dead","http429","transport")}, "to retry:",len(need),flush=True)
    json.dump(done, open(f"{WD}/team20_verify_pass1.json",'w'), ensure_ascii=False, indent=1)
    print("PASS1 DONE")
if __name__=="__main__":
    main()
