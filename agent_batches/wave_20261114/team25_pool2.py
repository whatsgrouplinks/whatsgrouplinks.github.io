import json, re, html
from team25_extract import extract

union = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
pool = json.load(open('team25_raw/pool.json'))

def add(code, name, country, source, section=''):
    if not re.fullmatch(r'[A-Za-z0-9]{20,24}', code.strip()): return
    name = html.unescape(re.sub(r'\s+',' ',name or '')).strip()
    if code not in pool:
        pool[code] = {"name": name, "country": country, "source": source, "section": section}

for c, n in extract('team25_raw/https_77links_com_arabic_whatsapp_group_links_.html').items():
    add(c, n, '', '77links.com Arabic')
add('E26Ge2oCqbOALX52nXzVPd', 'Seada Kasim Ethiopian Community', 'ET', 'tiktok.com')

fresh_all = {c: v for c, v in pool.items() if c not in union}
done = json.load(open('team25_raw/verify_results.json')) if __import__('os').path.exists('team25_raw/verify_results.json') else {}
fresh2 = {c: v for c, v in fresh_all.items() if c not in done}
print("pool now:", len(pool), "| fresh total:", len(fresh_all), "| already verified:", len(done), "| fresh2 (to verify):", len(fresh2))
from collections import Counter
print("fresh2 by source:", Counter(v['source'] for v in fresh2.values()))
json.dump(pool, open('team25_raw/pool.json','w'), indent=1, ensure_ascii=False)
json.dump(fresh2, open('team25_raw/fresh2.json','w'), indent=1, ensure_ascii=False)
