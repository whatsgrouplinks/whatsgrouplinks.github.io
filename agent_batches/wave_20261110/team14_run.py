import json, re, subprocess, time, html, os
from concurrent.futures import ThreadPoolExecutor

WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def curl(url, out):
    p=subprocess.run(["curl","-s","-A",UA,"--max-time","25","-o",out,"-w","%{http_code}",url],
                     capture_output=True,text=True,timeout=40)
    return p.stdout.strip()

# 1. fetch pages
for url, fn in [("https://77links.com/karachi-whatsapp-group-links/","team14_kar.html"),
                ("https://77links.com/islamic-whatsapp-group-links/","team14_isl.html")]:
    print(url, curl(url, os.path.join(WD,fn)), flush=True)

# 2. extract (code -> directory label)
def extract(fn):
    t=open(os.path.join(WD,fn),encoding='utf-8',errors='ignore').read()
    pat=re.compile(r'wp-block-columns[^>]*>.*?<p[^>]*>(.*?)</p>.*?href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', re.S)
    d={}
    for name,code in pat.findall(t):
        name=html.unescape(re.sub(r'<[^>]+>','',name))
        name=re.sub(r'\s+',' ',name).strip()
        d.setdefault(code,name)
    return d
kar=extract("team14_kar.html"); isl=extract("team14_isl.html")
allc={**kar, **isl}
print("kar",len(kar),"isl",len(isl),"combined",len(allc), flush=True)

# 3. dedupe
a=json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'))
g=json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
s=set(a)
for it in g:
    m=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', it.get('invite',''))
    if m: s.add(m.group(1))
print("union",len(s), flush=True)
fresh={c:n for c,n in allc.items() if c not in s}
print("fresh",len(fresh),"dup",len(allc)-len(fresh), flush=True)
json.dump(fresh, open(os.path.join(WD,"team14_fresh_raw.json"),'w'))

# 4. verify with per-code checkpointing
CK=os.path.join(WD,"team14_verify_ckpt.jsonl")
done={}
if os.path.exists(CK):
    for line in open(CK):
        r=json.loads(line); done[r["code"]]=r
print("already verified:",len(done), flush=True)

def fetch(code):
    if code in done: return done[code]
    url=f"https://chat.whatsapp.com/{code}"
    last=None
    for attempt in range(3):
        try:
            p=subprocess.run(["curl","-s","-A",UA,"--max-time","15","-w","\n%{http_code}",url],
                             capture_output=True,text=True,timeout=20)
            out=p.stdout
            parts=out.rsplit("\n",1)
            body=parts[0] if len(parts)>1 else out
            status=parts[1].strip() if len(parts)>1 else ""
            m=re.search(r'<meta property="og:title" content="([^"]*)"', body)
            title=html.unescape(m.group(1)).strip() if m else ""
            if status=="200" and title:
                r={"code":code,"status":"live","title":title}; break
            if status=="200" and not title:
                last={"code":code,"status":"dead","title":"","reason":"empty og:title after retries"}
                time.sleep(2); continue
            if status in ("404","410"):
                r={"code":code,"status":"dead","title":"","reason":f"http {status}"}; break
            if status=="":
                r={"code":code,"status":"pending","title":"","reason":"transport: no HTTP status"}; break
            r={"code":code,"status":"dead","title":"","reason":f"http {status}"}; break
        except Exception as e:
            r={"code":code,"status":"pending","title":"","reason":f"transport: {e}"}; break
    else:
        r=last
    with open(CK,"a") as f:
        f.write(json.dumps(r)+"\n")
    return r

codes=[c for c in fresh if c not in done]
def run(code):
    r=fetch(code)
    time.sleep(0.55)
    return r
with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(run, codes))
print("verify done", flush=True)
