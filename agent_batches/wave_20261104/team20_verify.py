import requests, re, json, html, time
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}

def new_session():
    s = requests.Session(); s.headers.update(UA); return s

def og_title(code):
    s = new_session()
    try:
        r = s.get("https://chat.whatsapp.com/"+code, timeout=55, allow_redirects=True)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        t = html.unescape(m.group(1)).strip() if m else ""
        return (code, r.status_code, t, None)
    except Exception as e:
        return (code, None, "", type(e).__name__)

codes = ["BufShnZESAB5kbVh9BJmbF","JEOjeSsRlAeKZykFdL6r8O","L45MoGL59pgDnn8js9vQGt",
"DVJniTbpMNmIWL3h8dNxul","D3I1qb7qW81IVXP6XJUUNt","DpP8S0yEaDjLdlH9WEcTP9",
"ButmH0acT3d6UQNdp3nki8","H3OUyLDAZtV4fLZstRVvDV","I0Lqi05I9PfLUQryGQz4f7",
"IXN2oAFlanB3yAcHGVvAGQ","GdMdEFHIY5RAseR8CQrKXy","EID2RkEKKLn7mJECBWRlxO",
"EsSgJ3o1qxV8OLN4nTlZxR","JsdMljjqlaCFZWI972hpY3","HngILSEB3K7D9oTl2pAQBj","D2V0KDN7VAPBNZyR6ae5q6"]

print("verifying", len(codes), "codes...", flush=True)
t0=time.time()
with ThreadPoolExecutor(max_workers=16) as ex:
    results = list(ex.map(og_title, codes))
dt=time.time()-t0
out=[]
for code, st, title, err in results:
    tag = "LIVE" if title else ("ERR:"+str(err) if err else "DEAD")
    print(f"{code} -> {tag} [{title[:60]}]", flush=True)
    out.append({"code":code,"status":st,"og_title":title,"err":err})
json.dump({"elapsed":dt,"results":out}, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team20_verify_out.json","w"), ensure_ascii=False, indent=1)
print("done in %.1fs"%dt, flush=True)
