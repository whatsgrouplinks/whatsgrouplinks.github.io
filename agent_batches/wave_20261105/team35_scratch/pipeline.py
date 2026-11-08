#!/usr/bin/env python3
"""team35 pipeline (resume-safe): igrupos tag harvest -> detail -> dedupe/filter -> verify.
Checkpoints live in team35_scratch/ so a VM reboot loses at most one batch."""
import requests, re, html as ihtml, json, time, random, os, sys
from concurrent.futures import ThreadPoolExecutor
W='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105/'
S=W+'team35_scratch/'
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
MAIN=['aesthetic','amistad','amor','anime','arte','bailar-salsa','compra-venta','emprendimiento',
 'free-fire','futbol','gamers','gays','humor','instagram','juegos','juegos-online','k-pop','lesbianas',
 'libros','memes','minecraft','mujeres','musica','negocios','otakus','peliculas','rol','roleplay',
 'running','solteros','stickers','trans']
EXTRA=['amigas','amigos','army','armys','blackpink','boku-no-hero','busco-novia','chicas','chicos',
 'de-todo','disney','dragon-ball','encuentros','femboy','humor-negro','hype','hype-group','infieles',
 'karmaland','kpop','lbgt','lgbtq','literatura','mobile-legends','netflix','osos','pubg','reggaeton',
 'seguidores','shitpost','shitposting','solteras','stray-kids','tinder','todo','transexuales','traps',
 'trapitos','zoom']
ALL_TAGS=MAIN+EXTRA
CAT={'aesthetic':'Entertainment','amistad':'Friendship','amor':'Friendship','anime':'Entertainment',
 'arte':'Entertainment','bailar-salsa':'Entertainment','compra-venta':'Buy & Sell','emprendimiento':'Business',
 'free-fire':'Gaming','futbol':'Sports','gamers':'Gaming','gays':'Friendship','humor':'Funny',
 'instagram':'Community & Social','juegos':'Gaming','juegos-online':'Gaming','k-pop':'Entertainment',
 'lesbianas':'Friendship','libros':'Education','memes':'Funny','minecraft':'Gaming','mujeres':'Friendship',
 'musica':'Entertainment','negocios':'Business','otakus':'Entertainment','peliculas':'Movies',
 'rol':'Gaming','roleplay':'Gaming','running':'Sports','solteros':'Friendship','stickers':'Funny','trans':'Friendship',
 'amigas':'Friendship','amigos':'Friendship','army':'Entertainment','armys':'Entertainment',
 'blackpink':'Entertainment','boku-no-hero':'Entertainment','busco-novia':'Friendship','chicas':'Friendship',
 'chicos':'Friendship','de-todo':'Entertainment','disney':'Entertainment','dragon-ball':'Entertainment',
 'encuentros':'Friendship','femboy':'Friendship','humor-negro':'Funny','hype':'Community & Social',
 'hype-group':'Community & Social','infieles':'Friendship','karmaland':'Gaming','kpop':'Entertainment',
 'lbgt':'Friendship','lgbtq':'Friendship','literatura':'Education','mobile-legends':'Gaming',
 'netflix':'Movies','osos':'Friendship','pubg':'Gaming','reggaeton':'Entertainment','seguidores':'Community & Social',
 'shitpost':'Funny','shitposting':'Funny','solteras':'Friendship','stray-kids':'Entertainment',
 'tinder':'Friendship','todo':'Entertainment','transexuales':'Friendship','traps':'Friendship',
 'trapitos':'Friendship','zoom':'Entertainment'}
