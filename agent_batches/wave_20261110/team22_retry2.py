import json, re, subprocess, time, html
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
PEND=["IEVw3U2h2nk7b6Zl5oM3Fu","KzwO6LVoaS8DT0LBwqu16S","FmYjiEhElyY6X2bC5Vfix5","Fp53YAbEUa78T4zAZcCjRZ","KR7gWco4iCw3aRB8JtcI70","IeZiqR3jpEE7N160llnfET","GFTTUzali7E6Ec1SBMh0mi","ChMoC5eTdOkDdLeyPjiIE0","IKv4AvhauPx1RkzQOwWXQ6"]
out={}
for code in PEND:
    try:
        r=subprocess.run(["curl","-s","-w","\n%{http_code}","-A",UA,"--max-time","15",f"https://chat.whatsapp.com/{code}"],
                         capture_output=True, text=True, timeout=20)
        body=r.stdout or ""
        lines=body.rsplit("\n",1)
        httpcode=lines[1] if len(lines)>1 else "?"
        htmlbody=lines[0]
        m=re.search(r'<meta property="og:title" content="([^"]*)"', htmlbody)
        title=html.unescape(m.group(1)) if m else ""
        out[code]={"rc":r.returncode,"http":httpcode,"og_title":title,"bytes":len(htmlbody)}
        print(code,'rc',r.returncode,'http',httpcode,'og',repr(title),'bytes',len(htmlbody), flush=True)
    except Exception as e:
        out[code]={"rc":"exc","http":None,"og_title":"","err":str(e)}
        print(code,'EXC',e, flush=True)
    time.sleep(3)
json.dump(out, open('team22_retry2_raw.json','w'), ensure_ascii=False, indent=1)
