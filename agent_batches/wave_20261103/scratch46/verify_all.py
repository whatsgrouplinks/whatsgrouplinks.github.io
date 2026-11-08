import requests, re, json, time, html as hm
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
BASE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/scratch46/'
fresh=json.load(open(BASE+'fresh1.json'))+json.load(open(BASE+'fresh2.json'))
done=json.load(open(BASE+'state.json')) if __import__('os').path.exists(BASE+'state.json') else {'done_codes':[],'verified':[],'pending':[],'flagged':[],'porn_drops':0,'ratelimited':False}
done_codes=set(done['done_codes'])
porn_re=re.compile(r'porn|pornhub|xxx|nude|sex\s*video|escort|call\s*girl|fuck|dick|pussy|boobs|anal|\U0001F975|\U0001F346|\U0001F351|\U0001F51E|\U0001F4A6|\U0001F445|\U0001F444|\U0001F48B', re.I)
scam_re=re.compile(r'passcode|loader|paypal\s*(receiver|loader)|counterfeit|fake\s*(currency|money|dollar)|money\s*mule|flashing\s*(software|usdt)|carding|cvv|dumps', re.I)
stop_flag={'v':False}
def check(f):
    code=f['code']; url='https://chat.whatsapp.com/'+code
    try:
        r=requests.get(url, headers=UA, timeout=25)
        if r.status_code==429:
            stop_flag['v']=True; return ('pending',f,'rate-limited')
        m=re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', r.text)
        title=hm.unescape(m.group(1)).strip() if m else ''
        if not title: return ('dead',f,'')
        txt=title+' '+f['name']
        if porn_re.search(txt): return ('porn',f,'')
        if scam_re.search(txt): return ('flagged',f,title)
        name=f['name'] if (f['name'] and not re.search(r'^(join|join now|click|link|here|join group)$',f['name'].strip(),re.I)) else title
        return ('verified',f,title,name)
    except Exception as e:
        return ('pending',f,'transport failure: '+type(e).__name__)
import threading
lock=threading.Lock()
todo=[f for f in fresh if f['code'] not in done_codes]
print('todo:',len(todo))
def worker(f):
    if stop_flag['v']: return
    kind,f2,extra, *rest = check(f)
    with lock:
        done['done_codes'].append(f2['code'])
        if kind=='verified': done['verified'].append({'code':f2['code'],'name':rest[0],'og:title':extra})
        elif kind=='pending': done['pending'].append({'code':f2['code'],'name':f2['name'],'note':extra})
        elif kind=='flagged': done['flagged'].append({'code':f2['code'],'og:title':extra})
        elif kind=='porn': done['porn_drops']+=1
        done['ratelimited']=stop_flag['v']
        json.dump(done,open(BASE+'state.json','w'))
    time.sleep(0.5)
with ThreadPoolExecutor(max_workers=5) as ex:
    ex.map(worker, todo)
print('DONE verified:',len(done['verified']),'pending:',len(done['pending']),'flagged:',len(done['flagged']),'porn:',done['porn_drops'],'ratelimited:',done['ratelimited'])
