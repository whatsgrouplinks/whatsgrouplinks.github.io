import requests, re, json, html, unicodedata
from concurrent.futures import ThreadPoolExecutor

P = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
TAG = re.compile(r'<[^>]+>')
def clean(t): return html.unescape(TAG.sub("", t)).replace("\xa0"," ").strip()
PAIR = re.compile(r'<div style="text-align: center;">([^<]{1,120})</div>\s*<div style="text-align: center;">\s*<div[^>]*>\s*<a href="https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})"', re.S)

PORN_WORDS = ["porn","pornhub","xxx","nude","sex video","escort","call girl","fuck","dick","pussy","boobs","anal","bokep","shaggers"]
EXCLUDE = {"Videos Group 💦","Indian Aunties","Get Oyo","AYUSH KUMAR CARDING FORUM","NNU DAILY INCOME 💸💶",
 "Forsage 💸💵🤑","RICHNET FUND 2","MONEY MAKERS","Lesbin sex video girl","Naughty Girls Groups",
 "paid kerala girls come","Indian adult WhatsApp group","Whatsapp adult group","School Girls","Aunty Of Delhi",
 "1X bet","9-level income","EBL Pakistan","Pubg low rate uc carding","Data mil jaega all nadra","PAYWAY GREAT factor"}

def cat_pk(name):
    n = name.lower()
    if any(k in n for k in ["news","headlines","journalist"]): return "News"
    if "cricket" in n or "psl" in n or "football" in n: return "Sports"
    if "pubg" in n or "gaming" in n or "game" in n: return "Gaming"
    if "movie" in n or "drama" in n or "film" in n: return "Movies"
    if "song" in n or "music" in n: return "Music"
    if "crypto" in n or "binance" in n or "forex" in n: return "Crypto"
    if "earn" in n or "income" in n or "money" in n or "fiverr" in n or "freelanc" in n: return "Finance"
    if "job" in n or "rozgar" in n: return "Jobs"
    if "study" in n or "exam" in n or "student" in n or "islam" in n or "quran" in n: return "Education" if "islam" not in n and "quran" not in n else "Islamic"
    if "girl" in n or "rishta" in n or "bhabhi" in n: return "Girls"
    if "poetry" in n or "shayari" in n or "funny" in n or "meme" in n: return "Entertainment"
    if "shop" in n or "bazaar" in n or "deal" in n or "store" in n: return "Buy-Sell"
    if "business" in n: return "Business"
    if "friend" in n: return "Friendship"
    if "tech" in n: return "Technology"
    if any(k in n for k in ["pakistan","pakistani","lahore","karachi","islamabad"]): return "Regional"
    return "Community"

DESC_T = {
 "Girls": "a Pakistani girls community for friendship, daily chatting and making new social connections.",
 "Regional": "a Pakistani regional community for local chat, city updates and everyday discussions.",
 "News": "a Pakistani news group sharing breaking headlines, updates and current affairs discussions.",
 "Jobs": "a Pakistani jobs group posting job alerts, career opportunities and employment updates.",
 "Education": "a Pakistani study group for students with learning resources, exam help and discussions.",
 "Entertainment": "a Pakistani entertainment group for fun posts, videos, memes and lively chat.",
 "Sports": "a Pakistani sports group for fans with match updates, discussions and sports news.",
 "Gaming": "a Pakistani gaming group for players to team up, share tips and discuss games.",
 "Movies": "a Pakistani movies and drama group for film talk, reviews and entertainment updates.",
 "Music": "a Pakistani music group for song sharing, music talk and entertainment.",
 "Finance": "a Pakistani online earning group discussing income ideas, work opportunities and tips.",
 "Crypto": "a Pakistani crypto group for trading talk, market updates and digital currency news.",
 "Business": "a Pakistani business group for entrepreneurs, networking and business discussions.",
 "Friendship": "a Pakistani friendship group for meeting new people and friendly conversations.",
 "Community": "a Pakistani community group for discussions, networking and shared interests.",
 "Islamic": "an Islamic group for Pakistani members with religious discussions and faith content.",
 "Technology": "a Pakistani technology group for tech news, discussions and digital trends.",
 "Buy-Sell": "a Pakistani buy and sell group for shopping deals, trading and marketplace posts.",
 "Other": "a Pakistani WhatsApp community for discussions and connecting with new people.",
}

union = set(json.load(open(P+"dedupe_union.json")))
t = open(P+"team20_glfy_pk.html").read()
pairs = [(clean(m.group(1)), m.group(2)) for m in PAIR.finditer(t) if clean(m.group(1)) and "join now" not in clean(m.group(1)).lower()]
print("glfy-pk pairs:", len(pairs), flush=True)
porn=0; cand=[]; seen=set()
for name, code in pairs:
    nl = name.lower()
    if name in EXCLUDE or any(w in nl for w in PORN_WORDS):
        porn+=1; continue
    if code in union or code in seen: continue
    seen.add(code); cand.append({"src":name,"code":code,"cat":cat_pk(name),"cc":"PK","adj":"Pakistani"})
print("fresh candidates:", len(cand), "porn/scam drops:", porn, flush=True)

def verify(r):
    s = requests.Session(); s.headers.update(UA)
    try:
        resp = s.get("https://chat.whatsapp.com/"+r["code"], timeout=55)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', resp.text)
        t = html.unescape(m.group(1)).strip() if m else ""
        return (r, t, None)
    except Exception as e:
        return (r, "", type(e).__name__)

def content_ok(name):
    nl = unicodedata.normalize('NFD', name).lower()
    nl = ''.join(c for c in nl if not unicodedata.combining(c))
    bad_words = PORN_WORDS + ['leak','mms','scandal','වැල්','15 අඩු','school girl','fast pay','online transfers','vendor','receiver and loader','money mule','sim number','number details','nadra']
    if any(w in nl for w in bad_words): return False
    if any(e in name for e in ['🥵','🍆','🍑','🔞','💦','👅','👄','💋']): return False
    return True

items=[]; pend=[]; dead=0; cdrop=0
with ThreadPoolExecutor(max_workers=24) as ex:
    for r, title, err in ex.map(verify, cand):
        if title and len(title)>=3 and not re.fullmatch(r'(?i)whatsapp( group)?', title.strip()):
            if not content_ok(title):
                cdrop+=1; continue
            d = DESC_T[r["cat"]]
            items.append({"name":title,"category":r["cat"],"country":r["cc"],
                "description":f"{title} — {d}",
                "invite":"https://chat.whatsapp.com/"+r["code"],"image":""})
        elif err:
            d = DESC_T[r["cat"]]
            pend.append({"name":r["src"],"category":r["cat"],"country":r["cc"],
                "description":f"{r['src']} — {d}",
                "invite":"https://chat.whatsapp.com/"+r["code"],"image":"","note":"transport failure"})
        else:
            dead+=1
print(f"VERIFIED={len(items)} PENDING={len(pend)} DEAD={dead} CONTENT_DROPS={cdrop}", flush=True)
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
