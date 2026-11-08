import requests, re, json, html
from concurrent.futures import ThreadPoolExecutor

P = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
TAG = re.compile(r'<[^>]+>')
def clean(t): return html.unescape(TAG.sub("", t)).replace("\xa0"," ").strip()
# name div then button div; capture code; REJECT invite/ channel codes
PAIR = re.compile(r'<div style="text-align: center;">([^<]{1,120})</div>\s*<div style="text-align: center;">\s*<div[^>]*>\s*<a href="https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})"', re.S)

PORN_WORDS = ["porn","pornhub","xxx","nude","sex video","escort","call girl","fuck","dick","pussy","boobs","anal","bokep","shaggers"]
EXCLUDE = {"Videos Group 💦","Indian Aunties","Get Oyo","AYUSH KUMAR CARDING FORUM","NNU DAILY INCOME 💸💶",
 "Forsage 💸💵🤑","RICHNET FUND 2","MONEY MAKERS","Lesbin sex video girl","Naughty Girls Groups",
 "paid kerala girls come","Indian adult WhatsApp group","Whatsapp adult group","School Girls","Aunty Of Delhi"}

def cat_lk(name):
    n = name.lower()
    if any(k in n for k in ["news","headlines"]): return "News"
    if "cricket" in n or "rugby" in n or "football" in n: return "Sports"
    if "pubg" in n or "free fire" in n or "gaming" in n or "game" in n: return "Gaming"
    if "movie" in n or "film" in n or "teledrama" in n: return "Movies"
    if "song" in n or "music" in n: return "Music"
    if "crypto" in n or "forex" in n or "binance" in n: return "Crypto"
    if "earn" in n or "income" in n or "money" in n: return "Finance"
    if "job" in n or "vacan" in n: return "Jobs"
    if "study" in n or "exam" in n or "class" in n or "university" in n or "a/l" in n or "o/l" in n: return "Education"
    if "girl" in n: return "Girls"
    if "friend" in n: return "Friendship"
    if "sri lanka" in n or "lanka" in n or "colombo" in n or "kandy" in n or "jaffna" in n: return "Regional"
    if "shop" in n or "deal" in n: return "Buy-Sell"
    if "business" in n: return "Business"
    return "Community"

def cat_pkg(name):
    n = name.lower()
    if "islam" in n or "quran" in n or "naat" in n: return "Islamic"
    if "poetry" in n or "shayari" in n: return "Entertainment"
    return "Girls"

DESC_T = {
 "Girls": ("a {adj} girls community for friendship, daily chatting and making new social connections.",),
 "Regional": ("a {adj} regional community for local chat, cultural updates and everyday discussions.",),
 "News": ("a {adj} news group sharing breaking headlines, updates and current affairs discussions.",),
 "Jobs": ("a {adj} jobs group posting job alerts, career opportunities and employment updates.",),
 "Education": ("a {adj} study group for students with learning resources, exam help and discussions.",),
 "Entertainment": ("an entertainment group for fun posts, videos, memes and lively chat.",),
 "Sports": ("a {adj} sports group for fans with match updates, discussions and sports news.",),
 "Gaming": ("a {adj} gaming group for players to team up, share tips and discuss games.",),
 "Movies": ("a {adj} movies group for film talk, reviews and entertainment updates.",),
 "Music": ("a {adj} music group for song sharing, music talk and entertainment.",),
 "Finance": ("an online earning group discussing income ideas, work opportunities and tips.",),
 "Crypto": ("a {adj} crypto group for trading talk, market updates and digital currency news.",),
 "Business": ("a {adj} business group for entrepreneurs, networking and business discussions.",),
 "Friendship": ("a {adj} friendship group for meeting new people and friendly conversations.",),
 "Community": ("a {adj} community group for discussions, networking and shared interests.",),
 "Islamic": ("an Islamic group for {adj} members with religious discussions and faith content.",),
 "Buy-Sell": ("a {adj} buy and sell group for shopping deals, trading and marketplace posts.",),
 "Other": ("a {adj} WhatsApp community for discussions and connecting with new people.",),
}

union = set(json.load(open(P+"dedupe_union.json")))
jobs = [
 ("team20_glfy_lk.html", "LK", "Sri Lankan", cat_lk),
 ("team20_glfy_pkgirls.html", "PK", "Pakistani", cat_pkg),
]
allcand=[]; porn=0
for path, cc, adj, catfn in jobs:
    try:
        t = open(P+path).read()
    except FileNotFoundError:
        print(path, "missing", flush=True); continue
    pairs = [(clean(m.group(1)), m.group(2)) for m in PAIR.finditer(t) if clean(m.group(1)) and "join now" not in clean(m.group(1)).lower()]
    print(path, "pairs:", len(pairs), flush=True)
    for name, code in pairs:
        nl = name.lower()
        if name in EXCLUDE or any(w in nl for w in PORN_WORDS):
            porn+=1; continue
        allcand.append({"src":name,"code":code,"cat":catfn(name),"cc":cc,"adj":adj})
print("total rows:", len(allcand), "porn drops:", porn, flush=True)
seen=set(); cand=[]
for r in allcand:
    if r["code"] in union or r["code"] in seen: continue
    seen.add(r["code"]); cand.append(r)
print("fresh candidates:", len(cand), flush=True)
json.dump(cand, open(P+"team20_candidates4.json","w"), ensure_ascii=False, indent=1)

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
            d = DESC_T[r["cat"]][0].format(adj=r["adj"])
            items.append({"name":title,"category":r["cat"],"country":r["cc"],
                "description":f"{title} — {d}",
                "invite":"https://chat.whatsapp.com/"+r["code"],"image":""})
        elif err:
            d = DESC_T[r["cat"]][0].format(adj=r["adj"])
            pend.append({"name":r["src"],"category":r["cat"],"country":r["cc"],
                "description":f"{r['src']} — {d}",
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
