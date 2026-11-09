import json, re, subprocess, sys, time, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})")

def fetch(url):
    try:
        r = subprocess.run(["curl","-sL","--max-time","30","-A",UA,url],
                           capture_output=True, text=True, timeout=45)
        return r.stdout or ""
    except Exception as e:
        return ""

def norm(code):
    return code.split("?")[0].split("#")[0].rstrip("/")

leads = json.load(open("leads_slice_04.json"))
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
seen = {}
dead = []
new_leads = []
for i, l in enumerate(leads):
    url = l["url"]; src = l.get("source","")
    body = fetch(url)
    if not body or len(body) < 200:
        dead.append({"url":url,"source":src,"note":"empty/short fetch"})
        print(i, "DEAD/EMPTY", url[:90], len(body), flush=True); continue
    codes = set(norm(c) for c in CODE_RE.findall(body))
    # also discover other listing URLs on same domain (pagination / related)
    for m in re.findall(r'href="([^"]+)"', body):
        u = urllib.parse.urljoin(url, m)
        if u.startswith("http") and "chat.whatsapp.com" not in u:
            # keep same-domain listing-ish links
            if any(d in u for d in ["appgrouplink.com/","whtspgrouplink.com/","linkado.app/categoria","igrupos.com/tag","groupizo.com/"]):
                if u != url and u not in [x["url"] for x in leads]:
                    new_leads.append({"url":u,"source":"team04-discovered","from":url})
    fresh = [c for c in codes if c not in existing and c not in seen]
    dup = len(codes) - len(fresh)
    for c in fresh:
        seen[c] = {"code":c,"from_url":url,"from_source":src}
    print(i, "codes", len(codes), "fresh", len(fresh), "dup", dup, url[:80], flush=True)
    time.sleep(0.3)

json.dump(list(seen.values()), open("team04_raw_fresh.json","w"), indent=1)
json.dump(dead, open("team04_dead_listings.json","w"), indent=1)
# dedupe new leads
uniq = {}
for x in new_leads: uniq[x["url"]] = x
json.dump(list(uniq.values()), open("team04_discovered_leads.json","w"), indent=1)
print("TOTAL fresh codes:", len(seen), "dead listings:", len(dead), "discovered leads:", len(uniq))
