import json, re, html, os

WD="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"

PAGE_CAT = {
 "karachi":"Community & Social","islamic":"Islamic","canada":"Community & Social",
 "indonesia":"Community & Social","islamabad":"Community & Social","lahore":"Community & Social",
 "pakistan-cricket":"Sports","photo-editing":"Technology","psl":"Sports","sri-lanka":"Community & Social",
 "tamil":"Community & Social","usa":"Community & Social","arabic":"Islamic","dawateislami":"Islamic",
 "madani-channel":"Islamic","quran":"Islamic","ramadan":"Islamic","educational":"Education",
 "entertainment":"Entertainment","jobs":"Jobs","news":"News","poetry":"Poetry","romantic":"Friendship",
 "status":"Entertainment","gaming":"Gaming","anime":"Entertainment","balochistan":"Community & Social",
 "buy-and-sell":"Buy Sell","cooking":"Cooking","courses-training":"Education","cryptocurrency":"Crypto",
 "digital-marketing":"Business","english-learning":"Education","fashion":"Community & Social",
 "forex-trading":"Finance","freefire":"Gaming","friendship":"Friendship","funny-video":"Funny",
 "general-knowledge":"Education","graphic-design":"Technology","drama":"Entertainment",
 "international-business":"Business","kerala":"Community & Social","kurulus-osman":"Entertainment",
 "malayalam":"Community & Social","marriage":"Community & Social","movies":"Entertainment",
 "music":"Entertainment","novels":"Entertainment","online-earning":"Online Earning",
 "pakistan":"Community & Social","pdf-books":"Education","pti":"News","pubg":"Gaming",
 "rawalpindi":"Community & Social","real-estate":"Real Estate","science-technology":"Technology",
 "shopping":"Buy Sell","sindhi":"Community & Social","students":"Education","sub4sub":"Community & Social",
 "tlp":"News","turkish":"Entertainment","urdu":"Community & Social","viral-tiktok":"Entertainment",
 "viral-video":"Entertainment","stickers":"Entertainment","youtube":"Entertainment",
 "zambia":"Community & Social","cartoon":"Entertainment","class":"Education",
 "hamster-kombat":"Crypto","all-groups":"Community & Social","pakistan-dating":"Friendship",
}
TITLE_OVERRIDES = [
 (r'cricket|psl|football|hockey|sports', "Sports"),
 (r'quran|naat|islamic|madani|dawat|ramadan|hadees|hadith|tilawat|bayan', "Islamic"),
 (r'poetry|shayari|شاعری|ghazal|nazm', "Poetry"),
 (r'\bjob|jobs|rozgar|روزگار|vacanc', "Jobs"),
 (r'\bnews|خبر|headlines', "News"),
 (r'forex|trading|forex trading', "Finance"),
 (r'crypto|bitcoin|binance|usdt|ethereum', "Crypto"),
 (r'pubg|free ?fire|gaming|game', "Gaming"),
 (r'funny|joke|comedy|memes?', "Funny"),
 (r'cooking|recipe|khana|food', "Cooking"),
 (r'movie|film|drama|netflix', "Entertainment"),
 (r'music|song|audio', "Entertainment"),
 (r'study|education|course|class|exam|admission|scholarship', "Education"),
 (r'buy|sell|shop|shopping|market', "Buy Sell"),
 (r'real estate|property|plot|house', "Real Estate"),
 (r'travel|tour|tourism', "Travel"),
 (r'health|fitness|doctor|medical', "Health"),
 (r'business|marketing|startup', "Business"),
 (r'friend|friendship|girls|dating', "Friendship"),
 (r'technolog|software|program|developer|computer', "Technology"),
 (r'earn|earning|online earning|make money', "Online Earning"),
 (r'freelanc', "Freelance"),
]

