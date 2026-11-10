import json, re, time, subprocess, os, sys
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
SCAM_PAT=re.compile(r"b-?love|forsage|shey(i)?\s*airdrop|paypal\s*loader|bitfinex|counterfeit|carding|crypto.?doubling|double (your )?(btc|bitcoin|crypto)|bitcoin (invest|trading|profit|earn)|earn (free )?(btc|bitcoin|crypto)|mining (pool|investment)|forex (signal|profit)|investment (plan|group|opportunity)", re.I)
ADULT_PAT=re.compile(r"🔞|🥵|sexy|hookup|escort|\bporn\b|xxx|adult (video|sex|chat|18)|18\+ (sex|video|adult|hot)|nude|naked|sex (video|chat|group)|call girl|desi (sex|bhabhi|porn)", re.I)
gids=sys.argv[1:]
prescreen=json.load(open(os.path.join(W,"team16_prescreen.json")))
by_gid={p["gid"]:p for p in prescreen}
def check_code(code, attempts=3, timeout=10):
    og=""; http=""; n200empty=0; n000=0
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
            if http=="200" and og: return "LIVE", og, http
            if http in ("404","403","410"): return "DEAD", og, http
            if http=="200" and not og:
                n200empty+=1
                if n200empty>=2: return "DEAD", og, http
                time.sleep(4); continue
            if http in ("000",""):
                n000+=1; time.sleep(4); continue
            time.sleep(3)
        except Exception:
            n000+=1; time.sleep(4); continue
    if n200empty>=1 and n000==0: return "DEAD", og, http
    return "PENDING", og, http
ckpt=os.path.join(W,"team16_finalpass.jsonl")
for gid in gids:
    p=by_gid[gid]
    st,og,http=check_code(p["code"], attempts=3)
    reason=""
    if st=="LIVE" and (SCAM_PAT.search(og) or ADULT_PAT.search(og)):
        st="EXCLUDED"; reason="og:title matches scam/adult screen: "+og
    if st=="PENDING": reason="transport failure (curl error/timeout, no HTTP status) after 3 spaced attempts"
    e={"gid":gid,"verify":st,"og_title":og,"http":http,"reason":reason}
    with open(ckpt,"a") as f: f.write(json.dumps(e,ensure_ascii=False)+"\n")
    print(gid, p["name"][:30], p["code"], "->", st, "| og:", og[:50], "| http:", http, flush=True)
    time.sleep(2)
print("BATCH DONE", flush=True)
