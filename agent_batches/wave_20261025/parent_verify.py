import json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
items = json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261025/merged_wave_20261025_parent.json'))
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
def check(it):
    url = it['invite']
    try:
        p = subprocess.run(['curl','-s','-L','--max-time','20','-A',UA,url], capture_output=True, text=True, timeout=30)
        html = p.stdout
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
        title = m.group(1).strip() if m else ''
        code = p.returncode
        return (it, code, title)
    except Exception as e:
        return (it, 'ERR', str(e)[:80])
with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(check, items))
live, dead, unk = [], [], []
for it, code, title in results:
    if code == 0 and title:
        live.append((it, title))
    elif code == 0 and not title:
        dead.append(it)
    else:
        unk.append((it, code, title))
print(f"LIVE: {len(live)}  DEAD(empty og:title): {len(dead)}  UNCHECKABLE: {len(unk)}")
json.dump([i for i,_ in live], open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261025/parent_verified.json','w'), ensure_ascii=False)
json.dump([i for i in dead], open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261025/parent_dead.json','w'), ensure_ascii=False)
json.dump([{'item': i, 'code': str(c)} for i,c,_ in unk], open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261025/parent_uncheckable.json','w'), ensure_ascii=False)
for i in dead[:20]: print("DEAD:", i['name'], i['invite'])
for i,c,_ in unk[:20]: print("UNK:", c, i['name'], i['invite'])
