import json, re, subprocess, os, html, time, threading
from concurrent.futures import ThreadPoolExecutor

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
RAW = os.path.join(W, "team04_raw_pages")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{10,})")
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)
CKPT = os.path.join(W, "team04_fetch_ckpt.jsonl")

def fetch(url):
    try:
        r = subprocess.run(["curl","-sL","--max-time","25","-A",UA,url],
                           capture_output=True, text=True, timeout=35)
        return r.stdout or ""
    except Exception:
        return ""

def clean_text(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S|re.I)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S|re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

leads = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_04.json"))
done = set()
if os.path.exists(CKPT):
    with open(CKPT) as f:
        for line in f:
            try: done.add(json.loads(line)["idx"])
            except Exception: pass
print(f"resuming: {len(done)} done of {len(leads)}", flush=True)
lock = threading.Lock()

def work(item):
    i, l = item
    if i in done:
        return
    url = l["url"]; src = l.get("source","")
    body = fetch(url)
    path = os.path.join(RAW, f"{i}.html")
    with open(path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(body)
    rec = {"idx": i, "url": url, "source": src, "len": len(body), "groups": [], "dead": None, "lead_urls": []}
    if not body or len(body) < 200:
        rec["dead"] = "empty/short fetch"
    elif "api.groupjoin.link" in url:
        try:
            data = json.loads(body).get("data", [])
            for g in data:
                link = g.get("link","") or ""
                m = CODE_RE.search(link)
                if not m: continue
                rec["groups"].append({
                    "code": m.group(1), "title": (g.get("group_title") or "").strip(),
                    "desc": (g.get("group_desc") or "").strip(),
                    "category": (g.get("category") or {}).get("category_name","") if isinstance(g.get("category"), dict) else (g.get("category") or ""),
                    "country": (g.get("country") or {}).get("iso2","") if isinstance(g.get("country"), dict) else "",
                    "nsfw": g.get("nsfw"), "contentRating": g.get("contentRating"),
                    "tags": g.get("tags", []) if isinstance(g.get("tags"), list) else [],
                })
            if not rec["groups"]:
                rec["dead"] = "api json: no groups"
        except Exception as e:
            rec["dead"] = f"json parse fail: {e}"
    else:
        title_m = re.search(r"<title>(.*?)</title>", body, re.S|re.I)
        page_title = clean_text(title_m.group(1)) if title_m else ""
        plain = clean_text(body)
        seen = {}
        for m in CODE_RE.finditer(body):
            code = m.group(1)
            if code in seen: continue
            idx = plain.find(code)
            ctx = plain[max(0,idx-400):idx+150] if idx >= 0 else ""
            seen[code] = ctx
        for code, ctx in seen.items():
            rec["groups"].append({"code": code, "title": "", "desc": "",
                                  "context": ctx, "page_title": page_title,
                                  "category": "", "country": ""})
        # discovered listing-page leads: same-domain hrefs that look like category/tag/list pages
        for h in set(HREF_RE.findall(body)):
            h = html.unescape(h).strip()
            if not h or h.startswith("#") or h.startswith("javascript:"):
                continue
            if "chat.whatsapp.com" in h or "whatsapp.com/channel" in h:
                continue
            if h.startswith("/"):
                from urllib.parse import urlparse
                base = urlparse(url)
                h = f"{base.scheme}://{base.netloc}{h}"
            if h == url:
                continue
            low = h.lower()
            if any(k in low for k in ("/category", "/tag", "/tags", "/groups", "/group-links", "/whatsapp-group", "page=", "/p/", "/list", "/categories")):
                rec["lead_urls"].append(h)
        if not rec["groups"]:
            rec["dead"] = "no invite codes on page"
    with lock:
        with open(CKPT, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{i} len={len(body)} groups={len(rec['groups'])} leads={len(rec['lead_urls'])} {url[:70]}", flush=True)

todo = [(i,l) for i,l in enumerate(leads) if i not in done]
print(f"todo: {len(todo)}", flush=True)
with ThreadPoolExecutor(max_workers=5) as ex:
    list(ex.map(work, todo))
print("FETCH DONE", flush=True)
