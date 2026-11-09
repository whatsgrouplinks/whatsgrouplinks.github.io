import json, re, os, html as htmllib

leads=json.load(open('leads_slice_06.json'))
newcodes=json.load(open('team06_raw/newcodes.json'))
newset=set(newcodes)
code_re=re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})')

def strip_scripts(s):
    s=re.sub(r'<script.*?</script>',' ',s,flags=re.S|re.I)
    s=re.sub(r'<style.*?</style>',' ',s,flags=re.S|re.I)
    return s

def text_lines(seg):
    seg=htmllib.unescape(seg)
    seg=re.sub(r'<[^>]+>','\n',seg)
    seg=htmllib.unescape(seg)
    return [ln.strip() for ln in seg.split('\n') if ln.strip()]

JUNK={'join','join now','join group','click here','join whatsapp group','join the group','join now!','join group now','join group'}
BADNAME=re.compile(r'^(group\s+\d+|\d+\s*members?|#\d+\s*largest)$', re.I)
def ok_name(n):
    if not n: return False
    n=n.strip()
    if len(n)<3 or len(n)>90: return False
    if BADNAME.match(n): return False
    if re.search(r'[{}"]', n): return False
    if n.lower() in JUNK: return False
    return True

def pick_name(lines):
    cand=[ln for ln in lines if len(ln)>=3 and not ln.lower().startswith(('http','www.','{','"','}','<'))
          and '@type' not in ln and 'chat.whatsapp.com' not in ln]
    for ln in reversed(cand):
        if ok_name(ln): return ln
    return None

def cat_from_url(u):
    u=u.lower()
    for kw,c in [('gaming','Gaming'),('game','Gaming'),('education','Education'),('study','Education'),
                 ('earning','Online Earning'),('earn','Online Earning'),('business','Business'),
                 ('friend','Friendship'),('girls','Friendship'),('islam','Islamic'),('quran','Islamic'),
                 ('job','Jobs'),('cricket','Sports'),('football','Sports'),('sport','Sports'),
                 ('movie','Entertainment'),('entertain','Entertainment'),('funny','Funny'),
                 ('news','News'),('health','Health'),('buy','Buy Sell'),('sell','Buy Sell'),
                 ('crypto','Finance'),('forex','Finance'),('trading','Finance'),('tech','Technology'),
                 ('food','Community & Social'),('government','Jobs'),('bank','Jobs')]:
        if kw in u: return c
    return None

ctx={}
for i in range(184):
    p=f'team06_raw/p{i}.html'
    if not os.path.exists(p): continue
    raw=open(p,encoding='utf-8',errors='ignore').read()
    url=leads[i]['url']; src=leads[i].get('source','')
    clean=strip_scripts(raw)
    # JSON-LD name map
    jmap={}
    for nm, cd in re.findall(r'"name":"([^"]+)","url":"https://chat\.whatsapp\.com/([A-Za-z0-9_-]+)"', raw):
        if ok_name(nm): jmap[cd]=htmllib.unescape(nm)
    for cd, nm in re.findall(r'"url":"https://chat\.whatsapp\.com/([A-Za-z0-9_-]+)"[^}]{0,200}?"name":"([^"]+)"', raw):
        if ok_name(nm): jmap.setdefault(cd, htmllib.unescape(nm))
    # groupsnest table rows
    row_names={}; row_cat={}
    for rm in re.finditer(r'<tr>(.*?)</tr>', clean, flags=re.S|re.I):
        row=rm.group(1)
        cm=code_re.search(row)
        if not cm: continue
        cd=cm.group(1).strip().strip('/')
        th=re.search(r'<th[^>]*>(.*?)</th>', row, flags=re.S|re.I)
        if th:
            nm=text_lines(th.group(1))
            nm=[x for x in nm if len(x)>1]
            if nm and ok_name(' '.join(nm)): row_names[cd]=' '.join(nm)
        catm=re.search(r'data-label="Collection"[^>]*>\s*<a[^>]*>([^<]+)</a>', row)
        if catm: row_cat[cd]=catm.group(1).strip()
    for m in code_re.finditer(raw):
        code=m.group(1).strip().strip('/')
        if code not in newset or code in ctx: continue
        name=None; desc=None; cat=None
        if code in row_names: name=row_names[code]
        if code in row_cat: cat=row_cat[code]
        window=raw[max(0,m.start()-1500):m.start()]
        jm=re.findall(r'\\"group_title\\":\\"((?:[^\\"\\\\]|\\\\.)*)\\"', window)
        if jm: name=htmllib.unescape(jm[-1]).replace('\\"','"')
        dm=re.findall(r'\\"group_desc\\":\\"((?:[^\\"\\\\]|\\\\.)*)\\"', window)
        if dm: desc=htmllib.unescape(dm[-1]).replace('\\"','"')
        cm2=re.findall(r'\\"category_name\\":\\"((?:[^\\"\\\\]|\\\\.)*)\\"', window)
        if cm2: cat=htmllib.unescape(cm2[-1])
        if not name and code in jmap: name=jmap[code]
        if not name:
            pos=clean.find('chat.whatsapp.com/'+code)
            if pos==-1: pos=clean.find(code)
            if pos!=-1:
                seg=clean[max(0,pos-1500):pos]
                gm=re.findall(r'class="group-name">([^<]+)<', seg)
                if gm and ok_name(gm[-1]): name=gm[-1].strip()
                if not name:
                    h3=re.findall(r'<h3[^>]*>([^<]+)</h3>', seg)
                    if h3 and ok_name(h3[-1]): name=h3[-1].strip()
                if not name: name=pick_name(text_lines(seg))
        if not cat: cat=cat_from_url(url)
        ctx[code]={'name':name,'desc':desc,'cat':cat,'page':url,'source':src}

print("ctx:", len(ctx), "of", len(newcodes))
print("no name:", sum(1 for v in ctx.values() if not v['name']))
print("bad 'members' names:", sum(1 for v in ctx.values() if v['name'] and 'members' in v['name'].lower()))
print("with desc:", sum(1 for v in ctx.values() if v['desc']))
json.dump(ctx, open('team06_raw/ctx.json','w'), ensure_ascii=False)
import random
random.seed(2)
for c in random.sample(list(ctx), 15): print(repr(ctx[c]['name']), '|', ctx[c]['cat'], '|', ctx[c]['source'])
