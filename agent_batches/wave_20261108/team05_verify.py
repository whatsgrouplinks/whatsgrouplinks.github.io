import json, re, time, requests, html, sys
from concurrent.futures import ThreadPoolExecutor
BASE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}
CANON=["Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health","Business","Gaming","Friendship","Community & Social","Online Earning","Crypto","Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell","Finance","Funny"]
ALIAS={"buy-sell":"Buy & Sell","buysell":"Buy & Sell","buy & sell":"Buy & Sell","movies":"Entertainment","movie":"Entertainment","music":"Entertainment","religious":"Islamic","religion":"Islamic","islam":"Islamic","education":"Education","study":"Education","learning":"Education","jobs":"Jobs","job":"Jobs","work":"Jobs","employment":"Jobs","entertainment":"Entertainment","fun":"Funny","funny":"Funny","humor":"Funny","news":"News","sports":"Sports","sport":"Sports","football":"Sports","futbol":"Sports","cricket":"Sports","technology":"Technology","tech":"Technology","health":"Health","medical":"Health","business":"Business","negocios":"Business","gaming":"Gaming","game":"Gaming","games":"Gaming","free-fire":"Gaming","friendship":"Friendship","amistad":"Friendship","amizade":"Friendship","friends":"Friendship","community":"Community & Social","social":"Community & Social","other":"Community & Social","online earning":"Online Earning","earning":"Online Earning","earning-money":"Online Earning","earn-money":"Online Earning","earn money":"Online Earning","crypto":"Crypto","cryptocurrency":"Crypto","bitcoin":"Crypto","cooking":"Cooking","food":"Cooking","poetry":"Poetry","shayari":"Poetry","urdu-poetry":"Poetry","poesia":"Poetry","travel":"Travel","scholarship":"Scholarship","freelance":"Freelance","real estate":"Real Estate","finance":"Finance","money":"Finance","dinheiro":"Finance","namoro":"Friendship","series":"Entertainment","fitness":"Health","politica":"News","politics":"News","status":"Entertainment","moda-e-beleza":"Entertainment","carros":"Community & Social","cidades":"Community & Social","lgbt":"Community & Social","religiao":"Islamic","links":"Community & Social","comprar-e-venda":"Buy & Sell","trabalho":"Jobs","educacao":"Education","tecnologia":"Technology","esportes":"Sports","musica":"Entertainment","figurinhas":"Entertainment","love":"Friendship","romance":"Friendship","students":"Education","studying":"Education"}
def canon(cat):
    if not cat: return "Community & Social"
    c=cat.strip()
    if c in CANON: return c
    low=c.lower()
    if low in ALIAS: return ALIAS[low]
    for k,v in ALIAS.items():
        if k in low: return v
    return "Community & Social"
ADULT_EMOJI=set("🥵🍆🍑🔞💦👅👄💋")
BLOCK_WORDS=["porno","porn","xxx","sexo","sexe","baise","escort","call girl","call-girl","callgirl","bitfinex","paypay loader","paypal loader","counterfeit","fake currency","fake money","onlyfans","nude","desnuda","erotic","erotica","adult","18+","+18","18 +","hot babes","webseries ullu","ullu"]
SCAM_WORDS=["bitfinexinvests","paypal loader","money mule","double your money","counterfeit currency"]
def blocked(name,desc):
    t=((name or "")+" "+(desc or "")).lower()
    if any(e in (name or "")+(desc or "") for e in ADULT_EMOJI): return "adult-emoji"
    for w in BLOCK_WORDS:
        if w in t: return "blocked:"+w
    return None
def clean_name(n, code):
    n=html.unescape(n or "")
    n=re.sub(r"\s+"," ",n).strip(" -|–—")
    n=re.sub(r"\s*\|\s*(iGrupos|Linkado|Groupizo|Grupbul|Groupssor|WhatsApp.*)$","",n,flags=re.I)
    n=re.sub(r"^(Grupo de WhatsApp|WhatsApp Group|Join|Group:?)\s*","",n,flags=re.I).strip(" -|")
    n=n[:100]
    return n
