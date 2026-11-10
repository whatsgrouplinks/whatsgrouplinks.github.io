import json, re, time, subprocess, html, os
from concurrent.futures import ThreadPoolExecutor

W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def curl_text(url, timeout=30, headers_only=False):
    args=["curl","-s","-A",UA,"--max-time",str(timeout)]
    if headers_only: args+=["-D","-","-o","/dev/null"]
    else: args+=["-w","\n%{http_code}"]
    args+=[url]
    try:
        r=subprocess.run(args, capture_output=True, text=True, timeout=timeout+10)
        return r.stdout, None
    except Exception as e:
        return "", str(e)

# 1. union
ex=json.load(open('/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'))
g=json.load(open('/home/hatch/workspace/whatsapp-groups-site/groups.json'))
union=set(ex)
for it in g:
    inv=it.get('invite','') if isinstance(it,dict) else ''
    c=inv.rstrip('/').split('/')[-1]
    if c: union.add(c)
print("union:", len(union), flush=True)

# 2. listing pages
def fetch_listing(url):
    out,err=curl_text(url, timeout=30)
    if err: return ""
    body=out[:out.rfind("\n")]
    return body

chat_html=fetch_listing("https://grupbul.com/en/category/whatsapp/15/chat-friendship")
food_html=fetch_listing("https://grupbul.com/en/category/whatsapp/53/food")
print("chat len", len(chat_html), "food len", len(food_html), flush=True)

def parse_items(h):
    items=re.findall(r'<a href="https://grupbul\.com/group/(\d+)"[^>]*>(.*?)</a>', h, re.S)
    out=[]
    for gid, inner in items:
        t=re.sub(r'<[^>]+>','|',inner)
        parts=[html.unescape(p).strip() for p in t.split('|') if p.strip()]
        if len(parts)>=3:
            out.append({"gid":gid,"name":parts[0],"catlabel":parts[1],"desc":parts[2]})
    return out

chat_items=parse_items(chat_html)
food_items=parse_items(food_html)
print("chat items:", len(chat_items), "food items:", len(food_items), flush=True)
# extra food detail pages found via web search (Food-topic groups on grupbul)
extra=[
 {"gid":"207356","name":"BAR DO CUSCUZ É FAMÍLIA✅","catlabel":"Food","desc":"Bar do Cuscuz food and family group sharing recipes and culinary tips."},
 {"gid":"187582","name":"Nasi Lemak Bitcoin","catlabel":"Food","desc":"Nasi Lemak Bitcoin group."},
 {"gid":"638413","name":"HomeCookingShow","catlabel":"Food","desc":"HomeCookingShow WhatsApp Channel."},
]
allitems=chat_items+food_items+extra
json.dump({"chat":chat_items,"food":food_items,"extra":extra}, open(os.path.join(W,"team16_raw_items.json"),"w"), ensure_ascii=False, indent=1)

# 3. detail pages -> redirect
def fetch_detail(it):
    gid=it["gid"]
    for attempt in range(3):
        body,err=curl_text(f"https://grupbul.com/group/{gid}", timeout=35)
        if err:
            time.sleep(2); continue
        m=re.search(r'/redirect/%s/(\d+)'%gid, body)
        if m:
            it["redirect"]=f"https://grupbul.com/redirect/{gid}/{m.group(1)}"
            return it
        time.sleep(2)
    it["redirect"]=None
    return it

with ThreadPoolExecutor(max_workers=3) as ex:
    details=list(ex.map(fetch_detail, allitems))
json.dump(details, open(os.path.join(W,"team16_details.json"),"w"), ensure_ascii=False, indent=1)
print("details with redirect:", sum(1 for d in details if d.get("redirect")), "/", len(details), flush=True)

# 4. follow redirects via refresh header
def follow(d):
    if not d.get("redirect"): return d
    for attempt in range(2):
        out,err=curl_text(d["redirect"], timeout=30, headers_only=True)
        if err:
            time.sleep(2); continue
        m=re.search(r'refresh:\s*\d+;\s*url=(\S+)', out, re.I)
        if not m:
            m2=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', out)
            if m2:
                d["location"]="https://chat.whatsapp.com/"+m2.group(1); d["code"]=m2.group(1); return d
            time.sleep(2); continue
        loc=m.group(1).strip()
        d["location"]=loc
        if 'whatsapp.com/channel' in loc:
            d["code"]="CHANNEL"
        else:
            mm=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)', loc)
            d["code"]=mm.group(1) if mm else None
        return d
    d["location"]=None; d["code"]=None
    return d

with ThreadPoolExecutor(max_workers=3) as ex:
    details=list(ex.map(follow, details))
json.dump(details, open(os.path.join(W,"team16_details.json"),"w"), ensure_ascii=False, indent=1)
for d in details:
    print(d["gid"], d["name"][:35], "| code:", d.get("code"), flush=True)
