import json, subprocess, time
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
def get(url, t=45):
    r=subprocess.run(["curl","-s","-w","\n%{http_code}","--max-time",str(t),"-A",UA,url],capture_output=True,text=True,timeout=t+10)
    nl=r.stdout.rfind("\n")
    try: code=int(r.stdout[nl+1:].strip())
    except: code=0
    return code, r.stdout[:nl]
for url in [
 "https://api.groupjoin.link/tags",
 "https://api.groupjoin.link/groups?tag=business&page=21&limit=20&safeSearch=blur",
 "https://api.groupjoin.link/groups?tag=gaming&page=16&limit=20&safeSearch=blur",
]:
    code,body=get(url)
    print(url, "->", code, "len", len(body))
    print(body[:600].replace("\n"," ")[:600])
    print("---")