DESC = {
 "Education":"An education group where members share study material, notes and learning resources.",
 "Jobs":"A jobs group sharing vacancies, career updates and employment opportunities with members.",
 "Entertainment":"An entertainment group where members share fun content and lively discussions.",
 "Islamic":"A religious group sharing Islamic reminders, learning and community updates.",
 "News":"A news group sharing the latest headlines and updates with members.",
 "Sports":"A sports group for fans to share match updates, scores and lively discussion.",
 "Technology":"A technology group where members share tech news, tips and discussions.",
 "Health":"A health group sharing wellness tips and healthy-living discussions.",
 "Business":"A business group where members share ideas, updates and opportunities.",
 "Gaming":"A gaming group for players to share tips, updates and connect with fellow gamers.",
 "Friendship":"A friendship group for making friends and chatting in a friendly community.",
 "Community & Social":"A community group for chatting and sharing updates with members.",
 "Online Earning":"A group sharing online earning ideas and opportunities with members.",
 "Crypto":"A crypto group where members discuss digital currency news and market updates.",
 "Cooking":"A cooking group sharing recipes, tips and food ideas with members.",
 "Poetry":"A poetry group sharing verses, shayari and literary pieces with members.",
 "Travel":"A travel group sharing trip ideas, destinations and travel tips.",
 "Scholarship":"A scholarship group sharing study-abroad and funding opportunities.",
 "Freelance":"A freelance group sharing work opportunities and tips for freelancers.",
 "Real Estate":"A real-estate group sharing property listings and market updates.",
 "Buy Sell":"A buy-and-sell group where members post items for sale and find deals.",
 "Finance":"A group sharing financial insights and market updates with members.",
 "Funny":"A funny group sharing jokes, memes and light-hearted entertainment.",
}

SCAM_RE = re.compile(r'b-?love|blove|forsage|shey(i|ee)|holiverse|meta[\s-]?whale|1xbet|betpro|betting|match[\s-]?fixing|double[\s-]?money|investment[\s-]?doubl|earn[\s-]?daily[\s-]?profit', re.I)
PORN_RE = re.compile(r'\bxxx\b|porn|adult[\s-]?video|sex[\s-]?chat|sex[\s-]?video|nude|sexy[\s-]?video|فحش|پورن', re.I)
NEG_RE = re.compile(r'(no|not|never|don\'t|dont|not allowed|prohibited|strictly no|no porn|porn not|no xxx|xxx not)[^.,;]{0,40}(porn|xxx|sex|nude|adult)', re.I)
ENDED_RE = re.compile(r'گروپ ختم|group (has )?(ended|closed|end)|this group (is )?(ended|closed)|group deleted', re.I)
PHONE_RE = re.compile(r'\+?\d[\d\s().-]{7,}\d')
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

def clean_name(s):
    if not s: return ""
    s = html.unescape(s)
    s = EMAIL_RE.sub("", s)
    s = PHONE_RE.sub("", s)
    s = re.sub(r'[\s\-–—:;,.]+$', '', s).strip()
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.strip(' -–—|')
    return s

def screen(name, title):
    """return exclusion reason or None"""
    for txt in (name, title):
        if not txt: continue
        t = txt
        # strip negated prohibition sentences before porn screen
        t2 = NEG_RE.sub("", t)
        if SCAM_RE.search(t):
            return f"scam keyword in {'og:title' if txt is title else 'name'}: {txt[:80]}"
        if PORN_RE.search(t2):
            return f"adult/porn content in {'og:title' if txt is title else 'name'}: {txt[:80]}"
        if ENDED_RE.search(t):
            return f"group-ended signal in {'og:title' if txt is title else 'name'}: {txt[:80]}"
    return None

def category_for(page, name, title):
    text = f"{title} {name}"
    for pat, cat in TITLE_OVERRIDES:
        if re.search(pat, text, re.I):
            return cat
    return PAGE_CAT.get(page, "Community & Social")

allc=json.load(open(os.path.join(WD,"team14_all_extracted.json")))
ckpt={}
for line in open(os.path.join(WD,"team14_verify_ckpt.jsonl")):
    r=json.loads(line); ckpt[r["code"]]=r

# recompute fresh set (union of .existing + groups.json + yesterday verified)
a=json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'))
g=json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
s=set(a)
for it in g:
    m=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', it.get('invite',''))
    if m: s.add(m.group(1))
prev=json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team14-77links.json'))
for it in prev:
    m=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', it.get('invite',''))
    if m: s.add(m.group(1))
fresh={c:v for c,v in allc.items() if c not in s}

