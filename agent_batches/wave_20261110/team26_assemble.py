"""Assemble team26 outputs from verify jsonl files. Run after verification completes."""
import json, re, html, os
W='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110'
RAW=os.path.join(W,'team26_raw')
fresh=json.load(open(os.path.join(RAW,'team26_fresh_candidates.json')))
recs={}
for fn in ['team26_verify.jsonl','team26_verify2.jsonl','team26_verify3.jsonl','team26_verify4.jsonl']:
    p=os.path.join(RAW,fn)
    if not os.path.exists(p): continue
    for line in open(p):
        r=json.loads(line)
        # round2 overrides round1 pending
        if r['code'] not in recs or recs[r['code']]['status']=='pending':
            recs[r['code']]=r
print('verified records:', len(recs), 'of', len(fresh))
from collections import Counter
print(Counter(r['status'] for r in recs.values()))

BAD = [r'🔞', r'🥵', r'sexy', r'hookup', r'escort', r'porn', r'\bxxx\b', r'18\+',
       r's3x', r'ßex', r'video call girl', r'🍑', r'🍆', r'nude', r'naked',
       r'call girl', r'hot girl', r'sex ', r' sex', r'fuck', r'boobs', r'pussy',
       r'dick', r'onlyfans']
SCAM = ['b-love','forsage','shey','airdrop','paypal loader','bitfinex','counterfeit',
        'crypto-doubling','carding','double your','doubling','free money','earn $',
        'investment double','money doubling','payeer','perfect money doubler']
def screen(text):
    t=text.lower()
    for pat in BAD:
        if re.search(pat, t): return 'adult-sexual signal: '+pat
    for s in SCAM:
        if s in t: return 'scam signal: '+s
    return None

def clean_title(t):
    t=html.unescape(t or '').strip()
    t=re.sub(r'\s+',' ',t)
    return t

CATS = {
 'Islamic': ['islam','quran','allah','prophet','hadith','madina','makkah','mecca','mosque','prayer','ramadan','الله','اسلام','النبوة','أدعية','دعاء','الفرقان','الدعوة','قرآن','صلاة','مسجد','نبوة','محاضرات'],
 'Education': ['ieb','school','student','study','learn','exam','university','college','tutorial','education','academy','class','matric','grade','syllabus','teacher','lesson','دراسة','تعليم','مدرسة'],
 'Jobs': ['job','jobs','vacanc','employment','hiring','career','work ','وظائف','وظيفة'],
 'Sports': ['football','soccer','cricket','sport','bet','betting','match','premier league','fifa'],
 'Finance': ['forex','crypto','trading','invest','finance','money','business','earn'],
 'Buy Sell': ['buy','sell','shop','market','store','sale','property','cars for sale','house','بيع','متجر','وهميه','اسعار','جمله','تسوق'],
 'Entertainment': ['movie','music','fun','meme','comedy','entertain','video','song','drama'],
 'Funny': ['funny','joke','meme','laugh','comedy','نكت','مضحكه','ضحك'],
 'News': ['news','update','daily'],
 'Gaming': ['game','gaming','pubg','free fire'],
 'Technology': ['tech','ai ','chatgpt','gpt','computer','software','coding','crypto'],
 'Health': ['health','fitness','doctor','medical'],
 'Business': ['business','entrepreneur','trade','import','export'],
 'Community & Social': [],
}
def categorize(name, srcname):
    t=(name+' '+srcname).lower()
    for cat, kws in CATS.items():
        if cat=='Community & Social': continue
        if any(k in t for k in kws): return cat
    return 'Community & Social'

verified, pending, exclusions = [], [], []
dead=0
for code, r in sorted(recs.items()):
    if r['status']=='live':
        title=clean_title(r['og_title'])
        if len(re.sub(r'[^A-Za-z0-9\u0600-\u06FF]','',title)) < 2:
            title=''
        name=title or clean_title(r['name'])
        # screen og:title AND listing name
        why = screen(title) or screen(r['name'])
        if why:
            exclusions.append({'code':code,'reason':why+' | og_title='+title[:80]})
            continue
        if not name:
            exclusions.append({'code':code,'reason':'live but no usable name'})
            continue
        # country: keep source country; m3luma/elmostajadat are pan-Arab/Gulf -> SA default is weak;
        # use listing hints: m3luma groups are Arab-wide -> International unless name says Saudi/Gulf
        cc=r['country']
        low=name.lower()
        if r['source'] in ('m3luma','elmostajadat'):
            if any(k in low for k in ['saudi','السعود','سعودي']): cc='SA'
            elif any(k in low for k in ['egypt','مصر','مصري']): cc='EG'
            elif any(k in low for k in ['emarat','dubai','الإمارات','امارات']): cc='AE'
            elif any(k in low for k in ['qatar','قطر']): cc='QA'
            elif any(k in low for k in ['kuwait','الكويت']): cc='KW'
            elif any(k in low for k in ['oman','عمان']): cc='OM'
            elif any(k in low for k in ['bahrain','البحرين']): cc='BH'
            elif any(k in low for k in ['gulf','الخليج','خليج']): cc='SA'
            elif any(k in low for k in ['يمن','يماني','🇾🇪']): cc='YE'
            else: cc='International'
        cat=categorize(name, r['name'])
        # description: plain 1-2 sentences, no source name/link, no personal info
        if cc=='ZA':
            desc=f"A study group for {name}. Members share notes, past papers and exam help for South African learners."
        elif cat=='Education':
            desc=f"A study and learning group for {name}. Members share notes, study help and exam preparation."
        elif cat=='Jobs':
            desc=f"A jobs group for {name}. Members share vacancies, job news and work opportunities."
        elif cat=='Islamic':
            desc=f"An Islamic group for {name}. Members share Islamic lectures, reminders and prayers."
        elif cat=='Community & Social':
            desc=f"A community group for {name}. Members chat, share updates and connect with each other."
        else:
            art='An' if cat.lower()[0] in 'aeiou' else 'A'
            desc=f"{art} {cat.lower()} group for {name}. Members share updates and chat about {name}."
        verified.append({'name':name,'category':cat,'country':cc,'description':desc,
                         'invite':'https://chat.whatsapp.com/'+code})
    elif r['status']=='pending':
        pending.append({'code':code,'invite':'https://chat.whatsapp.com/'+code,
                        'reason':r.get('reason','transport failure'),'source':r['source'],
                        'name':clean_title(r['name'])})
    elif r['status']=='dead':
        dead+=1
# dedupe verified by code (already unique)
verified.sort(key=lambda x: (x['country'], x['name'].lower()))
json.dump(verified, open(os.path.join(W,'team26-newdirs-africa-mideast.json'),'w'), ensure_ascii=False, indent=1)
json.dump(pending, open(os.path.join(W,'team26-newdirs-africa-mideast-pending.json'),'w'), ensure_ascii=False, indent=1)
print('verified:', len(verified), 'pending:', len(pending), 'dead:', dead, 'exclusions:', len(exclusions))
for v in verified: print(' ', v['country'], v['category'], '|', v['name'][:60])
for e in exclusions: print('EXCL', e)
json.dump(exclusions, open(os.path.join(RAW,'team26_exclusions.json'),'w'), ensure_ascii=False, indent=1)
