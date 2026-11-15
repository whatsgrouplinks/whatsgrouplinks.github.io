import json, re, time, html, requests
WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.S)
s = requests.Session()
s.headers.update({'User-Agent': UA})

def check(code):
    try:
        r = s.get(f"https://chat.whatsapp.com/{code}", timeout=90, allow_redirects=True)
        if r.status_code == 429:
            return {"code": code, "status": "http429", "title": "", "http": 429}
        m = TITLE_RE.search(r.text)
        t = html.unescape(m.group(1)).strip() if m else ""
        return {"code": code, "status": "live" if t else "dead", "title": t, "http": r.status_code}
    except Exception as e:
        return {"code": code, "status": "transport", "title": "", "error": str(e)[:200]}

# retry home page (failed in fetch run)
try:
    r = s.get("https://linktogroups.com/en", timeout=60)
    open(f"{WD}/team18_ltg_home.html", "w", encoding="utf-8").write(r.text)
    countries = sorted(set(re.findall(r'href="https://linktogroups\.com/en/([a-z\-]+)"', r.text)))
    print("home retry:", r.status_code, "countries:", countries, flush=True)
    json.dump(countries, open(f"{WD}/team18_ltg_home_countries.json", "w"))
except Exception as e:
    print("home retry FAIL", str(e)[:200], flush=True)

resolved = json.load(open(f"{WD}/team18_ltg_new_resolved.json"))
todo = [x for x in resolved if x["destination"].startswith("https://chat.whatsapp.com/")]
print("to verify:", len(todo), flush=True)
results = {}
ckpt_path = f"{WD}/team18_verify_ckpt.jsonl"
ckpt = open(ckpt_path, "a", encoding="utf-8")
for rec in todo:
    code = rec["destination"].rstrip("/").split("/")[-1]
    res = check(code)
    res.update({"id": rec["id"], "name": rec["name"], "pages": rec["pages"], "pass": 1})
    results[code] = res
    ckpt.write(json.dumps(res, ensure_ascii=False) + "\n"); ckpt.flush()
    print(res, flush=True)
    time.sleep(3)
ckpt.close()

# spaced retries for dead / 429 / transport (2 more passes, 20s apart)
for p in (2, 3):
    need = [c for c, r in results.items() if r["status"] in ("dead", "http429", "transport")]
    if not need:
        break
    print(f"pass {p}: retrying {len(need)}", flush=True)
    time.sleep(20)
    ckpt = open(ckpt_path, "a", encoding="utf-8")
    for code in need:
        res = check(code)
        res.update({"id": results[code]["id"], "name": results[code]["name"],
                    "pages": results[code]["pages"], "pass": p})
        # keep live result if it turns live; otherwise latest
        if res["status"] == "live":
            results[code] = res
        else:
            results[code] = res
        ckpt.write(json.dumps(res, ensure_ascii=False) + "\n"); ckpt.flush()
        print(res, flush=True)
        time.sleep(3)
    ckpt.close()

json.dump(results, open(f"{WD}/team18_verify_results.json", "w"), ensure_ascii=False, indent=1)
print("SUMMARY:", {st: sum(1 for r in results.values() if r["status"] == st)
                   for st in ("live", "dead", "http429", "transport")}, flush=True)
print("DONE VERIFY")
