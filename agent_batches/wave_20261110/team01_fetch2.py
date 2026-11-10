#!/usr/bin/env python3
"""Team 01 wave 20261110 slice 1: fetch listing pages, extract invite codes + context.
Parallel (3 workers), checkpointed, resumes from cached raw files."""
import json, os, re, subprocess, time, html as htmlmod
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/whatsapp-groups-site"
WAVE = os.path.join(BASE, "agent_batches/wave_20261110")
RAW = os.path.join(WAVE, "team01_raw")
os.makedirs(RAW, exist_ok=True)
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

def fetch_one(args):
    i, lead = args
    url = lead["url"]
    fn = os.path.join(RAW, f"p{i:03d}.html")
    if os.path.exists(fn) and os.path.getsize(fn) > 500:
        return i, "cached", fn
    try:
        r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "25",
                            "-o", fn, "-w", "%{http_code} %{size_download}", url],
                           capture_output=True, text=True, timeout=35)
        return i, r.stdout.strip(), fn
    except Exception as e:
        return i, f"ERR {e}", fn

def clean_text(s):
    s = htmlmod.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def process(i, lead, fn):
    url = lead["url"]
    try:
        html = open(fn, encoding="utf-8", errors="ignore").read()
    except Exception:
        html = ""
    ctx = {}
    unesc = html.replace('\\"', '"').replace("\\/", "/")
    for m in re.finditer(r'"title"\s*:\s*"([^"]{2,120})"\s*,\s*"description"\s*:\s*"([^"]{0,500})"\s*,\s*"categoryName"\s*:\s*"([^"]{1,60})"', unesc):
        tail = unesc[m.end():m.end()+1500]
        im = re.search(r'"inviteUrl"\s*:\s*"https://chat\.whatsapp\.com/([A-Za-z0-9_\-]{8,22})"', tail)
        if im:
            code = im.group(1)
            ctx.setdefault(code, {"name": clean_text(m.group(1)), "description": clean_text(m.group(2)),
                                  "category_raw": clean_text(m.group(3)), "country": "TR" if "whatsappkanali" in url else "BR",
                                  "listing_url": url, "source": lead.get("source", "")})
    if "linkado" in url and "sitemap" not in url:
        for m in re.finditer(r'"(?:name|titulo|title)"\s*:\s*"([^"]{2,120})"', unesc):
            tail = unesc[m.end():m.end()+2000]
            im = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{8,22})', tail)
            if im:
                code = im.group(1)
                if code not in ctx:
                    ctx.setdefault(code, {"name": clean_text(m.group(1)), "description": "",
                                          "category_raw": "", "country": "BR",
                                          "listing_url": url, "source": lead.get("source", "")})
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
            if code not in ctx:
                ctx[code] = {"name": name, "description": clean_text(dm.group(1)) if dm else "",
                             "category_raw": catm.group(1) if catm else "",
                             "country": cm.group(1) if cm else "",
                             "listing_url": url, "source": lead.get("source", "")}
    codes = set()
    for m in CODE_RE.finditer(html):
        c = m.group(1)
        if len(c) > 22:
            c = c[:22]
        if c.lower() in ("invite",):
            continue
        codes.add(c)
    fresh = [c for c in codes if c not in existing]
    for c in fresh:
        ctx.setdefault(c, {"name": "", "description": "", "category_raw": "",
                           "country": "TR" if "whatsappkanali" in url else ("BR" if "linkado" in url else ""),
                           "listing_url": url, "source": lead.get("source", "")})
    discovered = {}
    input_urls = {l["url"] for l in leads}
    for m in re.finditer(r'href="(https://(?:groupsinvite\.link|whatsappkanali\.com|linkado\.app)[^"]+)"', html):
        u = m.group(1).split("#")[0].rstrip("/")
        if u in input_urls or u == url.rstrip("/"):
            continue
        if re.search(r'/(group/link/|group/category/|group/country/|sehir/|grup/|grupo/|categorias?/|categoria/|populares)', u):
            discovered.setdefault(u, url)
    return {"idx": i, "url": url, "source": lead.get("source", ""),
            "bytes": len(html), "codes_found": len(codes), "fresh": len(fresh),
            "fresh_codes": sorted(fresh)}, ctx, discovered

results = [None] * len(leads)
all_ctx = {}
all_disc = {}
done = [0]
t0 = time.time()
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(fetch_one, (i, leads[i])): i for i in range(len(leads))}
    for fut in futs:
        i, status, fn = fut.result()
        res, ctx, disc = process(i, leads[i], fn)
        res["fetch"] = status
        results[i] = res
        all_ctx.update(ctx)
        all_disc.update(disc)
        done[0] += 1
        print(f"{i:3d} {status} bytes={res['bytes']} codes={res['codes_found']} fresh={res['fresh']} {leads[i]['url']} [{done[0]}/{len(leads)} {time.time()-t0:.0f}s]", flush=True)
        if done[0] % 10 == 0:
            json.dump([r for r in results if r], open(os.path.join(WAVE, "team01_fetch_log.json"), "w"), indent=1)
            json.dump(all_ctx, open(os.path.join(WAVE, "team01_context.json"), "w"), indent=1, ensure_ascii=False)

seen_new = {}
for r in results:
    for c in r["fresh_codes"]:
        seen_new.setdefault(c, r["url"])
json.dump(results, open(os.path.join(WAVE, "team01_fetch_log.json"), "w"), indent=1)
json.dump({c: u for c, u in sorted(seen_new.items())},
          open(os.path.join(WAVE, "team01_fresh_codes.json"), "w"), indent=1)
json.dump(all_ctx, open(os.path.join(WAVE, "team01_context.json"), "w"), indent=1, ensure_ascii=False)
json.dump([{"url": u, "found_on": s} for u, s in sorted(all_disc.items())],
          open(os.path.join(WAVE, "team01_discovered_raw.json"), "w"), indent=1)
print("TOTAL fresh unique codes:", len(seen_new))
print("TOTAL pages:", len(results))
print("TOTAL discovered listing urls:", len(all_disc))
print("TOTAL ctx entries:", len(all_ctx))
print("ELAPSED", round(time.time() - t0, 1))
