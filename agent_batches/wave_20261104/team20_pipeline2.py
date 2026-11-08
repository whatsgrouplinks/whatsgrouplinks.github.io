import requests, re, json, html
from concurrent.futures import ThreadPoolExecutor

P = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
H2 = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
TAG = re.compile(r'<[^>]+>')
def clean(t): return html.unescape(TAG.sub("", t)).replace("\xa0"," ").strip()

# whatgroups PK rows
WGROW = re.compile(r'<tr><td[^>]*>(.*?)</td><td><strong><a href="https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})"', re.S)
# whatz BD rows: <p ...>NAME <strong>➺</strong> <strong><a href="...CODE"
WZROW = re.compile(r'<p[^>]*>(.*?)<strong[^>]*>\s*➺\s*</strong>\s*<strong><a href="https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})"', re.S)

PORN_WORDS = ["porn","pornhub","xxx","nude","sex video","escort","call girl","fuck","dick","pussy","boobs","anal","bokep","shaggers"]
EXCLUDE_NAMES = {"Pubg low rate uc carding","Data mil jaega all nadra","EBL Pakistan","EBL PAKISTAN REAL ONLINE BUSINESS PAKISTAN NO.1","EBL PAKISTAN ONLINE WORK","1X bet","9-level income","PAYWAY GREAT factor","Bangali couple2couple fun","Chim divo"}

def cat_pk(sec, name):
    n = name.lower()
    if "cricket" in sec.lower() or "psl" in n or "cricket" in n or "t20" in n or "icc" in n or "pcb" in n: return "Sports"
    if "earning" in sec.lower() or "earn" in n or "income" in n or "fiverr" in n or "freelanc" in n: return "Finance"
    if "crypto" in n or "binance" in n or "forex" in n or "trading" in n: return "Crypto"
    if "news" in n or "journalist" in n or "pti" == n.strip().lower(): return "News"
    if "islam" in n or "quran" in n or "madina" in n or "deen" in n: return "Islamic"
    if "job" in n or "rozgar" in n or "cv" in n: return "Jobs"
    if "pubg" in n or "game" in n: return "Gaming"
    if "shop" in n or "bazaar" in n or "market" in n or "store" in n or "daraz" in n: return "Buy-Sell"
    if "poetry" in n or "shayari" in n or "novel" in n: return "Entertainment"
    if "girl" in n or "rishta" in n: return "Girls"
    if "tech" in n or "program" in n: return "Technology"
    if "cricket" in n: return "Sports"
    if any(k in n for k in ["lahore","karachi","islamabad","pakistan","balochistan","orangi"]): return "Regional"
    return "Community"

def cat_bd(name):
    n = name.lower()
    if "cricket" in n or "football" in n or "sports" in n: return "Sports"
    if "news" in n: return "News"
    if "job" in n or "income" in n or "earn" in n or "work from home" in n: return "Jobs" if "job" in n else "Finance"
    if "cricket" in n: return "Sports"
    if "islam" in n or "muslim" in n: return "Islamic"
    if "student" in n or "study" in n or "hacking" in n: return "Education"
    if "music" in n or "song" in n: return "Music"
    if "girl" in n: return "Girls"
    if "business" in n or "trade" in n or "factory" in n: return "Business"
    if "shop" in n or "clothes" in n: return "Buy-Sell"
    if "youtuber" in n or "tiktok" in n or "video" in n or "comedy" in n: return "Entertainment"
    if "bangladesh" in n or "bangla" in n or "bengali" in n: return "Regional"
    return "Community"

DESC = {
 "Girls": "a {adj} girls community for friendship, daily chatting and making new social connections.",
 "Regional": "a {adj} regional community for local chat, city updates and everyday discussions.",
 "News": "a {adj} news group sharing breaking headlines, updates and current affairs discussions.",
 "Jobs": "a {adj} jobs group posting job alerts, career opportunities and employment updates.",
 "Education": "a {adj} study group for students with learning resources, exam help and discussions.",
 "Entertainment": "a {adj} entertainment group for fun posts, videos, memes and lively chat.",
 "Funny": "a {adj} funny group sharing jokes, memes and hilarious clips for daily laughs.",
 "Sports": "a {adj} sports group for fans with match updates, discussions and sports news.",
 "Gaming": "a {adj} gaming group for players to team up, share tips and discuss games.",
 "Movies": "a {adj} movies and drama group for film talk, reviews and entertainment updates.",
 "Music": "a {adj} music group for song sharing, music talk and entertainment.",
 "Finance": "a {adj} online earning group discussing income ideas, work opportunities and tips.",
 "Crypto": "a {adj} crypto group for trading talk, market updates and digital currency news.",
 "Business": "a {adj} business group for entrepreneurs, networking and business discussions.",
 "Friendship": "a {adj} friendship group for meeting new people and friendly conversations.",
 "Community": "a {adj} community group for discussions, networking and shared interests.",
 "Islamic": "an Islamic group for {adj} members with religious discussions and faith content.",
 "Technology": "a {adj} technology group for tech news, discussions and digital trends.",
 "Buy-Sell": "a {adj} buy and sell group for shopping deals, trading and marketplace posts.",
 "Other": "a {adj} WhatsApp community for discussions and connecting with new people.",
}

