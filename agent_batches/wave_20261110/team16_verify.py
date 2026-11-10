import json, re, time, subprocess, os
from concurrent.futures import ThreadPoolExecutor
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
ex=json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'))
g=json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
union=set(ex)
for it in g:
    inv=it.get('invite','') if isinstance(it,dict) else ''
    c=inv.rstrip('/').split('/')[-1]
    if c: union.add(c)
print("union:", len(union), flush=True)
details=json.load(open(os.path.join(W,"team16_details.json")))

SCAM_PAT=re.compile(r"b-?love|forsage|shey(i)?\s*airdrop|paypal\s*loader|bitfinex|counterfeit|carding|crypto.?doubling|double (your )?(btc|bitcoin|crypto)|bitcoin (invest|trading|profit|earn)|earn (free )?(btc|bitcoin|crypto)|mining (pool|investment)|forex (signal|profit)|investment (plan|group|opportunity)", re.I)
ADULT_PAT=re.compile(r"🔞|🥵|sexy|hookup|escort|\bporn\b|xxx|adult (video|sex|chat|18)|18\+ (sex|video|adult|hot)|nude|naked|sex (video|chat|group)|call girl|desi (sex|bhabhi|porn)", re.I)

def check_code(code):
    """returns (status, og_title, http) ; status LIVE/DEAD/PENDING"""
    og=""
    http=""
    for attempt in range(3):
        try:
            r=subprocess.run(["curl","-s","-A",UA,"--max-time","15","-w","\n%{http_code}",
                              f"https://chat.whatsapp.com/{code}"],
                             capture_output=True, timeout=20)
            out=r.stdout.decode('utf-8', errors='replace')
            http=out.rsplit("\n",1)[-1].strip()
            body=out[:out.rfind("\n")]
            m=re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', body)
            og=(m.group(1).strip() if m else "")
            if http=="200" and og:
                return "LIVE", og, http
            if http=="200" and not og:
                time.sleep(3); continue  # retry for empty title
            if http in ("404","403","410"):
                return "DEAD", og, http
            if http=="000" or http=="":
                return "PENDING", og, http
            time.sleep(2)
        except Exception as e:
            return "PENDING", "", ""
    if http=="200" and not og:
        return "DEAD", og, http
    return "PENDING", og, http

results=[]
for d in details:
    code=d.get("code")
    name=d.get("name","")
    entry={"gid":d["gid"],"name":name,"code":code,"catlabel":d.get("catlabel","")}
    if not code:
        entry["status"]="PENDING"; entry["reason"]="no code extracted (redirect fetch failed)"
        results.append(entry); continue
    if code=="CHANNEL":
        entry["status"]="EXCLUDED"; entry["reason"]="WhatsApp channel, not a group"
        results.append(entry); continue
    if code in union:
        entry["status"]="DUPE"; results.append(entry); continue
    if SCAM_PAT.search(name) or ADULT_PAT.search(name):
        entry["status"]="EXCLUDED"; entry["reason"]="name matches scam/adult screen"
        results.append(entry); continue
    entry["status"]="TO_VERIFY"; results.append(entry)
print("dupes:", sum(1 for r in results if r["status"]=="DUPE"),
      "excluded-prescreen:", sum(1 for r in results if r["status"]=="EXCLUDED"),
      "to_verify:", sum(1 for r in results if r["status"]=="TO_VERIFY"), flush=True)
json.dump(results, open(os.path.join(W,"team16_prescreen.json"),"w"), ensure_ascii=False, indent=1)

def verify_one(entry):
    st, og, http = check_code(entry["code"])
    entry["verify"]=st; entry["og_title"]=og; entry["http"]=http
    if st=="LIVE" and (SCAM_PAT.search(og) or ADULT_PAT.search(og)):
        entry["verify"]="EXCLUDED"; entry["reason"]="og:title matches scam/adult screen: "+og
    time.sleep(0.6)
    print(entry["gid"], entry["name"][:30], entry["code"], "->", entry["verify"], "| og:", og[:60], flush=True)
    return entry
tov=[r for r in results if r["status"]=="TO_VERIFY"]
with ThreadPoolExecutor(max_workers=3) as ex2:
    verified=list(ex2.map(verify_one, tov))
by_gid={v["gid"]:v for v in verified}
for r in results:
    if r["gid"] in by_gid: r.update(by_gid[r["gid"]])
json.dump(results, open(os.path.join(W,"team16_verify_results.json"),"w"), ensure_ascii=False, indent=1)
print("LIVE:", sum(1 for r in results if r.get("verify")=="LIVE"),
      "DEAD:", sum(1 for r in results if r.get("verify")=="DEAD"),
      "PENDING:", sum(1 for r in results if r.get("verify")=="PENDING"),
      "EXCLUDED:", sum(1 for r in results if r.get("verify")=="EXCLUDED" or r["status"]=="EXCLUDED"), flush=True)
