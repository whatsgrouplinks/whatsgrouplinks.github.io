import json, re, time, subprocess, html, os
from concurrent.futures import ThreadPoolExecutor
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
def curl_text(url, timeout=40, headers_only=False):
    args=["curl","-s","-A",UA,"--max-time",str(timeout)]
    if headers_only: args+=["-D","-","-o","/dev/null"]
    else: args+=["-w","\n%{http_code}"]
    args+=[url]
    try:
        r=subprocess.run(args, capture_output=True, text=True, timeout=timeout+10)
        return r.stdout, None
    except Exception as e:
        return "", str(e)

chat_html=""
for a in range(5):
    out,err=curl_text("https://grupbul.com/en/category/whatsapp/15/chat-friendship", timeout=45)
    if not err and out:
        chat_html=out[:out.rfind("\n")]
    print("attempt",a+1,"len",len(chat_html), flush=True)
    if len(chat_html)>50000: break
    time.sleep(3)
print("final chat len", len(chat_html), flush=True)
open(os.path.join(W,"team16_chat_page.html"),"w",errors="ignore").write(chat_html)

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
print("chat items:", len(chat_items), [i["gid"] for i in chat_items], flush=True)

def fetch_detail(it):
    gid=it["gid"]
    for attempt in range(3):
        body,err=curl_text(f"https://grupbul.com/group/{gid}", timeout=40)
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
    details=list(ex.map(fetch_detail, chat_items))
print("details with redirect:", sum(1 for d in details if d.get("redirect")), "/", len(details), flush=True)

def follow(d):
    if not d.get("redirect"): return d
    for attempt in range(2):
        out,err=curl_text(d["redirect"], timeout=35, headers_only=True)
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
for d in details:
    print(d["gid"], d["name"][:35], "| code:", d.get("code"), flush=True)
# merge with extras already in team16_details.json
old=json.load(open(os.path.join(W,"team16_details.json")))
merged={d["gid"]:d for d in old}
for d in details: merged[d["gid"]]=d
json.dump(list(merged.values()), open(os.path.join(W,"team16_details.json"),"w"), ensure_ascii=False, indent=1)
json.dump(chat_items, open(os.path.join(W,"team16_chat_items.json"),"w"), ensure_ascii=False, indent=1)
print("merged total:", len(merged), flush=True)
