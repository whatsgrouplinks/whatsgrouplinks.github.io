import json, re, subprocess, time, html, threading
from concurrent.futures import ThreadPoolExecutor

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
KEEPS=[
 ("JmcRrXGFgyiHqndAn7VHsW","Dating Girls Online","Community & Social"),
 ("GFTVdCpaXA53GD2E5zUWMv","pak girl meetup","Community & Social"),
 ("G62CUkZciTfF6buEqvQMQR","Girls Group","Community & Social"),
 ("BQPSgynhRtL46JgW8bXnGQ","Girls Group WhatsApp","Community & Social"),
 ("E8EHpwkECDL64vs0fN0R0Q","Desi Girl Group","Community & Social"),
 ("BfHXQMIhIYj0AT5SY4lL5p","Girl WhatsApp Group","Community & Social"),
 ("IEVw3U2h2nk7b6Zl5oM3Fu","Desi Group","Community & Social"),
 ("I4jvFgDg4j24YVVKWUfaVD","XXiv Girl Group","Community & Social"),
 ("KzwO6LVoaS8DT0LBwqu16S","WhatsApp Group Girl","Community & Social"),
 ("KK5hCAezfhvCeoPIWPtFws","Ertugrul & Osman Fanclub","Entertainment"),
 ("FmYjiEhElyY6X2bC5Vfix5","Private Meetup","Community & Social"),
 ("Fp53YAbEUa78T4zAZcCjRZ","College Girls","Community & Social"),
 ("KR7gWco4iCw3aRB8JtcI70","Punjab Group girls","Community & Social"),
 ("IeZiqR3jpEE7N160llnfET","Medical College Friends","Community & Social"),
 ("GFTTUzali7E6Ec1SBMh0mi","Sweet girl 3","Community & Social"),
 ("ChMoC5eTdOkDdLeyPjiIE0","DATING SITE","Community & Social"),
 ("HXhsIL7LkdKCNBl3pQSQeo","Poetry group","Entertainment"),
 ("IKv4AvhauPx1RkzQOwWXQ6","Secret Girls Group","Community & Social"),
 ("ChQ53L6gyJJChMeQDsTTcO","Lahore Private Girls","Community & Social"),
]
# note: #27 KK5h... already had 1 empty attempt; treat as attempt 1 of 2 retries in this run
lock=threading.Lock(); last=[0.0]
def spaced():
    with lock:
        now=time.time(); wait=0.6-(now-last[0])
        if wait>0: time.sleep(wait)
        last[0]=time.time()
def check(code):
    spaced()
    try:
        r=subprocess.run(["curl","-s","-A",UA,"--max-time","15",f"https://chat.whatsapp.com/{code}"],
                         capture_output=True, text=True, timeout=20)
        body=r.stdout or ""
        # curl -s gives no status; use og:title presence + body size; re-run with -w if needed
        m=re.search(r'<meta property="og:title" content="([^"]*)"', body)
        title=html.unescape(m.group(1)) if m else ""
        if not body.strip():
            return {"code":code,"status":"transport-fail","og_title":"","http":None}
        return {"code":code,"status":"ok","og_title":title,"http":200,"bytes":len(body)}
    except subprocess.TimeoutExpired:
        return {"code":code,"status":"transport-fail","og_title":"","http":None}
    except Exception as e:
        return {"code":code,"status":"transport-fail","og_title":"","http":None,"err":str(e)}

results={}
def work(item):
    code,name,cat=item
    first=check(code)
    # KK5h already empty once before this run; count that as attempt 1
    prior_empty = 1 if code=="KK5hCAezfhvCeoPIWPtFws" else 0
    attempts=1+prior_empty
    res=dict(first); res.update({"name":name,"category":cat,"attempts":attempts})
    if first["status"]=="ok" and first["og_title"]=="":
        time.sleep(6)
        second=check(code)
        res["attempts"]=attempts+1
        res["retry"]=second
        if second["status"]=="ok" and second["og_title"]!="":
            res["og_title"]=second["og_title"]
    results[code]=res
    print(code, name, '->', res["status"], repr(res["og_title"]), 'attempts', res["attempts"], flush=True)

with ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(work, KEEPS))
json.dump(results, open('team22_verify_raw.json','w'), ensure_ascii=False, indent=1)
live=[c for c,r in results.items() if r["status"]=="ok" and r["og_title"]!=""]
dead=[c for c,r in results.items() if r["status"]=="ok" and r["og_title"]==""]
pend=[c for c,r in results.items() if r["status"]!="ok"]
print("LIVE:",len(live),"DEAD:",len(dead),"PENDING:",len(pend))
