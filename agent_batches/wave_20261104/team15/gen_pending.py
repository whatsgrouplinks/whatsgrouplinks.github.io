import json, re
T='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team15'
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104'
classify=json.load(open(f'{T}/classify.json'))
verify=json.load(open(f'{T}/verify.json'))
union=set(x.lower() for x in json.load(open(f'{WAVE}/dedupe_union.json')))
t30=json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103/team30R-groupsinvite.json'))
t30codes=set(re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})',i['invite']).group(1).lower() for i in t30)
slug_meta=json.load(open(f'{T}/slug_meta.json'))
pending=[]; seen=set(); u=0; pornp=0
PW=['porn','pornhub','xxx','nude','sex video','escort','call girl','fuck','dick','pussy','boobs','anal','bokep',
    '\U0001f975','\U0001f346','\U0001f351','\U0001f51e','\U0001f4a6','\U0001f445','\U0001f444','\U0001f48b',
    '\u0645\u0632\u0627 \u062f\u06cc\u0646\u06d2','\u0645\u0632\u06c1 \u062f\u06cc\u0646\u06d2']
for slug,v in classify.items():
    if v.get('kind')!='chat': continue
    code=v.get('code','')
    if not re.match(r'^[A-Za-z0-9]{20,24}$',code): continue
    key=code.lower()
    if key in union or key in t30codes or key in seen: u+=1; continue
    if code in verify: continue
    seen.add(key)
    title=''
    sm=slug_meta.get(slug,{})
    if sm.get('titles'): title=sm['titles'][0]
    if any(w in title.lower() for w in PW): pornp+=1
    pending.append({'name':title or f'groupsinvite.link group ({slug})','category':'Other',
        'country':'International','description':'Unverified groupsinvite.link group listing.',
        'invite':f'https://chat.whatsapp.com/{code}','image':'',
        'note':'transport blocked: groupsinvite.link Cloudflare-403 (browser.open) + read timeouts via egress proxy on 2026-11-04 ~12:05 PKT — re-verify next wave'})
import sys
sys.stdout.write(json.dumps(pending, ensure_ascii=False, indent=1))
sys.stderr.write(f'STATS pending={len(pending)} excluded={u} pornp={pornp}\n')
#x
