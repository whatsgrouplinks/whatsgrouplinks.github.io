import json, re, time, subprocess, os, sys
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
SCAM_PAT=re.compile(r"b-?love|forsage|shey(i)?\s*airdrop|paypal\s*loader|bitfinex|counterfeit|carding|crypto.?doubling|double (your )?(btc|bitcoin|crypto)|bitcoin (invest|trading|profit|earn)|earn (free )?(btc|bitcoin|crypto)|mining (pool|investment)|forex (signal|profit)|investment (plan|group|opportunity)", re.I)
ADULT_PAT=re.compile(r"🔞|🥵|sexy|hookup|escort|\bporn\b|xxx|adult (video|sex|chat|18)|18\+ (sex|video|adult|hot)|nude|naked|sex (video|chat|group)|call girl|desi (sex|bhabhi|porn)", re.I)

# known results from killed run 1 (verified)
known={
 "187582":("EXCLUDED","Xxx group","200"),
 "315149":("DEAD","","200"),
 "207356":("DEAD","","200"),
 "856191":("PENDING","","000"),
 "976715":("PENDING","","000"),
 "792999":("PENDING","","000"),
 "813979":("PENDING","","000"),
 "444836":("PENDING","","000"),
 "962515":("DEAD","","200"),
 "380628":("DEAD","","200"),
 "593435":("DEAD","","200"),
 "197480":("DEAD","","200"),
 "696815":("DEAD","","200"),
 "430588":("DEAD","","200"),
}
def check_code(code, attempts=3, timeout=12):
    og=""; http=""
    for a in range(attempts):
        try:
            r=subprocess.run(["curl","-s","-A",UA,"--max-time",str(timeout),"-w","\n%{http_code}",
                              f"https://chat.whatsapp.com/{code}"],
                             capture_output=True, timeout=timeout+8)
            out=r.stdout.decode('utf-8', errors='replace')
            http=out.rsplit("\n",1)[-1].strip()
            body=out[:out.rfind("\n")]
            m=re.search(r'og:title"\s+content="([^"]*)"', body)
            og=(m.group(1).strip() if m else "")
            og=og.replace("&#x1f30d;","").strip()
            if http=="200" and og: return "LIVE", og, http
            if http in ("404","403","410"): return "DEAD", og, http
            if http=="200" and not og:
                time.sleep(3); continue
            if http in ("000",""): return "PENDING", og, http
            time.sleep(2)
        except Exception:
            return "PENDING", "", ""
    return ("DEAD" if http=="200" else "PENDING"), og, http

prescreen=json.load(open(os.path.join(W,"team16_prescreen.json")))
ckpt_path=os.path.join(W,"team16_verify_ckpt.jsonl")
done={}
if os.path.exists(ckpt_path):
    for line in open(ckpt_path):
        e=json.loads(line); done[e["gid"]]=e
# seed checkpoint with known results
for gid,(st,og,http) in known.items():
    if gid not in done:
        done[gid]={"gid":gid,"verify":st,"og_title":og,"http":http}
        with open(ckpt_path,"a") as f: f.write(json.dumps(done[gid],ensure_ascii=False)+"\n")

# work list: fresh 4 + retry PENDING/DEAD from known (2 fresh attempts each)
fresh=["377833","791674","757428","175618"]
retry=[g for g,(st,_,_) in known.items() if st in ("PENDING","DEAD")]
by_gid={p["gid"]:p for p in prescreen}
def process(gid, attempts):
    p=by_gid[gid]
    st,og,http=check_code(p["code"], attempts=attempts)
    reason=""
    if st=="LIVE" and (SCAM_PAT.search(og) or ADULT_PAT.search(og)):
        st="EXCLUDED"; reason="og:title matches scam/adult screen: "+og
    if st=="PENDING": reason="transport failure (curl error/timeout, no HTTP status)"
    e={"gid":gid,"verify":st,"og_title":og,"http":http,"reason":reason}
    with open(ckpt_path,"a") as f: f.write(json.dumps(e,ensure_ascii=False)+"\n")
    print(gid, p["name"][:30], p["code"], "->", st, "| og:", og[:50], flush=True)
    time.sleep(1)
    return e
for gid in fresh:
    if gid in done and done[gid].get("verify") in ("LIVE","DEAD","EXCLUDED"):
        print(gid,"already done",done[gid]["verify"],flush=True); continue
    done[gid]=process(gid, 3)
for gid in retry:
    # only retry if previous was PENDING or DEAD; one more pass of 2 attempts
    done[gid]=process(gid, 2)
json.dump(done, open(os.path.join(W,"team16_verify_done.json"),"w"), ensure_ascii=False, indent=1)
print("DONE fresh+retry", flush=True)
