import json, re, subprocess, time, html
from concurrent.futures import ThreadPoolExecutor
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
rows=[json.loads(l) for l in open('team14_verify_ckpt.jsonl')]
todo=[r['code'] for r in rows if r['status']=='dead' and r['reason']=='http 000']
print("retrying", len(todo), flush=True)
def fetch(code):
    for attempt in range(2):
        try:
            p=subprocess.run(["curl","-s","-A",UA,"--max-time","15","-w","\n%{http_code}",f"https://chat.whatsapp.com/{code}"],
                             capture_output=True,text=True,timeout=20)
            parts=p.stdout.rsplit("\n",1)
            body=parts[0] if len(parts)>1 else p.stdout
            status=parts[1].strip() if len(parts)>1 else ""
            m=re.search(r'<meta property="og:title" content="([^"]*)"', body)
            title=html.unescape(m.group(1)).strip() if m else ""
            if status=="200" and title:
                return {"code":code,"status":"live","title":title}
            if status=="200" and not title:
                time.sleep(2); continue
            if status in ("404","410"):
                return {"code":code,"status":"dead","title":"","reason":f"http {status}"}
            if status in ("","000"):
                time.sleep(3); continue
            return {"code":code,"status":"dead","title":"","reason":f"http {status}"}
        except Exception as e:
            time.sleep(3); continue
    return {"code":code,"status":"pending","title":"","reason":"transport: no HTTP status (curl 000) after 2 attempts"}
def run(code):
    r=fetch(code); time.sleep(1.0); return r
with ThreadPoolExecutor(max_workers=2) as ex:
    res=list(ex.map(run, todo))
with open('team14_verify_ckpt2.jsonl','w') as f:
    for r in res: f.write(json.dumps(r)+"\n")
from collections import Counter
print(Counter(r['status'] for r in res))
for r in res:
    if r['status']!='pending': print(r)
