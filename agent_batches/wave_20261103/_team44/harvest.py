import sys, json, os, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import fetch, extract_li_join, extract_table_join
D=os.path.dirname(os.path.abspath(__file__))
OUT=D+'/raw_candidates.json'
cand=json.load(open(OUT)) if os.path.exists(OUT) else {}
def save(): json.dump(cand,open(OUT,'w'))
def add(url, items):
    if url not in cand or cand[url] is None:
        cand[url]=items; save()
PAGES=[
 ('whtsp', 'https://www.whtspgrouplink.com/%s', 'li', [
  'chicago-whatsapp-group-links','new-york-whatsapp-group-links','georgia-whatsapp-group-links',
  'kenyans-in-usa-whatsapp-group-links','usa-business-whatsapp-group-links','california-whatsapp-group-links',
  'texas-jobs-whatsapp-group-links','usa-friends-whatsapp-group-links','usa-investment-whatsapp-group-links',
  'usa-real-estate-whatsapp-group-links','american-students-whatsapp-group-links',
  'american-english-learning-whatsapp-group-links','american-whatsapp-group-links',
  'usa-jobs-whatsapp-group-links','usa-buy-and-sell-whatsapp-group-links','usa-video-editing-whatsapp-group-links']),
]
# archive domain (www variant)
arc=[]
for n in range(1,50):
    arc.append('latest-whatsapp-group-links/page/%d' % n)
arc.append('latest-whatsapp-group-links')
PAGES.append(('arc','https://www.whtspgrouplinks.com/%s','li',arc))
# fresh dirs
PAGES.append(('fresh','%s','auto',[
 'https://thewhatspgrouplinks.com/los-angeles-whatsapp-group-links/',
 'https://wagroupshub.com/usa-whatsapp-group-links/',
 'https://wahublink.com/usa-whatsapp-group-links/',
 'https://pkwhatsgrouplinks.com/usa-whatsapp-group-links/',
 'https://newgrouplinks.pk/usa-whatsapp-group-links/',
 'https://thinkingoutsidethesandbox.ca/135-best-business-whatsapp-group-links/',
]))
for tag, tmpl, kind, slugs in PAGES:
    for s in slugs:
        url = tmpl % s if '%s' in tmpl else tmpl + s if False else (tmpl % s)
        if url in cand and cand[url] is not None: continue
        t=fetch(url, tries=3)
        if t is None:
            print('MISS',url,flush=True); add(url,None)
        else:
            items = extract_li_join(t) if kind=='li' else (extract_li_join(t)+extract_table_join(t) if kind=='auto' else extract_table_join(t))
            print('HIT',url,len(items),flush=True); add(url,items)
        time.sleep(0.8)
print('HARVEST-DONE pages:',len(cand),'items:',sum(len(v) for v in cand.values() if v))
