import sys, json, os, time, re, html as h
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D)
import requests
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
ver=json.load(open(D+'/verified_draft.json'))
pend=json.load(open(D+'/pending_draft.json'))
codes_done={v['invite'].split('/')[-1] for v in ver}
def og_title(page):
    m=re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"',page) or re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:title"',page)
    return h.unescape(m.group(1)).strip() if m else ''
PORN=['porn','pornhub','xxx','nude','sex video','sexy','escort','call girl','fuck','dick','pussy','boobs','anal',
      '\U0001f975','\U0001f346','\U0001f351','\U0001f51e','\U0001f4a6','\U0001f445','\U0001f444','\U0001f48b']
MULE=['passcode','paypal loader','cashapp flip','money flip','counterfeit','cloned card','western union flip','doubled money']
def drop_reason(t):
    t=t.lower()
    if any(k in t for k in PORN): return 'porn'
    if any(k in t for k in MULE): return 'mule'
    return None
still=[]
for p in pend:
    code=p['invite'].split('/')[-1]
    if code in codes_done: continue
    try:
        r=requests.get(p['invite'],headers=UA,timeout=30)
        t=og_title(r.text)
        if r.status_code==429:
            print('RATE-LIMITED'); still.append(p); break
        if not t: print('DEAD',code); continue
        dr=drop_reason(t)
        if dr: print('DROPPED',dr,code); continue
        nm=t if len(t)>3 and 'whatsapp' not in t.lower() else p['name']
        ver.append({'name':nm,'category':p['category'],'country':'US','description':p['description'],'invite':p['invite'],'image':''})
        codes_done.add(code)
        print('OK',code,nm[:50])
    except Exception as e:
        print('STILL-PEND',code,str(e)[:60]); still.append(p)
    time.sleep(1.0)
json.dump(ver,open(D+'/verified_draft.json','w'),indent=1)
json.dump(still,open(D+'/pending_draft.json','w'),indent=1)
print('RESULT verified=%d still-pending=%d'%(len(ver),len(still)))
