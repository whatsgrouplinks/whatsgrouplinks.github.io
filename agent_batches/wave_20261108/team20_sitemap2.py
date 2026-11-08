import requests, re, json, time
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
KW = ["study","student","job","scholarship","freelance","education","exam","career","english","ielts","upsc","neet","govt","sarkari","earn","business"]
def locs(url):
    r=requests.get(url, headers=UA, timeout=25)
    return re.findall(r'<loc>([^<]+)</loc>', r.text)
gl=[]
for i in range(1,16):
    try:
        gl+=locs(f"https://grouplink.com.in/post-sitemap{i}.xml")
    except Exception as e: print("gl",i,"ERR",e)
print("grouplink posts:", len(gl))
gl_f=[u for u in gl if any(k in u.lower() for k in KW)]
print("grouplink in-scope urls:", len(gl_f))
for u in gl_f: print(" GL:", u)
gi=[]
for i in range(1,12):
    try: gi+=locs(f"https://groupsinvite.link/sitemap-{i}.xml")
    except Exception as e: print("gi",i,"ERR",e)
print("groupsinvite urls:", len(gi))
gi_f=[u for u in gi if any(k in u.lower() for k in KW)]
print("groupsinvite in-scope urls:", len(gi_f))
for u in gi_f: print(" GI:", u)
json.dump({"grouplink":gl_f,"groupsinvite":gi_f}, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team20_sitemap_urls.json","w"), indent=1)
