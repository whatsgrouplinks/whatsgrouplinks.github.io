import requests, re, json, time, html

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
URLS = [
 ("thinkingoutsidethesandbox-business", "https://thinkingoutsidethesandbox.ca/135-best-business-whatsapp-group-links/"),
 ("newgrouplinks-crypto", "https://newgrouplinks.pk/crypto-trading-whatsapp-group-links/"),
 ("grouplink-com-in-1800", "https://grouplink.com.in/1800-new-whatsapp-group-link/"),
 ("wahublink-earning", "https://wahublink.com/online-earning-whatsapp-group-links/"),
 ("joingram-earning", "https://joingram.in/online-earning-whatsapp-group-links/"),
 ("whatstele-stock", "https://whatstele.com/whatsapp/group-links/stock-market/"),
 ("freshgrouplinks-crypto", "https://freshgrouplinks.com/crypto-trading-whatsapp-group-links/"),
 ("coinweb-signals", "https://coinweb.com/crypto-trading-signals-on-whatsapp/"),
 ("blockpool-crypto", "https://blockpool.io/blog/best-crypto-whatsapp-groups.html"),
 ("77links-earning", "https://77links.com/online-earning-whatsapp-groups/"),
 ("groupsgyani", "https://groupsgyani.org/whatsapp-group-links"),
 ("activewagroup", "https://activewagroup.com/"),
 ("groupsop-investors", "https://groupsop.shop/invite/FGCjBbFnDm655h3aBIhpF9"),
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
json.dump(out, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_raw.json","w"))
print("saved")
