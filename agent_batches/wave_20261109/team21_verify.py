import json, subprocess, re, time, html
pool=json.load(open('team21_verify_pool.json'))
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
results=[]
for r in pool:
    code=r['code']; url=f"https://chat.whatsapp.com/{code}"
    title=""; desc=""; status=None; attempts=0
    for attempt in range(3):
        attempts+=1
        try:
            p=subprocess.run(['curl','-s','-L','--max-time','25','-A',UA,'-w','\n%{http_code}',url],
                             capture_output=True, text=True, timeout=40)
            body, httpcode = p.stdout.rsplit('\n',1)[0], p.stdout.rsplit('\n',1)[1]
            status=int(httpcode)
        except Exception as e:
            body=""; status=0
        m=re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', body)
        if not m:
            m=re.search(r"<meta\s+property='og:title'\s+content='([^']*)'", body)
        if not m:
            m=re.search(r'<meta\s+content="([^"]*)"\s+property="og:title"', body)
        t=html.unescape(m.group(1)).strip() if m else ""
        d=""
        dm=re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', body)
        if dm: d=html.unescape(dm.group(1)).strip()
        if status==200 and t:
            title, desc = t, d
            break
        title=t; desc=d
        if attempt<2: time.sleep(3)
        # if not 200, retry too (could be transient)
    verdict = 'live' if (status==200 and title) else ('ambiguous' if status==200 else 'dead')
    results.append({'code':code,'status':status,'attempts':attempts,'og_title':title,'og_description':desc,
                    'verdict':verdict,'source_file':r.get('source_file'),'context':r.get('context',''),
                    'category_hint':r.get('category_hint'),'country_hint':r.get('country_hint')})
    print(code, status, attempts, verdict, '|', title[:80], flush=True)
    time.sleep(1.0)
json.dump(results, open('team21_verify_results.json','w'), indent=1, ensure_ascii=False)
print("live:", sum(1 for x in results if x['verdict']=='live'),
      "dead:", sum(1 for x in results if x['verdict']=='dead'),
      "ambiguous:", sum(1 for x in results if x['verdict']=='ambiguous'))
