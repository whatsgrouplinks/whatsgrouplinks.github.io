import requests, re, json
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
def fetch(u):
    r=requests.get(u,headers=UA,timeout=30); return r.text
# whatshub codes
t=fetch("https://www.whatshub.es/")
for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})',t):
    print('WHATSAPPHUB code',m.group(1),'ctx:',t[max(0,m.start()-200):m.start()+40].replace('\n',' ')[:260])
# groupsinvite homepage codes
t2=fetch("https://groupsinvite.link/")
for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})',t2):
    print('GI code',m.group(1),'ctx:',t2[max(0,m.start()-300):m.start()+40].replace('\n',' ')[:340])
# whatsappkanali tekirdag codes
t3=fetch("https://whatsappkanali.com/sehir/tekirdag/sohbet")
for m in re.finditer(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})',t3):
    print('WK code',m.group(1),'ctx:',t3[max(0,m.start()-300):m.start()+40].replace('\n',' ')[:340])
# grupbul structure
t4=fetch("https://grupbul.com/en/category/whatsapp/5/game-groups")
print('GRUPBUL sample:',t4[:2000])
