import requests, re
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
t=requests.get("https://grupbul.com/group/257436",headers=UA,timeout=30).text
print('grupbul detail len',len(t))
codes=re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9]{22})\b',t)
print('codes:',codes)
print(t[:1500].replace('\n',' ')[:1500])
t2=requests.get("https://whatsappkanali.com/sehir/tekirdag/sohbet",headers=UA,timeout=30).text
sehir=sorted(set(re.findall(r'href="(/sehir/[^"]+)"',t2)))
print('sehir links:',len(sehir))
for s in sehir[:40]: print(s)