TOPIC={'aesthetic':'aesthetic and lifestyle','amistad':'friendship','amor':'love and romance','anime':'anime',
 'arte':'art and creativity','bailar-salsa':'salsa dancing','compra-venta':'buying and selling','emprendimiento':'entrepreneurship',
 'free-fire':'Free Fire','futbol':'football','gamers':'gaming','gays':'gay friendship','humor':'humor and jokes',
 'instagram':'Instagram growth','juegos':'games','juegos-online':'online games','k-pop':'K-pop',
 'lesbianas':'lesbian friendship','libros':'books and reading','memes':'memes','minecraft':'Minecraft',
 'mujeres':'women friendship','musica':'music','negocios':'business','otakus':'otaku culture',
 'peliculas':'movies and series','rol':'roleplay games','roleplay':'roleplay','running':'running and fitness',
 'solteros':'singles and dating','stickers':'stickers','trans':'trans friendship',
 'amigas':'girls friendship','amigos':'friendship','army':'BTS ARMY','armys':'BTS ARMY','blackpink':'BLACKPINK',
 'boku-no-hero':'My Hero Academia','busco-novia':'dating','chicas':'girls friendship','chicos':'friendship',
 'de-todo':'mixed topics','disney':'Disney','dragon-ball':'Dragon Ball','encuentros':'meetups and dating',
 'femboy':'femboy community','humor-negro':'dark humor','hype':'Instagram hype groups','hype-group':'Instagram hype groups',
 'infieles':'dating','karmaland':'Karmaland','kpop':'K-pop','lbgt':'LGBT friendship','lgbtq':'LGBTQ friendship',
 'literatura':'literature','mobile-legends':'Mobile Legends','netflix':'Netflix','osos':'gay bears community',
 'pubg':'PUBG','reggaeton':'reggaeton','seguidores':'gaining followers','shitpost':'shitposting and memes',
 'shitposting':'shitposting and memes','solteras':'single women and dating','stray-kids':'Stray Kids',
 'tinder':'dating','todo':'mixed topics','transexuales':'trans friendship','traps':'femboy and trans community',
 'trapitos':'femboy and trans community','zoom':'Zoom meetups'}
def log(*a): print(*a, flush=True)
def clean(s): return re.sub(r'\s+',' ',ihtml.unescape(re.sub(r'<[^>]+>',' ',s or ''))).strip()
def fetch(url, timeout=40):
    for _ in range(2):
        try:
            r=requests.get(url, headers=UA, timeout=timeout)
            if r.status_code==200: return r.text
        except Exception: time.sleep(2)
    return ''
def parse_cards(h):
    out=[]
    for m in re.finditer(r'<article id="grupo-(\d+)"[^>]*>(.*?)</article>', h, re.S):
        gid, block = m.group(1), m.group(2)
        t=re.search(r'class="group-title"[^>]*>(.*?)</', block, re.S)
        d=re.search(r'class="group-description"[^>]*>(.*?)</p>', block, re.S)
        flag=re.search(r'images/banderas24/([A-Z]{2})\.png', block)
        out.append({'gid':gid,'title':clean(t.group(1)) if t else '','desc':clean(d.group(1)) if d else '',
                    'flag':flag.group(1) if flag else ''})
    return out
# ---- Stage A: tag cards ----
if os.path.exists(S+'tag_cards.json'):
    all_cards=json.load(open(S+'tag_cards.json')); log('A: resume tag_cards', sum(len(v) for v in all_cards.values()))
else:
    def one_tag(tag):
        h=fetch(f'https://www.igrupos.com/tag/whatsapp/{tag}')
        cards=parse_cards(h) if h else []
        for c in cards: c['tag']=tag
        return tag, cards
    all_cards={}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for tag, cards in ex.map(one_tag, ALL_TAGS):
            all_cards[tag]=cards; log('A:', tag, len(cards))
    json.dump(all_cards, open(S+'tag_cards.json','w'), ensure_ascii=False)
    log('A TOTAL cards:', sum(len(v) for v in all_cards.values()))
flat={}
for tag, cs in all_cards.items():
    for c in cs: flat.setdefault(c['gid'], c)
flat=list(flat.values())
log('A unique gids:', len(flat))
# ---- Stage B: detail fetch (checkpoint every 100) ----
done={}
if os.path.exists(S+'detail_ckpt.json'):
    done={d['gid']: d for d in json.load(open(S+'detail_ckpt.json'))}
    log('B: resume detail ckpt', len(done))
todo=[c for c in flat if c['gid'] not in done]
def detail(c):
    for _ in range(2):
        try:
            r=requests.get(f"https://www.igrupos.com/grupo/{c['gid']}", headers=UA, timeout=35)
            if r.status_code==200:
                h=r.text
                if 'chat.whatsapp.com/invite/' in h: return {**c,'code':'','note':'channel/invite-format'}
                codes=re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', h)
                if 'chat.whatsapp.com/channel/' in h: return {**c,'code':'','note':'channel'}
                return {**c,'code':codes[0] if codes else '','note':''}
        except Exception: time.sleep(1)
    return {**c,'code':'','note':'fetch-fail'}
if todo:
    with ThreadPoolExecutor(max_workers=12) as ex:
        for i,res in enumerate(ex.map(detail, todo)):
            done[res['gid']]=res
            if (i+1)%100==0:
                json.dump(list(done.values()), open(S+'detail_ckpt.json','w'), ensure_ascii=False)
                log('B:', len(done), 'with code:', sum(1 for x in done.values() if x['code']))
    json.dump(list(done.values()), open(S+'detail_ckpt.json','w'), ensure_ascii=False)
