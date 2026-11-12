#!/usr/bin/env python3
"""Team19 controls: known-live code must show og:title; fabricated code must show empty og:title.
Uses persistent requests Session (keep-alive) per task spec."""
import json, re, time, requests
RAW="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/team19_raw"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OG=re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OGD=re.compile(r'<meta\s+property="og:description"\s+content="([^"]*)"', re.I)
s=requests.Session(); s.headers.update({"User-Agent":UA})
def check(code):
    t0=time.time()
    try:
        r=s.get(f"https://chat.whatsapp.com/{code}", timeout=90, allow_redirects=True)
        html=r.text
        m=OG.search(html); md=OGD.search(html)
        return {"code":code,"http":r.status_code,"og_title":m.group(1).strip() if m else "",
                "og_description":(md.group(1).strip() if md else "")[:120],"elapsed_s":round(time.time()-t0,1)}
    except Exception as e:
        return {"code":code,"http":"transport-failure","og_title":"","error":str(e)[:200],"elapsed_s":round(time.time()-t0,1)}
res={}
res["control_live"]=check("KrDwdK8EIkB6vgauHg5M7N")
print("CONTROL LIVE:",res["control_live"],flush=True)
time.sleep(3)
res["control_fabricated"]=check("ZZZZZZZZZZZZZZZZZZZZ99")
print("CONTROL FABRICATED:",res["control_fabricated"],flush=True)
json.dump(res,open(f"{RAW}/controls.json","w"),ensure_ascii=False,indent=1)
print("CONTROLS_DONE live_ok=",(bool(res["control_live"]["og_title"])),"fabricated_empty=",(not res["control_fabricated"]["og_title"]))
