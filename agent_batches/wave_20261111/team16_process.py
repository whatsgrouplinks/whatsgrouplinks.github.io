"""Team 16 wave 20261111: process candidate gids -> codes -> dedupe -> slow verify.
Candidates come from team16_candidates.json (built after listing fetch).
Writes checkpoint JSONL as it goes; safe to re-run (skips gids already in checkpoint)."""
import json, re, time, subprocess, html, os, sys
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

SCAM_PAT=re.compile(r"b-?love|forsage|shey(i)?\s*airdrop|holiverse|meta-?whale|paypal\s*loader|bitfinex|counterfeit|carding|crypto.?doubling|double (your )?(btc|bitcoin|crypto)|bitcoin (invest|trading|profit|earn)|earn (free )?(btc|bitcoin|crypto)|mining (pool|investment)|forex (signal|profit)|investment (plan|group|opportunity)|betting|1xbet|aviator (bet|predict)", re.I)
def strip_negations(t):
    # remove sentences that prohibit adult content, so 'no porn' is not flagged
    t=re.sub(r'[^.!?\n]*(no|not|never|don\'t|do not|strictly no|prohibit\w*|forbidden)[^.!?\n]*(porn|xxx|sex|nude|adult)[^.!?\n]*[.!?\n]?', ' ', t, flags=re.I)
    return t
ADULT_PAT=re.compile(r"🔞|🥵|sexy|hookup|escort|\bporn\b|xxx|adult (video|sex|chat|18)|18\+ (sex|video|adult|hot)|nude|naked|sex (video|chat|group)|call girl|desi (sex|bhabhi|porn)|hard ?core", re.I)

def curl(url, timeout=35, headers_only=False):
    args=["curl","-s","-A",UA,"--max-time",str(timeout)]
    if headers_only: args+=["-D","-","-o","/dev/null"]
    else: args+=["-w","\n%{http_code}"]
    args+=[url]
    try:
        r=subprocess.run(args, capture_output=True, timeout=timeout+10)
        return r.stdout.decode('utf-8', errors='replace'), None
    except Exception as e:
        return "", str(e)

# union
ex=json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'))
g=json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
union=set(ex)
for it in g:
    inv=it.get('invite','') if isinstance(it,dict) else ''
    c=inv.rstrip('/').split('/')[-1]
    if c: union.add(c)
print("union:", len(union), flush=True)

cands=json.load(open(os.path.join(W,"team16_candidates.json")))
print("candidates:", len(cands), flush=True)

ckpt_path=os.path.join(W,"team16_ckpt.jsonl")
done={}
if os.path.exists(ckpt_path):
    for line in open(ckpt_path, encoding="utf-8"):
        line=line.strip()
        if line:
            e=json.loads(line); done[e["gid"]]=e
print("already checkpointed:", len(done), flush=True)

def fetch_detail(c):
    gid=c["gid"]
    for attempt in range(3):
        out,err=curl(f"https://grupbul.com/group/{gid}", timeout=35)
        if err:
            time.sleep(3); continue
        body=out[:out.rfind("\n")]
        m=re.search(r'/redirect/%s/(\d+)'%gid, body)
        if m:
            c["redirect"]=f"https://grupbul.com/redirect/{gid}/{m.group(1)}"
            # also grab name/desc from detail page if missing
            tm=re.search(r'<title>(.*?)</title>', body, re.S)
            if tm and not c.get("name"):
                c["name"]=html.unescape(re.sub(r'<[^>]+>','',tm.group(1))).replace("[WhatsApp Group] - Grupbul.com","").replace("[WhatsApp Channel] - Grupbul.com","").strip()
            return c
        time.sleep(3)
    c["redirect"]=None
    return c

def follow(c):
    if not c.get("redirect"): return c
    for attempt in range(2):
        out,err=curl(c["redirect"], timeout=30, headers_only=True)
        if err:
            time.sleep(3); continue
        m=re.search(r'refresh:\s*\d+;\s*url=(\S+)', out, re.I)
        if not m:
            m2=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', out)
            if m2:
                c["location"]="https://chat.whatsapp.com/"+m2.group(1); c["code"]=m2.group(1); return c
            time.sleep(3); continue
        loc=m.group(1).strip()
        c["location"]=loc
        if 'whatsapp.com/channel' in loc:
            c["code"]="CHANNEL"
        else:
            mm=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', loc)
            c["code"]=mm.group(1) if mm else None
        return c
    c["location"]=None; c["code"]=None
    return c

def check_code(code):
    """SLOW sequential check. Returns (status, og, http)."""
    og=""; http=""
    for attempt in range(3):
        try:
            r=subprocess.run(["curl","-s","-A",UA,"--max-time","15","-w","\n%{http_code}",
                              f"https://chat.whatsapp.com/{code}"],
                             capture_output=True, timeout=20)
            out=r.stdout.decode('utf-8', errors='replace')
            http=out.rsplit("\n",1)[-1].strip()
            body=out[:out.rfind("\n")]
            m=re.search(r'og:title"\s+content="([^"]*)"', body)
            og=(m.group(1).strip() if m else "")
            if http=="200" and og:
                return "LIVE", og, http
            if http in ("404","403","410"):
                return "DEAD", og, http
            if http=="200" and not og:
                time.sleep(5); continue
            time.sleep(5)
        except Exception:
            time.sleep(5); continue
    if http=="200" and not og:
        return "DEAD", og, http
    return "PENDING", og, http

for c in cands:
    gid=c["gid"]
    if gid in done:
        continue
    c=fetch_detail(c)
    time.sleep(1.5)
    c=follow(c)
    time.sleep(1.5)
    code=c.get("code")
    entry=dict(c)
    entry["status"]="UNRESOLVED"
    if not code:
        entry["status"]="PENDING"; entry["reason"]="no code extracted (redirect/detail fetch failed)"
    elif code=="CHANNEL":
        entry["status"]="EXCLUDED"; entry["reason"]="WhatsApp channel, not a group"
    elif code in union:
        entry["status"]="DUPE"
    else:
        name=c.get("name","")
        if SCAM_PAT.search(name) or ADULT_PAT.search(strip_negations(name)):
            entry["status"]="EXCLUDED"; entry["reason"]="name matches scam/adult screen: "+name
        else:
            st, og, http = check_code(code)
            entry["verify"]=st; entry["og_title"]=og; entry["http"]=http
            if st=="LIVE" and (SCAM_PAT.search(og) or ADULT_PAT.search(strip_negations(og))):
                entry["verify"]="EXCLUDED"; entry["reason"]="og:title matches scam/adult screen: "+og
                entry["status"]="EXCLUDED"
            elif st=="LIVE":
                entry["status"]="LIVE"
            elif st=="DEAD":
                entry["status"]="DEAD"
            else:
                entry["status"]="PENDING"; entry["reason"]="transport failure (no HTTP status) after 3 spaced attempts"
    with open(ckpt_path,"a",encoding="utf-8") as f:
        f.write(json.dumps(entry,ensure_ascii=False)+"\n")
    print(gid, (c.get("name") or "")[:35], "| code:", code, "->", entry["status"],
          "| og:", entry.get("og_title","")[:50], "| http:", entry.get("http",""), flush=True)
    time.sleep(2)
print("PROCESS DONE", flush=True)
