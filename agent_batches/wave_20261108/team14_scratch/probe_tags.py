import json, subprocess
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
r=subprocess.run(["curl","-s","--max-time","60","-A",UA,"https://api.groupjoin.link/tags"],capture_output=True,text=True,timeout=70)
d=json.loads(r.stdout)
tags=d["data"]
print("total tags:",len(tags))
for t in tags:
    print(f"{t['count']:>7}  {t['slug']}")
with open("team14_tags_snapshot.json","w") as f: json.dump(tags,f,indent=1)
print("saved")