out=list(done.values())
log('B total:', len(out), 'with code:', sum(1 for x in out if x['code']))
# ---- Stage C: dedupe + filter ----
union=set(json.load(open(W+'dedupe_union.json')))
extra_ban=set()
for f in ['team24-ongrupos-slices.json','team25-igrupos-ongrupos-new.json']:
    try:
        d=json.load(open(W+f))
        for x in d:
            m=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', x.get('invite',''))
            if m: extra_ban.add(m.group(1))
    except Exception as e: log('ban load', f, repr(e)[:80])
log('C: extra-ban codes (team24/25):', len(extra_ban))
uniq={}
for x in out:
    if x['code']: uniq.setdefault(x['code'], x)
fresh=[x for x in uniq.values() if x['code'] not in union and x['code'] not in extra_ban]
log('C: unique codes:', len(uniq), 'fresh:', len(fresh), 'dupes:', len(uniq)-len(fresh))
DROP_EXTRA={'HNLoAL1yA9WLPPM99YGOVZ':'minors 17-30 + dating','D84UpYQd3QlBFIqblcEWyW':'sexualised femboy-thighs fan group',
 'LNuTm9tnf1E0j168SgXAFP':'explicit masturbation videocalls','LdDmZgoXIbR1dCuRpK8z6B':'sexually explicit title Femboys hots',
 'GmeXytpm3juIjXcI8HMOWp':'explicit sexual hookup text','J6p5GtrLcNBDRdEC6k917U':'sexually explicit title Femboys hot',
 'EOTXonoNq2F0cKIn8YmbhO':'porn group (desc: Grupo de porno trans)','K4NcEuiYzeFE2bR2SrUqMr':'explicit masturbation text',
 'J1DOqCOpIl2B7qYllFbzGk':'explicit sexual text','EFzRYiSrdMiIoIqZrHYxFo':'adult erotic roleplay (Palacio de la lujuria)',
 'FGx22lOtjgJ9myTdsToYDH':'paid-girls money setup','I0vnzt8n85PKvFbja8U7V5':'minors 15-18 truth-or-dare',
 'B5UnA9dLIlq1kyljM6H0kD':'personal ad: personal name + phone number in listing'}
PORN_WORDS=['porno','porn','xxx','hentai','onlyfans','xvideos','redtube','brazzers','putaria','pelada',
 'novinha','novinhas','nudes','nude','sexo','sex video','escort','caliente','tetas','pene','vagina',
 'desnudo','desnuda','erótico','erotico','erotic','pornô','pornografia','chupar','mamada','paja',
 'polla','gemidos','lujuria','futanari','shemale']
STEMS=[r'masturb', r'\bcog[eéi]', r'\bfoll(o|as|a|amos|an|ar|ando|ado|arse)\b']
SCAM=['hyip','crypto pump','pump signal','money mule','counterfeit','satta','matka','forex signals',
 'double your money','dinero facil','dinero fácil','gana dinero rapido','ganar dinero rápido',
 'inversion garantizada','rentabilidad garantizada','venta de droga','documentos falsos','clonar tarjetas',
 'tarjetas clonadas','cocaina','cocaína','marihuana']
NEG=r'(prohibid[oa]s?|no se permite|no se permiten|sin |no |nada de |queda prohibido|está prohibido|esta prohibido|❌|🚫)'
def wb(t,w): return re.search(r'(?<![a-záéíóúñ])'+re.escape(w)+r'(?![a-záéíóúñ])', t)
def adult_purpose(title, desc):
    t=title.lower(); d=desc.lower()
    for w in PORN_WORDS+['packs','hot']:
        m=wb(t,w)
        if m:
            if re.search(r'\b(no|sin)\s*$', t[max(0,m.start()-12):m.start()]): continue
            return 'porn-title:'+w
    for w in PORN_WORDS+['packs']:
        for m in re.finditer(r'(?<![a-záéíóúñ])'+re.escape(w)+r'(?![a-záéíóúñ])', d):
            if re.search(NEG, d[max(0,m.start()-45):m.start()]): continue
            return 'porn-desc:'+w
    for s in STEMS:
        for m in re.finditer(s, d):
            if re.search(NEG, d[max(0,m.start()-45):m.start()]): continue
            return 'porn-desc-stem:'+s
        m=re.search(s, t)
        if m: return 'porn-title-stem:'+s
    if re.search(r'vendo (mi )?contenido', d): return 'selling adult content'
    return None
def scam_hit(title, desc):
    t=(title+' '+desc).lower()
    for w in SCAM:
        for m in re.finditer(re.escape(w), t):
            if re.search(NEG, t[max(0,m.start()-45):m.start()]): continue
            return 'scam:'+w
    return None
