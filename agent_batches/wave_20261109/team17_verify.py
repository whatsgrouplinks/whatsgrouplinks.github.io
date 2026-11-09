import json, re, subprocess, time, html, os
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
pool=json.load(open('team17_verify_pool.json'))
codes=list(pool.keys())
def check(code):
    url=f"https://chat.whatsapp.com/{code}"
    for attempt in range(3):
        p=subprocess.run(['curl','-s','-L','--max-time','25','-A',UA,'-w','\n%{http_code}',url],
                         capture_output=True,text=True)
        out=p.stdout
        lines=out.rsplit('\n',1)
        body=lines[0] if len(lines)>1 else out
        try: status=int(lines[1].strip())
        except: status=0
        m=re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"',body)
        title=html.unescape(m.group(1)).strip() if m else ''
        m2=re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"',body)
        desc=html.unescape(m2.group(1)).strip() if m2 else ''
        if status==200 and title:
            return {'code':code,'status':status,'title':title,'description':desc,'attempts':attempt+1,'verdict':'live'}
        if status==200 and not title:
            if attempt<2:
                time.sleep(4); continue
            return {'code':code,'status':status,'title':'','description':desc,'attempts':3,'verdict':'ambiguous-empty-title'}
        if status in (0,429,403,500,502,503):
            if attempt<2:
                time.sleep(5); continue
            return {'code':code,'status':status,'title':title,'description':desc,'attempts':3,'verdict':'transport-failed'}
        return {'code':code,'status':status,'title':title,'description':desc,'attempts':attempt+1,'verdict':'dead'}
    return {'code':code,'status':0,'title':'','description':'','attempts':3,'verdict':'transport-failed'}
results={}
for i,c in enumerate(codes):
    r=check(c)
    results[c]=r
    if (i+1)%25==0: print(f"{i+1}/{len(codes)} live={sum(1 for v in results.values() if v['verdict']=='live')} dead={sum(1 for v in results.values() if v['verdict']=='dead')} amb={sum(1 for v in results.values() if v['verdict']=='ambiguous-empty-title')} fail={sum(1 for v in results.values() if v['verdict']=='transport-failed')}",flush=True)
    if i < len(codes)-1: time.sleep(0.7)
json.dump(results,open('team17_verify_raw.json','w'),ensure_ascii=False,indent=1)
from collections import Counter
print(Counter(v['verdict'] for v in results.values()))
print('done',len(results))
