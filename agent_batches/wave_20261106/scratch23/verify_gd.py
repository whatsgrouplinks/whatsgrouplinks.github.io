import requests, re, json, os, time, html
from concurrent.futures import ThreadPoolExecutor
WAVE=os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261106")
S=os.path.join(WAVE,"scratch23")
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
PORN=re.compile(r'porn|pornhub|xxx|nudes?|sex video|escort|call girl|randi|fuck|dick|pussy|boobs|anal|orgasm|cumshot|blowjob|\bmms\b|leak(ed|s)?\s*(video|mms|clip)|desi\s+(video|mms)|viral\s+mms|adult\s*(video|18\+|xxx)',re.I)
SCAM=re.compile(r'receiver and loader|money.?mule|double (your|the) money|investment.*doubl|doubl.*investment|counterfeit (currency|money|note)|buy (drugs?|cocaine|heroin)|phishing|credential',re.I)
PHONE=re.compile(r'\+?\d[\d\s\-]{9,}\d')
CATMAP={"business":"business","buysell":"buy-sell","education":"education","study":"education","games":"gaming","dating":"friendship","matrimonial":"community-social"}
COUNTRIES=[("pakistan","PK"),("india","IN"),("indian","IN"),("usa","US"),("america","US"),("united states","US"),("uk","GB"),("england","GB"),("london","GB"),("france","FR"),("poland","PL"),("bangladesh","BD"),("nepal","NP"),("sri lanka","LK"),("dubai","AE"),("uae","AE"),("saudi","SA"),("canada","CA"),("australia","AU"),("germany","DE"),("italy","IT"),("spain","ES"),("turkey","TR"),("nigeria","NG"),("kenya","KE"),("ghana","GH"),("philippines","PH"),("indonesia","ID"),("malaysia","MY"),("thailand","TH"),("vietnam","VN"),("china","CN"),("japan","JP"),("korea","KR"),("russia","RU"),("ukraine","UA"),("brazil","BR"),("mexico","MX"),("egypt","EG"),("morocco","MA"),("tanzania","TZ"),("uganda","UG"),("zimbabwe","ZW"),("somalia","SO"),("lesotho","LS"),("kampala","UG"),("indore","IN"),("maharashtra","IN"),("nashik","IN"),("surat","IN"),("ahmedabad","IN"),("bhopal","IN"),("coimbatore","IN"),("karnataka","IN"),("madurai","IN"),("mysore","IN"),("vizag","IN"),("hyderabad","IN"),("hydrabad","IN"),("bahrain","BH"),("germany","DE"),("italy","IT"),("kuwait","KW"),("philippines","PH"),("pune","IN"),("telugu","IN"),("tamil","IN")]
CATKW=[("jobs","jobs"),("job ","jobs"),("earning","online-earning"),("earn money","online-earning"),("islamic","islamic"),("quran","islamic"),("nikah","community-social"),("cricket","sports"),("football","sports"),("sports","sports"),("news","news"),("study","education"),("education","education"),("exam","education"),("ias","education"),("upsc","education"),("business","business"),("buy","buy-sell"),("sell","buy-sell"),("shopping","buy-sell"),("wholesale","buy-sell"),("funny","funny"),("joke","funny"),("meme","funny"),("game","gaming"),("gaming","gaming"),("pubg","gaming"),("free fire","gaming"),("bgmi","gaming"),("health","health"),("crypto","finance"),("finance","finance"),("trading","finance"),("stock","finance"),("movie","entertainment"),("song","entertainment"),("music","entertainment"),("video","entertainment"),("friendship","friendship"),("friends","friendship"),("dating","friendship"),("matrimony","community-social"),("marriage","community-social"),("shayari","entertainment"),("poetry","entertainment")]
def classify(title, cat_hint):
    text=((title or "")+" "+(cat_hint or "")).lower()
    cat=CATMAP.get((cat_hint or "").lower().strip())
    if not cat:
        cat="community-social"
        for kw,c in CATKW:
            if kw in text: cat=c; break
    else:
        # refine with keywords from title when generic
        if cat in ("business","gaming","community-social"):
            for kw,c in CATKW:
                if kw in text: cat=c; break
    country="International"
    for kw,cc in COUNTRIES:
        if kw in text: country=cc; break
    return cat, country