verified, pending, exclusions = [], [], []
dead = 0
unverified = 0
for code, v in fresh.items():
    r = ckpt.get(code)
    if r is None:
        unverified += 1
        continue
    if r["status"] == "live":
        title = r.get("title","")
        label = v.get("label","")
        name = clean_name(title) if title and title.lower() not in ("whatsapp group invite","whatsapp group") else clean_name(label)
        if not name:
            name = clean_name(label) or clean_name(title) or "WhatsApp Group"
        if len(name) > 120: name = name[:120].rsplit(" ",1)[0]
        reason = screen(name, title)
        if reason:
            exclusions.append({"code": code, "reason": reason}); continue
        cat = category_for(v["page"], name, title)
        verified.append({
            "name": name,
            "category": cat,
            "country": v.get("country","") or "",
            "description": DESC.get(cat, DESC["Community & Social"]),
            "invite": f"https://chat.whatsapp.com/{code}",
        })
    elif r["status"] == "pending":
        label = v.get("label","")
        name = clean_name(label) or "WhatsApp Group"
        cat = category_for(v["page"], name, "")
        pending.append({
            "name": name, "category": cat, "country": v.get("country","") or "",
            "description": "Pending verification: directory listing; transport failure on invite check, re-check needed.",
            "invite": f"https://chat.whatsapp.com/{code}",
            "reason": r.get("reason","transport failure"),
        })
    else:
        dead += 1

verified.sort(key=lambda x: x["invite"])
pending.sort(key=lambda x: x["invite"])
json.dump(verified, open(os.path.join(WD,"team14-77links.json"),'w'), ensure_ascii=False, indent=2)
json.dump(pending, open(os.path.join(WD,"team14-77links-pending.json"),'w'), ensure_ascii=False, indent=2)

FAILED_PAGES = [
 ("kurulus-osman","https://77links.com/kurulus-osman-whatsapp-group-links/","HTTP 000 twice, retry next wave"),
 ("malayalam","https://77links.com/malayalam-whatsapp-group-links/","HTTP 000 twice, retry next wave"),
 ("marriage","https://77links.com/marriage-whatsapp-group-links/","HTTP 000 twice, retry next wave"),
 ("online-earning","https://77links.com/online-earning-whatsapp-groups/","HTTP 000 twice, retry next wave"),
 ("pdf-books","https://77links.com/pdf-books-whatsapp-group-links/","HTTP 000 twice, retry next wave"),
 ("pti","https://77links.com/pti-whatsapp-group-links/","HTTP 000 twice, retry next wave"),
 ("pubg","https://77links.com/pubg-whatsapp-group-links/","HTTP 000 twice, retry next wave"),
]
leads=[{"url":u,"note":n} for _,u,n in FAILED_PAGES]
# channel pages on the sitemap are not group listings (whatsapp.com/channel links) - note only
leads.append({"url":"https://77links.com/cricket-whatsapp-channels/","note":"channel page, not group links; unmined"})
leads.append({"url":"https://77links.com/educational-whatsapp-channels/","note":"channel page, not group links; unmined"})
leads.append({"url":"https://77links.com/islamic-whatsapp-channels/","note":"channel page, not group links; unmined"})
leads.append({"url":"https://77links.com/poetry-whatsapp-channels/","note":"channel page, not group links; unmined"})
json.dump(leads, open(os.path.join(WD,"team14-77links-leads.json"),'w'), ensure_ascii=False, indent=2)

summary={
 "team":14,
 "slice":"77links.com Karachi/Islamic + new categories",
 "sources":[u for _,u,_ in FAILED_PAGES] and [v["url"] for v in allc.values()][:0] or sorted(set(v["url"] for v in allc.values())),
 "verified":len(verified),
 "pending":len(pending),
 "leads":len(leads),
 "dead":dead,
 "exclusions":exclusions,
 "resume":f"Extracted {len(allc)} codes from 77links.com listing pages; {len(fresh)} fresh vs union; {len(ckpt)} checkpointed; {unverified} fresh codes still unverified (not in checkpoint) - re-run team14_verify.py to finish them. 7 listing pages still unmined (HTTP 000 twice): kurulus-osman, malayalam, marriage, online-earning, pdf-books, pti, pubg. Raw extraction: team14_all_extracted.json; checkpoints: team14_verify_ckpt.jsonl.",
 "notes":f"77links.com was UP. First fetch: 2859 codes (28 pages HTTP 000); retry fetch recovered 21 of 28 pages, total 4254 codes. Fresh 1492, dup {len(allc)-len(fresh)}. Live check: HTTP 200 + non-empty og:title. Names prefer og:title, sanitized (phone numbers/emails stripped); directory label as fallback. Unverified fresh codes: {unverified}.",
}
json.dump(summary, open(os.path.join(WD,"team14-77links-summary.json"),'w'), ensure_ascii=False, indent=2)
print("verified",len(verified),"pending",len(pending),"dead",dead,"exclusions",len(exclusions),"unverified",unverified)
