import json, re, html as htmllib
from collections import Counter

ALLOWED=["Gaming","Education","Online Earning","Community & Social","Business","Friendship",
         "Finance","Buy Sell","Islamic","Entertainment","Jobs","Technology","Funny","Sports",
         "Health","News"]

# ---------- screening ----------
ADULT_RES=[
 r'\bporn\b', r'\bxxx\b', r'\bsex\b', r'\bsexy\b', r'\bhookup\b', r'\bescort\b',
 r'cam[\s\-]?girl', r'\bnude\b', r'\badult\b.*\b(video|pic|content|group)\b',
 r'\b(video|pic|photo)s?\b.*\b(adult|xxx|porn)\b',
 r'hot[\s\U0001F525\U0001F975]*\s*(video|videos|pics?|girls?|group)\b',
 r'\bdesi\s+(girls?|bhabhi|aunty)\b.*\b(hot|sexy|video)\b',
 r'\b(mms|leak(ed)?)\b.*\b(video|pic)\b',
]
SCAM_RES=[
 r'b[\s\-]?love\b', r'\bforsage\b', r'\bsheyi\b', r'\bairdrop\b',
 r'free\s+money\b', r'\bdouble\s+(your\s+)?money\b', r'\bdouble\s+(your\s+)?investment\b',
 r'\bearn\s+money\s+free\b', r'\bfree\s+earning\b.*\b(click|join|invest)\b',
 r'\bclick\s+and\s+earn\b', r'\bwatch\s+and\s+earn\b', r'\bcopy\s+paste\s+earn\b',
 r'\binvest\s+\d+\s*(rs|pkr|inr|usd)?\s*(and|&)?\s*(get|earn|receive)\b',
]
PROHIBIT_RES=[
 r'(inappropriate|adult|porn|xxx|sexy|nude|sexual)\s+(content|video|pic|material|post|link|image)[^.?!]*(share|send|post|upload|allow|not|na\s+karein|na\s+karen|mana|forbidden|prohibit)',
 r'(share|send|post|upload)[^.?!]*\b(not|na\s+karein|mana|forbidden)\b',
 r'no\s+(porn|xxx|sex|adult|nude|sexy)',
 r'galat\s+(content|video|pic)',
]

def strip_prohibitions(text):
    if not text: return text
    parts=re.split(r'(?<=[.!?])\s+', text)
    kept=[p for p in parts if not any(re.search(rx, p, re.I) for rx in PROHIBIT_RES)]
    return ' '.join(kept).strip()

def screen_fail(text):
    """return reason or None"""
    t=strip_prohibitions(text or '')
    for rx in ADULT_RES:
        if re.search(rx, t, re.I): return 'adult:'+rx
    for rx in SCAM_RES:
        if re.search(rx, t, re.I): return 'scam:'+rx
    return None

PHONE_RE=re.compile(r'(\+?\d[\d\s\-().]{7,}\d)')
URL_RE=re.compile(r'https?://\S+|www\.\S+')

def clean_text(t):
    if not t: return ''
    t=htmllib.unescape(t)
    t=URL_RE.sub('', t)
    t=PHONE_RE.sub('', t)
    t=re.sub(r'\s+', ' ', t).strip(' .,-')
    return t

