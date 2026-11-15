import requests, re, json
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
s = requests.Session()
def get(url, timeout=90):
    try:
        r = s.get(url, headers=UA, timeout=timeout)
        return r.status_code, r.text
    except Exception as e:
        return None, f"ERR {type(e).__name__}: {e}"

# 1. linkado newest pages
for p in [1,2]:
    st, t = get(f"https://linkado.app/?pagina={p}" if p>1 else "https://linkado.app/")
    print("linkado p",p,"status",st,"len",len(t) if isinstance(t,str) else t)
    if st==200:
        open(f"team24-linkado-p{p}.html","w").write(t)
        print("  codes:", len(re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,})', t)))
# 2. freewagroup WP API newest
st, t = get("https://freewagroup.com/wp-json/wp/v2/posts?per_page=20&_fields=id,date,modified,slug,link,title&orderby=date&order=desc&page=1")
print("freewagroup API status", st, "len", len(t) if isinstance(t,str) else t)
if st==200:
    open("team24-freewagroup-api.json","w").write(t)
    d=json.loads(t)
    for x in d[:10]: print("  ", x.get("date"), x.get("slug"))
