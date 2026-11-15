import json, re, glob, html

# --- load union ---
union = set(json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json')))
print("union:", len(union))

from team25_extract import extract

pool = {}  # code -> {name, country, source, section}
def add(code, name, country, source, section=''):
    code = code.strip()
    if not re.fullmatch(r'[A-Za-z0-9]{20,24}', code): return
    name = html.unescape(re.sub(r'\s+',' ',name or '')).strip()
    if code not in pool:
        pool[code] = {"name": name, "country": country, "source": source, "section": section}
    elif name and len(name) > len(pool[code]["name"]):
        pool[code]["name"] = name

def add_file(path, country, source, section=''):
    for c, n in extract(path).items():
        add(c, n, country, source, section)

# --- directory pages ---
add_file('team25_raw/https_newgrouplinks_pk_dubai_whatsapp_group_links_.html', 'AE', 'newgrouplinks.pk Dubai')
add_file('team25_raw/https_grouplink_com_in_join_uae_job_whatsapp_group_links_instant_hiring_.html', 'AE', 'grouplink.com.in UAE jobs')
add_file('team25_raw/https_groupwa_com_city_jeddah_whatsapp_groups_.html', 'SA', 'groupwa.com Jeddah')
add_file('team25_raw/https_groupwa_com_city_riyadh_whatsapp_groups_.html', 'SA', 'groupwa.com Riyadh')
add_file('team25_raw/https_groupwa_com_country_zimbabwe_whatsapp_groups_.html', 'ZW', 'groupwa.com Zimbabwe')
add_file('team25_raw/https_anygulfjobs_com_saudi_arabia_jobs_whatsapp_group_ksa_.html', 'SA', 'anygulfjobs.com KSA jobs')
add_file('team25_raw/https_whatsagroupslinks_com_zimbabwe_whatsapp_group_links_.html', 'ZW', 'whatsagroupslinks.com Zimbabwe')
add_file('team25_raw/https_pkwhatsgrouplinks_com_zimbabwe_whatsapp_group_links_.html', 'ZW', 'pkwhatsgrouplinks.com Zimbabwe')

# whatsagroupslinks Tanzania — names from <li> parse (verified order)
h = open('team25_raw/whatsagroupslinks-tz.html', encoding='utf-8', errors='ignore').read()
for m in re.finditer(r'<li[^>]*>(.*?)</li>', h, re.S):
    li = m.group(1)
    code = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', li)
    if code:
        txt = re.sub(r'\s+',' ', re.sub(r'<[^>]+>',' ',li)).strip()
        nm = txt.split('–')[0].split('-')[0].strip()
        add(code.group(1), nm, 'TZ', 'whatsagroupslinks.com Tanzania')

# --- tglinkhub Africa sections ---
sec = json.load(open('team25_raw/sections_team25_raw_tglinkhub_html.json'))
for c, n, s in sec['team25_raw/tglinkhub.html']:
    if s == 'Kenyan Groups': add(c, n, 'KE', 'tglinkhub.com', s)
    elif s == 'Tanzania WhatsApp Groups': add(c, n, 'TZ', 'tglinkhub.com', s)
    elif s == 'Zimbabwe WhatsApp Groups': add(c, n, 'ZW', 'tglinkhub.com', s)

# --- activewagroup International section only ---
sec2 = json.load(open('team25_raw/sections_team25_raw_https_activewagroup_com_html.json'))
for c, n, s in sec2['team25_raw/https_activewagroup_com_.html']:
    if s == 'International WhatsApp Group':
        cc = ''
        nl = n.lower()
        if 'dubai' in nl or 'uae' in nl: cc = 'AE'
        elif 'kenya' in nl: cc = 'KE'
        elif 'ghana' in nl: cc = 'GH'
        elif 'nigeria' in nl: cc = 'NG'
        elif 'saudi' in nl: cc = 'SA'
        add(c, n, cc, 'activewagroup.com', s)

# --- snippet codes ---
snip = [
 ("JEVYxol0FRi39OhPaJM6Z1","Kuwait Self Evacuation","KW","mylifesamovie.com evacuation"),
 ("ICSfdA0gsWgA5mPaIlYT7w","Dubai Self Evacuation","AE","mylifesamovie.com evacuation"),
 ("C2QliqoXOhU8yvys7QJ9Yp","Doha Self Evacuation","QA","mylifesamovie.com evacuation"),
 ("HV9auNWmmmK8OV1kuQbMFU","ZBIN Marondera Area Group","ZW","zbinworld.com"),
 ("CPtzyW1rET76B7tbcK2Xpr","ZBIN Waterfalls Hatfield Area Group","ZW","zbinworld.com"),
 ("BfwdnETfIrZ1noDKm1kC6d","ZBIN Harare North Area Group","ZW","zbinworld.com"),
 ("IknWcPKhXPK5uAtkF91QWM","ZBIN Ruwa Area Group","ZW","zbinworld.com"),
 ("BfaMrp5Icj7Hj6ozLmrmhl","ZBIN Norton Area Group","ZW","zbinworld.com"),
 ("KyYMoHHU4nIILefEuP4QFt","ZBIN Harare West Area Group","ZW","zbinworld.com"),
 ("GWCw9w40d9A0QlJ2TMZqQY","ZBIN Kuwadzana Area Group","ZW","zbinworld.com"),
 ("F0GzqYlQQWkJGevqtpbsmF","ZBIN Zambia","ZM","zbinworld.com"),
 ("EYAaV1WY6QIHXF9V73UcS9","ZBIN Botswana","BW","zbinworld.com"),
 ("KUh6lk3vZ7qL1pdoZt3tFm","ZBIN Malawi","MW","zbinworld.com"),
 ("D93xDY0lBsD646BvUGHa9s","ZBIN Namibia","NA","zbinworld.com"),
 ("IRiDR0l1XXyFzUY2yjlNkh","ZBIN Mozambique","MZ","zbinworld.com"),
 ("DaF44nn6l0S8OLOzkpEVvH","Techzim Community B","ZW","techzim.co.zw"),
 ("HSunmuUHg090R9Z54S25Jj","Techzim Community C","ZW","techzim.co.zw"),
 ("JJnmRqAgd5C4QBPiWGaiWC","Techzim Community D","ZW","techzim.co.zw"),
 ("LSPXWSEqjlbGwb1YPWBaKP","Techzim Community E","ZW","techzim.co.zw"),
 ("CC448avubYhEk8NDw4rAXE","Techzim News 1","ZW","techzim.co.zw"),
 ("L2btZtKjTOk0mDbgaZqwu9","Techzim AI for Techies","ZW","techzim.co.zw"),
 ("EiPHou6MSRMAO1j2jX4gUA","Techzim Airtime and Internet","ZW","techzim.co.zw"),
 ("He4QXAFtY34LUAJ1Fg2mzs","Techzim Airtime and Internet 2","ZW","techzim.co.zw"),
 ("GzTyvwHD2LJBmOjCc2BGvK","Techzim Starlink Discussions","ZW","techzim.co.zw"),
 ("EsbdgQxNOPrJYVuikhIstt","Techzim Starlink Discussions 2","ZW","techzim.co.zw"),
 ("E6gRoCUFiOM5nwGc1d6MPA","Techzim Community Group","ZW","techzim.co.zw"),
 ("ESX7vmdIR8fIZmKzKXFa0M","Uganda Real Estate Community","UG","realestatedatabase.net"),
 ("HCjE3bh0YEqHSwjKuCa5xe","Human Unity Burundi Bujumbura","BI","human-unity.org"),
 ("EIbwcah8GygLfLnVwI6IC1","Human Unity Nigeria Ebonyi","NG","human-unity.org"),
 ("B7W0IaBfls7J1FyW4ir4sl","Human Unity Uganda Kampala","UG","human-unity.org"),
 ("IWXLaXzHIZpHiU4Vi3gZwE","Human Unity Uganda Kaliro","UG","human-unity.org"),
 ("B4gcn8lNsFjD4axxwUY5gL","Ibrahim Moustafa Wrestling Tournament Alexandria","EG","cdn.uww.org PDF"),
 ("BZ1g8KJs1U4D4CBeDut9yr","North Indian Community Dubai","AE","meetup.com"),
 ("EwUlMEbqclL23iJdOEHLqj","Akwaaba NYC Young Ghanaians","GH","tiktok.com"),
]
for c, n, cc, src in snip:
    add(c, n, cc, src)

print("raw pool (unique codes):", len(pool))
fresh = {c: v for c, v in pool.items() if c not in union}
dupes = len(pool) - len(fresh)
print("fresh vs union:", len(fresh), "| dupes:", dupes)
json.dump(pool, open('team25_raw/pool.json','w'), indent=1, ensure_ascii=False)
json.dump(fresh, open('team25_raw/fresh.json','w'), indent=1, ensure_ascii=False)
# per-source counts
from collections import Counter
print(Counter(v['source'] for v in pool.values()))
print("fresh by source:", Counter(v['source'] for v in fresh.values()))
