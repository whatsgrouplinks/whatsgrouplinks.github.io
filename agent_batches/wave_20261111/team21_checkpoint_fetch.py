import json, urllib.request, re, os
BASE='https://freewagroup.com/wp-json/wp/v2/posts?per_page=100&_fields=id,date,modified,slug,link,title,content,categories'
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
posts=[]; page=1; total=None
while True:
    req=urllib.request.Request(f'{BASE}&page={page}', headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        if total is None: total=int(r.headers.get('X-WP-Total','0'))
        data=json.loads(r.read())
    if not data: break
    posts+=data
    print(f'page {page}: {len(data)} posts (total header {total})')
    if len(posts)>=total or len(data)<100: break
    page+=1
json.dump(posts, open('team21-freewagroup-posts-raw.json','w'), ensure_ascii=False)
print('TOTAL POSTS:', len(posts))
dates=sorted(p['date'] for p in posts)
print('oldest:', dates[0], 'newest:', dates[-1])
print('newest 5:', sorted(posts, key=lambda p:p['date'], reverse=True)[:5])
codes={}
for p in posts:
    for c in re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9]{10,30})', p.get('content',{}).get('rendered','')):
        codes.setdefault(c, []).append(p['slug'])
print('distinct codes:', len(codes))
json.dump(codes, open('team21-freewagroup-codes.json','w'), indent=1)
