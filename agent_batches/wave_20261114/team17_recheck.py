import json, re, time, html, os
import requests
WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
print("cooldown 240s before recheck...",flush=True)
time.sleep(240)
S=requests.Session(); S.headers.update(UA)
rows=[json.loads(l) for l in open(os.path.join(WD,"team17_verify_ckpt.jsonl"))]
pend=[r["code"] for r in rows if r["status"]=="pending"]
print("pending to recheck:",len(pend),flush=True)
def og_title(body):
    m=re.search(r'<meta property="og:title" content="([^"]*)"', body)
    return html.unescape(m.group(1)).strip() if m else ""
out=[]
for code in pend:
    r=None
    for a in range(3):
        try:
            resp=S.get(f"https://chat.whatsapp.com/{code}", timeout=75)
            title=og_title(resp.text)
            if title=="WhatsApp Group Invite": title=""
            if resp.status_code==200 and title:
                r={"code":code,"status":"live","title":title}; break
            if resp.status_code in (404,410):
                r={"code":code,"status":"dead","title":"","reason":f"http {resp.status_code}"}; break
            if resp.status_code==429:
                if a<2: time.sleep(30); continue
                r={"code":code,"status":"pending","title":"","reason":"http 429 after recheck"}; break
            if resp.status_code==200 and not title:
                if a<2: time.sleep(6); continue
                r={"code":code,"status":"dead","title":"","reason":"empty og:title after recheck retries"}; break
            r={"code":code,"status":"pending","title":"","reason":f"http {resp.status_code} after recheck"}; break
        except Exception as e:
            r={"code":code,"status":"pending","title":"","reason":f"transport after recheck: {type(e).__name__}"}; break
    print(code, r["status"], r.get("title",""), r.get("reason",""), flush=True)
    out.append(r)
    with open(os.path.join(WD,"team17_recheck_ckpt.jsonl"),"a") as f:
        f.write(json.dumps(r,ensure_ascii=False)+"\n")
    time.sleep(3)
import collections
print("RECHECK DONE", collections.Counter(x["status"] for x in out), flush=True)