def check(code):
    """returns (status, title) status in live/dead/transport"""
    url=f"https://chat.whatsapp.com/{code}"
    for attempt in range(2):
        try:
            s=requests.Session(); s.headers.update(UA)
            r=s.get(url,timeout=20,allow_redirects=True)
            if r.status_code!=200:
                return ("dead", f"http{r.status_code}")
            m=re.search(r'property="og:title"\s+content="([^"]*)"', r.text)
            title=html.unescape(m.group(1)).strip() if m else ""
            if not title:
                m2=re.search(r"<title>([^<]*)</title>", r.text)
                title=html.unescape(m2.group(1)).strip() if m2 else ""
            if title and title not in ("WhatsApp Group","Join this group on WhatsApp","WhatsApp"):
                return ("live", title)
            if title in ("WhatsApp Group","Join this group on WhatsApp"):
                return ("dead","generic-title")
            # empty title: ambiguous -> retry once after pause
            if attempt==0:
                time.sleep(3); continue
            return ("dead","empty-title-after-retry")
        except requests.exceptions.RequestException as e:
            if attempt==0:
                time.sleep(3); continue
            return ("transport", str(e)[:100])
    return ("dead","unknown")

def main():
    src=sys.argv[1] if len(sys.argv)>1 else BASE+"team05_phase2.json"
    cands=json.load(open(src))
    union=set(json.load(open(BASE+"dedupe_union.json")))
    fresh=[]; seen=set()
    for c in cands:
        code=c["code"]
        if code in union or code in seen: continue
        seen.add(code); fresh.append(c)
    print(f"cands {len(cands)} fresh-after-union {len(fresh)}", flush=True)
    results={}
    def work(c):
        time.sleep(0.6)
        st,title=check(c["code"])
        return c,st,title
    verified=[]; pending=[]; dead=0; blocked_n=0
    with ThreadPoolExecutor(max_workers=3) as ex:
        for c,st,title in ex.map(work, fresh):
            if st=="live":
                name=clean_name(title or c.get("name") or "", c["code"])
                if not name: name=clean_name(c.get("name") or "WhatsApp Group", c["code"])
                cat=canon(c.get("category") or "")
                desc=(c.get("desc") or "").strip()
                b=blocked(name,desc)
                if b:
                    blocked_n+=1; continue
                if not desc:
                    desc=f"Join {name}, a WhatsApp group listed under {cat}. Connect with members, share updates and stay in touch with the community."
                country=(c.get("country") or "International").strip() or "International"
                if len(country)!=2: country="International"
                verified.append({"name":name,"category":cat,"country":country,"description":desc[:500],"invite":f"https://chat.whatsapp.com/{c['code']}","image":""})
            elif st=="transport":
                pending.append({"name":clean_name(c.get("name") or "WhatsApp Group",c["code"]),"category":canon(c.get("category") or ""),"country":(c.get("country") or "International"),"description":(c.get("desc") or "")[:300] or "WhatsApp group.","invite":f"https://chat.whatsapp.com/{c['code']}","image":"","reason":"transport"})
            else:
                dead+=1
            if (len(verified)+len(pending)+dead+blocked_n)%50==0:
                print(f"progress verified={len(verified)} pending={len(pending)} dead={dead} blocked={blocked_n}", flush=True)
    print(f"FINAL verified={len(verified)} pending={len(pending)} dead={dead} blocked={blocked_n}", flush=True)
    for attempt in range(5):
        try:
            json.dump(verified, open(BASE+"team05-leads-harvest-e.json","w"), ensure_ascii=False, indent=1)
            json.dump(pending, open(BASE+"team05-leads-harvest-e-pending.json","w"), ensure_ascii=False, indent=1)
            break
        except Exception as e:
            print("write retry",e); time.sleep(2)
    print("wrote outputs")
if __name__=="__main__": main()