def clean_name(t):
    t=html.unescape(t or "").strip()
    t=re.sub(r'\s+',' ',t)
    t=re.sub(r'^(join|join this|join the)\s+','',t,flags=re.I)
    t=re.sub(r'\s*[\|\-–—]\s*whatsapp.*$','',t,flags=re.I)
    t=re.sub(r'\s*whatsapp group (invite|link).*$','',t,flags=re.I)
    return t.strip(" -–—|").strip()
def blocked(name):
    if not name: return True
    if PORN.search(name) or SCAM.search(name): return True
    if PHONE.search(name): return True
    return len(name)<2
# candidates from saved process-log page (lines 0-69 of fetch_print output)
saved=json.load(open(os.path.expanduser("~/workspace/agents/af97b50f-bc6d-4054-8c64-e35a60ecc6f5/tool-output/process.log-call_01a1afeb4af0706eb3ac2c6a15670668.json")))
cands={}
for line in saved["lines"]:
    if not line.startswith("POSTLINE "): continue
    try: d=json.loads(line[len("POSTLINE "):])
    except Exception: continue
    for code in d.get("codes",[]):
        if code not in cands:
            cands[code]={"code":code,"name_hint":d.get("title",""),"cat_hint":d.get("cat",""),"country_hint":"","src":d.get("src","")}
print("GDRAWUNIQUE",len(cands),flush=True)
union=set(json.load(open(os.path.join(WAVE,"dedupe_union.json"))))
seen_pk=set()
for f in ["pk_api_raw.json","pk_html_raw.json"]:
    p=os.path.join(S,f)
    if os.path.exists(p):
        for it in json.load(open(p)): seen_pk.add(it["code"])
fresh={c:v for c,v in cands.items() if c not in union and c not in seen_pk}
print("GDFRESH",len(fresh),flush=True)
pref=[(c,v) for c,v in fresh.items() if not blocked(v.get("name_hint",""))]
print("GDTOVERIFY",len(pref),flush=True)
def check(item):
    code,v=item
    url=f"https://chat.whatsapp.com/{code}"
    for attempt in range(2):
        try:
            r=requests.get(url,headers=UA,timeout=30)
            if r.status_code==200:
                m=re.search(r'<meta property="og:title" content="([^"]*)"',r.text)
                title=html.unescape(m.group(1)).strip() if m else ""
                if title: return (code,"live",title,v)
                return (code,"dead","",v)
            if r.status_code in (429,500,502,503,504):
                time.sleep(60); continue
            return (code,"dead","",v)
        except Exception:
            time.sleep(60)
    return (code,"pending","",v)
nv=np=0
with ThreadPoolExecutor(max_workers=8) as ex:
    for i,res in enumerate(ex.map(check,pref)):
        code,status,title,v=res
        if status=="live":
            name=clean_name(title)
            if blocked(name) or blocked(title): continue
            cat,country=classify(v.get("name_hint",""),v.get("cat_hint",""))
            # refine category with the REAL group name too
            cat2,country2=classify(name, v.get("cat_hint",""))
            if cat2!="community-social" or cat=="community-social": cat=cat2
            if country=="International": country=country2
            desc=f"Join the {name} WhatsApp group for {cat.replace('-',' ')} updates, chats and discussions" + (f" from {country}." if country!="International" else " with members from around the world.") + f" Active {cat.replace('-',' ')} community — connect, share and stay updated."
            print("GDVERIFIED "+json.dumps({"name":name,"category":cat,"country":country,"description":desc,"invite":f"https://chat.whatsapp.com/{code}","image":""},ensure_ascii=False),flush=True)
            nv+=1
        elif status=="pending":
            cat,country=classify(v.get("name_hint",""),v.get("cat_hint",""))
            print("GDPENDING "+json.dumps({"code":code,"name":clean_name(v.get("name_hint",""))[:80],"category":cat,"country":country,"invite":f"https://chat.whatsapp.com/{code}"},ensure_ascii=False),flush=True)
            np+=1
        if (i+1)%50==0: print(f"GDCHECKED {i+1}/{len(pref)} live={nv} pending={np}",flush=True)
print(f"GDSUMMARY verified={nv} pending={np} checked={len(pref)}",flush=True)
