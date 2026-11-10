#!/usr/bin/env python3
"""Team 01 wave 20261110 slice 1 - step 2: retry failed pages, re-extract discovery (incl. relative hrefs + sitemap)."""
import json, os, re, subprocess, time, html as htmlmod
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site"
WAVE = os.path.join(BASE, "agent_batches/wave_20261110")
RAW = os.path.join(WAVE, "team01_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

leads = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_01.json"))
existing = set(json.load(open(os.path.join(BASE, ".existing_codes.json"))))
groups = json.load(open(os.path.join(BASE, "groups.json")))
for it in groups:
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]+)', it.get('invite', ''))
    if m:
        existing.add(m.group(1))
print("existing union codes:", len(existing), flush=True)

CODE_RE = re.compile(r"chat\.whatsapp\.com(?:/|\\u002f|\\/|%2F)+(?:invite/)?([A-Za-z0-9_\-]{8,})")

def clean_text(s):
    s = htmlmod.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# --- retry failed/missing pages: indices from fetch log with 000/ERR, plus p005 ---
log = json.load(open(os.path.join(WAVE, "team01_fetch_log.json")))
retry_idx = [r["idx"] for r in log if r["fetch"].startswith("000") or r["fetch"].startswith("ERR")]
if not os.path.exists(os.path.join(RAW, "p005.html")):
    retry_idx.append(5)
retry_idx = sorted(set(retry_idx))
print("retry indices:", retry_idx, flush=True)

def fetch_one(i):
    url = leads[i]["url"]
    fn = os.path.join(RAW, f"p{i:03d}.html")
    try:
        r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "40",
                            "-o", fn, "-w", "%{http_code} %{size_download}", url],
                           capture_output=True, text=True, timeout=55)
        return i, r.stdout.strip()
    except Exception as e:
        return i, f"ERR {e}"

with ThreadPoolExecutor(max_workers=2) as ex:
    for i, status in ex.map(fetch_one, retry_idx):
        print(f"retry {i} {status} {leads[i]['url']}", flush=True)

# --- full re-extraction over all raw files ---
input_urls = {l["url"] for l in leads}
all_ctx = {}
try:
    all_ctx = json.load(open(os.path.join(WAVE, "team01_context.json")))
except Exception:
    all_ctx = {}
discovered = {}
try:
    for d in json.load(open(os.path.join(WAVE, "team01_discovered_raw.json"))):
        discovered[d["url"]] = d["found_on"]
except Exception:
    pass
fresh = {}
results = {r["idx"]: r for r in log}

for i, lead in enumerate(leads):
    url = lead["url"]
    fn = os.path.join(RAW, f"p{i:03d}.html")
    if not os.path.exists(fn):
        continue
    html = open(fn, encoding="utf-8", errors="ignore").read()
    if len(html) < 500:
        continue
    unesc = html.replace('\\"', '"').replace("\\/", "/")
    # context: whatsappkanali/linkado JSON objects
    for m in re.finditer(r'"title"\s*:\s*"([^"]{2,120})"\s*,\s*"description"\s*:\s*"([^"]{0,500})"\s*,\s*"categoryName"\s*:\s*"([^"]{1,60})"', unesc):
        tail = unesc[m.end():m.end()+1500]
        im = re.search(r'"inviteUrl"\s*:\s*"https://chat\.whatsapp\.com/([A-Za-z0-9_\-]{8,22})"', tail)
        if im:
            all_ctx.setdefault(im.group(1), {"name": clean_text(m.group(1)), "description": clean_text(m.group(2)),
                "category_raw": clean_text(m.group(3)), "country": "TR" if "whatsappkanali" in url else "BR",
                "listing_url": url, "source": lead.get("source", "")})
    # groupinvite detail page meta for its own + related codes
    if "groupsinvite.link/group/link/" in url:
        t = re.search(r'<title>(.*?)</title>', html, re.S)
        cm = re.search(r'/group/country/([a-z\-]+)/', html)
        catm = re.search(r'/group/category/([a-z\-]+)/', html)
        dm = re.search(r'<meta name="description" content="([^"]*)"', html)
        name = clean_text(t.group(1)) if t else ""
        name = re.sub(r'\s*WhatsApp Group Invite Link.*$', '', name, flags=re.I).strip()
        name = re.sub(r'\s*\|\s*GroupsInvite.*$', '', name).strip()
        for m in CODE_RE.finditer(html):
            code = m.group(1)
            if len(code) > 22:
                code = code[:22]
            if code not in all_ctx:
                all_ctx[code] = {"name": name, "description": clean_text(dm.group(1)) if dm else "",
                    "category_raw": catm.group(1) if catm else "", "country": cm.group(1) if cm else "",
                    "listing_url": url, "source": lead.get("source", "")}
    codes = set()
    for m in CODE_RE.finditer(html):
        c = m.group(1)
        if len(c) > 22:
            c = c[:22]
        if c.lower() == "invite":
            continue
        codes.add(c)
    fresh_here = [c for c in codes if c not in existing]
    for c in fresh_here:
        fresh.setdefault(c, url)
        all_ctx.setdefault(c, {"name": "", "description": "", "category_raw": "",
            "country": "TR" if "whatsappkanali" in url else ("BR" if "linkado" in url else ""),
            "listing_url": url, "source": lead.get("source", "")})
    if i in results:
        results[i]["codes_found"] = len(codes)
        results[i]["fresh"] = len(fresh_here)
        results[i]["fresh_codes"] = sorted(fresh_here)
        if i in retry_idx:
            try:
                results[i]["fetch"] = "retry:" + str(os.path.getsize(fn))
            except Exception:
                pass
    # discovery: absolute + relative hrefs
    for m in re.finditer(r'href="((?:https://(?:groupsinvite\.link|whatsappkanali\.com|linkado\.app))?/(?:group/link/|group/category/|group/country/|sehir/|grup/|grupo/|categorias?/|categoria/|populares)[^"]*)"', html):
        u = m.group(1)
        if u.startswith("/"):
            dom = "groupsinvite.link" if "groupsinvite" in url else ("whatsappkanali.com" if "whatsappkanali" in url else "linkado.app")
            u = "https://" + dom + u
        u = u.split("#")[0].rstrip("/")
        if u in input_urls or u == url.rstrip("/"):
            continue
        discovered.setdefault(u, url)
    # linkado sitemap grupo urls
    if url.endswith("sitemap.xml"):
        for m in re.finditer(r'<loc>(https://linkado\.app/grupo/[^<]+)</loc>', html):
            discovered.setdefault(m.group(1).rstrip("/"), url)

json.dump(list(results.values()), open(os.path.join(WAVE, "team01_fetch_log.json"), "w"), indent=1)
json.dump({c: u for c, u in sorted(fresh.items())},
          open(os.path.join(WAVE, "team01_fresh_codes.json"), "w"), indent=1)
json.dump(all_ctx, open(os.path.join(WAVE, "team01_context.json"), "w"), indent=1, ensure_ascii=False)
json.dump([{"url": u, "found_on": s} for u, s in sorted(discovered.items())],
          open(os.path.join(WAVE, "team01_discovered_raw.json"), "w"), indent=1)
print("TOTAL fresh unique codes:", len(fresh))
print("TOTAL discovered listing urls:", len(discovered))
print("TOTAL ctx entries:", len(all_ctx))
