import re, json, subprocess, time, html
D='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team10_gb/'
parsed=json.load(open(D+'parsed.json'))
# unique gids, keep first occurrence (prefer non-p2 slug)
gids={}
for slug,ents in parsed.items():
    for e in ents:
        gids.setdefault(e['gid'], e)
print("unique gids:", len(gids))
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
def curl(url, headers=False):
    cmd=['curl','-s','-m','30','-A',UA]
    if headers: cmd+=['-D','-','-o','/dev/null']
    cmd+=[url]
    r=subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout
out={}
for gid,e in gids.items():
    try:
        h=curl(f'https://grupbul.com/group/{gid}')
        m=re.search(r'/redirect/%s/(\d+)'%gid, h)
        if not m:
            print(gid,'NO-REDIRECT-LINK'); out[gid]={**e,'code':None,'err':'no-redirect-link'}; time.sleep(0.6); continue
        rid=m.group(1)
        hdrs=curl(f'https://grupbul.com/redirect/{gid}/{rid}', headers=True)
        rm=re.search(r'refresh:\s*\d+;\s*url=https://chat\.whatsapp\.com/([A-Za-z0-9]{22})', hdrs, re.I)
        if not rm:
            print(gid,'NO-REFRESH-CODE', hdrs[:200].replace('\n',' ')); out[gid]={**e,'code':None,'err':'no-refresh-code'}; time.sleep(0.6); continue
        code=rm.group(1)
        print(gid,'->',code,'|',e['name'][:40])
        out[gid]={**e,'code':code,'err':None}
    except Exception as ex:
        print(gid,'ERR',repr(ex)); out[gid]={**e,'code':None,'err':repr(ex)}
    time.sleep(0.6)
json.dump(out, open(D+'redirects.json','w'), ensure_ascii=False, indent=1)
print("with code:", sum(1 for v in out.values() if v.get('code')))
