import json, time, os
W='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
def write_json_retry(path, obj):
    data=json.dumps(obj, ensure_ascii=False, indent=1)
    for attempt in range(5):
        try:
            with open(path,'w',encoding='utf-8') as f:
                f.write(data)
            # verify read-back
            back=json.load(open(path,encoding='utf-8'))
            assert back==obj, 'read-back mismatch'
            print('wrote', path, len(data), 'bytes,', len(obj), 'records')
            return
        except Exception as e:
            print('write attempt',attempt,'failed:',repr(e)[:100])
            time.sleep(2)
    raise RuntimeError('write failed: '+path)

# Verified live groups (og:title = real WhatsApp group name; category/country from listing-page title)
verified=[
 {"name":"GB FT CS BY MUZENXR [1]","category":"Gaming","country":"ID",
  "description":"Join GB FT CS BY MUZENXR [1], a WhatsApp group listed under Gaming. Connect with members from Indonesia and join the conversation.",
  "invite":"https://chat.whatsapp.com/HmYlSlyvv8DBA3gaWJs3as","image":""},
 {"name":"مملكه الهبد 😂🤚🏻","category":"Funny","country":"EG",
  "description":"Join مملكه الهبد 😂🤚🏻, a WhatsApp group listed under Funny. Connect with members from Egypt and join the conversation.",
  "invite":"https://chat.whatsapp.com/Exd1VD6TRS31e2FH8lbVJ2","image":""},
 {"name":"عشق كوره القدم","category":"Sports","country":"EG",
  "description":"Join عشق كوره القدم, a WhatsApp group listed under Sports. Connect with members from Egypt and join the conversation.",
  "invite":"https://chat.whatsapp.com/EafUEhMOmbh7ZbrYn68qdG","image":""},
 {"name":"ساتوشيات","category":"Crypto","country":"SY",
  "description":"Join ساتوشيات, a WhatsApp group listed under Crypto. Connect with members from Syria and join the conversation.",
  "invite":"https://chat.whatsapp.com/LV5raMC7dsH1LoIGrTNp7E","image":""},
 {"name":"احلى لمه 😊🫶✅","category":"Community & Social","country":"YE",
  "description":"Join احلى لمه 😊🫶✅, a WhatsApp group listed under Community & Social. Connect with members from Yemen and join the conversation.",
  "invite":"https://chat.whatsapp.com/IKxR2Iwxi28DQvfPeoZOkV","image":""},
]
# dedupe + union guard
union=set(json.load(open(W+'dedupe_union.json')))
seen=set(); final=[]
for g in verified:
    code=g['invite'].rsplit('/',1)[-1]
    assert code not in union, code
    assert code not in seen, code
    seen.add(code); final.append(g)
CANON={"Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health","Business","Gaming","Friendship","Community & Social","Online Earning","Crypto","Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell","Finance","Funny"}
for g in final:
    assert g['category'] in CANON, g
    assert g['country'] and g['description'] and g['name']
    assert 'chat.whatsapp.com/' in g['invite']
write_json_retry(W+'team03-leads-harvest-c.json', final)
write_json_retry(W+'team03-leads-harvest-c-pending.json', [])

# New listing-page leads: similar groupe/channel links from crawled pages, not already in slice 03
crawl=json.load(open(W+'team03_crawl_raw.json'))
slice_urls=set(e['url'] for e in json.load(open(W+'leads_slice_03.json')))
sim=set()
for rec in crawl:
    for s in rec.get('similar',[]): sim.add(s)
new_leads=[{"url":u,"source":"groupchatconnect.info"} for u in sorted(sim - slice_urls)]
assert all('/groupe/' in l['url'] or '/channel/' in l['url'] for l in new_leads)
assert all('chat.whatsapp.com' not in l['url'] for l in new_leads)
write_json_retry(W+'team03-leads-harvest-c-leads.json', new_leads)
print('verified:', len(final), 'pending: 0, leads:', len(new_leads))
