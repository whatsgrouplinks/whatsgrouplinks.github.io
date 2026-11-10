import json, subprocess, re, time
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
cands = json.load(open("team24_fresh_candidates.json"))

def check(code):
    """returns (status, og_title, http_code, error)"""
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(3):
        try:
            r = subprocess.run(["curl","-s","-A",UA,"--max-time","15","-w","\n%{http_code}",url],
                               capture_output=True, text=True, timeout=20)
            body = r.stdout
            m = re.search(r'\n(\d{3})\s*$', body)
            http = m.group(1) if m else "000"
            html = body[:m.start()] if m else body
            t = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
            if not t:
                t = re.search(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:title\"", html)
            title = t.group(1).strip() if t else ""
            if http == "200" and title:
                return ("live", title, http, "")
            if http == "200" and not title:
                # retry after spacing
                time.sleep(2)
                continue
            if http in ("000",):
                return ("transport", "", http, "curl no http status")
            return ("dead", title, http, f"http {http}")
        except subprocess.TimeoutExpired:
            return ("transport", "", "000", "curl timeout 15s")
        except Exception as e:
            return ("transport", "", "000", str(e)[:80])
    return ("dead", "", "200", "empty og:title after retries")

results = {}
def work(c):
    time.sleep(0.0)
    st, title, http, err = check(c["code"])
    return c["code"], {"status": st, "og_title": title, "http": http, "error": err}

# stagger starts >=0.5s: submit with small delays via executor + sleep in submit loop
out = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = []
    for c in cands:
        futs.append(ex.submit(work, c))
        time.sleep(0.55)
    for f in futs:
        code, res = f.result()
        out[code] = res
        print(code, res, flush=True)
json.dump(out, open("team24_verify_raw.json","w"), indent=1, ensure_ascii=False)
live = sum(1 for v in out.values() if v["status"]=="live")
dead = sum(1 for v in out.values() if v["status"]=="dead")
pend = sum(1 for v in out.values() if v["status"]=="transport")
print(f"LIVE={live} DEAD={dead} PENDING={pend}")
