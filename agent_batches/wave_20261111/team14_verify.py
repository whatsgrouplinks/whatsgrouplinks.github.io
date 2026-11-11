import json, re, subprocess, time, html, os, sys
from concurrent.futures import ThreadPoolExecutor

WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# ---------- dedupe ----------
allc=json.load(open(os.path.join(WD,"team14_all_extracted.json")))
a=json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'))
g=json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
s=set(a)
for it in g:
    m=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', it.get('invite',''))
    if m: s.add(m.group(1))
print("union",len(s), flush=True)

# also dedupe against yesterday's team14 verified (already in groups? no - not merged yet;
# yesterday's verified are NOT in .existing_codes.json nor groups.json, so add them)
prev=json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team14-77links.json'))
for it in prev:
    m=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', it.get('invite',''))
    if m: s.add(m.group(1))
# and this wave's other teams' files already written? only leads_slice* exist (no verified yet). skip.

fresh={c:v for c,v in allc.items() if c not in s}
print("extracted",len(allc),"fresh",len(fresh),"dup",len(allc)-len(fresh), flush=True)
json.dump(fresh, open(os.path.join(WD,"team14_fresh_raw.json"),'w'), ensure_ascii=False, indent=1)

# ---------- verify (slow, checkpointed) ----------
CK=os.path.join(WD,"team14_verify_ckpt.jsonl")
done={}
if os.path.exists(CK):
    for line in open(CK):
        try:
            r=json.loads(line); done[r["code"]]=r
        except Exception: pass
print("already checkpointed:",len(done), flush=True)

def fetch(code):
    if code in done: return done[code]
    url=f"https://chat.whatsapp.com/{code}"
    r=None
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
                r={"code":code,"status":"dead","title":"","reason":"empty og:title after retries"}
                time.sleep(2); continue
            if status in ("404","410"):
                r={"code":code,"status":"dead","title":"","reason":f"http {status}"}; break
            if status=="":
                r={"code":code,"status":"pending","title":"","reason":"transport: no HTTP status"}; break
            r={"code":code,"status":"dead","title":"","reason":f"http {status}"}; break
        except Exception as e:
            r={"code":code,"status":"pending","title":"","reason":f"transport: {e}"}; break
    if r is None:
        r={"code":code,"status":"dead","title":"","reason":"empty og:title after retries"}
    with open(CK,"a") as f:
        f.write(json.dumps(r, ensure_ascii=False)+"\n")
    return r

# priority order: pending retries from Nov-10 first, then karachi/islamic fresh, then rest by page order
prev_pending=json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team14-77links-pending.json'))
retry_codes=[re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', it['invite']).group(1) for it in prev_pending]
page_order=["karachi","islamic","canada","indonesia","islamabad","lahore","pakistan-cricket","photo-editing","psl","sri-lanka","tamil","usa","arabic","dawateislami","madani-channel","quran","ramadan"]
def prio(c):
    v=fresh.get(c)
    if c in retry_codes: return (0,0)
    if v is None: return (9,99)
    pg=v["page"]
    return (1, page_order.index(pg)) if pg in page_order else (2,99)

codes=[c for c in fresh if c not in done]
# include retry codes even if already in done? No - re-verify only if checkpoint says pending.
retry_todo=[c for c in retry_codes if c in done and done[c]["status"]=="pending" and c not in fresh]
# retry_todo codes are fresh too (they were fresh yesterday); ensure in fresh dict
for c in retry_todo:
    if c not in fresh:
        # recover label from pending file
        for it in prev_pending:
            if c in it['invite']:
                fresh[c]={"label":it["name"],"page":"karachi","country":"PK","url":"https://77links.com/karachi-whatsapp-group-links/"}
        json.dump(fresh, open(os.path.join(WD,"team14_fresh_raw.json"),'w'), ensure_ascii=False, indent=1)
codes=sorted(set(codes)|set(retry_todo), key=prio)
print("to verify:",len(codes), flush=True)

def run(code):
    r=fetch(code)
    time.sleep(0.55)
    return r
with ThreadPoolExecutor(max_workers=6) as ex:
    list(ex.map(run, codes))
print("verify done", flush=True)
