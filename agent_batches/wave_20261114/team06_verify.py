#!/usr/bin/env python3
"""team06 whts.club re-check: verify the 39 apparent-new sitemap entries.
Controls first; then fetch each page, extract invite code, dedupe vs union,
verify non-dupe codes with a keep-alive Session. Bank partial results."""
import json, re, time, requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
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

# ---- CONTROLS ----
print("CONTROL live:", og_title("KrDwdK8EIkB6vgauHg5M7N"), flush=True)
print("CONTROL fabricated:", og_title("ZzZzZzZzZzZzZzZzZzZzZzZz"), flush=True)

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
print("union size:", len(union), flush=True)

entries = json.load(open(f"{WAVE}/team06-sitemap-entries.json"))
mined = set(json.load(open(f"{WAVE}/team06-mined-set.json")))
# 6554 confirmed mined at code level by team16 verify-out (HQPCFBLlmukBYsQQSedLPr dead-empty)
diff = [e for e in entries if e["url"] not in mined]
print("diff count:", len(diff), flush=True)

CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
META_RE = re.compile(r'<meta name="description" content="([^"]*)"', re.S)

pages = []
for e in diff:
    try:
        r = S.get(e["url"], timeout=60)
        html = r.text
        codes = list(dict.fromkeys(CODE_RE.findall(html)))
        t = TITLE_RE.search(html)
        md = META_RE.search(html)
        pages.append({"url": e["url"], "lastmod": e["lastmod"], "http": r.status_code,
                      "title": (t.group(1).strip() if t else ""),
                      "meta_desc": (md.group(1).strip() if md else ""),
                      "codes": codes})
        print("PAGE", e["url"], r.status_code, codes, flush=True)
        time.sleep(0.5)
    except Exception as ex:
        pages.append({"url": e["url"], "lastmod": e["lastmod"], "http": "ERR",
                      "title": "", "meta_desc": "", "codes": [], "err": str(ex)})
        print("PAGE ERR", e["url"], ex, flush=True)

json.dump(pages, open(f"{WAVE}/team06-pages.json", "w"), ensure_ascii=False, indent=1)

# classify codes (dedupe within team + vs union) happens in to_verify build below
to_verify = []
seen = set()
for p in pages:
    for c in p["codes"]:
        if c in seen:
            continue
        seen.add(c)
        if c not in union:
            to_verify.append({"url": p["url"], "title": p["title"], "meta_desc": p["meta_desc"], "code": c})
print("codes to verify (fresh, non-union):", len(to_verify), flush=True)

verify_out = []
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
    verify_out.append(v2)
    print("VERIFY", v["code"], v2["status"], repr(title)[:80], flush=True)
    time.sleep(1.0)

json.dump(verify_out, open(f"{WAVE}/team06-verify-out.json", "w"), ensure_ascii=False, indent=1)
print("done. live:", sum(1 for v in verify_out if v["status"]=="live"),
      "dead:", sum(1 for v in verify_out if v["status"]=="dead-empty"),
      "pending:", sum(1 for v in verify_out if v["status"]=="pending"), flush=True)
