import json, re, subprocess, time, html, os
W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
leads = json.load(open(f"{W}/leads_slice_05.json"))
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{10,30})")
def fetch(url):
    try:
        r = subprocess.run(["curl","-sL","--max-time","30","-A",UA,url], capture_output=True, text=True, timeout=40)
        return r.stdout or ""
    except Exception as e:
        return ""
out = {}  # code -> {urls:[], contexts:[], page_titles:[]}
dead = []
for i, item in enumerate(leads):
    url = item["url"]
    body = fetch(url)
    if not body or len(body) < 500:
        dead.append({"url":url,"source":item.get("source"),"note":"fetch empty/short"})
        print(i, "DEAD", url, len(body)); continue
    codes = CODE_RE.findall(body)
    # also title
    m = re.search(r"<title>(.*?)</title>", body, re.S|re.I)
    title = html.unescape(re.sub(r"<[^>]+>","",m.group(1))).strip() if m else ""
    print(i, url, "codes:", len(set(codes)), "len", len(body))
    if not codes:
        dead.append({"url":url,"source":item.get("source"),"note":"no invite codes on page"})
    for c in set(codes):
        # context: find first occurrence, grab surrounding text stripped of tags
        idx = body.find(c)
        seg = body[max(0,idx-600):idx+600]
        seg = re.sub(r"<script.*?</script>"," ",seg,flags=re.S|re.I)
        seg = re.sub(r"<style.*?</style>"," ",seg,flags=re.S|re.I)
        seg = re.sub(r"<[^>]+>"," ",seg)
        seg = html.unescape(seg)
        seg = re.sub(r"\s+"," ",seg).strip()[:800]
        e = out.setdefault(c, {"code":c,"urls":[],"contexts":[],"page_titles":[]})
        e["urls"].append(url)
        e["contexts"].append(seg)
        if title and title not in e["page_titles"]: e["page_titles"].append(title)
    time.sleep(0.3)
json.dump({"codes": out, "dead": dead}, open(f"{W}/team05-extracted.json","w"), indent=1, ensure_ascii=False)
fresh = [c for c in out if c not in existing]
print("TOTAL unique codes:", len(out), "fresh (not in existing):", len(fresh))
print("dead pages:", len(dead))
