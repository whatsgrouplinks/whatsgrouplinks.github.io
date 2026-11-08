import json
WAVE='/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/'
ADULT_EMOJI=set(['🥵','🍆','🍑','🔞','💦','👅','👄','💋'])
v=json.load(open(WAVE+'team01-linkado-verify.json'))
raw=json.load(open(WAVE+'team01-linkado-raw.json'))

def cat_from_listing(listing_name):
    n=listing_name.lower()
    if ' - amizade' in n: return 'Friendship'
    if ' - games' in n: return 'Gaming'
    if ' - esportes' in n: return 'Sports'
    if ' - dinheiro' in n: return 'Online Earning'
    if ' - trabalho' in n: return 'Jobs'
    if ' - comprar e venda' in n: return 'Buy & Sell'
    if ' - tecnologia' in n: return 'Technology'
    if ' - lgbt' in n: return 'Community & Social'
    if ' - status' in n: return 'Community & Social'
    if ' - links' in n: return 'Community & Social'
    return 'Community & Social'

keep={
 'IhksM8Hv5AtCxgWgVHWxy0':None,
 'DHGb5JO4aig3eN1o18Xme5':None,
 'HxqVT5lT6KU1slcTLLQ0LR':None,
 'JvfQCRfXM6c5YyYB5wjblo':'Brasileirão efootball',
 'LckbxadJbQP3SoXEhd1njG':None,
 'BwvqA3Vlrwh8FZxwd2908J':None,
 'FgzrBCWxREsL4WKbCzAaSG':None,
 'Kyc9HTMMaDIL40nPRsPM8C':'PUBLIC <> CITY',
 'GgFUGqGn9KUGjWCDmHl4v0':None,
 'HfFz5CdezMAH2pcQQleTmH':None,
 'LvXLvYB2s1HAD1xz8MVj8w':None,
 'CMjxOgwIesNLQuNVEPHZpk':None,
}
# category overrides by code
cat_override={'HfFz5CdezMAH2pcQQleTmH':'Education'}
verified=[]
for code,name_override in keep.items():
    x=v[code]; rec=x['rec']
    name=name_override or x['title'].strip()
    if name=='PUBLIC <\\> CITY': name='PUBLIC <> CITY'
    cat=cat_override.get(code,cat_from_listing(rec['name']))
    if any(e in name for e in ADULT_EMOJI):
        continue
    desc=f"Join {name}, a WhatsApp group listed under {cat}. Connect with members from Brazil, share updates and chat with the community."
    verified.append({"name":name,"category":cat,"country":"BR","description":desc,
                     "invite":"https://chat.whatsapp.com/"+code,"image":""})
print('verified:',len(verified))
for g in verified: print(' ',g['category'],'|',g['name'],'|',g['invite'])

def w(path,data):
    for attempt in range(5):
        try:
            with open(path,'w') as f: json.dump(data,f,ensure_ascii=False,indent=1)
            return True
        except Exception as e:
            print('WRITE FAIL',path,attempt,e); time.sleep(2)
    return False
import time
w(WAVE+'team01-leads-harvest-a.json',verified)
w(WAVE+'team01-leads-harvest-a-pending.json',[])
# leads: existing 61 + linkado listing pages
leads=json.load(open(WAVE+'team01-leads-harvest-a-leads.json'))
seen=set(l['url'] for l in leads)
add=[
 ("https://linkado.app/sitemap.xml","linkado sitemap"),
 ("https://linkado.app/categorias","linkado category index"),
 ("https://linkado.app/populares","linkado popular groups"),
]
cats=['amizade','carros','cidades','comprar-e-venda','dinheiro','educacao','esportes','figurinhas','games','lgbt','links','moda-e-beleza','musica','namoro','politica','religiao','series','status','tecnologia','trabalho']
for c in cats: add.append((f"https://linkado.app/categoria/{c}",f"linkado category {c}"))
for url,src in add:
    if url not in seen:
        seen.add(url); leads.append({"url":url,"source":src})
assert all('chat.whatsapp.com' not in l['url'] for l in leads)
w(WAVE+'team01-leads-harvest-a-leads.json',leads)
print('leads:',len(leads))
# validate schema
for g in verified:
    assert set(g)== {"name","category","country","description","invite","image"}, g
    assert g['invite'].startswith('https://chat.whatsapp.com/') and len(g['invite'].split('/')[-1])==22
print('SCHEMA OK')
