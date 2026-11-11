import json, re, time, sys, os, html, subprocess
from concurrent.futures import ThreadPoolExecutor

WAVE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
def fetch(url):
    for attempt in (1,2):
        try:
            p=subprocess.run(["curl","-sL","-A",UA,"--compressed","--max-time","90",url],
                             capture_output=True, timeout=100)
            h=p.stdout.decode('utf-8','ignore')
            if p.returncode==0 and h and '<title>' in h:
                return h
        except Exception:
            pass
        time.sleep(5)
    return ""
def extract(h, url):
    m=re.search(r'<title>(.*?)</title>', h, re.S|re.I)
    title=html.unescape(m.group(1)).strip() if m else ""
    name=title
    cat_raw=""
    if name.startswith("Grupo de WhatsApp "): name=name[len("Grupo de WhatsApp "):]
    if " - " in name: name, cat_raw = name.rsplit(" - ",1)
    d=re.search(r'property="og:description"\s+content="([^"]*)"', h)
    desc=html.unescape(d.group(1)).strip() if d else ""
    codes=list(dict.fromkeys(re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})', h)))
    return {"url":url,"name":name.strip(),"cat_raw":cat_raw.strip(),"desc":desc,"codes":codes,"title":title}
if __name__=="__main__":
    urls=json.load(open(WAVE+"leads_slice2.json"))
    out_file=WAVE+"team02-extracted.jsonl"
    done=set()
    if os.path.exists(out_file):
        with open(out_file) as f:
            for line in f:
                try: done.add(json.loads(line)["url"])
                except: pass
    todo=[u for u in urls if u not in done]
    print(f"slice {len(urls)} done {len(done)} todo {len(todo)}", flush=True)
    def work(u):
        h=fetch(u)
        if not h: return {"url":u,"error":"fetch-fail"}
        return extract(h,u)
    t0=time.time(); n=0
    with open(out_file,"a") as f, ThreadPoolExecutor(max_workers=12) as ex:
        for rec in ex.map(work, todo):
            f.write(json.dumps(rec, ensure_ascii=False)+"\n"); f.flush(); n+=1
            if n%100==0: print(f"{n}/{len(todo)} elapsed {time.time()-t0:.0f}s", flush=True)
    print(f"DONE {n} elapsed {time.time()-t0:.0f}s", flush=True)
