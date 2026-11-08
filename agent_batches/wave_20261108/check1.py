import requests, re, json
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
union=set(json.load(open('dedupe_union.json')))
codes=['LUMZAqG2aGV6Jhs3NUFt5q','JPBvIpyfjDnJAbqY6eYLWn','H9PX9qPXxhrLoDvPqGjqnu',
'D4MehDMkmxo3TN7w3rQNLv','KUjrZQqOBmk6EK61v4bsnm','HjwDh3D6ge9FTKTGtQV4Gj',
'Jpl6rk2qL1wH4jgBkY2bL9','KHOP4ftGR5q4oqP2nyaHhm','BO88nRxmEw4550h7NHwpGB']
for c in codes:
    print(c, 'IN UNION' if c in union else 'FRESH')
# grupbul links
t=requests.get("https://grupbul.com/en/category/whatsapp/5/game-groups",headers=UA,timeout=30).text
hrefs=sorted(set(re.findall(r'href="([^"]+)"',t)))
print('--- grupbul hrefs ---')
for h in hrefs: print(h)
