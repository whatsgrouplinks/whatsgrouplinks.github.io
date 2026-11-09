import json, subprocess, re, time, html, os
from concurrent.futures import ThreadPoolExecutor

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
todo=json.load(open('team19_to_verify.json'))
out_path='team19_verify.jsonl'
done=set()
if os.path.exists(out_path):
    for line in open(out_path):
        try: done.add(json.loads(line)['code'])
        except: pass
todo=[r for r in todo if r['code'] not in done]
print(f"to verify: {len(todo)} (already done: {len(done)})", flush=True)

def check(code):
    url=f"https://chat.whatsapp.com/{code}"
    title=''; status=0; attempts=0
    for attempt in range(3):
        attempts=attempt+1
        try:
            p=subprocess.run(['curl','-s','-m','25','-A',UA,'-w','\n%{http_code}',url],
                             capture_output=True, text=True, timeout=30)
            body, _, code_s = p.stdout.rpartition('\n')
            status=int(code_s.strip()) if code_s.strip().isdigit() else 0
            m=re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', body, re.I)
            if not m:
                m=re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', body, re.I)
            title=html.unescape(m.group(1)).strip() if m else ''
        except Exception as e:
            status=0; title=''
        if status==200 and title:
            break
        if status!=200 and status!=0:
            break  # 404/410 etc: dead, no retry needed for non-200
        time.sleep(2.5)  # retry spacing for empty-title / transport fail
    return {'code':code,'http':status,'og_title':title,'attempts':attempts}

results=[]
with ThreadPoolExecutor(max_workers=3) as ex:
    for i,res in enumerate(ex.map(check, [r['code'] for r in todo])):
        results.append(res)
        with open(out_path,'a') as f: f.write(json.dumps(res, ensure_ascii=False)+'\n')
        if (i+1)%25==0: print(f"  {i+1}/{len(todo)} done", flush=True)
print("verify pass complete", flush=True)
