#!/usr/bin/env python3
"""team06 retry: re-fetch the 19 pages that failed with ProxyError.
Fresh session per page + Connection: close (the keep-alive pool was
returning a dead pooled connection on alternating requests)."""
import json, re, time, requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
META_RE = re.compile(r'<meta name="description" content="([^"]*)"', re.S)

pages = json.load(open(f"{WAVE}/team06-pages.json"))
failed = [p for p in pages if p.get("http") == "ERR"]
print("retrying", len(failed), "failed pages", flush=True)

def fetch_page(url):
    for attempt in range(1, 4):
        try:
            s = requests.Session()
            s.headers.update(UA)
            s.headers.update({"Connection": "close"})
            r = s.get(url, timeout=60)
            s.close()
            return r.status_code, r.text
        except Exception as e:
            print(f"  attempt {attempt} {url} ERR {type(e).__name__}", flush=True)
            time.sleep(6 * attempt)
    return "ERR", ""

for p in failed:
    status, html = fetch_page(p["url"])
    p["http"] = status
    p.pop("err", None)
    if status == 200:
        p["codes"] = list(dict.fromkeys(CODE_RE.findall(html)))
        t = TITLE_RE.search(html)
        md = META_RE.search(html)
        p["title"] = t.group(1).strip() if t else ""
        p["meta_desc"] = md.group(1).strip() if md else ""
    print("PAGE", p["url"], status, p.get("codes"), flush=True)
    time.sleep(1.0)

json.dump(pages, open(f"{WAVE}/team06-pages.json", "w"), ensure_ascii=False, indent=1)

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
prev = json.load(open(f"{WAVE}/team06-verify-out.json"))
done_codes = {v["code"] for v in prev}
to_verify = []
seen = set()
for p in pages:
    for c in p.get("codes", []):
        if c in seen or c in done_codes or c in union:
            continue
        seen.add(c)
        to_verify.append({"url": p["url"], "title": p["title"], "meta_desc": p["meta_desc"], "code": c})
print("fresh codes still to verify:", len(to_verify), flush=True)

S = requests.Session()
S.headers.update(UA)

def og_title(code):
    try:
        r = S.get(f"https://chat.whatsapp.com/{code}", timeout=75)
        if r.status_code == 429:
            return ("pending-429", "", r.status_code)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        return ("ok", (m.group(1).strip() if m else ""), r.status_code)
    except Exception as e:
        return ("pending-transport", "", str(e))

for v in to_verify:
    status, title, http = og_title(v["code"])
    tries = 1
    while status == "ok" and title == "" and tries < 3:
        time.sleep(8)
        tries += 1
        status, title, http = og_title(v["code"])
    v2 = dict(v)
    v2["status"] = ("live" if (status == "ok" and title) else
                    ("pending" if status.startswith("pending") else "dead-empty"))
    v2["og_title"] = title
    v2["http"] = http
    v2["tries"] = tries
    prev.append(v2)
    print("VERIFY", v["code"], v2["status"], repr(title)[:80], flush=True)
    time.sleep(1.0)

json.dump(prev, open(f"{WAVE}/team06-verify-out.json", "w"), ensure_ascii=False, indent=1)
print("TOTAL verified:", len(prev), "live:", sum(1 for v in prev if v["status"] == "live"),
      "dead:", sum(1 for v in prev if v["status"] == "dead-empty"),
      "pending:", sum(1 for v in prev if v["status"] == "pending"), flush=True)
print("pages still failed:", sum(1 for p in pages if p.get("http") == "ERR"), flush=True)
