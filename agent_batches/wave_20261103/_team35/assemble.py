import json, os, re

W=os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261103")
D=os.path.join(W,"_team35")

CATEGORIES=["Sports","Gaming","Jobs","Education","Entertainment","Friendship","News","Islamic",
"Business","Finance","Buy-Sell","Health","Community","Technology","Crypto","Travel","Music",
"Movies","Food","Pets","Funny","Girls","Regional","Other"]

import json, os, re, unicodedata

porn_keys=["porn","pornhub","xxx","nude","sex video","escort","call girl","callgirl","fuck","dick",
"pussy","boobs","anal","incest","randi","leak","leek","bhabhi","sexy","paid video","paid group",
"video call"]
urdu_keys=["ویڈیو کال","لیکیڈ","گرم","رانڈی","سیکسی"]
porn_emoji=["🥵","🍆","🍑","🔞","💦","👅","👄","💋","👙","🍌","😈"]
def is_porn(name):
    n=(name or "")
    norm=unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower()
    if any(k in norm for k in porn_keys): return True
    # strip tatweel + arabic diacritics for urdu keyword matching
    n2=''.join(ch for ch in n if ch!='\u0640' and unicodedata.category(ch)!='Mn')
    if any(k in n2 for k in urdu_keys): return True
    return any(e in n for e in porn_emoji)

def clean_name(n):
    n=(n or "").strip()
    n=re.sub(r'(?i)^join\s+group\s*','',n)
    n=re.sub(r'(?i)\s*(whatsapp\s+group|group\s+invite|invite\s+link)\s*$','',n)
    n=n.strip(' –-—:')
    if len(n)>90 or '{' in n or ';' in n: return ""
    return n

def pick_category(name, og):
    t=(name+" "+og).lower()
    if any(k in t for k in ["job","hiring","vacan","fpsc","ppsc","career","jobs","nokri"]): return "Jobs"
    if any(k in t for k in ["cricket","psl","sports","football"]): return "Sports"
    if any(k in t for k in ["game","tournament","gaming","pubg"]): return "Gaming"
    if any(k in t for k in ["quran","islam","islamic","deen","dawah","hadith","ramadan","namaz","hadees","ayat"]): return "Islamic"
    if any(k in t for k in ["earn","income","fiverr","freelan","money","binance","trading","crypto","nft"]): return "Finance"
    if any(k in t for k in ["shop","buy","sell","bazar","market","store","deal","reseller","brand","official store","e-commerce","ecommerce"]): return "Buy-Sell"
    if any(k in t for k in ["study","student","exam","education","css","university","college","school","admission","educational"]): return "Education"
    if any(k in t for k in ["music","song","shayari","poetry"]): return "Music"
    if any(k in t for k in ["movie","drama","film"]): return "Movies"
    if any(k in t for k in ["news"]): return "News"
    if any(k in t for k in ["business"]): return "Business"
    if any(k in t for k in ["travel","tour","agency"]): return "Travel"
    if any(k in t for k in ["health","fitness","gym"]): return "Health"
    if any(k in t for k in ["girl","ladies","women","single girl"]): return "Girls"
    if any(k in t for k in ["friend","masti","chat room","chill"]): return "Friendship"
    if any(k in t for k in ["funny","meme","joke"]): return "Funny"
    if any(k in t for k in ["photography","photo"]): return "Entertainment"
    if any(k in t for k in ["literature","novel","book"]): return "Entertainment"
    if any(k in t for k in ["overseas","expat","pakistani"]): return "Community"
    return "Community"

