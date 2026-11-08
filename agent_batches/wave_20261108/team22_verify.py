import json, re, time, html, requests
names = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_fresh_names.json"))
# fix names for the 4 checked codes
names["CindfGo478i2qz49wyN4vB"]["name_ctx"] = "Real Online Earning No Scam"
names["HDXdN6CBXEkCGldXqtfEa7"]["name_ctx"] = "Binance Big Signals"
names["Ge1yF51cHAMEU2ayEw2JRR"]["name_ctx"] = "Best Buy"
names["FGCjBbFnDm655h3aBIhpF9"]["name_ctx"] = "Investors Alliance"

DROP_SCAM = {"I3saZjXGVj6A8zlfzq8Xg7","KavylKrdt9hAqybQVZpJMn","L9iSXPHidh84ZRe9qSs4NH","LHJP0kfGiHv8agIRNpqWPd"}
SKIP_OOS = {"0Y7Ptz9CIOBDugnwqT6ZHi","4n0iv98qCmj0Fnq6Npm8kU","9LHaCY8PpgCIGENrSxM9o5","Bfz32si8drcI1LD06P9lPb","DRIfzjfftY3Cx2WykOekF","DTXIQl7Fbxp795dGqrg0xg","FGPTZsNmiMn1Gr2NGrX0Rj","GireW9e1QkN5rA0PAXW06E","GrojEfuzq1r7oUrf8tPcj2","Grqql1clYg09eBIj4DY60l","HWmUdLdEfFPGIb3CGqknZK","Hrjh8cjHWPqJjeoGKQaFwI","J1LO3khUGbr4RUoluZULYD","JZPnk3bQ8V1L0heM7eo0HJ"}
todo = [c for c in names if c not in DROP_SCAM and c not in SKIP_OOS]
print("to verify:", len(todo), "dropped scam:", len(DROP_SCAM), "skipped oos:", len(SKIP_OOS))
json.dump({"drop_scam": sorted(DROP_SCAM), "skip_oos": sorted(SKIP_OOS), "todo": todo},
          open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_todo.json","w"))

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in (1,2):
        try:
            s = requests.Session()
            r = s.get(url, headers=UA, timeout=20)
            m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
            if not m:
                m = re.search(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:title\"", r.text)
            title = html.unescape(m.group(1)).strip() if m else ""
            return {"code": code, "status": r.status_code, "title": title, "attempt": attempt, "error": ""}
        except Exception as e:
            err = str(e)
            if attempt == 1:
                time.sleep(3)
                continue
            return {"code": code, "status": 0, "title": "", "attempt": attempt, "error": err}
    return {"code": code, "status": 0, "title": "", "attempt": 2, "error": "unknown"}

results = []
for i, code in enumerate(todo):
    res = check(code)
    results.append(res)
    print(i+1, code, res["status"], repr(res["title"][:80]), res["error"][:60])
    time.sleep(0.7)
json.dump(results, open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_verify_raw.json","w"), indent=1)
live = [r for r in results if r["status"]==200 and r["title"] and r["title"] not in ("WhatsApp Group","Join this group on WhatsApp")]
print("LIVE named:", len(live), "| 200-empty:", len([r for r in results if r["status"]==200 and not r["title"]]), "| non200:", len([r for r in results if r["status"]!=200]))
