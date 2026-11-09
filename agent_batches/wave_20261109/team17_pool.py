import json, re
existing=set(json.load(open('../../.existing_codes.json')))
fresh=json.load(open('team17_fresh_raw.json'))
names=json.load(open('team17_listing_names.json'))
todo=json.load(open('../wave_20261108/team22_todo.json'))
# team22 carry-over
carry={}
for c in todo['skip_oos']+todo['todo']:
    if c not in existing and c not in fresh:
        carry[c]={'code':c,'sources':['team22-carryover'],'ctx':'team22 Nov8 todo/skip_oos'}
print('carry-over fresh vs union:',len(carry),'of',len(todo['skip_oos'])+len(todo['todo']))
print('carry already in union:',len(todo['skip_oos'])+len(todo['todo'])-len(carry))
print('carry already in fresh180:',len([c for c in todo['skip_oos']+todo['todo'] if c in fresh]))
# pre-screen: egregious adult listing names (unambiguous)
ADULT=re.compile(r'\b(sex|xxx|porn|sexy|leak|hot\s*girl|nude|desi\s*girl|call\s*girl|fuck|milf|rape|thoot|mall\b.*(girl|video)|18\+|only\s*hot|chill.*video|leaked)\b',re.I)
def adultish(nm):
    if not nm: return False
    s=nm.lower()
    return bool(re.search(r'\bsex\b|\bxxx\b|\bporn\b|\bsexy\b|\bleak\b|\bnude\b|\bfuck\b|\bmilf\b|\brape\b',s)) or 'desi girl' in s or 'call girl' in s or 'hot girl' in s or '18+' in s or 'leaked' in s
pool={}
prescreen_drop=[]
for c,v in list(fresh.items())+list(carry.items()):
    nm=names.get(c,'')
    if adultish(nm):
        prescreen_drop.append({'code':c,'listing_name':nm,'reason':'adult listing name','source':v['sources']})
    else:
        pool[c]=v
print('pool to verify:',len(pool),'| pre-screen adult drops:',len(prescreen_drop))
json.dump(pool,open('team17_verify_pool.json','w'),ensure_ascii=False,indent=1)
json.dump(prescreen_drop,open('team17_prescreen_drop.json','w'),ensure_ascii=False,indent=1)
json.dump(carry,open('team17_carryover.json','w'),ensure_ascii=False,indent=1)