union = set(json.load(open(P+"dedupe_union.json")))
rows=[]; porn=0; scam=0
# --- whatgroups PK ---
text = open(P+"team20_wgpk.html").read()
parts = H2.split(text)
for i in range(1, len(parts), 2):
    sec = clean(parts[i]); body = parts[i+1] if i+1 < len(parts) else ""
    for m in WGROW.finditer(body):
        name = clean(m.group(1)); code = m.group(2); nl = name.lower()
        if name in EXCLUDE_NAMES or any(w in nl for w in PORN_WORDS): porn+=1; continue
        rows.append({"src":name,"code":code,"cat":cat_pk(sec,name),"cc":"PK","adj":"Pakistani"})
print("wg-pk rows:", len(rows), "porn/scam drops:", porn, flush=True)
# --- whatz BD ---
text = open(P+"team20_whatzbd.html").read()
n0=len(rows)
for m in WZROW.finditer(text):
    name = clean(m.group(1)); code = m.group(2); nl = name.lower()
    if name in EXCLUDE_NAMES or any(w in nl for w in PORN_WORDS): porn+=1; continue
    rows.append({"src":name,"code":code,"cat":cat_bd(name),"cc":"BD","adj":"Bangladeshi"})
print("whatz-bd rows:", len(rows)-n0, flush=True)

seen=set(); cand=[]
for r in rows:
    if r["code"] in union or r["code"] in seen: continue
    seen.add(r["code"]); cand.append(r)
print("candidates after dedupe:", len(cand), "of", len(rows), flush=True)
json.dump(cand, open(P+"team20_candidates2.json","w"), ensure_ascii=False, indent=1)

def verify(r):
    s = requests.Session(); s.headers.update(UA)
    try:
        resp = s.get("https://chat.whatsapp.com/"+r["code"], timeout=55)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', resp.text)
        t = html.unescape(m.group(1)).strip() if m else ""
        return (r, t, None)
    except Exception as e:
        return (r, "", type(e).__name__)

items=[]; pend=[]; dead=0
with ThreadPoolExecutor(max_workers=24) as ex:
    for r, title, err in ex.map(verify, cand):
        if title and len(title)>=3 and not re.fullmatch(r'(?i)whatsapp( group)?', title.strip()):
            items.append({"name":title,"category":r["cat"],"country":r["cc"],
                "description":f"{title} — {DESC[r['cat']].format(adj=r['adj'])}",
                "invite":"https://chat.whatsapp.com/"+r["code"],"image":""})
        elif err:
            pend.append({"name":r["src"],"category":r["cat"],"country":r["cc"],
                "description":f"{r['src']} — {DESC[r['cat']].format(adj=r['adj'])}",
                "invite":"https://chat.whatsapp.com/"+r["code"],"image":"","note":"transport failure"})
        else:
            dead+=1
print(f"VERIFIED={len(items)} PENDING={len(pend)} DEAD={dead}", flush=True)
final = json.load(open(P+"team20-southasia-dirs.json"))
have = {x["invite"].rsplit("/",1)[1] for x in final}
for it in items:
    if it["invite"].rsplit("/",1)[1] not in have:
        final.append(it); have.add(it["invite"].rsplit("/",1)[1])
json.dump(final, open(P+"team20-southasia-dirs.json","w"), ensure_ascii=False, indent=1)
pj = json.load(open(P+"team20-unverified-pending.json"))
for p_ in pend: pj.append(p_)
json.dump(pj, open(P+"team20-unverified-pending.json","w"), ensure_ascii=False, indent=1)
print("FINAL verified:", len(final), "pending:", len(pj), flush=True)
