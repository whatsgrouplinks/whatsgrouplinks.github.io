import json, re, subprocess, html, os, urllib.parse
from concurrent.futures import ThreadPoolExecutor
W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CODE_RE = re.compile(r"chat\.whatsapp\.com\\?/([A-Za-z0-9_\-]{10,30})")
st = json.load(open(f"{W}/team05-extracted.json"))
dead_urls = [d["url"] for d in st["dead"]]
print("refetching dead:", len(dead_urls), flush=True)
def fetch_one(url):
    try:
        r = subprocess.run(["curl","-sL","--max-time","25","--connect-timeout","10","-A",UA,
                            "-H","Accept: text/html,application/xhtml+xml","-H","Accept-Language: en-US,en;q=0.9", url],
                           capture_output=True, text=True, timeout=35)
        body = r.stdout or ""
    except Exception:
        body = ""
    codes = set(CODE_RE.findall(body))
    m = re.search(r"<title>(.*?)</title>", body, re.S|re.I)
    title = html.unescape(re.sub(r"<[^>]+>","",m.group(1))).strip() if m else ""
    ctxs = {}
    for c in codes:
        idx = body.find(c)
        seg = body[max(0,idx-500):idx+500]
        seg = re.sub(r"<script.*?</script>"," ",seg,flags=re.S|re.I)
        seg = re.sub(r"<style.*?</style>"," ",seg,flags=re.S|re.I)
        seg = re.sub(r"<[^>]+>"," ",seg)
        seg = html.unescape(seg)
        seg = re.sub(r"\s+"," ",seg).strip()[:700]
        ctxs[c] = seg
    return {"url": url, "len": len(body), "codes": sorted(codes), "title": title, "contexts": ctxs}
results = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(fetch_one, dead_urls):
        results[res["url"]] = res
        print(res["url"][:70], "len", res["len"], "codes", len(res["codes"]), flush=True)
json.dump(results, open(f"{W}/team05-refetch-dead.json","w"), indent=1, ensure_ascii=False)
# merge into extracted state
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))
new_fresh = 0
for url, res in results.items():
    if not res["codes"]:
        continue
    st["dead"] = [d for d in st["dead"] if d["url"] != url]
    for c in res["codes"]:
        e = st["codes"].setdefault(c, {"code": c, "urls": [], "contexts": [], "page_titles": []})
        if url not in e["urls"]: e["urls"].append(url)
        if c in res["contexts"]: e["contexts"].append(res["contexts"][c])
        if res["title"] and res["title"] not in e["page_titles"]: e["page_titles"].append(res["title"])
        if c not in existing: new_fresh += 1
json.dump(st, open(f"{W}/team05-extracted.json","w"), indent=1, ensure_ascii=False)
print("MERGED. total codes now:", len(st["codes"]), "new fresh codes from refetch:", new_fresh, "still dead:", len(st["dead"]), flush=True)
