import json, re, time, random, html, sys
import requests

WAVE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language":"en-US,en;q=0.9"}
OG_RE=re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]*>', re.I)
CONTENT_RE=re.compile(r'content=["\'](.*?)["\']', re.S)

def og_title(session, code):
    url=f"https://chat.whatsapp.com/{code}"
    last_err=""
    for attempt in range(3):
        try:
            r=session.get(url, headers=UA, timeout=60, allow_redirects=True)
            if r.status_code==429:
                return ("pending", "", f"HTTP 429 attempt {attempt+1}")
            if r.status_code!=200:
                return ("dead", "", f"HTTP {r.status_code}")
            m=OG_RE.search(r.text)
            title=""
            if m:
                cm=CONTENT_RE.search(m.group(0))
                if cm: title=html.unescape(cm.group(1)).strip()
            if title and title.lower()!="whatsapp group invite":
                return ("live", title, "")
            # empty/generic -> spaced retry
            last_err="empty og:title"
            time.sleep(5+random.uniform(0,3))
        except requests.exceptions.RequestException as e:
            last_err=f"transport: {type(e).__name__}: {str(e)[:120]}"
            time.sleep(5+random.uniform(0,3))
    return ("dead", "", last_err)

def main():
    session=requests.Session()
    # CONTROLS FIRST
    st, title, err = og_title(session, "KrDwdK8EIkB6vgauHg5M7N")
    print("CONTROL live:", st, repr(title), err, flush=True)
    assert st=="live" and title=="JAY - PHP & Python Full Stack Developer", "LIVE CONTROL FAILED"
    st2, title2, err2 = og_title(session, "ZzZzZzZzZzZzZzZzZzZzZzZz")
    print("CONTROL fabricated:", st2, repr(title2), err2, flush=True)
    assert st2=="dead" and title2=="", "FABRICATED CONTROL FAILED"
    print("CONTROLS PASSED", flush=True)
    vlist=json.load(open(f"{WAVE}/team09-verify-list.json"))
    results={}
    # resume support
    try:
        results=json.load(open(f"{WAVE}/team09-verify-results.json"))
        print(f"resumed {len(results)} results", flush=True)
    except Exception:
        pass
    for i, item in enumerate(vlist):
        code=item["code"]
        if code in results:
            continue
        st, title, err = og_title(session, code)
        results[code]={"code":code, "status":st, "og_title":title, "error":err,
                       "name":item["name"], "cat_raw":item["cat_raw"], "desc":item["desc"],
                       "wave12_exclusion":item["wave12_exclusion"]}
        print(f"[{i+1}/80] {code} {st} {title!r} {err}", flush=True)
        json.dump(results, open(f"{WAVE}/team09-verify-results.json","w"), ensure_ascii=False, indent=1)
        time.sleep(2.0+random.uniform(0,1.5))
    print("DONE", {s: sum(1 for r in results.values() if r["status"]==s) for s in ("live","dead","pending")}, flush=True)

if __name__=="__main__":
    main()
