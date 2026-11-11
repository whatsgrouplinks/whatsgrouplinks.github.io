"""Re-verify the 4 Nov-10 transport-only PENDING codes with a fresh slow pass.
Sequential, 3 attempts each, 6s pauses. Writes team16_pending_reverify.json."""
import json, re, time, subprocess, os
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
PENDING=[
 {"gid":"791674","name":"Sohbete gel","code":"H3H6SCPltU22xsKwEtM97A"},
 {"gid":"757428","name":"Arkadas tanisma","code":"EuosowMQIqe833l9le383G"},
 {"gid":"175618","name":"Girls Fun Masti","code":"Bo6Splc8d3oC3gr4xf0UA2"},
 {"gid":"444836","name":"Romantic","code":"FlFcwNtXfzP0DB52GQ7uZ4"},
]
def check(code):
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
            print(f"  attempt {a+1}: http={http} og={og!r}", flush=True)
            if http=="200" and og: return "LIVE", og, http
            if http in ("404","403","410"): return "DEAD", og, http
            if http=="200" and not og:
                time.sleep(6); continue
            time.sleep(6)
        except Exception as e:
            print("  attempt error:", e, flush=True)
            time.sleep(6)
    if http=="200" and not og: return "DEAD", og, http
    return "PENDING", og, http
out=[]
for p in PENDING:
    print(p["gid"], p["name"], p["code"], flush=True)
    st, og, http = check(p["code"])
    e=dict(p); e["verify"]=st; e["og_title"]=og; e["http"]=http
    out.append(e)
    print(" ->", st, "| og:", og, "| http:", http, flush=True)
    time.sleep(8)
json.dump(out, open(os.path.join(W,"team16_pending_reverify.json"),"w"), ensure_ascii=False, indent=1)
print("REVERIFY DONE", flush=True)
