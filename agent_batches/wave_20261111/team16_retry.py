"""Final retry pass: cool-down, then re-follow 2 failed redirects and
re-verify the 3 transport-pending codes (plus any newly extracted code).
Sequential only. Writes team16_retry.json + appends to team16_ckpt2.jsonl."""
import json, re, time, subprocess, os
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
SCAM_PAT=re.compile(r"b-?love|forsage|shey(i)?\s*airdrop|holiverse|meta-?whale|bitcoin (invest|trading|profit|earn)|investment (plan|group|opportunity)", re.I)
ADULT_PAT=re.compile(r"🔞|🥵|sexy|hookup|escort|\bporn\b|xxx|adult (video|sex|chat|18)|nude|naked|sex (video|chat|group)|call girl", re.I)

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

ex=json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'))
g=json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
union=set(ex)
for it in g:
    inv=it.get('invite','') if isinstance(it,dict) else ''
    c=inv.rstrip('/').split('/')[-1]
    if c: union.add(c)

ckpt={}
for line in open(os.path.join(W,"team16_ckpt.jsonl"), encoding="utf-8"):
    line=line.strip()
    if line:
        e=json.loads(line); ckpt[e["gid"]]=e

print("cool-down 90s ...", flush=True)
time.sleep(90)

def follow_redirect(url):
    for attempt in range(3):
        out,err=curl(url, timeout=30, headers_only=True)
        if err:
            print("  redirect fetch err:", err, flush=True); time.sleep(6); continue
        m=re.search(r'refresh:\s*\d+;\s*url=(\S+)', out, re.I)
        if m:
            loc=m.group(1).strip()
            if 'whatsapp.com/channel' in loc: return "CHANNEL", loc
            mm=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', loc)
            return (mm.group(1) if mm else None), loc
        m2=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', out)
        if m2: return m2.group(1), "https://chat.whatsapp.com/"+m2.group(1)
        print("  redirect attempt", attempt+1, "no location; head:", out[:200].replace("\n"," | "), flush=True)
        time.sleep(6)
    return None, None

def check_code(code):
    og=""; http=""
    for a in range(3):
        try:
            r=subprocess.run(["curl","-s","-A",UA,"--max-time","20","-w","\n%{http_code}",
                              f"https://chat.whatsapp.com/{code}"],
                             capture_output=True, timeout=28)
            out=r.stdout.decode('utf-8', errors='replace')
            http=out.rsplit("\n",1)[-1].strip()
            body=out[:out.rfind("\n")]
            m=re.search(r'og:title"\s+content="([^"]*)"', body)
            og=(m.group(1).strip() if m else "")
            print(f"  verify attempt {a+1}: http={http} og={og!r}", flush=True)
            if http=="200" and og: return "LIVE", og, http
            if http in ("404","403","410"): return "DEAD", og, http
            time.sleep(8)
        except Exception as e:
            print("  verify err:", e, flush=True); time.sleep(8)
    if http=="200" and not og: return "DEAD", og, http
    return "PENDING", og, http

results=[]
out2=open(os.path.join(W,"team16_ckpt2.jsonl"),"a",encoding="utf-8")

# 1. re-follow failed redirects
for gid in ("662627","400673"):
    e=dict(ckpt[gid])
    print(gid, e["name"], "re-following", e["redirect"], flush=True)
    code, loc = follow_redirect(e["redirect"])
    e["code"]=code; e["location"]=loc
    if not code:
        e["status"]="PENDING"; e["reason"]="no code extracted after retry (redirect fetch failed)"
    elif code=="CHANNEL":
        e["status"]="EXCLUDED"; e["reason"]="WhatsApp channel, not a group"
    elif code in union:
        e["status"]="DUPE"
    else:
        st, og, http = check_code(code)
        e["verify"]=st; e["og_title"]=og; e["http"]=http
        if st=="LIVE" and (SCAM_PAT.search(og) or ADULT_PAT.search(og)):
            e["status"]="EXCLUDED"; e["reason"]="og:title matches scam/adult screen: "+og
        elif st=="LIVE": e["status"]="LIVE"
        elif st=="DEAD": e["status"]="DEAD"
        else:
            e["status"]="PENDING"; e["reason"]="transport failure (no HTTP status) after retry"
    results.append(e)
    out2.write(json.dumps(e,ensure_ascii=False)+"\n"); out2.flush()
    print(" ->", e["status"], "| code:", code, "| og:", e.get("og_title","")[:50], flush=True)
    time.sleep(10)

# 2. re-verify transport-pending codes
for gid in ("440817","865745","219135"):
    e=dict(ckpt[gid])
    print(gid, e["name"], "re-verifying", e["code"], flush=True)
    st, og, http = check_code(e["code"])
    e["verify"]=st; e["og_title"]=og; e["http"]=http
    if st=="LIVE" and (SCAM_PAT.search(og) or ADULT_PAT.search(og)):
        e["status"]="EXCLUDED"; e["reason"]="og:title matches scam/adult screen: "+og
    elif st=="LIVE": e["status"]="LIVE"
    elif st=="DEAD": e["status"]="DEAD"
    else:
        e["status"]="PENDING"; e["reason"]="transport failure (no HTTP status) after retry pass"
    results.append(e)
    out2.write(json.dumps(e,ensure_ascii=False)+"\n"); out2.flush()
    print(" ->", e["status"], "| og:", og[:60], "| http:", http, flush=True)
    time.sleep(10)

out2.close()
json.dump(results, open(os.path.join(W,"team16_retry.json"),"w"), ensure_ascii=False, indent=1)
print("RETRY DONE", flush=True)
