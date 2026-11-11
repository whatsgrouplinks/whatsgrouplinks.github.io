import json, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor
# 12 fresh codes: first 6 + the 2 Nov-10 cross-checked + 4 spread through the list
fresh=json.load(open('team21-fresh-codes.json'))
sample=[fresh[0],fresh[1],fresh[2],'F9Vgqc9PSZX0trsy9yksNq','IKTH3CsUUP16goKZDUxIQv',fresh[30],fresh[55],fresh[80],fresh[100],fresh[105],fresh[50],fresh[70]]
sample=list(dict.fromkeys(sample))
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
def check(code):
    time.sleep(0.6)
    try:
        r=subprocess.run(['curl','-s','-m','25','-A',UA,'-o','/dev/stdout','-w','\n%{http_code}',f'https://chat.whatsapp.com/{code}'],capture_output=True,text=True,timeout=40)
        body,http=r.stdout.rsplit('\n',1)[0],r.stdout.rsplit('\n',1)[-1]
        m=re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)',body) or re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']',body)
        return code,http,(m.group(1).strip() if m else '')
    except Exception as e:
        return code,'ERR',str(e)
def run(codes):
    with ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(check,codes))
print('--- control: known-live code ---')
print(run(['Gs2YArMZSPG2hTUmkzqWCE']))
print('--- spot sample (12 fresh codes) ---')
res=run(sample)
for c,h,t in res: print(c,h,repr(t))
empties=[c for c,h,t in res if h=='200' and not t]
print('empty-og, retrying after pause:',empties)
time.sleep(5)
if empties:
    for c,h,t in run(empties): print('RETRY',c,h,repr(t))
json.dump({'sample':sample,'first_pass':[(c,h,t) for c,h,t in res]},open('team21-spotcheck.json','w'),indent=1)
