import requests, re, time, json, html as htmllib
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
res=json.load(open('team03_resolve2_raw.json'))
union=set(json.load(open('dedupe_union.json')))
# already decided this run (verified live or dead, with retry)
LIVE={'HmYlSlyvv8DBA3gaWJs3as':'&#x1d406;&#x1d401; &#x1d405;&#x1d413; &#x1d402;&#x1d412; &#x1d401;&#x1d418; &#x1d40c;&#x1d414;&#x1d419;&#x1d404;&#x1d40d;&#x1d417;&#x1d411; [1]',
      'Exd1VD6TRS31e2FH8lbVJ2':'&#x645;&#x645;&#x644;&#x643;&#x647; &#x627;&#x644;&#x647;&#x628;&#x62f; &#x1f602;&#x1f91a;&#x1f3fb;'}
DEAD={'LdBaFKO5dpnA4fNx6K7NKY','DIxKZptcIO0EpOUbL1013u','EH30UyXvX6P2oBdxPv0Bf4','E33osfyL8Dr9c8DqF82ScG','FV9YPuHywJ4CC8lJGFwfs2'}
cands={}
for r in res:
    d=r['dest']
    m=re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})', d) or re.search(r'groupsor\.link/group/join/([A-Za-z0-9_-]{15,30})', d)
    if m:
        code=m.group(1)
        cands.setdefault(code, {'gids':[], 'titles':[]})
        cands[code]['gids'].append(r['gid'])
        cands[code]['titles'].append(r['title'])
todo=[c for c in cands if c not in union and c not in LIVE and c not in DEAD]
print('candidates to verify:', len(todo), '| skipped union:', sum(1 for c in cands if c in union),
      '| already live:', len([c for c in cands if c in LIVE]), '| already dead:', len([c for c in cands if c in DEAD]), flush=True)
def check(code):
    title=''; status=None; err=None
    for attempt in range(2):
        try:
            s=requests.Session(); s.headers.update(UA)
            r=s.get('https://chat.whatsapp.com/'+code, timeout=30)
            status=r.status_code
            m=re.search(r'property="og:title" content="([^"]*)"', r.text)
            title=m.group(1) if m else ''
            if title: break
            time.sleep(6)
        except Exception as e:
            err=repr(e)[:100]
            time.sleep(4)
    live = bool(title) and title.strip() not in ('WhatsApp Group','Join this group on WhatsApp')
    print(code, status, 'LIVE' if live else 'dead', repr(htmllib.unescape(title)[:70]) if title else '', err or '', flush=True)
    time.sleep(1)
    return {'code':code,'status':status,'og_title':htmllib.unescape(title) if title else '','live':live,'error':err}
results=[]
with ThreadPoolExecutor(max_workers=3) as ex:
    for res2 in ex.map(check, todo):
        results.append(res2)
for code,t in LIVE.items():
    if code in cands:
        results.append({'code':code,'status':200,'og_title':htmllib.unescape(t),'live':True,'error':None,'note':'verified earlier this run'})
json.dump({'results':results,'cands':{c:{'gids':v['gids'],'titles':v['titles']} for c,v in cands.items()}},
          open('team03_verify_raw.json','w'), ensure_ascii=False, indent=1)
print('DONE live:', sum(1 for r in results if r['live']), 'dead:', sum(1 for r in results if not r['live']))
