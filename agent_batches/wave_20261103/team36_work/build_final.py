import json, re, html

WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103'
work=WAVE+'/team36_work'
union=set(json.load(open(WAVE+'/dedupe_union.json')))

def pick_name(page_name, og_title):
    t=(og_title or '').strip()
    t=re.sub(r'\s+',' ',t)
    # strip leading decorative emoji/buttons that are clearly not part of the name
    t=re.sub(r'^[🈸🏆🔥✅⭐★💫‼️❗\s]+','',t).strip()
    if t:
        return t[:90]
    return page_name[:90]

def desc_for(name, cat):
    n=name.lower()
    hints={
      'News': f"Stay updated with this Indian WhatsApp group for {name.strip()} - daily news headlines, breaking updates and current affairs for members across India.",
      'Education': f"Join this Indian WhatsApp study group for {name.strip()} - exam preparation material, study notes and learning discussions for students in India.",
      'Jobs': f"Indian WhatsApp jobs group for {name.strip()} - job alerts, vacancies and employment updates shared daily for job seekers in India.",
      'Buy-Sell': f"Indian WhatsApp shopping group for {name.strip()} - deals, product listings and buy-sell offers for members across India.",
      'Community': f"Indian WhatsApp community group for {name.strip()} - connect, chat and share updates with people from India.",
      'Other': f"Active Indian WhatsApp group for {name.strip()} - join the conversation and connect with members from India.",
    }
    return hints.get(cat, hints['Other'])

# (page_name, code, og_title, category)
items=[]
def add(page_name, code, og_title, category):
    name=pick_name(page_name, og_title)
    if code in union: return
    items.append({'name':name,'category':category,'country':'IN',
                  'description':desc_for(name,category),
                  'invite':'https://chat.whatsapp.com/'+code,'image':''})

add('बिहार न्यूज पेपर 13','GcE5LUFYneFLvDEltzQ4c3','बिहार न्यूज पेपर  13','News')
add('राजस्थान शिक्षा समाचार 1','L7nQzxbuI2q6MdY5sda3HF','🈸राजस्थान शिक्षा समाचार1️⃣','Education')
add('PRINTING & PACKAGING NCR WORK','EAUCM7ssVVhCYuQ94gJM4v','PRINTING & PACKAGING','Jobs')
add('विजय पथ सेना (उत्तर प्रदेश)','FRUNW4uZqXNIWvLTFY9cyh','विजय पथ सेना (उत्तर प्रदेश)','Community')
add('UPP Target 2026','ElqiRyKPyIV3MO3x0zHPHq','UPP Target 🎯 2026','Education')
add('RONIS KING','K0pj5dd5G7K0at6E4LFDZy','RONIS KING','Other')
add('SHOP WELL','IYNDSBfV1ZK6vi732aP9U9','SHOP WELL','Buy-Sell')
add('online king','IxjLQ6ze1NG8IbqXqAUQTA','╰•★★  ơŋƖıŋɛ ƙıŋɠ ★★•╯','Other')

# Hindi post verified results (verify6.json) - category hints
v6=json.load(open(work+'/verify6.json'))
catmap={
 'IaDONjVaRKOKcyDXTD4cC2':'Other',   # Hindi BF Indian
 'BmJ4v3bcR0aAlXnaD8Xrxw':'Entertainment',  # Hindi status video
 'LozWZWowvhTDJtWVX1wy8P':'Education',  # ebooks
 'KJ1l1K5T51s2j9VwpUWgJt':'Entertainment',  # stickers for whatsapp
 'FDZNnRPfFatI3xtLNnMMF9':'Friendship',  # Indian group
 'GLh75eJr6Oy1rsfCtgrHJ0':'Music',    # Hindi new song
 'LcZ1eth9PuhEeg3Tvlys51':'Education',  # translation
 'Euwzn7gwMnx1SAs1GkuP99':'Education',  # sahitya
 'Hkdkjl7aMtaCJ2UpZKbDNX':'Education',  # sahitya parishad
 'B6gz6DkuRIiJo8nUSUcwCX':'Education',  # kavya peeth
 'HG9IA0H6jHDFEXMTAec2EU':'Education',  # sahitya parishad
 'IkaSLZnCOVD7UHUT4LA4Gy':'Finance',  # money making
 'BZloEy5vwL5EYYMf3BBenh':'Finance',  # IPO SIP investment
}
porn=0
for r in v6:
    title=r.get('title','')
    if not title: continue  # dead
    if r.get('note'): continue
    code=r['code']
    low=title.lower()
    if any(k in low for k in ['porn','pornhub','xxx','nude','sex video','escort','call girl','fuck','dick','pussy','boobs','anal']) or re.search(r'\bsex\b',low) or any(e in title for e in ['🥵','🍆','🍑','🔞','💦','👅','👄','💋']):
        porn+=1; continue
    cat=catmap.get(code,'Other')
    add(r['name'],code,title,cat)

seen=set(); out=[]
for it in items:
    code=it['invite'].rsplit('/',1)[-1]
    if code in seen: continue
    seen.add(code); out.append(it)

json.dump(out,open(WAVE+'/team36-india.json','w'),ensure_ascii=False,indent=1)
print('verified items:',len(out),'porn dropped in v6:',porn)

# pending: transport failure
pend=[{'name':'India (Bharat)','category':'Community','country':'IN',
       'description':'Active Indian WhatsApp community group for India (Bharat) members to chat and connect.','invite':'https://chat.whatsapp.com/Lo6ZCycBr0UCRrJvQIe0Mx','image':'','note':'transport failure'}]
json.dump(pend,open(WAVE+'/team36-unverified-pending.json','w'),ensure_ascii=False,indent=1)
print('pending:',len(pend))
