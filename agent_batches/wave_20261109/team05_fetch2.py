import json, re, subprocess, time, html, os, urllib.parse
from concurrent.futures import ThreadPoolExecutor
W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{10,30})")
leads = json.load(open(f"{W}/leads_slice_05.json"))
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))
CK = f"{W}/team05-extracted.json"
# resume from checkpoint if present
state = {"codes": {}, "dead": [], "done": []}
if os.path.exists(CK):
    try:
        state = json.load(open(CK))
        print("resumed:", len(state["done"]), "done", len(state["codes"]), "codes", flush=True)
    except Exception:
        pass
done_urls = set(state["done"])
def save():
    json.dump(state, open(CK, "w"), indent=1, ensure_ascii=False)
def fetch_one(item):
    url = item["url"]
    if url in done_urls:
        return None
    try:
        r = subprocess.run(["curl","-sL","--max-time","20","--connect-timeout","10","-A",UA,url],
                           capture_output=True, text=True, timeout=30)
        body = r.stdout or ""
    except Exception:
        body = ""
    res = {"url": url, "source": item.get("source"), "len": len(body), "codes": [], "title": "", "contexts": {}, "new_leads": []}
    if len(body) < 500:
        res["dead"] = "fetch empty/short"
        return res
    m = re.search(r"<title>(.*?)</title>", body, re.S|re.I)
    if m: res["title"] = html.unescape(re.sub(r"<[^>]+>","",m.group(1))).strip()
    codes = set(CODE_RE.findall(body))
    res["codes"] = sorted(codes)
    for c in codes:
        if c in existing: continue
        idx = body.find(c)
        seg = body[max(0,idx-500):idx+500]
        seg = re.sub(r"<script.*?</script>"," ",seg,flags=re.S|re.I)
        seg = re.sub(r"<style.*?</style>"," ",seg,flags=re.S|re.I)
        seg = re.sub(r"<[^>]+>"," ",seg)
        seg = html.unescape(seg)
        seg = re.sub(r"\s+"," ",seg).strip()[:700]
        res["contexts"][c] = seg
    # discover same-domain listing links
    dom = urllib.parse.urlparse(url).netloc
    for h in set(re.findall(r'href="([^"]+)"', body)):
        u = urllib.parse.urljoin(url, h)
        p = urllib.parse.urlparse(u)
        if p.netloc == dom and "chat.whatsapp.com" not in u and ("whatsapp-group" in p.path or "group-link" in p.path) and u != url:
            res["new_leads"].append(u)
    return res
todo = [l for l in leads if l["url"] not in done_urls]
print("todo:", len(todo), flush=True)
n = 0
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(fetch_one, todo):
        if res is None: continue
        n += 1
        state["done"].append(res["url"])
        if res.get("dead"):
            state["dead"].append({"url": res["url"], "source": res["source"], "note": res["dead"]})
        elif not res["codes"]:
            state["dead"].append({"url": res["url"], "source": res["source"], "note": "no invite codes on page"})
        for c in res["codes"]:
            e = state["codes"].setdefault(c, {"code": c, "urls": [], "contexts": [], "page_titles": []})
            e["urls"].append(res["url"])
            if c in res["contexts"]: e["contexts"].append(res["contexts"][c])
            if res["title"] and res["title"] not in e["page_titles"]: e["page_titles"].append(res["title"])
        if n % 5 == 0:
            save()
            print(n, "/", len(todo), "codes:", len(state["codes"]), "dead:", len(state["dead"]), flush=True)
save()
fresh = [c for c in state["codes"] if c not in existing]
print("DONE total unique codes:", len(state["codes"]), "fresh:", len(fresh), "dead pages:", len(state["dead"]), flush=True)
