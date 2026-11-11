import json, re, time, subprocess, html, os
W="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def fetch(url, timeout=35):
    try:
        r=subprocess.run(["curl","-s","-A",UA,"--max-time",str(timeout),"-w","\n%{http_code}",url],
                         capture_output=True, timeout=timeout+10)
        out=r.stdout.decode('utf-8', errors='replace')
        http=out.rsplit("\n",1)[-1].strip()
        body=out[:out.rfind("\n")]
        return body, http
    except Exception as e:
        return "", "ERR:"+str(e)

def parse_items(h):
    items=re.findall(r'<a href="https://grupbul\.com/group/(\d+)"[^>]*>(.*?)</a>', h, re.S)
    out=[]
    for gid, inner in items:
        t=re.sub(r'<[^>]+>','|',inner)
        parts=[html.unescape(p).strip() for p in t.split('|') if p.strip()]
        if len(parts)>=3:
            out.append({"gid":gid,"name":parts[0],"catlabel":parts[1],"desc":parts[2][:400]})
    return out

urls = [
 ("food_p1","https://grupbul.com/en/category/whatsapp/53/food"),
 ("food_p2","https://grupbul.com/en/category/whatsapp/53/food?page=2"),
 ("food_p3","https://grupbul.com/en/category/whatsapp/53/food?page=3"),
 ("food_slash2","https://grupbul.com/en/category/whatsapp/53/food/2"),
 ("food_tr","https://grupbul.com/tr/category/whatsapp/53/yemek"),
 ("chat_p1","https://grupbul.com/en/category/whatsapp/15/chat-friendship"),
 ("chat_p2","https://grupbul.com/en/category/whatsapp/15/chat-friendship?page=2"),
 ("chat_p3","https://grupbul.com/en/category/whatsapp/15/chat-friendship?page=3"),
 ("chat_p4","https://grupbul.com/en/category/whatsapp/15/chat-friendship?page=4"),
 ("chat_slash2","https://grupbul.com/en/category/whatsapp/15/chat-friendship/2"),
 ("chat_page2","https://grupbul.com/en/category/whatsapp/15/chat-friendship/page/2"),
]
results={}
for key, url in urls:
    body, http = fetch(url)
    items = parse_items(body)
    # pagination hints
    pag = re.findall(r'page=\d+|/page/\d+|pagination[^<]{0,80}|>(\d+)<', body)
    results[key]={"url":url,"http":http,"len":len(body),"n_items":len(items),
                  "gids":[i["gid"] for i in items],
                  "items":items}
    print(key, "http",http,"len",len(body),"items",len(items), [i["gid"] for i in items][:5], flush=True)
    # save raw html for inspection (first two only to save space? save all, small)
    open(os.path.join(W,f"team16_{key}.html"),"w",encoding="utf-8").write(body)
    time.sleep(2)

json.dump(results, open(os.path.join(W,"team16_listings.json"),"w"), ensure_ascii=False, indent=1)
# diff vs nov10 chat items
prev=json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team16_chat_items.json"))
prev_gids={x["gid"] for x in prev}
for key in ("chat_p1","chat_p2","chat_p3","chat_p4"):
    gids=set(results[key]["gids"])
    print(key,"new vs nov10:", sorted(gids-prev_gids), "missing vs nov10:", sorted(prev_gids-gids), flush=True)
print("DONE", flush=True)