def minor_hit(title, desc):
    t=(title+' '+desc).lower()
    if re.search(r'edad de 1[3-7]\b', t) and re.search(r'pareja|novio|novia|citas|ligar|conocer gente', t): return 'minors-age-range'
    if re.search(r'(solo )?(gente|personas|chicos|chicas) de 1[3-7]\b', t): return 'minors-age-range'
    return None
kept, dropped=[], []
for x in fresh:
    title=x.get('title') or ''; desc=x.get('desc') or ''
    why = DROP_EXTRA.get(x['code']) or adult_purpose(title, desc) or scam_hit(title, desc) or minor_hit(title, desc)
    if not why and re.match(r'^(https?://|www\.)', title.strip(), re.I): why='name-is-url'
    if why: dropped.append({'code':x['code'],'name':title,'tag':x.get('tag'),'reason':why})
    else: kept.append(x)
log('C kept:', len(kept), 'dropped:', len(dropped))
from collections import Counter
log('C drop reasons:', dict(Counter(d['reason'] for d in dropped)))
json.dump(kept, open(S+'kept.json','w'), ensure_ascii=False)
json.dump(dropped, open(S+'dropped.json','w'), ensure_ascii=False)
# ---- Stage D: build records + verify with checkpoints ----
def build(k, i):
    topic=TOPIC[k['tag']]; name=(k.get('title') or '').strip()
    tpls=[
      f"Join {name}, a WhatsApp group for {topic} lovers to chat, share and make new friends. Meet people who love {topic} and join the conversation every day.",
      f"{name} is a WhatsApp group about {topic}. Chat with members, share {topic} content and make new friends in a friendly community.",
      f"Looking for a WhatsApp group about {topic}? Join {name} to meet new people, share ideas and enjoy daily chats about {topic}.",
    ]
    return {'name':name,'category':CAT[k['tag']],'country':k.get('flag') or 'International',
            'description':tpls[i % 3],'invite':'https://chat.whatsapp.com/'+k['code'],'image':''}
recs=[build(k,i) for i,k in enumerate(kept)]
codes=[k['code'] for k in kept]
json.dump(recs, open(S+'recs.json','w'), ensure_ascii=False)
H={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
def og(code):
    for attempt in range(2):
        try:
            time.sleep(random.uniform(0.5,2.0))
            r=requests.get(f'https://chat.whatsapp.com/{code}', headers=H, timeout=25)
            if r.status_code==429:
                time.sleep(120); continue
            body=r.text or ''
            m=re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', body)
            t=ihtml.unescape(m.group(1)).strip() if m else ''
            return code, ('live' if t else 'empty'), t
        except Exception:
            time.sleep(5)
    return code, 'error', ''
v_done={}
if os.path.exists(S+'verify_ckpt.json'):
    for v in json.load(open(S+'verify_ckpt.json')): v_done[v['code']]=v
    log('D: resume verify ckpt', len(v_done))
todo_idx=[i for i,c in enumerate(codes) if c not in v_done]
log('D: to verify:', len(todo_idx), 'of', len(codes))
def work(i):
    c, st, title = og(codes[i])
    return i, c, st, title
if todo_idx:
    with ThreadPoolExecutor(max_workers=4) as ex:
        for n,(i,c,st,title) in enumerate(ex.map(work, todo_idx)):
            v_done[c]={'code':c,'status':st,'og_title':title,'rec_idx':i}
            if (n+1)%25==0:
                json.dump(list(v_done.values()), open(S+'verify_ckpt.json','w'), ensure_ascii=False)
                lv=sum(1 for v in v_done.values() if v['status']=='live')
                log('D:', len(v_done), 'live:', lv, 'pending:', len(v_done)-lv)
    json.dump(list(v_done.values()), open(S+'verify_ckpt.json','w'), ensure_ascii=False)
verified=[recs[v['rec_idx']] for v in v_done.values() if v['status']=='live']
pending=[{'code':v['code'],'name':recs[v['rec_idx']]['name'],
          'note':'empty og:title (dead/expired)' if v['status']=='empty' else 'verification transport error/rate-limited'}
         for v in v_done.values() if v['status']!='live']
log('D DONE verified:', len(verified), 'pending:', len(pending))
json.dump(verified, open(W+'team35-new-tags.json','w'), ensure_ascii=False)
json.dump(pending, open(W+'team35-unverified-pending.json','w'), ensure_ascii=False)
log('WROTE team35-new-tags.json + team35-unverified-pending.json')
