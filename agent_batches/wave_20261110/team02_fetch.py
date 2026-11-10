#!/usr/bin/env python3
"""Team 02 wave 20261110 slice 2: fetch groupsinvite.link listing + rules pages.
Fresh re-run of wave_20261109 leads_slice_02 (184 URLs). Union dedupe =
.existing_codes.json + invite codes in groups.json. 3 parallel workers."""
import json, re, subprocess, html, os
from concurrent.futures import ThreadPoolExecutor

WAVE10 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
WAVE09 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CKPT = f"{WAVE10}/team02-extracted.json"
PROB = f"{WAVE10}/team02-fetch-problems.json"
LEADS = f"{WAVE10}/team02-new-leads-raw.json"

def fetch(url):
    try:
        r = subprocess.run(["curl","-s","-L","--max-time","60","-A",UA,url],
                           capture_output=True, timeout=70)
        return r.stdout.decode("utf-8", errors="ignore"), r.returncode
    except Exception:
        return "", -1

def norm_code(raw):
    return raw.split("?")[0].split("#")[0].rstrip("/")

existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
groups = json.load(open("/home/hatch/workspace/whatsapp-groups-site/groups.json"))
gcode_re = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)')
for e in groups:
    m = gcode_re.search(e.get("invite",""))
    if m:
        existing.add(m.group(1))
print(f"union={len(existing)}", flush=True)

slice_urls = json.load(open(f"{WAVE09}/leads_slice_02.json"))

done = {}
problems = {"dead": [], "transport_fail": []}
new_leads = {}
if os.path.exists(CKPT):
    for r in json.load(open(CKPT)):
        done[r["listing_url"]] = r
if os.path.exists(PROB):
    problems = json.load(open(PROB))
    for p in problems["dead"] + problems["transport_fail"]:
        done[p["url"]] = {"_problem": True}
if os.path.exists(LEADS):
    for l in json.load(open(LEADS)):
        new_leads[l["url"]] = l["source"]

COUNTRY_MAP = {"india":"IN","pakistan":"PK","bangladesh":"BD","nepal":"NP","sri-lanka":"LK",
 "united-states":"US","usa":"US","united-kingdom":"UK","uk":"GB","canada":"CA","australia":"AU",
 "uae":"AE","saudi-arabia":"SA","nigeria":"NG","kenya":"KE","ghana":"GH","south-africa":"ZA",
 "indonesia":"ID","malaysia":"MY","philippines":"PH","germany":"DE","france":"FR"}

def save():
    json.dump([v for v in done.values() if "_problem" not in v],
              open(CKPT,"w"), ensure_ascii=False, indent=1)
    json.dump(problems, open(PROB,"w"), ensure_ascii=False, indent=1)
    json.dump([{"url": u, "source": s} for u, s in sorted(new_leads.items())],
              open(LEADS,"w"), ensure_ascii=False, indent=1)

def process(item):
    url = item["url"]; src = item.get("source","")
    if url in done:
        return ("skip", url)
    listing_id = url.rstrip("/").split("/")[-1]
    body, rc = fetch(url)
    if not body or len(body) < 500:
        problems["transport_fail"].append({"url": url, "source": src, "stage": "listing", "note": f"empty/short fetch rc={rc}"})
        done[url] = {"_problem": True}
        return ("fail-listing", url)
    title_m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
    title = html.unescape(title_m.group(1)).strip() if title_m else ""
    if not title:
        tm = re.search(r'<title>([^<]*)</title>', body)
        title = html.unescape(tm.group(1)).replace(" WhatsApp Group Invite Link | GroupsInvite","").strip() if tm else ""
    desc_m = re.search(r'data-full-description="([^"]*)"', body)
    desc = html.unescape(desc_m.group(1)).strip() if desc_m else ""
    country = "IN"
    cm = re.search(r'href="https://groupsinvite\.link/group/country/([^"/]+)/"', body)
    if cm:
        country = COUNTRY_MAP.get(cm.group(1).lower(), "IN")
    for rid in set(re.findall(r'https://groupsinvite\.link/group/link/([a-z0-9]+)/', body)):
        rurl = f"https://groupsinvite.link/group/link/{rid}/"
        if rurl != url:
            new_leads.setdefault(rurl, "groupsinvite.link related group (found on listing page)")
    rules_url = f"https://groupsinvite.link/group/rules/{listing_id}/"
    rbody, rrc = fetch(rules_url)
    codes = re.findall(r'chat\.whatsapp\.com/invite/([A-Za-z0-9_\-]+)', rbody)
    codes += re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]{15,})', rbody)
    codes = [norm_code(c) for c in codes if norm_code(c).lower() != "invite"]
    if not codes:
        if not rbody or len(rbody) < 500:
            problems["transport_fail"].append({"url": url, "source": src, "stage": "rules", "note": f"empty rules fetch rc={rrc}", "title": title})
        else:
            problems["dead"].append({"url": url, "source": src, "title": title, "note": "no invite code on rules page (JS-gated?)"})
        done[url] = {"_problem": True}
        return ("no-code", url)
    code = codes[0]
    status = "new"
    if code in existing: status = "dup-existing"
    elif any(v.get("code")==code for v in done.values() if "_problem" not in v): status = "dup-in-slice"
    rec = {"listing_url": url, "rules_url": rules_url, "code": code,
           "title": title, "description": desc, "country": country,
           "status": status, "source": src}
    done[url] = rec
    return (status, f"{code} :: {title}")

todo = [it for it in slice_urls if it["url"] not in done]
print(f"slice={len(slice_urls)} already_done={len(done)} todo={len(todo)}", flush=True)
n = 0
with ThreadPoolExecutor(max_workers=4) as ex:
    for status, info in ex.map(process, todo):
        n += 1
        print(f"[{n}/{len(todo)}] {status} {info}", flush=True)
        if n % 10 == 0:
            save()
save()
res = [v for v in done.values() if "_problem" not in v]
print(f"DONE extracted={len(res)} new={sum(1 for r in res if r['status']=='new')} "
      f"dup-existing={sum(1 for r in res if r['status']=='dup-existing')} "
      f"dup-in-slice={sum(1 for r in res if r['status']=='dup-in-slice')} "
      f"dead={len(problems['dead'])} transport_fail={len(problems['transport_fail'])} new_leads={len(new_leads)}")
