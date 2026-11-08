import requests, re, json, html
from concurrent.futures import ThreadPoolExecutor

P = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
TAG = re.compile(r'<[^>]+>')
def clean(t): return html.unescape(TAG.sub("", t)).replace("\xa0"," ").strip()
# name div immediately precedes the Join-Now button div
PAIR = re.compile(r'<div style="text-align: center;">([^<]{1,100})</div>\s*<div[^>]*>\s*(?:<div[^>]*>\s*)?<a href="https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})"', re.S)

PORN_WORDS = ["porn","pornhub","xxx","nude","sex video","escort","call girl","fuck","dick","pussy","boobs","anal","bokep","shaggers"]
EXCLUDE = {"Videos Group 💦","❤️ Video ❤️😜","Indian Aunties","Get Oyo","AYUSH KUMAR CARDING FORUM",
 "NNU DAILY INCOME 💸💶","Forsage 💸💵🤑","RICHNET FUND 2","MONEY MAKERS","Lesbin sex video girl",
 "Naughty Girls Groups","paid kerala girls come","Indian adult WhatsApp group","Whatsapp adult group",
 "School Girls","Aunty Of Delhi","Chat With Girls ❤","Videos Link Group"}

def cat_in(name):
    n = name.lower()
    if any(k in n for k in ["news","headlines"]): return "News"
    if "cricket" in n or "ipl" in n or "wwe" in n: return "Sports"
    if "pubg" in n or "free fire" in n or "gaming" in n or "game" in n: return "Gaming"
    if "movie" in n or "film" in n or "netflix" in n: return "Movies"
    if "song" in n or "music" in n: return "Music"
    if "crypto" in n or "bitcoin" in n or "forex" in n or "binance" in n: return "Crypto"
    if "earn" in n or "income" in n or "money" in n or "loot" in n: return "Finance"
    if "job" in n: return "Jobs"
    if "study" in n or "exam" in n or "math" in n or "engineer" in n: return "Education"
    if "girl" in n or "aunty" in n or "bhabhi" in n: return "Girls"
    if "shayari" in n or "poetry" in n or "funny" in n or "meme" in n or "joke" in n: return "Entertainment"
    if "tamil" in n or "mumbai" in n or "punjab" in n or "bihar" in n or "delhi" in n or "indian" in n or "india" in n: return "Regional"
    if "friend" in n or "chat" in n: return "Friendship"
    if "shop" in n or "deal" in n or "mall" in n: return "Buy-Sell"
    if "health" in n or "fitness" in n: return "Health"
    if "business" in n: return "Business"
    return "Community"

DESC = {
 "Girls": "an Indian girls community for friendship, daily chatting and making new social connections.",
 "Regional": "an Indian regional community for local chat, cultural updates and everyday discussions.",
 "News": "an Indian news group sharing breaking headlines, updates and current affairs discussions.",
 "Jobs": "an Indian jobs group posting job alerts, career opportunities and employment updates.",
 "Education": "an Indian study group for students with learning resources, exam help and discussions.",
 "Entertainment": "an Indian entertainment group for fun posts, videos, memes and lively chat.",
 "Sports": "an Indian sports group for fans with match updates, discussions and sports news.",
 "Gaming": "an Indian gaming group for players to team up, share tips and discuss games.",
 "Movies": "an Indian movies group for film talk, reviews and entertainment updates.",
 "Music": "an Indian music group for song sharing, music talk and entertainment.",
 "Finance": "an Indian online earning group discussing income ideas, work opportunities and tips.",
 "Crypto": "an Indian crypto group for trading talk, market updates and digital currency news.",
 "Business": "an Indian business group for entrepreneurs, networking and business discussions.",
 "Friendship": "an Indian friendship group for meeting new people and friendly conversations.",
 "Community": "an Indian community group for discussions, networking and shared interests.",
 "Health": "an Indian health group sharing wellness tips, fitness talk and healthy living.",
 "Buy-Sell": "an Indian buy and sell group for shopping deals, trading and marketplace posts.",
 "Other": "an Indian WhatsApp community for discussions and connecting with new people.",
}

def parse_file(path):
    t = open(path).read()
    out=[]
    for m in PAIR.finditer(t):
        name = clean(m.group(1)); code = m.group(2)
        if not name or "join now" in name.lower(): continue
        out.append((name, code))
    return out

union = set(json.load(open(P+"dedupe_union.json")))
rows = [(n,c) for n,c in parse_file(P+"team20_glfy_in.html")]
print("glfy-in pairs:", len(rows), flush=True)
porn=0; cand=[]; seen=set()
for name, code in rows:
    nl = name.lower()
    if name in EXCLUDE or any(w in nl for w in PORN_WORDS):
        porn+=1; continue
    if code in union or code in seen: continue
    seen.add(code)
    cand.append({"src":name,"code":code,"cat":cat_in(name),"cc":"IN","adj":"Indian"})
print(f"fresh candidates: {len(cand)} porn/scam drops: {porn}", flush=True)
json.dump(cand, open(P+"team20_candidates3.json","w"), ensure_ascii=False, indent=1)

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
                "description":f"{title} — {DESC[r['cat']]}",
                "invite":"https://chat.whatsapp.com/"+r["code"],"image":""})
        elif err:
            pend.append({"name":r["src"],"category":r["cat"],"country":r["cc"],
                "description":f"{r['src']} — {DESC[r['cat']]}",
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
