import requests, re, json, html, time
from concurrent.futures import ThreadPoolExecutor

P = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
ROW = re.compile(r'<tr><td>(.*?)</td><td><a href="https://chat\.whatsapp\.com/([A-Za-z0-9]{20,24})"', re.S)
H2 = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
TAG = re.compile(r'<[^>]+>')

def clean(t): return html.unescape(TAG.sub("", t)).strip()

def fetch(url, path):
    s = requests.Session(); s.headers.update(UA)
    r = s.get(url, timeout=55, allow_redirects=True)
    open(path, "w").write(r.text)
    return r.text

pages = {
 "pk": ("https://wahublink.com/pakistani-whatsapp-group-links/", P+"team20_wahupk.html", "PK", "Pakistani", "Pakistan"),
 "in": ("https://wahublink.com/indian-whatsapp-group-links/", P+"team20_wahuin.html", "IN", "Indian", "India"),
}
# section -> category (None = drop whole section)
PK_SEC = {
 "Pakistani Single Girl WhatsApp Group Link": "Girls",
 "Latest Pakistani WhatsApp Group Links": "MIXED_PK",
 "School Girl WhatsApp Group Links Pakistan": None,
 "WhatsApp Group Link Pakistan Viral Video": "Entertainment",
 "Online Earning in Pakistani WhatsApp Group Links": "MIXED_EARN_PK",
 "Pakistani Girl WhatsApp Group Links": "Girls",
 "Business WhatsApp Group Link Pakistan Girl": "Business",
 "Call Girl for Friendship WhatsApp Group Pakistan": None,
 "Desi WhatsApp Group Link Pakistan": "Girls",
 "Pakistani WhatsApp Group Links Women": "Girls",
 "Pakistani WhatsApp Group Links Girl Hyderabad": "Girls",
 "Pakistani WhatsApp Group Links Girl Lahore": "Girls",
 "Pakistani Aunty WhatsApp Group Link": None,
 "Pakistani WhatsApp Group Links": "Regional",
 "WhatsApp Group Link Pakistani Drama": "Movies",
 "Pakistani Students WhatsApp Group Links": "Education",
 "Karachi WhatsApp Group Link": "Regional",
 "ARY News WhatsApp Group Link": "News",
 "WhatsApp Group For Job Seekers Pakistan": "Jobs",
 "Urdu Shayari WhatsApp Group Link": "Entertainment",
 "Overseas Pakistani WhatsApp Group Links": "Regional",
 "Sub4Sub Pakistani WhatsApp Group Links": "Entertainment",
 "All Pakistani WhatsApp Group Links": "Regional",
 "Funny Pakistani WhatsApp Group Link": "Funny",
}
IN_SEC = {
 "Tamil WhatsApp Group Links": "Regional",
 "Kerala WhatsApp Group Links": "MIXED_KERALA",
 "Goa WhatsApp Group Links": "Regional",
 "Indian News WhatsApp Group Links": "News",
 "Mumbai WhatsApp Group Links": "Regional",
 "Indian WhatsApp Group Links": "MIXED_IN",
 "Kolkata WhatsApp Group Links": "Regional",
 "Online Trading in India WhatsApp Group Links": "Finance",
 "Hindi Poetry WhatsApp Group Links": "Entertainment",
 "PUBG Lovers in India Group Links": "Gaming",
 "Online Earning for Indians WhatsApp Group Links": "Finance",
}
PORN_WORDS = ["porn","pornhub","xxx","nude","sex video","escort","call girl","fuck","dick","pussy","boobs","anal","bokep","shaggers"]
EXCLUDE_NAMES = {"1X bet","9-level income","EBL Pakistan","EBL PAKISTAN REAL ONLINE BUSINESS PAKISTAN NO.1",
 "EBL PAKISTAN ONLINE WORK","PAYWAY GREAT factor","Lesbin sex video girl","Naughty Girls Groups",
 "paid kerala girls come","Indian adult WhatsApp group","Whatsapp adult group","School Girls","Aunty Of Delhi"}