# ---------- category ----------
CAT_KW=[
 ('Gaming', ['game','gaming','pubg','free fire','freefire','ludo','cricket game','psl','fifa','gamer']),
 ('Education', ['study','education','school','college','university','student','exam','test prep','css','learn english','english learn','ielts','academy','tuition','teacher','admission','scholarship','mcqs','notes' ]),
 ('Online Earning', ['earning','earn money','online earning','freelancing','fiverr','upwork','make money']),
 ('Business', ['business','marketing','promotion','youtube promotion','shop','store','resell','supplier','wholesale','amazon','dropship','brand']),
 ('Funny', ['funny','joke','jokes','meme','memes','comedy']),
 ('Friendship', ['friend','friendship','girls','chat with girls','dosti','shayari','poetry','status','masti','gupshup','timepass','chatting','fun time','fun zone']),
 ('Finance', ['forex','trading','trade','crypto','bitcoin','signals','stock','investment','finance','binance','ethereum','usdt','trader']),
 ('Buy Sell', ['buy','sell','buy sell','olx','purchase','iphone sell','real estate','property','plot','cars for sale']),
 ('Islamic', ['islam','islamic','quran','naat','hadees','hadith','muslim','allah','ramadan','dua','wazifa','madrasa']),
 ('Entertainment', ['movie','movies','drama','dramas','entertainment','music','song','video','status video','youtube','tiktok','funny video','web series','netflix','cricket news','live cricket']),
 ('Jobs', ['job','jobs','vacancy','hiring','career','employment','govt jobs','government jobs','bank jobs','police jobs','army jobs','work from home','delivery jobs']),
 ('Technology', ['tech','technology','software','computer','programming','developer','android']),
 ('Sports', ['cricket','football','sports','hockey','kabaddi','ipl','toss','match']),
 ('Health', ['health','doctor','medical','fitness','gym','yoga','beauty','skin','diet']),
 ('News', ['news','newspaper','headline','breaking','updates']),
]
def map_cat(raw, name, title, page):
    hay=' '.join(x for x in [raw or '', name or '', title or '', page or ''] if x).lower()
    for cat, kws in CAT_KW:
        for kw in kws:
            if kw in hay: return cat
    return 'Community & Social'

COUNTRY_KW=[
 ('Pakistan',['pakistan','pakistani','lahore','karachi','islamabad','punjabi','urdu','sindh']),
 ('India',['india','indian','hindi','delhi','mumbai']),
 ('USA',['usa','america','us ','united states']),
 ('UK',['uk ','united kingdom','london','england']),
 ('UAE',['dubai','uae','abu dhabi','emirates']),
 ('Saudi Arabia',['saudi']),
 ('Bangladesh',['bangladesh','bangladeshi']),
 ('Sri Lanka',['sri lanka','sri-lanka']),
 ('Nigeria',['nigeria','nigerian']),
 ('Kenya',['kenya','kenyan']),
 ('Malaysia',['malaysia','malaysian']),
 ('Indonesia',['indonesia','indonesian']),
 ('Tanzania',['tanzania','tanzanian']),
 ('Canada',['canada','canadian']),
 ('Australia',['australia','australian']),
 ('Turkey',['turkey','turkish']),
 ('Nepal',['nepal','nepali']),
 ('South Africa',['south africa']),
]
ISO={'Pakistan':'PK','India':'IN','USA':'US','UK':'GB','UAE':'AE','Saudi Arabia':'SA',
     'Bangladesh':'BD','Sri Lanka':'LK','Nigeria':'NG','Kenya':'KE','Malaysia':'MY',
     'Indonesia':'ID','Tanzania':'TZ','Canada':'CA','Australia':'AU','Turkey':'TR',
     'Nepal':'NP','South Africa':'ZA'}
def guess_country(name, title, page, rawcat):
    hay=' '.join(x for x in [name or '', title or '', page or ''] if x).lower()
    for cname, kws in COUNTRY_KW:
        for kw in kws:
            if re.search(r'(?<![a-z])'+re.escape(kw.strip())+r'(?![a-z])', hay): return ISO[cname]
    # groupjoin country pages
    m=re.search(r'/country/([a-z\-]+)', page or '')
    if m:
        slug=m.group(1).replace('-',' ')
        for cname, kws in COUNTRY_KW:
            if cname.lower()==slug: return ISO[cname]
    return 'IN'