def make_desc(name, cat):
    safe=name if len(name)<=80 else name[:77]+"..."
    tpl={
     "Jobs": f"A Pakistani jobs community sharing daily job alerts, government and private vacancies, and career updates for members of {safe}.",
     "Education": f"A Pakistani education community sharing study material, exam updates, and learning resources with members of {safe}.",
     "Sports": f"A Pakistani sports community for fans to follow match updates, team discussions, and cricket news in {safe}.",
     "Islamic": f"An Islamic community for Pakistani members to share religious reminders, guidance, and faith discussions in {safe}.",
     "Finance": f"A Pakistani online-earning community where members discuss earning methods, freelancing tips, and income opportunities in {safe}.",
     "Buy-Sell": f"A Pakistani buy-and-sell community for shopping deals, product listings, and marketplace offers in {safe}.",
     "News": f"A Pakistani news community sharing daily updates, headlines, and current affairs with members of {safe}.",
     "Entertainment": f"A Pakistani entertainment community for fun content, videos, and lively discussions in {safe}.",
     "Technology": f"A Pakistani tech community discussing gadgets, programming, and digital trends in {safe}.",
     "Business": f"A Pakistani business community for entrepreneurs and traders to network and share opportunities in {safe}.",
     "Friendship": f"A Pakistani friendship community to meet new people, chat, and build connections in {safe}.",
     "Girls": f"A Pakistani girls community for social chat, lifestyle topics, and friendly conversation in {safe}.",
     "Funny": f"A Pakistani funny community sharing memes, jokes, and light-hearted entertainment in {safe}.",
     "Music": f"A Pakistani music community for sharing songs, poetry, and music discussions in {safe}.",
     "Movies": f"A Pakistani movies community for film and drama lovers to discuss entertainment in {safe}.",
     "Gaming": f"A Pakistani gaming community for players to discuss games, tournaments, and match updates in {safe}.",
     "Travel": f"A Pakistani travel community sharing travel guidance, agency updates, and trip discussions in {safe}.",
     "Community": f"A Pakistani WhatsApp community where members chat, share updates, and connect in {safe}.",
     "Other": f"A Pakistani WhatsApp community where members chat, share updates, and connect in {safe}.",
    }
    return tpl.get(cat, tpl["Community"])

all_results=[]
for f in ["verified_raw.json","agl_verified.json"]:
    fp=os.path.join(D,f)
    if os.path.exists(fp):
        r=json.load(open(fp))
        all_results += r.get("results", r) if isinstance(r,dict) else r

verified=[]; pending=[]; porn=0; dead=0; seen=set()
for r in all_results:
    code=r["code"]
    if code in seen: continue
    seen.add(code)
    v=r.get("verdict"); og=(r.get("og_title") or "").strip()
    if v=="rl":
        pending.append((code,"rate-limited",r.get("name",""))); continue
    if v=="tf":
        pending.append((code,"transport failure",r.get("name",""))); continue
    if v!="ok" or not og:
        dead+=1; continue  # dead link — excluded, not pending
    name=clean_name(og) or clean_name(r.get("name",""))
    if not name or is_porn(name) or is_porn(og):
        porn+=1; continue
    cat=pick_category(name, og)
    verified.append({"name":name,"category":cat,"country":"PK",
                     "description":make_desc(name,cat),
                     "invite":"https://chat.whatsapp.com/"+code,"image":""})

json.dump(verified, open(os.path.join(W,"team35-pakistan.json"),"w"), ensure_ascii=False, indent=1)
pend=[]
for code,note,nm in pending:
    pend.append({"name":clean_name(nm) or "Unknown","category":"Community","country":"PK",
                 "description":"A Pakistani WhatsApp community discovered during the wave 20261103 scrape.",
                 "invite":"https://chat.whatsapp.com/"+code,"image":"","note":note})
json.dump(pend, open(os.path.join(W,"team35-unverified-pending.json"),"w"), ensure_ascii=False, indent=1)

pre=json.load(open(os.path.join(D,"drops.json")))
porn_total=pre["porn"]+pre["other"]+porn  # other(nadra)+post-verify adult
print("verified:",len(verified),"pending:",len(pend),"dead:",dead,"porn_drops_total:",porn_total)
print("cats:",{c:sum(1 for x in verified if x['category']==c) for c in set(x['category'] for x in verified)})
for it in verified: print(it["category"],"|",it["name"][:60],"|",it["invite"].split('/')[-1])
