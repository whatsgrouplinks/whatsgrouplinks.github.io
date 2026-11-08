import requests, re, json, time
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
URLS = [
 ("grupbul-ganar-bitcoins", "https://grupbul.com/group/915743"),
 ("grupbul-free-bitcoin-cash", "https://grupbul.com/group/479310"),
 ("grupbul-bitcoin-earn", "https://grupbul.com/group/742466"),
 ("grupbul-btc-eth-ltc", "https://grupbul.com/group/358957"),
 ("grouplinksforyou-forex", "https://www.grouplinksforyou.com/search/label/Forex%20Trading?&max-results=5"),
]
out = {}
for label, url in URLS:
    try:
        r = requests.get(url, headers=UA, timeout=30)
        print(label, r.status_code, len(r.text))
        out[label] = {"url": url, "status": r.status_code, "html": r.text}
    except Exception as e:
        print(label, "ERR", e)
        out[label] = {"url": url, "status": 0, "html": "", "error": str(e)}
    time.sleep(1)
json.dump(out, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_raw2.json","w"))
pat = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/dedupe_union.json")))
for label, d in out.items():
    codes = sorted(set(pat.findall(d["html"])))
    fresh = [c for c in codes if c not in union]
    print(label, "uniq:", len(codes), "fresh:", fresh)
    # title
    m = re.search(r'<title>(.*?)</title>', d["html"], re.S)
    print("   title:", (m.group(1).strip()[:120] if m else ""))