def cat_for(secmap, sec, name):
    n = name.lower()
    base = secmap.get(sec.strip(), "Other")
    if base is None: return None
    if base == "MIXED_PK":
        if "cricket" in n: return "Sports"
        if n.strip() in ("pti",): return "News"
        if "gaming" in n or "game" in n: return "Gaming"
        if "movie" in n: return "Movies"
        return "Regional"
    if base == "MIXED_EARN_PK":
        if "crypto" in n: return "Crypto"
        return "Finance"
    if base == "MIXED_KERALA":
        if "viral" in n or "reels" in n: return "Entertainment"
        if "girl" in n: return "Girls"
        return "Regional"
    if base == "MIXED_IN":
        if any(k in n for k in ["girl","women","ladies","aunty","female","grils"]): return "Girls"
        return "Friendship"
    return base

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
 "Health": "a {adj} health group sharing wellness tips, fitness talk and healthy living.",
 "Travel": "a {adj} travel group for trip ideas, travel tips and tourism discussions.",
 "Food": "a {adj} food group for recipes, food talk and culinary fun.",
 "Pets": "a {adj} pets group for animal lovers to share photos and pet care tips.",
 "Buy-Sell": "a {adj} buy and sell group for shopping deals, trading and marketplace posts.",
 "Other": "a {adj} WhatsApp community for discussions and connecting with new people.",
}

union = set(json.load(open(P+"dedupe_union.json")))
rows = []
porn_drops = 0; minor_drops = 0; scam_drops = 0; sec_drops = 0
for key,(url,path,cc,adj,country_name) in pages.items():
    text = fetch(url, path)
    print(f"[{key}] fetched {len(text)} chars", flush=True)
    # split into sections
    parts = H2.split(text)
    # parts[0] = before first h2; then alternating title, body
    secmap = PK_SEC if key=="pk" else IN_SEC
    for i in range(1, len(parts), 2):
        sec = clean(parts[i]); body = parts[i+1] if i+1 < len(parts) else ""
        for m in ROW.finditer(body):
            name = clean(m.group(1)); code = m.group(2)
            nl = name.lower()
            if secmap.get(sec.strip()) is None:
                sec_drops += 1; continue
            if name in EXCLUDE_NAMES or any(w in nl for w in PORN_WORDS):
                porn_drops += 1; continue
            if "school girl" in nl:
                minor_drops += 1; continue
            cat = cat_for(secmap, sec, name)
            if cat is None:
                sec_drops += 1; continue
            rows.append({"src_name":name,"code":code,"category":cat,"country":cc,"adj":adj,"sec":sec})

print(f"rows parsed: {len(rows)} (sec_drops={sec_drops} porn={porn_drops} minor={minor_drops})", flush=True)
# dedupe
seen=set(); cand=[]
for r in rows:
    if r["code"] in union or r["code"] in seen: continue
    seen.add(r["code"]); cand.append(r)
print(f"candidates after dedupe: {len(cand)}", flush=True)
json.dump([{"code":c["code"],"src_name":c["src_name"],"category":c["category"],"country":c["country"],"adj":c["adj"]} for c in cand],
          open(P+"team20_candidates.json","w"), ensure_ascii=False, indent=1)

def verify(r):
    s = requests.Session(); s.headers.update(UA)
    try:
        resp = s.get("https://chat.whatsapp.com/"+r["code"], timeout=55)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', resp.text)
        t = html.unescape(m.group(1)).strip() if m else ""
        return (r, t, None)
    except Exception as e:
        return (r, "", type(e).__name__)

items=[]; pending=[]; dead=0
with ThreadPoolExecutor(max_workers=24) as ex:
    for r, title, err in ex.map(verify, cand):
        if title and not re.fullmatch(r'(?i)whatsapp( group)?', title.strip()) and len(title)>=3:
            name = title
            items.append({"name":name,"category":r["category"],"country":r["country"],
                "description":f"{name} — {DESC[r['category']].format(adj=r['adj'])}",
                "invite":"https://chat.whatsapp.com/"+r["code"],"image":""})
        elif err:
            r2=dict(r); r2["note"]="transport failure"; pending.append(r2)
        else:
            dead+=1
print(f"VERIFIED={len(items)} PENDING_RETRY={len(pending)} DEAD={dead}", flush=True)

# merge with the 8 already-verified snippet items
final = json.load(open(P+"team20-southasia-dirs.json"))
have = {x["invite"].rsplit("/",1)[1] for x in final}
for it in items:
    if it["invite"].rsplit("/",1)[1] not in have:
        final.append(it); have.add(it["invite"].rsplit("/",1)[1])
json.dump(final, open(P+"team20-southasia-dirs.json","w"), ensure_ascii=False, indent=1)
# rebuild pending file: transport-failure retries only
pj=[]
for r in pending:
    pj.append({"name":r["src_name"],"category":r["category"],"country":r["country"],
        "description":f"{r['src_name']} — {DESC[r['category']].format(adj=r['adj'])}",
        "invite":"https://chat.whatsapp.com/"+r["code"],"image":"","note":"transport failure during og:title check — retry next wave"})
json.dump(pj, open(P+"team20-unverified-pending.json","w"), ensure_ascii=False, indent=1)
print(f"FINAL verified file: {len(final)} items; pending file: {len(pj)}", flush=True)
