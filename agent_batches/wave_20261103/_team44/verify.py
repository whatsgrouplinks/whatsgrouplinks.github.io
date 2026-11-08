import sys, json, os, time, re, html as h
D=os.path.dirname(os.path.abspath(__file__))
WAVE=os.path.dirname(D)
sys.path.insert(0,D)
from lib import code_of
import requests
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
union=set(json.load(open(WAVE+'/dedupe_union.json')))
cand=json.load(open(D+'/raw_candidates.json'))
seen=set(); queue=[]
for url,items in cand.items():
    if not items: continue
    for name,link in items:
        code=code_of(link)
        if not code: continue
        if code in union or code in seen: continue
        seen.add(code); queue.append((name,code,url))
print('to verify:',len(queue),flush=True)
PORN=['porn','pornhub','xxx','nude','sex video','sexy','escort','call girl','fuck','dick','pussy','boobs','anal',
      '\U0001f975','\U0001f346','\U0001f351','\U0001f51e','\U0001f4a6','\U0001f445','\U0001f444','\U0001f48b']
MULE=['passcode','paypal loader','cashapp flip','money flip','counterfeit','cloned card','western union flip','doubled money']
def drop_reason(t):
    t=t.lower()
    if any(k in t for k in PORN): return 'porn'
    if any(k in t for k in MULE): return 'mule'
    return None
CATS=[
 ('Crypto',['crypto','bitcoin','btc','ethereum','web3','defi','nft']),
 ('Finance',['invest','trading','forex','stock','share market','earn money','passive income']),
 ('Jobs',['job','vacancy','career','hiring','recruit','employment']),
 ('Gaming',['game','gaming','mlbb','free fire','pubg','ff ']),
 ('Sports',['sport','nba','football','cricket','soccer','nfl','basketball']),
 ('Education',['study','student','university','college','school','learn english','ielts','scholarship','exam','tuition']),
 ('News',['news','update','updates','breaking','headline']),
 ('Movies',['movie','film','cinema','netflix','series']),
 ('Music',['music','song','singer','dj']),
 ('Food',['food','recipe','cooking','restaurant']),
 ('Funny',['funny','meme','joke','comedy']),
 ('Girls',['girl','girls','women','ladies','bhabhi']),
 ('Health',['health','fitness','gym','yoga','diet','doctor']),
 ('Technology',['tech','technology','ai ','software','developer','coding','app ']),
 ('Travel',['travel','trip','tour','tourism','visit']),
 ('Pets',['pet','dog','cat','animal']),
 ('Islamic',['islam','muslim','quran','madrasa','deen']),
 ('Buy-Sell',['buy','sell','shop','store','market','business','startup','entrepreneur','real estate','rental','property','dropship']),
 ('Friendship',['friend','chat','social','people','zone','publics','fun ']),
 ('Community',['chicago','new york','georgia','california','texas','houston','miami','dallas','atlanta','america','usa','kenyan','city','local','community']),
]
DESCT={
 'Jobs':'A USA jobs WhatsApp group sharing job vacancies, hiring alerts, and career opportunities for job seekers across the United States.',
 'Gaming':'A gaming WhatsApp group for players in the USA to team up, share tips, and chat about popular mobile and online games.',
 'Sports':'A sports WhatsApp group for fans in the USA to discuss matches, scores, and sports news together.',
 'Education':'An education WhatsApp group for students in the USA to share study material, exam tips, and learning resources.',
 'News':'A news WhatsApp group sharing daily updates, headlines, and current events for readers in the USA.',
 'Movies':'A movies WhatsApp group for film lovers in the USA to discuss new releases, series, and entertainment.',
 'Music':'A music WhatsApp group for music fans in the USA to share songs, artists, and playlists.',
 'Food':'A food WhatsApp group for food lovers in the USA to exchange recipes, restaurant tips, and cooking ideas.',
 'Funny':'A funny WhatsApp group sharing memes, jokes, and comedy content for laughs with members across the USA.',
 'Girls':'A girls WhatsApp group for friendly chats, lifestyle topics, and social conversations with members in the USA.',
 'Health':'A health WhatsApp group sharing fitness tips, wellness advice, and healthy lifestyle ideas for members in the USA.',
 'Technology':'A technology WhatsApp group for tech enthusiasts in the USA to discuss gadgets, apps, and digital trends.',
 'Travel':'A travel WhatsApp group for travel lovers in the USA to share trip plans, destinations, and travel tips.',
 'Pets':'A pets WhatsApp group for animal lovers in the USA to share pet photos, care tips, and stories.',
 'Islamic':'An Islamic WhatsApp group for Muslims in the USA to share religious knowledge, reminders, and community updates.',
 'Buy-Sell':'A buy and sell WhatsApp group for trading, shopping deals, and business listings across the USA.',
 'Crypto':'A crypto WhatsApp group for members in the USA to discuss cryptocurrency, trading signals, and market news.',
 'Finance':'A finance WhatsApp group for members in the USA to share investment ideas, money tips, and market updates.',
 'Friendship':'A friendship WhatsApp group for making new friends, casual chats, and social fun with people across the USA.',
 'Community':'A community WhatsApp group for people in the USA to connect, share local updates, and chat together.',
 'Other':'A WhatsApp community group for members in the USA to connect and share conversations on shared interests.',
}
def cat_of(name):
    n=' '+name.lower()+' '
    for c,kw in CATS:
        if any(k in n for k in kw): return c
    return 'Other'
def og_title(page):
    m=re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"',page) or re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:title"',page)
    return h.unescape(m.group(1)).strip() if m else ''
verified=[]; pending=[]; porn=0; mule=0; dead=0
resume_after=0
for i,(name,code,src) in enumerate(queue):
    if i<resume_after: continue
    r=drop_reason(name)
    if r=='porn': porn+=1; continue
    if r=='mule': mule+=1; continue
    url='https://chat.whatsapp.com/'+code
    try:
        resp=requests.get(url,headers=UA,timeout=25)
        if resp.status_code==429:
            for j in range(i,len(queue)):
                n2,c2,s2=queue[j]
                if c2 not in [x['invite'].split('/')[-1] for x in verified]:
                    pending.append({'name':n2,'category':cat_of(n2),'country':'US',
                        'description':DESCT[cat_of(n2)],'invite':'https://chat.whatsapp.com/'+c2,'image':'','note':'rate-limited'})
            print('RATE-LIMITED at',i,flush=True); break
        t=og_title(resp.text)
        if not t: dead+=1; continue
        r2=drop_reason(t)
        if r2=='porn': porn+=1; continue
        if r2=='mule': mule+=1; continue
        c=cat_of(name); d=DESCT[c]
        nm=t if len(t)>3 and 'whatsapp' not in t.lower() else name
        verified.append({'name':nm,'category':c,'country':'US','description':d,'invite':url,'image':''})
        print('OK',i,code,nm[:50],flush=True)
    except Exception as e:
        pending.append({'name':name,'category':cat_of(name),'country':'US','description':DESCT[cat_of(name)],
            'invite':url,'image':'','note':'transport failure'})
        print('PEND',i,code,str(e)[:60],flush=True)
    time.sleep(0.7)
json.dump(verified,open(D+'/verified_draft.json','w'),indent=1)
json.dump(pending,open(D+'/pending_draft.json','w'),indent=1)
print('RESULT verified=%d pending=%d porn=%d mule=%d dead=%d'%(len(verified),len(pending),porn,mule,dead))