DESC_TEMPLATES={
 'Gaming':'A WhatsApp gaming group where players chat, share tips and team up for matches.',
 'Education':'A WhatsApp study group for students to share notes, exam updates and learning resources.',
 'Online Earning':'A WhatsApp group for sharing online earning ideas, tips and opportunities.',
 'Business':'A WhatsApp business group for networking, promotions and business updates.',
 'Friendship':'A friendly WhatsApp group to chat, make new friends and share fun posts.',
 'Finance':'A WhatsApp group for trading signals, market updates and finance discussions.',
 'Buy Sell':'A WhatsApp buy and sell group for posting deals, products and offers.',
 'Islamic':'A WhatsApp Islamic group for sharing Quranic reminders, naats and Islamic knowledge.',
 'Entertainment':'A WhatsApp entertainment group for movies, dramas, music and fun videos.',
 'Jobs':'A WhatsApp jobs group for sharing vacancies, hiring updates and career news.',
 'Technology':'A WhatsApp technology group for tech news, tips and gadget discussions.',
 'Funny':'A WhatsApp funny group for jokes, memes and comedy videos to brighten your day.',
 'Sports':'A WhatsApp sports group for match updates, scores and sports discussions.',
 'Health':'A WhatsApp health group for fitness tips, wellness advice and healthy living.',
 'News':'A WhatsApp news group for daily headlines and the latest updates.',
 'Community & Social':'A WhatsApp community group to chat, share updates and connect with members.',
}

def main():
    res={}
    for ln in open('team06_raw/verify_results.jsonl'):
        r=json.loads(ln); res.setdefault(r['code'],[]).append(r)
    ctx=json.load(open('team06_raw/ctx.json'))
    last={c:v[-1] for c,v in res.items()}
    live=[c for c,v in last.items() if v['final']=='live']
    ambig=[c for c,v in last.items() if v['final']=='ambig']
    pend=[c for c,v in last.items() if v['final']=='pending']
    print(f"live={len(live)} ambig={len(ambig)} pending={len(pend)}")
    cands=[]; dropped=[]
    for code in sorted(live):
        title=last[code].get('title') or ''
        c=ctx.get(code, {})
        ctxname=c.get('name') or ''
        # clean og:title first; junk titles ('.', bare URLs/domains, phone-like) fall back to listing name
        tclean=clean_text(title.strip())
        if not tclean or re.fullmatch(r'[.\-_,!]+', tclean) or re.match(r'^\+?[\d\s.\-()]{6,}$', tclean):
            name=ctxname
        else:
            name=tclean
        if not name:
            dropped.append((code,'no-name')); continue
        name=clean_text(name)
        if not name:
            dropped.append((code,'no-name-after-clean')); continue
        if len(name)>90: name=name[:90].rsplit(' ',1)[0]
        rawcat=c.get('cat') or ''
        desc_raw=c.get('desc') or ''
        desc=clean_text(strip_prohibitions(desc_raw))
        hay=f"{name} {title} {desc}"
        fail=screen_fail(hay)
        if fail:
            dropped.append((code,fail)); continue
        cat=map_cat(rawcat, name, title, c.get('page',''))
        if cat not in ALLOWED: cat='Community & Social'
        if not desc:
            desc=DESC_TEMPLATES[cat]
        else:
            # keep 1-2 sentences, cap length
            sents=re.split(r'(?<=[.!?])\s+', desc)
            desc=' '.join(sents[:2])[:280]
            if not desc.endswith(('.', '!', '?')): desc+='.'
        if len(desc)<15:
            desc=DESC_TEMPLATES[cat]
        country=guess_country(name, title, c.get('page',''), rawcat)
        cands.append({'name':name,'category':cat,'country':country,
                      'description':desc,'invite':f'https://chat.whatsapp.com/{code}'})
    print(f"candidates={len(cands)} dropped={len(dropped)}")
    print("drop reasons:", Counter(r.split(':')[0] for _,r in dropped))
    print("categories:", Counter(x['category'] for x in cands))
    print("countries:", Counter(x['country'] for x in cands))
    json.dump(cands, open('team06-candidates.json','w'), ensure_ascii=False, indent=1)
    json.dump([{'code':c,'http':last[c].get('http'),'attempts':len(res[c]),
                'last_attempt':last[c].get('attempt')} for c in sorted(pend)],
              open('team06-pending.json','w'), ensure_ascii=False, indent=1)
    json.dump({'live':len(live),'ambig':len(ambig),'pending':len(pend),
               'candidates':len(cands),'dropped':len(dropped),
               'drop_sample':dropped[:20]}, open('team06_raw/format_stats.json','w'), ensure_ascii=False, indent=1)
    print("sample candidates:")
    for x in cands[:5]: print(" ", x)

if __name__=='__main__':
    main()
