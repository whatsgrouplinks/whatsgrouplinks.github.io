import re, json, html, os
D='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team10_gb/'
out={}
for fn in sorted(os.listdir(D)):
    if not fn.startswith('cat_') or not fn.endswith('.html'): continue
    slug=fn[4:-5]
    h=open(D+fn,encoding='utf-8',errors='ignore').read()
    pat=re.compile(r'<a href="https?://grupbul\.com/group/(\d+)"[^>]*>.*?<span class="text-whatsapp[^"]*"[^>]*>(.*?)</span>(?:\s*<span class="text-whatsapp[^"]*"[^>]*></span>)?\s*<div class="text-muted my-2">.*?>(.*?)</div>\s*(?:<div style="margin-right: 15px;[^>]*>(.*?)</div>)?', re.S)
    ents=[]
    for m in pat.finditer(h):
        gid=m.group(1)
        name=html.unescape(re.sub(r'<[^>]+>','',m.group(2))).strip()
        cat=html.unescape(re.sub(r'<[^>]+>','',m.group(3))).strip()
        desc=html.unescape(re.sub(r'<[^>]+>','',(m.group(4) or ''))).strip()
        ents.append({'gid':gid,'name':name,'cat_label':cat,'desc':desc[:400],'src_slug':slug})
    print(slug, len(ents))
    out[slug]=ents
allids={}
for slug,ents in out.items():
    for e in ents: allids.setdefault(e['gid'],[]).append(slug)
print("total entries:", sum(len(v) for v in out.values()), "unique gids:", len(allids))
json.dump(out, open(D+'parsed.json','w'), ensure_ascii=False, indent=1)
# check for load-more/ajax in a category page
h=open(D+'cat_food.html',encoding='utf-8',errors='ignore').read()
for pat in ['load','ajax','/jobs','page=','?page','daha','more']:
    print(pat, len(re.findall(pat,h,re.I)))
